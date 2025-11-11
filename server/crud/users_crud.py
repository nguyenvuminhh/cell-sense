from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.models.user_models import User, UserRequest
from server.schemas.user_schema import UserSchema
from server.utils import get_database_async_session


async def _create_user(session: AsyncSession, user: UserRequest) -> User:
    user_data = UserSchema(**user.model_dump())
    session.add(user_data)
    await session.flush()
    await session.refresh(user_data)
    return User(**user_data.__dict__)


async def _get_user_with_email(
    session: AsyncSession, email: str | None = None
) -> User | None:
    query = select(UserSchema).where(UserSchema.email == email)
    result = await session.execute(query)
    user_record = result.scalar_one_or_none()
    if user_record:
        return User(**user_record.__dict__)
    return None


async def _update_user(
    session: AsyncSession, id: int, user_update: UserRequest
) -> User | None:
    query = select(UserSchema).where(UserSchema.id == id)
    result = await session.execute(query)
    user_record = result.scalar_one_or_none()
    if user_record:
        for key, value in user_update.model_dump().items():
            setattr(user_record, key, value)
        session.add(user_record)
        await session.flush()
        await session.refresh(user_record)
        return User(**user_record.__dict__)
    return None


async def _delete_user(session: AsyncSession, id: int) -> bool:
    query = select(UserSchema).where(UserSchema.id == id)
    result = await session.execute(query)
    user_record = result.scalar_one_or_none()
    if user_record:
        await session.delete(user_record)
        await session.flush()
        return True
    return False


# Public API functions that manage their own sessions
async def create_user(user: UserRequest) -> User:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _create_user(session, user)


async def get_user_with_email(email: str | None = None) -> User | None:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _get_user_with_email(session, email)


async def update_user(id: int, user_update: UserRequest) -> User | None:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _update_user(session, id, user_update)


async def delete_user(id: int) -> bool:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _delete_user(session, id)
