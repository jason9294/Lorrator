from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import Column, Index, String, Text
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.shared.enums import RoomMessageRole, RoomMessageType
from app.shared.utils import uuid7

from .mixin.timestamp import TimestampMixin

if TYPE_CHECKING:
    from app.models.room_model import RoomModel
    from app.models.user_model import UserModel


class RoomMessageModel(TimestampMixin, SQLModel, table=True):
    __tablename__ = "room_messages"  # type: ignore

    id: UUID = Field(default_factory=uuid7, primary_key=True)

    room_id: UUID = Field(foreign_key="rooms.id")
    sender_id: UUID | None = Field(foreign_key="users.id")

    role: RoomMessageRole
    type: RoomMessageType = Field(
        default=RoomMessageType.CHAT,
        sa_column=Column(String, nullable=False, server_default="CHAT"),
    )
    content: str = Field(sa_column=Column(Text, nullable=False))
    detail: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    llm_calls: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
    )

    room: Optional["RoomModel"] = Relationship()
    sender: Optional["UserModel"] = Relationship()

    __table_args__ = (
        Index("ix_room_messages_room_id_created_at", "room_id", "created_at"),
    )
