from typing import Any
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import Index
from sqlmodel import Column, Field, SQLModel

from app.shared.utils import uuid7


class EmbeddingModel(SQLModel, table=True):
    __tablename__ = "embeddings"  # type: ignore

    # Primary Key
    id: UUID = Field(default_factory=uuid7, primary_key=True)

    scenario_id: UUID = Field(foreign_key="scenarios.id")

    content: str
    vector: Any = Field(sa_column=Column(Vector(1536)))

    target_type: str
    target_id: UUID

    __table_args__ = (Index("ix_embeddings_scenario_id", "scenario_id"),)
