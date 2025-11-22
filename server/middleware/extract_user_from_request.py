from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from server.crud import users_crud
from server.models.user_models import User, UserRequest
from server.utils import get_logger
from server.utils.get_database_async_session import get_database_async_session

logger = get_logger()


async def extract_user_from_request(
    user_email: str = Query(...),
    session: AsyncSession = Depends(get_database_async_session),
) -> User:
    user = await users_crud.get_user_with_email(session, email=user_email)
    if user:
        logger.info(f"User found: {user.email}")
        return user
    user = await users_crud.create_user(session, UserRequest(email=user_email))
    logger.info(f"User created: {user.email}")
    return user
