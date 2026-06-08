from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.enums import RoomMessageRole, RoomMessageType, RoomStatus


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
    created_at: datetime
    updated_at: datetime
