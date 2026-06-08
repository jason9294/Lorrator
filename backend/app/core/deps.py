from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyCookie, HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from openai import AsyncOpenAI

from app.core import get_settings
from app.core.security import TOKEN_COOKIE_NAME, decode_jwt
from app.core.security.schema import JWTPayload

settings = get_settings()

http_bearer = HTTPBearer(auto_error=False)
api_key_cookie = APIKeyCookie(name=TOKEN_COOKIE_NAME, auto_error=False)

OPENAI_CLIENT = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def _provide_token_form_header(
    token: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> str:
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token.credentials


def _provide_token_from_cookie(
    token: Optional[str] = Depends(api_key_cookie),
) -> str:
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid cookie token")
    return token


def _provide_jwt_payload(
    token: str = Depends(_provide_token_form_header),
) -> JWTPayload:
    try:
        data = decode_jwt(token)
        payload = JWTPayload.model_validate(data)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


JWTDependency = Annotated[JWTPayload, Depends(_provide_jwt_payload)]


def _provide_openai_client() -> AsyncOpenAI:
    return OPENAI_CLIENT
