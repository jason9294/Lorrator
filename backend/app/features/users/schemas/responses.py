from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: UUID
    username: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
