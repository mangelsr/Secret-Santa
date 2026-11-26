from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import secrets
import time
from typing import Dict, List, Optional, Tuple
import uuid

from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import settings
from app.core.santa_draw import generate_secret_santa_draw
from app.core.security import hash_passcode, mask_email, verify_passcode
from app.schemas.models import (
    CreateGroupRequest,
    ExecuteDrawRequest,
    GroupPublicResponse,
    GroupWithParticipantsResponse,
    ParticipantPublicResponse,
    RegisterParticipantRequest,
    UpdateParticipantRequest,
)
from app.services.dynamodb import (
    DrawAlreadyInProgressError,
    DuplicateEmailError,
    GroupClosedError,
    ParticipantNotFoundError,
    db_service,
)
from app.services.email_service import email_service

router = APIRouter(prefix="/api/v1")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check_group_lockout(group: Dict) -> None:
    locked_until = int(group.get("passcode_locked_until", 0) or 0)
    now_ts = int(time.time())
    if locked_until > now_ts:
        remaining_minutes = max(1, (locked_until - now_ts + 59) // 60)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed passcode attempts. Try again in {remaining_minutes} minute(s).",
        )


def _verify_group_admin_passcode(group: Dict, provided_passcode: Optional[str]) -> None:
    _check_group_lockout(group)

    if not provided_passcode:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin passcode is required",
        )

    if not verify_passcode(provided_passcode, group["admin_passcode"]):
        db_service.record_failed_passcode_attempt(
            group_id=group["group_id"],
            max_attempts=settings.MAX_PASSCODE_ATTEMPTS,
            lockout_seconds=settings.PASSCODE_LOCKOUT_SECONDS,
            now_ts=int(time.time()),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin passcode",
        )

    if int(group.get("failed_passcode_attempts", 0) or 0) > 0:
        db_service.reset_passcode_attempts(group["group_id"])


def _verify_participant_edit_access(
    group: Dict, participant: Dict, provided_passcode: Optional[str]
) -> None:
    _check_group_lockout(group)

    if not provided_passcode:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin passcode or personal edit PIN is required",
        )

    is_admin = verify_passcode(provided_passcode, group["admin_passcode"])
    participant_hash = participant.get("edit_passcode_hash")
    is_owner = bool(participant_hash and verify_passcode(provided_passcode, participant_hash))

    if not is_admin and not is_owner:
        db_service.record_failed_passcode_attempt(
            group_id=group["group_id"],
            max_attempts=settings.MAX_PASSCODE_ATTEMPTS,
            lockout_seconds=settings.PASSCODE_LOCKOUT_SECONDS,
            now_ts=int(time.time()),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect passcode or personal edit PIN",
        )

    if int(group.get("failed_passcode_attempts", 0) or 0) > 0:
        db_service.reset_passcode_attempts(group["group_id"])


def _dispatch_assignments_concurrently(
    group_id: str,
    group_name: str,
    assignments_to_send: List[Tuple[str, str]],
    part_map: Dict[str, Dict],
    now_iso: str,
) -> Tuple[int, int]:
    """Send Secret Santa notifications concurrently and persist per-assignment status."""
    if not assignments_to_send:
        return 0, 0

    if not (settings.SMTP_USER and settings.SMTP_PASSWORD):
        _ = email_service.ses_client

    def _send_one(giver_id: str, receiver_id: str) -> Tuple[str, bool]:
        giver = part_map.get(giver_id)
        receiver = part_map.get(receiver_id)
        if not giver or not receiver:
            return giver_id, False
        success = email_service.send_secret_santa_notification(
            giver_email=giver["email"],
            giver_name=giver["name"],
            receiver_name=receiver["name"],
            group_name=group_name,
        )
        return giver_id, success

    sent_count = 0
    failed_count = 0
    max_workers = min(10, len(assignments_to_send))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_send_one, giver_id, receiver_id)
            for giver_id, receiver_id in assignments_to_send
        ]
        for future in as_completed(futures):
            try:
                giver_id, success = future.result()
            except Exception:
                failed_count += 1
                continue

            status_value = "SENT" if success else "FAILED"
            db_service.update_assignment_status(group_id, giver_id, status_value, now_iso)
            if success:
                sent_count += 1
            else:
                failed_count += 1

    return sent_count, failed_count


@router.post("/groups", response_model=GroupPublicResponse, status_code=status.HTTP_201_CREATED)
def create_group(payload: CreateGroupRequest):
    group_id = f"g-{secrets.token_urlsafe(16)}"
    created_at = _utc_now_iso()
    passcode_hash = hash_passcode(payload.admin_passcode)

    item = db_service.create_group(
        group_id=group_id,
        name=payload.name,
        admin_email=payload.admin_email,
        admin_passcode_hash=passcode_hash,
        created_at=created_at,
    )

    return GroupPublicResponse(
        group_id=item["group_id"],
        name=item["name"],
        admin_email=mask_email(item["admin_email"]),
        status=item["status"],
        created_at=item["created_at"],
    )


@router.get("/groups/{group_id}", response_model=GroupWithParticipantsResponse)
def get_group_details(group_id: str):
    group = db_service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    participants_raw = db_service.get_participants(group_id)
    participants = [
        ParticipantPublicResponse(
            participant_id=p["participant_id"],
            group_id=p["group_id"],
            name=p["name"],
            email=mask_email(p["email"]),
            excluded_participant_ids=p.get("excluded_participant_ids", []),
            created_at=p["created_at"],
        )
        for p in participants_raw
    ]

    return GroupWithParticipantsResponse(
        group_id=group["group_id"],
        name=group["name"],
        admin_email=mask_email(group["admin_email"]),
        status=group["status"],
        created_at=group["created_at"],
        participants=participants,
    )


@router.post(
    "/groups/{group_id}/participants",
    response_model=ParticipantPublicResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_participant(group_id: str, payload: RegisterParticipantRequest):
    group = db_service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group["status"] != "OPEN":
        raise HTTPException(status_code=400, detail="The group is already closed for new registrations")

    # Catch duplicates early (including legacy records without EMAIL# sentinel)
    existing_participants = db_service.get_participants(group_id)
    if any(p["email"].lower() == payload.email.lower() for p in existing_participants):
        raise HTTPException(status_code=400, detail="This email address is already registered in this group")

    participant_id = f"p-{uuid.uuid4().hex[:8]}"
    created_at = _utc_now_iso()
    edit_passcode_hash = hash_passcode(payload.edit_passcode) if payload.edit_passcode else None

    try:
        item = db_service.add_participant(
            group_id=group_id,
            participant_id=participant_id,
            name=payload.name,
            email=payload.email,
            excluded_participant_ids=payload.excluded_participant_ids,
            created_at=created_at,
            edit_passcode_hash=edit_passcode_hash,
        )
    except GroupClosedError as exc:
        raise HTTPException(
            status_code=400, detail="The group is already closed for new registrations"
        ) from exc
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=400, detail="This email address is already registered in this group"
        ) from exc

    return ParticipantPublicResponse(
        participant_id=item["participant_id"],
        group_id=item["group_id"],
        name=item["name"],
        email=mask_email(item["email"]),
        excluded_participant_ids=item["excluded_participant_ids"],
        created_at=item["created_at"],
    )


@router.put("/groups/{group_id}/participants/{participant_id}", response_model=ParticipantPublicResponse)
def update_participant(
    group_id: str,
    participant_id: str,
    payload: UpdateParticipantRequest,
    x_admin_passcode: Optional[str] = Header(None),
    x_edit_passcode: Optional[str] = Header(None),
):
    group = db_service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group["status"] != "OPEN":
        raise HTTPException(status_code=400, detail="Cannot modify members in a closed group")

    existing_participants = db_service.get_participants(group_id)
    current_participant = next(
        (p for p in existing_participants if p["participant_id"] == participant_id), None
    )
    if not current_participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    _verify_participant_edit_access(group, current_participant, x_admin_passcode or x_edit_passcode)

    effective_email = payload.email or current_participant["email"]

    if any(
        p["email"].lower() == effective_email.lower() and p["participant_id"] != participant_id
        for p in existing_participants
    ):
        raise HTTPException(
            status_code=400,
            detail="This email address is already registered to another member in this group",
        )

    cleaned_exclusions = [e_id for e_id in payload.excluded_participant_ids if e_id != participant_id]
    now_iso = _utc_now_iso()

    try:
        db_service.update_participant(
            group_id=group_id,
            participant_id=participant_id,
            name=payload.name,
            email=effective_email,
            excluded_participant_ids=cleaned_exclusions,
            old_email=current_participant["email"],
            updated_at=now_iso,
        )
    except GroupClosedError as exc:
        raise HTTPException(status_code=400, detail="Cannot modify members in a closed group") from exc
    except ParticipantNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Participant not found") from exc
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=400,
            detail="This email address is already registered to another member in this group",
        ) from exc

    return ParticipantPublicResponse(
        participant_id=participant_id,
        group_id=group_id,
        name=payload.name,
        email=mask_email(effective_email),
        excluded_participant_ids=cleaned_exclusions,
        created_at=current_participant.get("created_at", ""),
    )


@router.delete("/groups/{group_id}/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_participant(
    group_id: str,
    participant_id: str,
    x_admin_passcode: Optional[str] = Header(None),
):
    group = db_service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    _verify_group_admin_passcode(group, x_admin_passcode)

    if group["status"] != "OPEN":
        raise HTTPException(status_code=400, detail="Cannot modify members in a closed group")

    participant = db_service.get_participant(group_id, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    try:
        db_service.delete_participant(
            group_id=group_id,
            participant_id=participant_id,
            email=participant["email"],
            updated_at=_utc_now_iso(),
        )
    except GroupClosedError as exc:
        raise HTTPException(status_code=400, detail="Cannot modify members in a closed group") from exc
    except ParticipantNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Participant not found") from exc

    return None


@router.post("/groups/{group_id}/draw")
def execute_group_draw(group_id: str, payload: ExecuteDrawRequest):
    group = db_service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    _verify_group_admin_passcode(group, payload.admin_passcode)

    group_status = group["status"]
    if group_status == "CLOSED":
        raise HTTPException(status_code=400, detail="The draw has already been performed for this group")
    if group_status == "DRAWING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A draw execution is already in progress. Please wait a moment and try again.",
        )

    participants = db_service.get_participants(group_id)
    part_map = {p["participant_id"]: p for p in participants}
    now_iso = _utc_now_iso()

    if group_status == "OPEN":
        if len(participants) < 3:
            raise HTTPException(
                status_code=400,
                detail="At least 3 participants are required to perform the draw",
            )

        draw_results = generate_secret_santa_draw(participants)
        if not draw_results:
            raise HTTPException(
                status_code=400,
                detail="Could not find a valid assignment matching all exclusion rules. Check if there are too many conflicting restrictions.",
            )

        try:
            db_service.begin_draw(group_id, draw_results, now_iso)
        except DrawAlreadyInProgressError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The draw is already in progress or completed.",
            ) from exc

        assignments_to_send = list(draw_results.items())
        previously_sent = 0
    elif group_status == "DRAW_PARTIAL":
        try:
            db_service.acquire_retry_draw(group_id, now_iso)
        except DrawAlreadyInProgressError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A draw retry is already in progress.",
            ) from exc

        all_assignments = db_service.get_assignments(group_id)
        previously_sent = sum(1 for a in all_assignments if a.get("delivery_status") == "SENT")
        assignments_to_send = [
            (a["giver_id"], a["receiver_id"])
            for a in all_assignments
            if a.get("delivery_status") != "SENT"
        ]
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported group status: {group_status}")

    try:
        sent_now, failed_now = _dispatch_assignments_concurrently(
            group_id=group_id,
            group_name=group["name"],
            assignments_to_send=assignments_to_send,
            part_map=part_map,
            now_iso=_utc_now_iso(),
        )
    except Exception:
        db_service.finalize_draw_status(group_id, "DRAW_PARTIAL", _utc_now_iso())
        raise

    total_participants = len(participants)
    total_sent = previously_sent + sent_now

    if failed_now == 0:
        db_service.finalize_draw_status(group_id, "CLOSED", _utc_now_iso())
        return {
            "message": "Draw completed and emails dispatched successfully",
            "status": "CLOSED",
            "total_participants": total_participants,
            "emails_sent": total_sent,
            "emails_failed": 0,
        }

    db_service.finalize_draw_status(group_id, "DRAW_PARTIAL", _utc_now_iso())
    return {
        "message": "Draw completed, but some emails failed to send. Please retry dispatching pending emails.",
        "status": "DRAW_PARTIAL",
        "total_participants": total_participants,
        "emails_sent": total_sent,
        "emails_failed": failed_now,
    }


@router.get("/health")
def healthcheck():
    return {"status": "ok", "timestamp": _utc_now_iso()}
