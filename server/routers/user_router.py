from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from server.middleware.extract_free_user_quota_from_request import (
    extract_free_user_quota_from_request,
)
from server.middleware.extract_user_from_request import (
    extract_user_from_request,
)
from server.models.free_user_quota_models import FreeUserQuota
from server.models.user_models import (
    ApiKeyUpdateRequest,
    User,
    UserWithTruncatedApiKey,
)
from server.services import user_service
from server.utils.get_database_async_session import get_database_async_session

user_router = APIRouter()


@user_router.get("/me", response_model=UserWithTruncatedApiKey)
async def get_current_user(
    user: Annotated[User, Depends(extract_user_from_request)],
) -> UserWithTruncatedApiKey:
    return UserWithTruncatedApiKey(**user.model_dump())


@user_router.get("/quota", response_model=FreeUserQuota)
async def get_free_user_quota(
    free_user_quota: Annotated[
        FreeUserQuota, Depends(extract_free_user_quota_from_request)
    ],
) -> FreeUserQuota:
    return free_user_quota


@user_router.patch("/api-key", response_model=UserWithTruncatedApiKey)
async def update_api_key(
    request: ApiKeyUpdateRequest,
    user: Annotated[User, Depends(extract_user_from_request)],
    session: Annotated[AsyncSession, Depends(get_database_async_session)],
) -> UserWithTruncatedApiKey:
    new_user_model = await user_service.update_api_key(session, request, user)
    return UserWithTruncatedApiKey(**new_user_model.model_dump())
