from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Index
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlmodel import Column, DateTime, Field, SQLModel

from app.shared.utils import datetime_utcnow, uuid7


class DocumentProcessingLlmCallModel(SQLModel, table=True):
    __tablename__ = "document_processing_llm_calls"  # type: ignore

    id: UUID = Field(default_factory=uuid7, primary_key=True)

    run_id: UUID = Field(foreign_key="document_processing_runs.id")

    step_id: str = Field(max_length=64)

    call_key: str = Field(max_length=128)

    label: str = Field(max_length=256)

    model: str = Field(max_length=128)

    request: list[dict[str, Any]] = Field(
        sa_column=Column(JSONB, nullable=False),
    )

    response: dict[str, Any] | str = Field(
        sa_column=Column(JSONB, nullable=False),
    )

    sequence: int = Field(default=0)

    created_at: datetime = Field(
        default_factory=datetime_utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    __table_args__ = (
        Index("ix_document_processing_llm_calls_run_id", "run_id"),
        Index(
            "ix_document_processing_llm_calls_run_step_key",
            "run_id",
            "step_id",
            "call_key",
        ),
    )
