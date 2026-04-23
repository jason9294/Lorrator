from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.enums import RoomStatus


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scenario_id: UUID
    host_id: UUID
    name: str
    description: str | None
    status: RoomStatus
    invite_code: str
