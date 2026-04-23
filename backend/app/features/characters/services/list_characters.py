from uuid import UUID

from app.db.uow import UnitOfWorkDependency
from app.features.characters.schemas.responses import CharacterResponse


class ListCharactersService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, owner_id: UUID) -> list[CharacterResponse]:
        characters = await self._uow.character_repo.list_by_owner(owner_id)

        return [CharacterResponse.model_validate(c) for c in characters]
