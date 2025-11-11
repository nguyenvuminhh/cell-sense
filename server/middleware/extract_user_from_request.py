from fastapi import Query

from server.crud import users_crud
from server.models.user_models import User, UserRequest
from server.utils import get_logger

logger = get_logger()


async def extract_user_from_request(user_email: str = Query(...)) -> User:
    user = await users_crud.get_user_with_email(email=user_email)
    if user:
        logger.info(f"User found: {user.email}")
        return user
    user = await users_crud.create_user(UserRequest(email=user_email))
    logger.info(f"User created: {user.email}")
    return user
