from uuid import UUID

from fastapi import HTTPException, status

from app.db.uow import UnitOfWorkDependency

from ..schemas.responses import MeResponse


class MeService:
    def __init__(
        self,
        uow: UnitOfWorkDependency,
    ) -> None:
        self._uow = uow

    async def execute(self, user_id: UUID) -> MeResponse:
        user = await self._uow.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return MeResponse(id=user.id, username=user.username)
