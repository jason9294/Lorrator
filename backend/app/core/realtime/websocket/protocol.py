from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClientMessageType(StrEnum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


class ClientMessage(BaseModel):
    """Client → server WebSocket frame: { \"type\": \"...\", \"payload\": { ... } }."""

    model_config = ConfigDict(extra="forbid")

    type: str
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("payload")
    @classmethod
    def _payload_must_be_object(cls, v: Any) -> dict[str, Any]:
        if not isinstance(v, dict):
            raise ValueError("payload 必須為 JSON object")
        return v


class TopicPayload(BaseModel):
    topic: str = Field(min_length=1)
