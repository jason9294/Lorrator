from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.enums import (
    DocumentStatus,
    GraphEntityType,
    GraphRelationshipType,
    RoomStatus,
    ScenarioStatus,
)


class ScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    system: str
    min_players: int | None
    max_players: int | None
    min_hours: float | None
    max_hours: float | None
    creator_id: UUID
    status: ScenarioStatus
    created_at: datetime
    updated_at: datetime


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scenario_id: UUID
    filename: str
    content_type: str | None
    file_path: str
    md_path: str | None
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime


class ScenarioGraphNodeResponse(BaseModel):
    id: str
    type: GraphEntityType | str
    label: str
    description: str = ""
    aliases: list[str] = []
    descriptions: list[str] = []


class ScenarioGraphEdgeResponse(BaseModel):
    id: str
    source: str
    target: str
    type: GraphRelationshipType | str = ""
    directed: bool = False


class ScenarioGraphResponse(BaseModel):
    nodes: list[ScenarioGraphNodeResponse]
    edges: list[ScenarioGraphEdgeResponse]


class CreateRoomParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    role: str
    is_ready: bool
    joined_at: datetime


class CreateRoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    scenario_id: UUID
    host_id: UUID
    name: str
    description: str | None
    status: RoomStatus
    invite_code: str
    participants: list[CreateRoomParticipantResponse]
