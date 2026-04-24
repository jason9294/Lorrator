from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=32000)


class JoinRoomRequest(BaseModel):
    invite_code: str = Field(min_length=1, max_length=16)


class SelectCharacterRequest(BaseModel):
    character_id: Optional[UUID] = None


class RollDiceRequest(BaseModel):
    count: int = Field(default=1, ge=1, le=100)
    faces: int = Field(default=100, ge=2, le=1000)


class SkillCheckRequest(BaseModel):
    skill_name: str = Field(min_length=1, max_length=50)
    skill_value: int = Field(ge=1, le=100)
