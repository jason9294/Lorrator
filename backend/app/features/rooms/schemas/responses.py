from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.enums import RoomMessageRole, RoomStatus


class RoomParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    role: str
    is_ready: bool
    joined_at: datetime


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
    content: str
    created_at: datetime
    updated_at: datetime
