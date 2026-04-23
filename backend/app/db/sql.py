from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import InstrumentedAttribute

# from sqlmodel import Session, create_engine
from app.core.setting import get_settings

settings = get_settings()

# --- Sync Session (SQLModel) ----------------------------------

# engine = create_engine(settings.DATABASE_URL, echo=True)


# def provide_session():
#     with Session(engine) as session:
#         yield session


# SessionDependency = Annotated[Session, Depends(provide_session)]
# ---------------------------------------------------------------

# --- Async Session (SQLAlchemy) -------------------------------
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    # 可視流量調整：
    # pool_size=10,
    # max_overflow=20,
)


async def provide_async_session():
    async with AsyncSession(async_engine) as session:
        yield session


AsyncSessionDependency = Annotated[AsyncSession, Depends(provide_async_session)]


# --- Helper ----------------------------------------------------
def attr(instance: Any) -> InstrumentedAttribute:
    return instance
