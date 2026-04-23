from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.shared.utils import uuid7

from .mixin.timestamp import TimestampMixin

if TYPE_CHECKING:
    ...


class UserModel(TimestampMixin, SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    # Primary Key
    id: UUID = Field(default_factory=uuid7, primary_key=True)

    username: str = Field(max_length=255)  # 使用者帳號，需唯一
    password: Optional[str]  # 密碼

    # discord_id: Optional[int]

    __table_args__ = (UniqueConstraint("username", name="uq_users_username"),)
