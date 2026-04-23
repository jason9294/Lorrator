from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JWTPayload(BaseModel):
    sub: UUID
    exp: datetime
