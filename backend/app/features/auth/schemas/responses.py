from uuid import UUID

from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class MeResponse(BaseModel):
    id: UUID
    username: str
