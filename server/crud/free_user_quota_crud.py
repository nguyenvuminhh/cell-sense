from datetime import datetime, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server import config
from server.models.free_user_quota_models import (
    FreeUserQuota,
    FreeUserQuotaRequest,
)
from server.schemas import FreeUserQuotaSchema
from server.utils import get_database_async_session


# --------------- Interface for Testing --------------- #
async def _reset_quota(
    session: AsyncSession,
    quota_record: FreeUserQuotaSchema,
) -> FreeUserQuotaSchema:
    if quota_record.next_reset <= datetime.now():
        quota_record.free_quota_remaining = config.FREE_USER_DAILY_QUOTA
        quota_record.next_reset = datetime.combine(
            datetime.today(), time(23, 59, 59)
        )
        session.add(quota_record)
        await session.flush()
        await session.refresh(quota_record)
        return quota_record
    return quota_record


async def _create_free_user_quota(
    session: AsyncSession,
    request: FreeUserQuotaRequest,
) -> FreeUserQuota:
    quota_data = FreeUserQuotaSchema(
        user_id=request.user_id,
        free_quota_remaining=request.free_quota_remaining,
        next_reset=request.next_reset,
    )
    session.add(quota_data)
    await session.flush()
    await session.refresh(quota_data)
    return FreeUserQuota(**quota_data.__dict__)


async def _get_free_user_quota_by_user_id(
    session: AsyncSession, user_id: int
) -> FreeUserQuota | None:
    query = select(FreeUserQuotaSchema).where(
        FreeUserQuotaSchema.user_id == user_id
    )
    result = await session.execute(query)
    quota_record = result.scalar_one_or_none()
    if quota_record:
        quota_record = await _reset_quota(session, quota_record)
        return FreeUserQuota(**quota_record.__dict__)
    return None


async def _decrement_free_user_quota(
    session: AsyncSession, user_id: int
) -> tuple[FreeUserQuota | None, bool]:
    query = select(FreeUserQuotaSchema).where(
        FreeUserQuotaSchema.user_id == user_id
    )
    result = await session.execute(query)
    quota_record = result.scalar_one_or_none()
    if quota_record:
        quota_record = await _reset_quota(session, quota_record)
        if quota_record.free_quota_remaining <= 0:
            return FreeUserQuota(**quota_record.__dict__), False
        quota_record.free_quota_remaining = (
            quota_record.free_quota_remaining - 1
        )
        session.add(quota_record)
        await session.flush()
        await session.refresh(quota_record)
        return FreeUserQuota(**quota_record.__dict__), True
    return None, False


# --------------- Interface for Public calls --------------- #
async def create_free_user_quota(
    request: FreeUserQuotaRequest,
) -> FreeUserQuota:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _create_free_user_quota(session, request)


async def get_free_user_quota_by_user_id(
    user_id: int,
) -> FreeUserQuota | None:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _get_free_user_quota_by_user_id(session, user_id)


async def decrement_free_user_quota(
    user_id: int, amount: int = 1
) -> tuple[FreeUserQuota | None, bool]:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _decrement_free_user_quota(session, user_id)
