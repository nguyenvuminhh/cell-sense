from collections.abc import AsyncGenerator

from fastapi.concurrency import asynccontextmanager
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from server.config import DATABASE_URL

async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

local_session = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def get_database_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as session:
        yield session
