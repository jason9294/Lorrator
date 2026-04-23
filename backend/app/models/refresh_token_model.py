from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, func

from app.shared.utils import uuid7

if TYPE_CHECKING:
    from .user_model import UserModel


class RefreshTokenModel(SQLModel, table=True):
    __tablename__ = "refresh_tokens"  # type: ignore

    # Primary Key
    id: UUID = Field(default_factory=uuid7, primary_key=True)

    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    user: "UserModel" = Relationship()

    validator_hash: str = Field(nullable=False)

    created_at: datetime = Field(
        default=func.now(),
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 由 DB 自動填入
            nullable=False,
        ),
    )

    expires_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        )
    )

    revoked: bool = Field(default=False, nullable=False)

    __table_args__ = (
        Index("ix_refresh_tokens_user_id", "user_id"),
        UniqueConstraint(
            "validator_hash", name="uq_refresh_tokens_validator_hash"
        ),
    )
