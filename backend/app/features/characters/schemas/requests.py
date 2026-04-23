from pydantic import BaseModel, Field

from app.shared.enums import GameSystem

from .coc_schema import CoCCharacterData


class CreateCharacterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    game_system: GameSystem = GameSystem.COC
    data: CoCCharacterData = Field(default_factory=CoCCharacterData)


class UpdateCharacterRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    data: CoCCharacterData | None = None
