from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Index
from sqlmodel import Field, Relationship, SQLModel

from app.shared.utils import uuid7

from .mixin.timestamp import TimestampMixin

if TYPE_CHECKING:
    from app.models.room_model import RoomModel
    from app.models.scenario_model import ScenarioModel


class FactModel(TimestampMixin, SQLModel, table=True):
    """跑團過程中已發生的事實（依房間與劇本歸檔）。"""

    __tablename__ = "facts"  # type: ignore

    id: UUID = Field(default_factory=uuid7, primary_key=True)

    room_id: UUID = Field(foreign_key="rooms.id")
    scenario_id: UUID = Field(foreign_key="scenarios.id")

    content: str

    room: Optional["RoomModel"] = Relationship()
    scenario: Optional["ScenarioModel"] = Relationship()

    __table_args__ = (Index("ix_facts_room_id", "room_id"),)
