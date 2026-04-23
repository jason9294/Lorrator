from datetime import datetime

from sqlmodel import DateTime, Field, SQLModel

from app.shared.utils import datetime_utcnow


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime_utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    updated_at: datetime = Field(
        default_factory=datetime_utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore
        sa_column_kwargs={"onupdate": datetime_utcnow},
    )
