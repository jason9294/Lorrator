from uuid import UUID

from sqlmodel import Field, SQLModel

from app.shared.utils import uuid7


class ModelName(SQLModel, table=True):
    __tablename__ = "model_name"  # type: ignore

    # Primary Key
    id: UUID = Field(default_factory=uuid7, primary_key=True)
