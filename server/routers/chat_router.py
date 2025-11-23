from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from server.middleware import extract_user_from_request
from server.middleware.extract_free_user_quota_from_request import (
    extract_free_user_quota_from_request,
)
from server.models.chat_models import Chat, ChatMessage
from server.models.free_user_quota_models import FreeUserQuota
from server.models.message_models import MessageRequest, MessageResponse
from server.models.user_models import User
from server.services import chat_service
from server.utils.get_database_async_session import get_database_async_session

chat_router = APIRouter()


@chat_router.post("/{chat_id}/send-message", response_model=MessageResponse)
async def send_message(
    request: MessageRequest,
    user: Annotated[User, Depends(extract_user_from_request)],
    free_user_quota: Annotated[
        FreeUserQuota, Depends(extract_free_user_quota_from_request)
    ],
    session: Annotated[AsyncSession, Depends(get_database_async_session)],
    chat_id: int,
) -> MessageResponse:
    return await chat_service.handle_message(session, request, user, chat_id)


@chat_router.get("/list", response_model=list[Chat])
async def get_chat_list(
    user: Annotated[User, Depends(extract_user_from_request)],
    session: Annotated[AsyncSession, Depends(get_database_async_session)],
) -> list[Chat]:
    return await chat_service.get_user_chats(user, session)


@chat_router.post("/new", response_model=Chat)
async def create_new_chat(
    user: Annotated[User, Depends(extract_user_from_request)],
    session: Annotated[AsyncSession, Depends(get_database_async_session)],
) -> Chat:
    return await chat_service.create_chat(session, user)


@chat_router.get("/latest", response_model=Chat)
async def get_latest_chat(
    user: Annotated[User, Depends(extract_user_from_request)],
    session: Annotated[AsyncSession, Depends(get_database_async_session)],
) -> Chat:
    return await chat_service.get_latest_chat(session, user)


@chat_router.get("/{chat_id}", response_model=Chat)
async def get_chat(
    chat_id: int,
    user: Annotated[User, Depends(extract_user_from_request)],
    session: Annotated[AsyncSession, Depends(get_database_async_session)],
) -> Chat:
    return await chat_service.get_chat(session, chat_id, user)


@chat_router.get("/{chat_id}/messages", response_model=list[ChatMessage])
async def get_chat_messages(
    chat_id: int,
    user: Annotated[User, Depends(extract_user_from_request)],
    session: Annotated[AsyncSession, Depends(get_database_async_session)],
) -> list[ChatMessage]:
    return await chat_service.get_chat_messages(session, chat_id, user)
