from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.models.chat_models import Chat, ChatMessage, ChatMessageRequest
from server.schemas.chat_schema import ChatMessageSchema, ChatSchema
from server.utils import get_database_async_session


# --------------- Interface for Testing --------------- #
async def _create_chat(session: AsyncSession, user_id: int) -> Chat:
    chat_data = ChatSchema(user_id=user_id)
    session.add(chat_data)
    await session.flush()
    await session.refresh(chat_data)
    return Chat(**chat_data.__dict__)


async def _get_chat(session: AsyncSession, chat_id: int) -> Chat | None:
    query = select(ChatSchema).where(ChatSchema.id == chat_id)
    result = await session.execute(query)
    chat_record = result.scalar_one_or_none()
    if chat_record:
        return Chat(**chat_record.__dict__)
    return None


async def _get_chats_by_user(session: AsyncSession, user_id: int) -> list[Chat]:
    query = (
        select(ChatSchema)
        .where(ChatSchema.user_id == user_id)
        .options(selectinload(ChatSchema.messages))
        .order_by(ChatSchema.updated_at.desc(), ChatSchema.id.desc())
    )
    result = await session.execute(query)
    chat_records = result.scalars().all()
    return [
        Chat.model_validate(chat, from_attributes=True) for chat in chat_records
    ]


async def _update_chat(
    session: AsyncSession, chat_id: int, chat_title: str
) -> Chat | None:
    query = select(ChatSchema).where(ChatSchema.id == chat_id)
    result = await session.execute(query)
    chat_record = result.scalar_one_or_none()
    if chat_record:
        chat_record.title = chat_title if chat_title else chat_record.title
        session.add(chat_record)
        await session.flush()
        await session.refresh(chat_record)
        return Chat(**chat_record.__dict__)
    return None


async def _delete_chat(session: AsyncSession, chat_id: int) -> bool:
    query = select(ChatSchema).where(ChatSchema.id == chat_id)
    result = await session.execute(query)
    chat_record = result.scalar_one_or_none()
    if chat_record:
        await session.delete(chat_record)
        await session.flush()
        return True
    return False


async def _create_message(
    session: AsyncSession, message: ChatMessageRequest
) -> ChatMessage:
    message_data = ChatMessageSchema(**message.model_dump())
    session.add(message_data)
    await session.flush()
    await session.refresh(message_data)
    return ChatMessage(**message_data.__dict__)


async def _get_messages_by_chat(
    session: AsyncSession, chat_id: int
) -> list[ChatMessage]:
    query = (
        select(ChatMessageSchema)
        .where(ChatMessageSchema.chat_id == chat_id)
        .order_by(ChatMessageSchema.created_at.asc())
    )
    result = await session.execute(query)
    message_records = result.scalars().all()
    return [ChatMessage(**message.__dict__) for message in message_records]


async def _delete_message(session: AsyncSession, message_id: int) -> bool:
    query = select(ChatMessageSchema).where(ChatMessageSchema.id == message_id)
    result = await session.execute(query)
    message_record = result.scalar_one_or_none()
    if message_record:
        await session.delete(message_record)
        await session.flush()
        return True
    return False


# --------------- Interface for Public calls --------------- #
async def create_chat(user_id: int) -> Chat:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _create_chat(session, user_id)


async def get_chat(chat_id: int) -> Chat | None:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _get_chat(session, chat_id)


async def get_chats_by_user(user_id: int) -> list[Chat]:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _get_chats_by_user(session, user_id)


async def update_chat(chat_id: int, chat_title: str) -> Chat | None:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _update_chat(session, chat_id, chat_title)


async def delete_chat(chat_id: int) -> bool:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _delete_chat(session, chat_id)


async def delete_chats(chat_ids: list[int]) -> int:
    async with get_database_async_session() as session:
        async with session.begin():
            deleted_count = 0
            for chat_id in chat_ids:
                success = await _delete_chat(session, chat_id)
                if success:
                    deleted_count += 1
            return deleted_count


async def create_message(message: ChatMessageRequest) -> ChatMessage:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _create_message(session, message)


async def get_messages_by_chat(chat_id: int) -> list[ChatMessage]:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _get_messages_by_chat(session, chat_id)


async def delete_message(message_id: int) -> bool:
    async with get_database_async_session() as session:
        async with session.begin():
            return await _delete_message(session, message_id)
