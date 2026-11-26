from typing import Any, Dict, List, Optional
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.dynamodb import (
    DrawAlreadyInProgressError,
    DuplicateEmailError,
    GroupClosedError,
    ParticipantNotFoundError,
)


class InMemoryDynamoDBService:
    """In-memory test double mimicking DynamoDBService transactional behavior."""

    def __init__(self):
        self.groups: Dict[str, Dict[str, Any]] = {}
        self.participants: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.emails: Dict[str, set] = {}
        self.assignments: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def create_group(
        self,
        group_id: str,
        name: str,
        admin_email: str,
        admin_passcode_hash: str,
        created_at: str,
    ) -> Dict[str, Any]:
        item = {
            "group_id": group_id,
            "name": name,
            "admin_email": admin_email,
            "admin_passcode": admin_passcode_hash,
            "status": "OPEN",
            "failed_passcode_attempts": 0,
            "passcode_locked_until": 0,
            "created_at": created_at,
            "updated_at": created_at,
        }
        self.groups[group_id] = item
        self.participants[group_id] = {}
        self.emails[group_id] = set()
        self.assignments[group_id] = {}
        return item

    def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        g = self.groups.get(group_id)
        return dict(g) if g else None

    def record_failed_passcode_attempt(
        self, group_id: str, max_attempts: int, lockout_seconds: int, now_ts: int
    ) -> int:
        g = self.groups[group_id]
        g["failed_passcode_attempts"] = g.get("failed_passcode_attempts", 0) + 1
        if g["failed_passcode_attempts"] >= max_attempts:
            g["passcode_locked_until"] = now_ts + lockout_seconds
        return g["failed_passcode_attempts"]

    def reset_passcode_attempts(self, group_id: str) -> None:
        g = self.groups[group_id]
        g["failed_passcode_attempts"] = 0
        g["passcode_locked_until"] = 0

    def add_participant(
        self,
        group_id: str,
        participant_id: str,
        name: str,
        email: str,
        excluded_participant_ids: List[str],
        created_at: str,
        edit_passcode_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        g = self.groups.get(group_id)
        if not g or g["status"] != "OPEN":
            raise GroupClosedError("Group is closed or does not exist")
        email_lower = email.strip().lower()
        if email_lower in self.emails[group_id]:
            raise DuplicateEmailError("Email already registered in group")

        item: Dict[str, Any] = {
            "participant_id": participant_id,
            "group_id": group_id,
            "name": name,
            "email": email,
            "excluded_participant_ids": list(excluded_participant_ids),
            "created_at": created_at,
        }
        if edit_passcode_hash:
            item["edit_passcode_hash"] = edit_passcode_hash

        self.emails[group_id].add(email_lower)
        self.participants[group_id][participant_id] = item
        return item

    def get_participants(self, group_id: str) -> List[Dict[str, Any]]:
        return [dict(p) for p in self.participants.get(group_id, {}).values()]

    def get_participant(self, group_id: str, participant_id: str) -> Optional[Dict[str, Any]]:
        p = self.participants.get(group_id, {}).get(participant_id)
        return dict(p) if p else None

    def update_participant(
        self,
        group_id: str,
        participant_id: str,
        name: str,
        email: str,
        excluded_participant_ids: List[str],
        old_email: str,
        updated_at: str,
    ) -> Dict[str, Any]:
        g = self.groups.get(group_id)
        if not g or g["status"] != "OPEN":
            raise GroupClosedError("Group is closed or does not exist")
        p = self.participants[group_id].get(participant_id)
        if not p:
            raise ParticipantNotFoundError("Participant not found")

        old_lower = old_email.strip().lower()
        new_lower = email.strip().lower()
        if new_lower != old_lower:
            if new_lower in self.emails[group_id]:
                raise DuplicateEmailError("Email already registered in group")
            self.emails[group_id].discard(old_lower)
            self.emails[group_id].add(new_lower)

        p["name"] = name
        p["email"] = email
        p["excluded_participant_ids"] = list(excluded_participant_ids)
        return dict(p)

    def delete_participant(
        self, group_id: str, participant_id: str, email: str, updated_at: str
    ) -> None:
        g = self.groups.get(group_id)
        if not g or g["status"] != "OPEN":
            raise GroupClosedError("Group is closed or does not exist")
        if participant_id not in self.participants[group_id]:
            raise ParticipantNotFoundError("Participant not found")
        del self.participants[group_id][participant_id]
        self.emails[group_id].discard(email.strip().lower())

    def begin_draw(self, group_id: str, assignments: Dict[str, str], now_iso: str) -> None:
        g = self.groups.get(group_id)
        if not g or g["status"] != "OPEN":
            raise DrawAlreadyInProgressError("Group is no longer OPEN")
        g["status"] = "DRAWING"
        for giver_id, receiver_id in assignments.items():
            self.assignments[group_id][giver_id] = {
                "giver_id": giver_id,
                "receiver_id": receiver_id,
                "delivery_status": "PENDING",
                "updated_at": now_iso,
            }

    def acquire_retry_draw(self, group_id: str, now_iso: str) -> None:
        g = self.groups.get(group_id)
        if not g or g["status"] != "DRAW_PARTIAL":
            raise DrawAlreadyInProgressError("Not in DRAW_PARTIAL")
        g["status"] = "DRAWING"

    def get_assignments(self, group_id: str) -> List[Dict[str, Any]]:
        return [dict(a) for a in self.assignments.get(group_id, {}).values()]

    def update_assignment_status(
        self, group_id: str, giver_id: str, delivery_status: str, now_iso: str
    ) -> None:
        self.assignments[group_id][giver_id]["delivery_status"] = delivery_status
        self.assignments[group_id][giver_id]["updated_at"] = now_iso

    def finalize_draw_status(self, group_id: str, new_status: str, now_iso: str) -> None:
        self.groups[group_id]["status"] = new_status
        self.groups[group_id]["updated_at"] = now_iso


client = TestClient(app)


def _create_sample_group(fake_db: InMemoryDynamoDBService) -> str:
    resp = client.post(
        "/api/v1/groups",
        json={
            "name": "Familia 2026",
            "admin_email": "admin@example.com",
            "admin_passcode": "admin123",
        },
    )
    assert resp.status_code == 201
    group_id = resp.json()["group_id"]
    assert len(group_id) >= 20
    assert resp.json()["admin_email"] == "ad***@example.com"
    # Verify passcode was hashed in storage and not leaked in response
    assert "admin_passcode" not in resp.json()
    assert fake_db.groups[group_id]["admin_passcode"].startswith("pbkdf2_sha256$")
    return group_id


def test_delete_requires_admin_passcode_no_bypass():
    fake_db = InMemoryDynamoDBService()
    with patch("app.api.routes.db_service", fake_db):
        group_id = _create_sample_group(fake_db)
        p_resp = client.post(
            f"/api/v1/groups/{group_id}/participants",
            json={"name": "Ana", "email": "ana@example.com", "excluded_participant_ids": []},
        )
        assert p_resp.status_code == 201
        pid = p_resp.json()["participant_id"]

        # Missing header must fail with 401 (no auth bypass)
        no_auth = client.delete(f"/api/v1/groups/{group_id}/participants/{pid}")
        assert no_auth.status_code == 401

        # Wrong header must fail with 401
        bad_auth = client.delete(
            f"/api/v1/groups/{group_id}/participants/{pid}",
            headers={"X-Admin-Passcode": "wrong"},
        )
        assert bad_auth.status_code == 401

        # Correct admin passcode succeeds and frees email
        ok_auth = client.delete(
            f"/api/v1/groups/{group_id}/participants/{pid}",
            headers={"X-Admin-Passcode": "admin123"},
        )
        assert ok_auth.status_code == 204
        assert len(fake_db.get_participants(group_id)) == 0


def test_update_requires_admin_or_personal_pin():
    fake_db = InMemoryDynamoDBService()
    with patch("app.api.routes.db_service", fake_db):
        group_id = _create_sample_group(fake_db)
        p_resp = client.post(
            f"/api/v1/groups/{group_id}/participants",
            json={
                "name": "Luis",
                "email": "luis@example.com",
                "excluded_participant_ids": [],
                "edit_passcode": "luis9999",
            },
        )
        assert p_resp.status_code == 201
        pid = p_resp.json()["participant_id"]

        # Missing passcode -> 401
        unauth = client.put(
            f"/api/v1/groups/{group_id}/participants/{pid}",
            json={"name": "Luis X", "email": "luis@example.com", "excluded_participant_ids": []},
        )
        assert unauth.status_code == 401

        # Personal edit PIN -> 200 (without changing email, preserves real email in DB)
        owner_ok = client.put(
            f"/api/v1/groups/{group_id}/participants/{pid}",
            headers={"X-Admin-Passcode": "luis9999"},
            json={"name": "Luis Edited", "excluded_participant_ids": []},
        )
        assert owner_ok.status_code == 200
        assert owner_ok.json()["name"] == "Luis Edited"
        assert owner_ok.json()["email"] == "lu***@example.com"
        assert fake_db.get_participant(group_id, pid)["email"] == "luis@example.com"

        # Organizer admin passcode -> 200 (changing email)
        admin_ok = client.put(
            f"/api/v1/groups/{group_id}/participants/{pid}",
            headers={"X-Admin-Passcode": "admin123"},
            json={"name": "Luis Admin", "email": "luis2@example.com", "excluded_participant_ids": []},
        )
        assert admin_ok.status_code == 200
        assert admin_ok.json()["email"] == "lu***@example.com"
        assert fake_db.get_participant(group_id, pid)["email"] == "luis2@example.com"

        # GET /groups/{id} masks all emails
        group_view = client.get(f"/api/v1/groups/{group_id}")
        assert group_view.status_code == 200
        assert group_view.json()["admin_email"] == "ad***@example.com"
        assert group_view.json()["participants"][0]["email"] == "lu***@example.com"


def test_passcode_brute_force_lockout():
    fake_db = InMemoryDynamoDBService()
    with patch("app.api.routes.db_service", fake_db):
        group_id = _create_sample_group(fake_db)
        for _ in range(5):
            r = client.post(
                f"/api/v1/groups/{group_id}/draw",
                json={"admin_passcode": "badpin"},
            )
            assert r.status_code == 401

        # Even with the right passcode, 6th attempt is locked out (429)
        locked = client.post(
            f"/api/v1/groups/{group_id}/draw",
            json={"admin_passcode": "admin123"},
        )
        assert locked.status_code == 429


def test_draw_partial_failure_and_idempotent_retry():
    fake_db = InMemoryDynamoDBService()
    sent_calls: List[str] = []

    def flaky_email(giver_email: str, giver_name: str, receiver_name: str, group_name: str) -> bool:
        sent_calls.append(giver_email)
        # Fail first attempt for bob@example.com, succeed on retry
        if giver_email == "bob@example.com" and sent_calls.count("bob@example.com") == 1:
            return False
        return True

    with patch("app.api.routes.db_service", fake_db), \
         patch("app.api.routes.email_service.send_secret_santa_notification", side_effect=flaky_email):
        group_id = _create_sample_group(fake_db)
        for name, email in [
            ("Alice", "alice@example.com"),
            ("Bob", "bob@example.com"),
            ("Charlie", "charlie@example.com"),
        ]:
            r = client.post(
                f"/api/v1/groups/{group_id}/participants",
                json={"name": name, "email": email, "excluded_participant_ids": []},
            )
            assert r.status_code == 201

        # First draw attempt: 2 succeed, 1 fails -> DRAW_PARTIAL
        draw1 = client.post(
            f"/api/v1/groups/{group_id}/draw",
            json={"admin_passcode": "admin123"},
        )
        assert draw1.status_code == 200
        body1 = draw1.json()
        assert body1["status"] == "DRAW_PARTIAL"
        assert body1["emails_sent"] == 2
        assert body1["emails_failed"] == 1
        assert fake_db.get_group(group_id)["status"] == "DRAW_PARTIAL"

        saved_assignments_before_retry = dict(fake_db.assignments[group_id])

        # Second draw attempt (retry): only bob@example.com should be emailed!
        draw2 = client.post(
            f"/api/v1/groups/{group_id}/draw",
            json={"admin_passcode": "admin123"},
        )
        assert draw2.status_code == 200
        body2 = draw2.json()
        assert body2["status"] == "CLOSED"
        assert body2["emails_sent"] == 3
        assert body2["emails_failed"] == 0
        assert fake_db.get_group(group_id)["status"] == "CLOSED"

        # Total emails attempted across both calls: 3 + 1 = 4 (Alice and Charlie not re-emailed)
        assert len(sent_calls) == 4
        assert sent_calls.count("alice@example.com") == 1
        assert sent_calls.count("charlie@example.com") == 1
        assert sent_calls.count("bob@example.com") == 2

        # Assignments remained identical across retry
        for giver_id, data in saved_assignments_before_retry.items():
            assert fake_db.assignments[group_id][giver_id]["receiver_id"] == data["receiver_id"]
            assert fake_db.assignments[group_id][giver_id]["delivery_status"] == "SENT"

        # Third draw attempt on CLOSED group must fail with 400
        draw3 = client.post(
            f"/api/v1/groups/{group_id}/draw",
            json={"admin_passcode": "admin123"},
        )
        assert draw3.status_code == 400


def test_draw_returns_409_when_drawing_in_progress():
    fake_db = InMemoryDynamoDBService()
    with patch("app.api.routes.db_service", fake_db):
        group_id = _create_sample_group(fake_db)
        fake_db.groups[group_id]["status"] = "DRAWING"

        resp = client.post(
            f"/api/v1/groups/{group_id}/draw",
            json={"admin_passcode": "admin123"},
        )
        assert resp.status_code == 409


def test_cors_restricts_origins_and_disables_credentials():
    disallowed = client.options(
        "/api/v1/health",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in disallowed.headers

    allowed = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert allowed.headers.get("access-control-allow-credentials") != "true"


def test_health_and_not_found_and_closed_group_guards():
    fake_db = InMemoryDynamoDBService()
    with patch("app.api.routes.db_service", fake_db):
        health = client.get("/api/v1/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        assert client.get("/api/v1/groups/nonexistent").status_code == 404

        group_id = _create_sample_group(fake_db)
        p1 = client.post(
            f"/api/v1/groups/{group_id}/participants",
            json={"name": "Ana", "email": "ana@example.com", "excluded_participant_ids": []},
        )
        assert p1.status_code == 201
        pid = p1.json()["participant_id"]

        # Duplicate email rejected (case-insensitive)
        dup = client.post(
            f"/api/v1/groups/{group_id}/participants",
            json={"name": "Ana 2", "email": "ANA@example.com", "excluded_participant_ids": []},
        )
        assert dup.status_code == 400

        # Non-existent participant on delete -> 404
        missing_del = client.delete(
            f"/api/v1/groups/{group_id}/participants/p-missing",
            headers={"X-Admin-Passcode": "admin123"},
        )
        assert missing_del.status_code == 404

        # Closed group rejects register, update, and delete
        fake_db.groups[group_id]["status"] = "CLOSED"
        assert (
            client.post(
                f"/api/v1/groups/{group_id}/participants",
                json={"name": "Bob", "email": "bob@example.com", "excluded_participant_ids": []},
            ).status_code
            == 400
        )
        assert (
            client.put(
                f"/api/v1/groups/{group_id}/participants/{pid}",
                headers={"X-Admin-Passcode": "admin123"},
                json={"name": "Ana New", "excluded_participant_ids": []},
            ).status_code
            == 400
        )
        assert (
            client.delete(
                f"/api/v1/groups/{group_id}/participants/{pid}",
                headers={"X-Admin-Passcode": "admin123"},
            ).status_code
            == 400
        )


