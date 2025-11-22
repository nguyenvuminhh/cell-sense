from datetime import datetime, time
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from server import config
from server.crud import free_user_quota_crud
from server.middleware.extract_user_from_request import (
    extract_user_from_request,
)
from server.models.free_user_quota_models import (
    FreeUserQuota,
    FreeUserQuotaRequest,
)
from server.models.user_models import User
from server.utils import get_logger
from server.utils.get_database_async_session import get_database_async_session

logger = get_logger()


async def extract_free_user_quota_from_request(
    user: Annotated[User, Depends(extract_user_from_request)],
    session: AsyncSession = Depends(get_database_async_session),
) -> FreeUserQuota:
    quota = await free_user_quota_crud.get_free_user_quota_by_user_id(
        session, user.id
    )
    if quota:
        logger.info(
            f"Free user quota found for user {user.email}: {quota.free_quota_remaining} remaining."
        )
        return quota
    # If no quota exists, create a new one with default values
    default_quota = FreeUserQuotaRequest(
        user_id=user.id,
        free_quota_remaining=config.FREE_USER_DAILY_QUOTA,  # Default free quota
        next_reset=datetime.combine(datetime.today(), time(23, 59, 59)),
    )
    created_quota = await free_user_quota_crud.create_free_user_quota(
        session, default_quota
    )
    logger.info(
        f"Free user quota created for user {user.email}: {created_quota.free_quota_remaining} remaining."
    )
    return created_quota
