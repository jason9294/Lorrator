from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WsTicketResponse(BaseModel):
    ticket: str
    expires_in_seconds: int


class WsMessageEnvelope(BaseModel):
    """WebSocket 傳輸訊息外層格式：{ \"type\": \"...\", \"payload\": { ... } }。"""

    model_config = ConfigDict(extra="forbid")

    type: str
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("payload")
    @classmethod
    def _payload_must_be_object(cls, v: Any) -> dict[str, Any]:
        if not isinstance(v, dict):
            raise ValueError("payload 必須為 JSON object")
        return v
