# JWT/金鑰/密碼雜湊策略
from datetime import timedelta
from typing import Any
from uuid import UUID

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

from app.core.setting import get_settings
from app.shared.utils.time_utils import datetime_utcnow

settings = get_settings()

ALGORITHM = "HS256"
SECRET_KEY = settings.SECRET_KEY

# 與 APIKeyCookie / set_cookie 共用，確保讀寫同一個 cookie 名稱
TOKEN_COOKIE_NAME = "token"


# 密碼雜湊策略
_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_password(password: str, hashed_password: str) -> bool:
    """驗證密碼是否匹配"""
    return _password_context.verify(password, hashed_password)


def hash_password(password: str) -> str:
    """雜湊密碼"""
    return _password_context.hash(password)


# JWT


def encode_jwt(payload: dict[str, Any]) -> str:
    """將 dict 轉換為 JWT 字串"""
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> Any:
    """將 JWT 字串轉換為 dict"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_access_token(
    *, user_id: UUID, expires_delta: timedelta = timedelta(minutes=15)
) -> str:
    """建立 access token"""
    return encode_jwt(
        {
            "sub": str(user_id),
            "exp": datetime_utcnow() + expires_delta,
        }
    )
