from typing import Any

from app.shared.enums import GameSystem

from .schemas.coc_schema import CoCCharacterData


def parse_character_data(
    game_system: GameSystem,
    raw: dict[str, Any] | None,
) -> CoCCharacterData | dict[str, Any] | None:
    if raw is None:
        return None

    if game_system == GameSystem.COC:
        return CoCCharacterData.model_validate(raw)

    return raw
