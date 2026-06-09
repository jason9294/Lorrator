from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import RoomMessageRole, RoomMessageType, RoomStatus
from app.shared.schemas.llm_call import LlmCallResponse


class RoomParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    username: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    is_ready: bool
    joined_at: datetime
    character_id: Optional[UUID] = None
    character_name: Optional[str] = None


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scenario_id: UUID
    host_id: UUID
    name: str
    description: str | None
    status: RoomStatus
    invite_code: str


class RoomDetailResponse(RoomResponse):
    participants: list[RoomParticipantResponse]


class RoomMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    room_id: UUID
    sender_id: UUID | None
    role: RoomMessageRole
    type: RoomMessageType
    content: str
    detail: str | None = None
    llm_calls: list[LlmCallResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
