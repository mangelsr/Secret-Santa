import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header, status
from typing import List, Optional

from app.schemas.models import (
    CreateGroupRequest, 
    GroupPublicResponse, 
    RegisterParticipantRequest, 
    ParticipantPublicResponse,
    GroupWithParticipantsResponse,
    ExecuteDrawRequest
)
from app.services.dynamodb import db_service
from app.services.ses import ses_service
from app.core.santa_draw import generate_secret_santa_draw

router = APIRouter(prefix="/api/v1")

@router.post("/groups", response_model=GroupPublicResponse, status_code=status.HTTP_201_CREATED)
def create_group(payload: CreateGroupRequest):
    group_id = f"g-{uuid.uuid4().hex[:8]}"
    created_at = datetime.utcnow().isoformat()
    
    item = db_service.create_group(
        group_id=group_id,
        name=payload.name,
        admin_email=payload.admin_email,
        admin_passcode=payload.admin_passcode,
        created_at=created_at
    )
    
    return GroupPublicResponse(
        group_id=item["group_id"],
        name=item["name"],
        admin_email=item["admin_email"],
        status=item["status"],
        created_at=item["created_at"]
    )

@router.get("/groups/{group_id}", response_model=GroupWithParticipantsResponse)
def get_group_details(group_id: str):
    group = db_service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
        
    participants_raw = db_service.get_participants(group_id)
    participants = [
        ParticipantPublicResponse(
            participant_id=p["participant_id"],
            group_id=p["group_id"],
            name=p["name"],
            email=p["email"],
            excluded_participant_ids=p.get("excluded_participant_ids", []),
            created_at=p["created_at"]
        ) for p in participants_raw
    ]
    
    return GroupWithParticipantsResponse(
        group_id=group["group_id"],
        name=group["name"],
        admin_email=group["admin_email"],
        status=group["status"],
        created_at=group["created_at"],
        participants=participants
    )

@router.post("/groups/{group_id}/participants", response_model=ParticipantPublicResponse, status_code=status.HTTP_201_CREATED)
def register_participant(group_id: str, payload: RegisterParticipantRequest):
    group = db_service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
        
    if group["status"] != "OPEN":
        raise HTTPException(status_code=400, detail="El grupo ya se encuentra cerrado para nuevos registros")

    # Verificar si el correo ya está registrado en este grupo
    existing_participants = db_service.get_participants(group_id)
    if any(p["email"].lower() == payload.email.lower() for p in existing_participants):
        raise HTTPException(status_code=400, detail="Este correo electrónico ya está inscrito en el grupo")

    participant_id = f"p-{uuid.uuid4().hex[:8]}"
    created_at = datetime.utcnow().isoformat()
    
    item = db_service.add_participant(
        group_id=group_id,
        participant_id=participant_id,
        name=payload.name,
        email=payload.email,
        excluded_participant_ids=payload.excluded_participant_ids,
        created_at=created_at
    )
    
    return ParticipantPublicResponse(
        participant_id=item["participant_id"],
        group_id=item["group_id"],
        name=item["name"],
        email=item["email"],
        excluded_participant_ids=item["excluded_participant_ids"],
        created_at=item["created_at"]
    )

@router.delete("/groups/{group_id}/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_participant(group_id: str, participant_id: str, x_admin_passcode: Optional[str] = Header(None)):
    group = db_service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
        
    if group["admin_passcode"] != x_admin_passcode:
        raise HTTPException(status_code=401, detail="Clave de administrador incorrecta")
        
    if group["status"] != "OPEN":
        raise HTTPException(status_code=400, detail="No se pueden modificar miembros en un grupo cerrado")

    db_service.delete_participant(group_id, participant_id)
    return None

@router.post("/groups/{group_id}/draw")
def execute_group_draw(group_id: str, payload: ExecuteDrawRequest):
    group = db_service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")

    if group["admin_passcode"] != payload.admin_passcode:
        raise HTTPException(status_code=401, detail="Clave de administrador incorrecta")

    if group["status"] != "OPEN":
        raise HTTPException(status_code=400, detail="El sorteo ya ha sido realizado previamente para este grupo")

    participants = db_service.get_participants(group_id)
    if len(participants) < 3:
        raise HTTPException(status_code=400, detail="Se requieren al menos 3 participantes inscritos para realizar el sorteo")

    # Ejecutar algoritmo de sorteo con exclusiones
    draw_results = generate_secret_santa_draw(participants)
    if not draw_results:
        raise HTTPException(
            status_code=400, 
            detail="No se pudo encontrar una asignación válida respetando las exclusiones indicadas. Revisa si hay demasiadas restricciones recíprocas."
        )

    # Mapear IDs a Objetos Participante
    part_map = {p["participant_id"]: p for p in participants}

    # Despachar correos vía AWS SES
    emails_sent = 0
    for giver_id, receiver_id in draw_results.items():
        giver = part_map[giver_id]
        receiver = part_map[receiver_id]
        
        success = ses_service.send_secret_santa_notification(
            giver_email=giver["email"],
            giver_name=giver["name"],
            receiver_name=receiver["name"],
            group_name=group["name"]
        )
        if success:
            emails_sent += 1

    # Marcar grupo como cerrado
    db_service.close_group(group_id)

    return {
        "message": "Sorteo completado y correos enviados con éxito vía AWS SES",
        "total_participants": len(participants),
        "emails_sent": emails_sent
    }

@router.get("/health")
def healthcheck():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
