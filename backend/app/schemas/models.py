from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class CreateGroupRequest(BaseModel):
    name: str = Field(..., description="Nombre del grupo (ej: Navidad Familia García)")
    admin_email: EmailStr = Field(..., description="Email del organizador del grupo")
    admin_passcode: str = Field(..., min_length=4, description="Clave de administrador para cerrar el grupo")

class GroupPublicResponse(BaseModel):
    group_id: str
    name: str
    admin_email: EmailStr
    status: str
    created_at: str

class RegisterParticipantRequest(BaseModel):
    name: str = Field(..., description="Nombre completo del participante")
    email: EmailStr = Field(..., description="Correo del participante para recibir el aviso")
    excluded_participant_ids: List[str] = Field(
        default_factory=list, 
        description="IDs o nombres de integrantes a los que ya se les ha dado regalo anteriormente"
    )

class ParticipantPublicResponse(BaseModel):
    participant_id: str
    group_id: str
    name: str
    email: EmailStr
    excluded_participant_ids: List[str]
    created_at: str

class GroupWithParticipantsResponse(GroupPublicResponse):
    participants: List[ParticipantPublicResponse]

class ExecuteDrawRequest(BaseModel):
    admin_passcode: str = Field(..., description="Clave de administración para autorizar el sorteo")
