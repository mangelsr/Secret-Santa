from pydantic import BaseModel, EmailStr, Field
from typing import List

class CreateGroupRequest(BaseModel):
    name: str = Field(..., description="Group name (e.g. Garcia Family Christmas 2026)")
    admin_email: EmailStr = Field(..., description="Organizer email address")
    admin_passcode: str = Field(..., min_length=4, description="Admin passcode to finalize and execute the draw")

class GroupPublicResponse(BaseModel):
    group_id: str
    name: str
    admin_email: EmailStr
    status: str
    created_at: str

class RegisterParticipantRequest(BaseModel):
    name: str = Field(..., description="Participant full name")
    email: EmailStr = Field(..., description="Participant email address to receive secret assignment")
    excluded_participant_ids: List[str] = Field(
        default_factory=list, 
        description="IDs or names of family members previously gifted to in past years"
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
    admin_passcode: str = Field(..., description="Admin passcode to authorize the draw")
