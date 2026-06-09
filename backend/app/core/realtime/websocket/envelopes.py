from enum import StrEnum
from typing import Any, ClassVar, Literal, Self
from uuid import UUID

from pydantic import BaseModel

from app.models import RoomMessageModel
from app.shared.enums import (
    DocumentStatus,
    ProcessingStepStatus,
    RoomMessageRole,
    RoomMessageType,
)


class EnvelopeType(StrEnum):
    """WebSocket message types (outer JSON `type` field)."""

    # System
    ERROR = "error"
    TOPIC_SUBSCRIPTION_ACK = "topic.subscription_ack"

    # Rooms
    ROOMS_JOIN_ROOM = "rooms.join_room"
    ROOMS_CREATE_MESSAGE = "rooms.create_message"
    ROOMS_AI_THINKING = "rooms.ai_thinking"
    ROOMS_SET_READY = "rooms.set_ready"
    ROOMS_SELECT_CHARACTER = "rooms.select_character"
    ROOMS_KICK = "rooms.kick"

    # Documents
    DOCUMENTS_PROCESS_UPDATED = "documents.process_updated"
    DOCUMENTS_PROCESSING_STEP_UPDATED = "documents.processing_step_updated"


WsErrorCode = Literal[
    "expected_text_frame",
    "invalid_envelope",
    "unknown_message_type",
]

TopicSubscriptionAction = Literal["subscribe", "unsubscribe"]


class BaseEnvelope(BaseModel):
    _type: ClassVar[EnvelopeType]

    def format(self) -> dict[str, Any]:
        return {
            "type": self._type.value,
            "payload": self.model_dump(mode="json"),
        }


class ErrorEnvelope(BaseEnvelope):
    _type = EnvelopeType.ERROR

    code: WsErrorCode


class TopicSubscriptionAckEnvelope(BaseEnvelope):
    _type = EnvelopeType.TOPIC_SUBSCRIPTION_ACK

    topic: str
    action: TopicSubscriptionAction
    ok: bool = True


class RoomsJoinEnvelope(BaseEnvelope):
    _type = EnvelopeType.ROOMS_JOIN_ROOM

    room_id: str
    user_id: str
    role: str
    is_ready: bool
    joined_at: str


class RoomsCreateMessageEnvelope(BaseEnvelope):
    _type = EnvelopeType.ROOMS_CREATE_MESSAGE

    id: str
    room_id: str
    sender_id: str | None
    role: RoomMessageRole
    type: RoomMessageType
    content: str
    detail: str | None = None
    llm_calls: list[dict[str, object]] = []
    created_at: str
    updated_at: str

    @classmethod
    def from_model(cls, msg: RoomMessageModel) -> Self:
        return cls(
            id=str(msg.id),
            room_id=str(msg.room_id),
            sender_id=str(msg.sender_id) if msg.sender_id else None,
            role=msg.role,
            type=msg.type,
            content=msg.content,
            detail=msg.detail,
            llm_calls=msg.llm_calls,
            created_at=msg.created_at.isoformat(),
            updated_at=msg.updated_at.isoformat(),
        )


class RoomsAiThinkingEnvelope(BaseEnvelope):
    _type = EnvelopeType.ROOMS_AI_THINKING

    room_id: str
    active: bool

    @classmethod
    def for_room(cls, room_id: UUID, *, active: bool) -> Self:
        return cls(room_id=str(room_id), active=active)


class RoomsSetReadyEnvelope(BaseEnvelope):
    _type = EnvelopeType.ROOMS_SET_READY

    room_id: str
    user_id: str
    is_ready: bool


class RoomsSelectCharacterEnvelope(BaseEnvelope):
    _type = EnvelopeType.ROOMS_SELECT_CHARACTER

    room_id: str
    user_id: str
    character_id: str | None
    character_name: str | None = None


class RoomsKickEnvelope(BaseEnvelope):
    _type = EnvelopeType.ROOMS_KICK

    room_id: str
    user_id: str


class DocumentsProcessUpdatedEnvelope(BaseEnvelope):
    _type = EnvelopeType.DOCUMENTS_PROCESS_UPDATED

    document_id: str
    scenario_id: str
    status: DocumentStatus
    error: str | None = None

    @classmethod
    def for_document(
        cls,
        *,
        document_id: UUID,
        scenario_id: UUID,
        status: DocumentStatus,
        error: str | None = None,
    ) -> Self:
        return cls(
            document_id=str(document_id),
            scenario_id=str(scenario_id),
            status=status,
            error=error,
        )


class DocumentsProcessingStepUpdatedEnvelope(BaseEnvelope):
    _type = EnvelopeType.DOCUMENTS_PROCESSING_STEP_UPDATED

    document_id: str
    run_id: str
    step_id: str
    status: ProcessingStepStatus
    summary: str | None = None
    error: str | None = None


type Envelope = (
    ErrorEnvelope
    | TopicSubscriptionAckEnvelope
    | RoomsJoinEnvelope
    | RoomsCreateMessageEnvelope
    | RoomsAiThinkingEnvelope
    | RoomsSetReadyEnvelope
    | RoomsSelectCharacterEnvelope
    | RoomsKickEnvelope
    | DocumentsProcessUpdatedEnvelope
    | DocumentsProcessingStepUpdatedEnvelope
)
