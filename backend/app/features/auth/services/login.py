from datetime import timedelta

from fastapi import HTTPException, status

from app.core.security import create_access_token, validate_password
from app.db.uow import UnitOfWorkDependency

from ..schemas.requests import LoginRequest
from ..schemas.responses import TokenResponse

_ACCESS_TOKEN_EXPIRE = timedelta(days=7)


class LoginService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, body: LoginRequest) -> TokenResponse:
        user = await self._uow.user_repo.get_by_username(body.username)
        if user is None or user.password is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        if not validate_password(body.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        access_token = create_access_token(
            user_id=user.id, expires_delta=_ACCESS_TOKEN_EXPIRE
        )
        return TokenResponse(access_token=access_token, token_type="Bearer")
