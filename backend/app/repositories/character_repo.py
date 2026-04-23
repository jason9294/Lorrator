from typing import Any
from uuid import UUID

from sqlmodel import select

from app.models.character_model import CharacterModel
from app.shared.enums import GameSystem

from ._base_repo import BaseRepository


class CharacterRepository(BaseRepository):
    async def get_by_id(self, character_id: UUID) -> CharacterModel | None:
        statement = select(CharacterModel).where(CharacterModel.id == character_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def list_by_owner(self, owner_id: UUID) -> list[CharacterModel]:
        statement = select(CharacterModel).where(CharacterModel.owner_id == owner_id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create(
        self,
        owner_id: UUID,
        name: str,
        game_system: GameSystem,
        data: dict[str, Any],
    ) -> CharacterModel:
        character = CharacterModel(
            owner_id=owner_id,
            name=name,
            game_system=game_system,
            data=data,
        )
        self.session.add(character)
        await self.session.flush()
        return character

    async def update(
        self,
        character: CharacterModel,
        name: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> CharacterModel:
        if name is not None:
            character.name = name
        if data is not None:
            character.data = data
        self.session.add(character)
        await self.session.flush()
        return character

    async def delete(self, character: CharacterModel) -> None:
        await self.session.delete(character)
        await self.session.flush()


def provide_character_repo_cls() -> type[CharacterRepository]:
    return CharacterRepository
