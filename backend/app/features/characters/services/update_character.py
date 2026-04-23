from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.characters.schemas.requests import UpdateCharacterRequest
from app.features.characters.schemas.responses import CharacterDetailResponse

from .._utils import parse_character_data


class UpdateCharacterService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(
        self,
        character_id: UUID,
        body: UpdateCharacterRequest,
        current_user_id: UUID,
    ) -> CharacterDetailResponse:
        character = await self._uow.character_repo.get_by_id(character_id)
        if character is None:
            raise HTTPException(status_code=404, detail="Character not found")

        if character.owner_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        character = await self._uow.character_repo.update(
            character=character,
            name=body.name,
            data=body.data.model_dump() if body.data is not None else None,
        )

        return CharacterDetailResponse(
            id=character.id,
            owner_id=character.owner_id,
            name=character.name,
            game_system=character.game_system,
            created_at=character.created_at,
            updated_at=character.updated_at,
            data=parse_character_data(character.game_system, character.data),
        )
