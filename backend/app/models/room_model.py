import secrets
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Index
from sqlmodel import Field, Relationship, SQLModel

from app.shared.enums import RoomStatus
from app.shared.utils import uuid7

if TYPE_CHECKING:
    from app.models.links.room_participant_link import RoomParticipantLink


def _generate_invite_code() -> str:
    return secrets.token_hex(4).upper()


class RoomModel(SQLModel, table=True):
    __tablename__ = "rooms"  # type: ignore

    # Primary Key
    id: UUID = Field(default_factory=uuid7, primary_key=True)

    scenario_id: UUID = Field(foreign_key="scenarios.id")

    # 基本資訊
    name: str = Field(max_length=255)
    description: Optional[str] = None

    status: RoomStatus = Field(default=RoomStatus.PREPARING)

    # 邀請碼
    invite_code: str = Field(default_factory=_generate_invite_code, max_length=16)

    # 房主（GM）
    host_id: UUID = Field(foreign_key="users.id")

    # 關聯：參與者
    participants: list["RoomParticipantLink"] = Relationship(back_populates="room")

    graph_group_id: UUID = Field(default_factory=uuid7)

    __table_args__ = (Index("ix_rooms_host_id", "host_id"),)
