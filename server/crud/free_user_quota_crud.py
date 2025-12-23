from datetime import datetime, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server import config
from server.models.free_user_quota_models import (
    FreeUserQuota,
    FreeUserQuotaRequest,
)
from server.schemas import FreeUserQuotaSchema


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


async def create_free_user_quota(
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


async def get_free_user_quota_by_user_id(
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


async def decrement_free_user_quota(
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
