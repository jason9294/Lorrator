from datetime import timedelta

from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password
from app.db.uow import UnitOfWorkDependency

from ..schemas.requests import RegisterRequest
from ..schemas.responses import TokenResponse

_ACCESS_TOKEN_EXPIRE = timedelta(days=7)


class RegisterService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, body: RegisterRequest) -> TokenResponse:
        if await self._uow.user_repo.get_by_username(body.username) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered",
            )
        hashed = hash_password(body.password)
        user = await self._uow.user_repo.create(body.username, hashed)
        access_token = create_access_token(
            user_id=user.id, expires_delta=_ACCESS_TOKEN_EXPIRE
        )
        return TokenResponse(access_token=access_token, token_type="Bearer")
