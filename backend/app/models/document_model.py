from uuid import UUID

from sqlalchemy import Index
from sqlmodel import Field, SQLModel

from app.shared.enums import DocumentStatus
from app.shared.utils import uuid7

from .mixin.timestamp import TimestampMixin


class DocumentModel(TimestampMixin, SQLModel, table=True):
    __tablename__ = "documents"  # type: ignore

    # Primary Key
    id: UUID = Field(default_factory=uuid7, primary_key=True)

    scenario_id: UUID = Field(foreign_key="scenarios.id")

    filename: str = Field(max_length=512)
    content_type: str = Field(max_length=255)
    file_path: str = Field(max_length=2048)
    md_path: str = Field(max_length=2048)

    status: DocumentStatus = Field(default=DocumentStatus.READY)

    __table_args__ = (Index("ix_documents_scenario_id", "scenario_id"),)
