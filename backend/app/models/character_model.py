from typing import TYPE_CHECKING, Any

from uuid import UUID

from sqlalchemy import Column, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.shared.enums import GameSystem
from app.shared.utils import uuid7

from .mixin.timestamp import TimestampMixin

if TYPE_CHECKING:
    from app.models.user_model import UserModel


class CharacterModel(TimestampMixin, table=True):  # type: ignore
    __tablename__ = "characters"  # type: ignore

    id: UUID = Field(default_factory=uuid7, primary_key=True)

    owner_id: UUID = Field(foreign_key="users.id")
    owner: "UserModel" = Relationship()

    name: str = Field(max_length=100)
    game_system: GameSystem = Field(default=GameSystem.COC)

    # 角色卡資料，以 JSONB 存放避免綁定特定遊戲系統
    data: dict[str, Any] = Field(
        default={},
        sa_column=Column(JSONB, nullable=False),
    )

    __table_args__ = (Index("ix_characters_owner_id", "owner_id"),)
