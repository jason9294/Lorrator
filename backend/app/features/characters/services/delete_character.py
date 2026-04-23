from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency


class DeleteCharacterService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, character_id: UUID, current_user_id: UUID) -> None:
        character = await self._uow.character_repo.get_by_id(character_id)
        if character is None:
            raise HTTPException(status_code=404, detail="Character not found")

        if character.owner_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        await self._uow.character_repo.delete(character)
