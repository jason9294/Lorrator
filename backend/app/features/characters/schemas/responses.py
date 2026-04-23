from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.enums import GameSystem

from .coc_schema import CoCCharacterData


class CharacterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    game_system: GameSystem
    created_at: datetime
    updated_at: datetime


class CharacterDetailResponse(CharacterResponse):
    data: CoCCharacterData | dict[str, Any] | None = None
