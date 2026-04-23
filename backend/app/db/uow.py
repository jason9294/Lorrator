from logging import getLogger
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.sql import AsyncSessionDependency
from app.repositories.character_repo import (
    CharacterRepository,
    provide_character_repo_cls,
)
from app.repositories.document_repo import (
    DocumentRepository,
    provide_document_repo_cls,
)
from app.repositories.refresh_token_repo import (
    RefreshTokenRepository,
    provide_refresh_token_repo_cls,
)
from app.repositories.room_message_repo import (
    RoomMessageRepository,
    provide_room_message_repo_cls,
)
from app.repositories.room_repo import RoomRepository, provide_room_repo_cls
from app.repositories.scenario_repo import (
    ScenarioRepository,
    provide_scenario_repo_cls,
)
from app.repositories.user_repo import UserRepository, provide_user_repo_cls

logger = getLogger("uow")


class AsyncUnitOfWork:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
        scenario_repo: ScenarioRepository,
        document_repo: DocumentRepository,
        room_repo: RoomRepository,
        room_message_repo: RoomMessageRepository,
        character_repo: CharacterRepository,
    ):
        self.session = session

        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.scenario_repo = scenario_repo
        self.document_repo = document_repo
        self.room_repo = room_repo
        self.room_message_repo = room_message_repo
        self.character_repo = character_repo

    async def __aenter__(self) -> "AsyncUnitOfWork":
        logger.info("Entering AsyncUnitOfWork")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        logger.info("Exiting AsyncUnitOfWork")
        try:
            if exc_type is None:
                logger.info("No exception, committing AsyncUnitOfWork")
                await self.session.commit()
            else:
                logger.info("Rolling back AsyncUnitOfWork")
                await self.session.rollback()
        finally:
            logger.info("Closing AsyncUnitOfWork")
            await self.session.close()


async def provide_async_uow(
    session: AsyncSessionDependency,
    user_repo_cls: type[UserRepository] = Depends(provide_user_repo_cls),
    refresh_token_repo_cls: type[RefreshTokenRepository] = Depends(
        provide_refresh_token_repo_cls
    ),
    scenario_repo_cls: type[ScenarioRepository] = Depends(provide_scenario_repo_cls),
    document_repo_cls: type[DocumentRepository] = Depends(provide_document_repo_cls),
    room_repo_cls: type[RoomRepository] = Depends(provide_room_repo_cls),
    room_message_repo_cls: type[RoomMessageRepository] = Depends(
        provide_room_message_repo_cls
    ),
    character_repo_cls: type[CharacterRepository] = Depends(
        provide_character_repo_cls
    ),
):
    async with AsyncUnitOfWork(
        session=session,
        user_repo=user_repo_cls(session),
        refresh_token_repo=refresh_token_repo_cls(session),
        scenario_repo=scenario_repo_cls(session),
        document_repo=document_repo_cls(session),
        room_repo=room_repo_cls(session),
        room_message_repo=room_message_repo_cls(session),
        character_repo=character_repo_cls(session),
    ) as uow:
        yield uow


UnitOfWorkDependency = Annotated[AsyncUnitOfWork, Depends(provide_async_uow)]
