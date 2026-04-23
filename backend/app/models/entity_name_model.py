from typing import Any
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from app.shared.utils import uuid7

from .mixin.timestamp import TimestampMixin


class EntityNameModel(TimestampMixin, SQLModel, table=True):
    __tablename__ = "entity_names"  # type: ignore

    id: UUID = Field(default_factory=uuid7, primary_key=True)

    name: str = Field(max_length=255)
    vector: Any = Field(sa_column=Column(Vector(1536), nullable=False))

    entity_id: UUID = Field(foreign_key="entities.id")
