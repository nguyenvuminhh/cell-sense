from collections.abc import AsyncGenerator
from datetime import datetime

from fastapi.concurrency import asynccontextmanager
from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
)

from server.config import DATABASE_URL


class BaseSchema(DeclarativeBase, MappedAsDataclass):
    # Automatically set when record is first created
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        init=False,
    )

    # Automatically updated whenever record changes
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )


async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

local_session = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def get_database_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as session:
        yield session
