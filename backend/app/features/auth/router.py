from datetime import timedelta

from fastapi import APIRouter, Depends, File, Response, UploadFile

from app.core.deps import JWTDependency
from app.core.security import TOKEN_COOKIE_NAME

from .schemas.requests import LoginRequest, RegisterRequest, UpdateProfileRequest
from .schemas.responses import MeResponse, TokenResponse
from .services import (
    LoginService,
    LogoutService,
    MeService,
    RegisterService,
    UpdateProfileService,
    UploadAvatarService,
)

_ACCESS_TOKEN_EXPIRE = timedelta(days=7)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookie(response: Response, access_token: str) -> None:
    max_age = int(_ACCESS_TOKEN_EXPIRE.total_seconds())
    response.set_cookie(
        key=TOKEN_COOKIE_NAME,
        value=access_token,
        max_age=max_age,
        httponly=True,
        samesite="lax",
        path="/",
    )


@router.get(
    path="/me",
    summary="current user",
)
async def me(
    jwt: JWTDependency,
    svc: MeService = Depends(),
) -> MeResponse:
    return await svc.execute(jwt.sub)


@router.patch(
    path="/me",
    summary="update current user profile",
)
async def update_me(
    body: UpdateProfileRequest,
    jwt: JWTDependency,
    svc: UpdateProfileService = Depends(),
) -> MeResponse:
    return await svc.execute(jwt.sub, body)


@router.post(
    path="/me/avatar",
    summary="upload avatar image",
)
async def upload_avatar(
    jwt: JWTDependency,
    file: UploadFile = File(...),
    svc: UploadAvatarService = Depends(),
) -> MeResponse:
    return await svc.execute(jwt.sub, file)


@router.post(path="/login", summary="login")
async def login(
    response: Response,
    body: LoginRequest,
    svc: LoginService = Depends(),
) -> TokenResponse:
    token = await svc.execute(body)
    # _set_auth_cookie(response, token.access_token)
    return token


@router.post(
    path="/logout",
    summary="logout",
)
async def logout(
    response: Response,
    svc: LogoutService = Depends(),
) -> dict[str, str]:
    return await svc.execute(response)


@router.post(
    path="/register",
    summary="register",
)
async def register(
    response: Response,
    body: RegisterRequest,
    svc: RegisterService = Depends(),
) -> TokenResponse:
    token = await svc.execute(body)
    # _set_auth_cookie(response, token.access_token)
    return token
