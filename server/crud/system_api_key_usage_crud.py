from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server import config
from server.models.system_api_key_usage_models import SystemApiKeyUsage
from server.schemas import SystemApiKeyUsageSchema


async def get_usage_for_today(
    session: AsyncSession,
) -> SystemApiKeyUsage | None:
    today = date.today()
    query = select(SystemApiKeyUsageSchema).where(
        SystemApiKeyUsageSchema.date == today
    )
    result = await session.execute(query)
    usage_record = result.scalar_one_or_none()
    if usage_record:
        return SystemApiKeyUsage(**usage_record.__dict__)
    return None


async def increment_usage(
    session: AsyncSession,
) -> tuple[SystemApiKeyUsage, bool]:
    """
    Increment the usage count for today.
    Returns (usage_record, success) where success is False if limit exceeded.
    """
    today = date.today()
    query = select(SystemApiKeyUsageSchema).where(
        SystemApiKeyUsageSchema.date == today
    )
    result = await session.execute(query)
    usage_record = result.scalar_one_or_none()

    if usage_record is None:
        # Create new record for today
        usage_record = SystemApiKeyUsageSchema(date=today, count=1)
        session.add(usage_record)
        await session.flush()
        await session.refresh(usage_record)
        return SystemApiKeyUsage(**usage_record.__dict__), True

    # Check if limit exceeded
    if usage_record.count >= config.SYSTEM_API_KEY_DAILY_LIMIT:
        return SystemApiKeyUsage(**usage_record.__dict__), False

    # Increment count
    usage_record.count = usage_record.count + 1
    session.add(usage_record)
    await session.flush()
    await session.refresh(usage_record)
    return SystemApiKeyUsage(**usage_record.__dict__), True
