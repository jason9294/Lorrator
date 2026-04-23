from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Index
from sqlmodel import Field, Relationship

from app.shared.enums import ScenarioStatus
from app.shared.utils import uuid7

from .mixin.timestamp import TimestampMixin

if TYPE_CHECKING:
    from app.models.user_model import UserModel


class ScenarioModel(TimestampMixin, table=True):  # type: ignore
    __tablename__ = "scenarios"  # type: ignore

    # Primary Key
    id: UUID = Field(default_factory=uuid7, primary_key=True)

    name: str
    description: Optional[str] = None

    system: str  # COC, DND, etc.

    min_players: Optional[int] = Field(
        default=None,
        ge=1,
        description="Minimum recommended player count",
    )
    max_players: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum recommended player count",
    )

    min_hours: Optional[float] = Field(
        default=None,
        ge=1,
        description="Minimum recommended playtime in hours",
    )
    max_hours: Optional[float] = Field(
        default=None,
        ge=1,
        description="Maximum recommended playtime in hours",
    )

    status: ScenarioStatus = Field(default=ScenarioStatus.DRAFT)

    creator_id: UUID = Field(foreign_key="users.id")
    creator: "UserModel" = Relationship()

    graph_group_id: UUID = Field(default_factory=uuid7)

    __table_args__ = (Index("ix_scenarios_creator_id", "creator_id"),)
