from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlmodel import Column, DateTime, Field, SQLModel

from app.shared.enums import ProcessingRunStatus
from app.shared.utils import datetime_utcnow, uuid7


class DocumentProcessingRunModel(SQLModel, table=True):
    __tablename__ = "document_processing_runs"  # type: ignore

    id: UUID = Field(default_factory=uuid7, primary_key=True)

    document_id: UUID = Field(foreign_key="documents.id")

    pipeline_id: str = Field(max_length=128)

    status: ProcessingRunStatus = Field(default=ProcessingRunStatus.RUNNING)

    started_at: datetime = Field(
        default_factory=datetime_utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    completed_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    total_duration_ms: int | None = Field(default=None)

    steps: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
    )

    error: str | None = Field(default=None, max_length=4096)

    __table_args__ = (
        UniqueConstraint("document_id", name="uq_document_processing_runs_document_id"),
        Index("ix_document_processing_runs_document_id", "document_id"),
    )
