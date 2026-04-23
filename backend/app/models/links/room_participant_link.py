from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Index
from sqlmodel import DateTime, Field, Relationship, SQLModel

from app.shared.utils import datetime_utcnow, uuid7

if TYPE_CHECKING:
    from app.models.room_model import RoomModel
    from app.models.user_model import UserModel


class RoomParticipantLink(SQLModel, table=True):
    __tablename__ = "room_participants"  # type: ignore

    id: UUID = Field(default_factory=uuid7, primary_key=True)

    # Foreign Keys
    room_id: UUID = Field(foreign_key="rooms.id")
    user_id: UUID = Field(foreign_key="users.id")

    role: str  # player / gm

    is_ready: bool = Field(default=False)

    joined_at: datetime = Field(
        default_factory=datetime_utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    # Relationships
    room: Optional["RoomModel"] = Relationship(back_populates="participants")
    user: Optional["UserModel"] = Relationship()

    __table_args__ = (
        Index("ix_room_participants_room_id", "room_id"),
        Index("ix_room_participants_user_id", "user_id"),
    )
