from uuid import UUID

from app.db.uow import UnitOfWorkDependency
from app.features.characters.schemas.requests import CreateCharacterRequest
from app.features.characters.schemas.responses import CharacterDetailResponse

from .._utils import parse_character_data


class CreateCharacterService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(
        self, body: CreateCharacterRequest, owner_id: UUID
    ) -> CharacterDetailResponse:
        character = await self._uow.character_repo.create(
            owner_id=owner_id,
            name=body.name,
            game_system=body.game_system,
            data=body.data.model_dump(),
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
