from typing import Any
from uuid import UUID

from pydantic import BaseModel


class LlmCallResponse(BaseModel):
    id: UUID
    step_id: str
    call_key: str
    label: str
    model: str
    request: list[dict[str, Any]]
    response: dict[str, Any] | str
    sequence: int
