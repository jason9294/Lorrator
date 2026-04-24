from typing import Optional
from uuid import UUID

from sqlmodel import select

from app.models import UserModel

from ._base_repo import BaseRepository

MOCK_USERNAME = "mock_user"


class UserRepository(BaseRepository):
    async def get_all(self) -> list[UserModel]:
        statement = select(UserModel)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_username(self, username: str) -> UserModel | None:
        statement = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_id(self, id: UUID) -> UserModel | None:
        statement = select(UserModel).where(UserModel.id == id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create(self, username: str, hashed_password: str) -> UserModel:
        user = UserModel(username=username, password=hashed_password)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_profile(
        self,
        user: UserModel,
        nickname: Optional[str],
        avatar_url: Optional[str],
    ) -> UserModel:
        user.nickname = nickname
        user.avatar_url = avatar_url
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_or_create_mock_user(self) -> UserModel:
        user = await self.get_by_username(MOCK_USERNAME)
        if user is not None:
            return user
        user = UserModel(username=MOCK_USERNAME, password=None)
        self.session.add(user)
        await self.session.flush()
        return user


def provide_user_repo_cls() -> type[UserRepository]:
    return UserRepository
