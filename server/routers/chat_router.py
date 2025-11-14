from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from server.middleware import extract_user_from_request
from server.models.chat_models import Chat, ChatMessage, ChatMessageRequest
from server.models.message_models import MessageRequest, MessageResponse
from server.models.user_models import User
from server.services import chat_service

chat_router = APIRouter()


@chat_router.post("/{chat_id}/send-message", response_model=MessageResponse)
async def send_message(
    request: MessageRequest,
    user: Annotated[User, Depends(extract_user_from_request)],
    chat_id: int,
) -> MessageResponse:
    """User sends a message and gets a response from the LLM. Both messages are stored in the DB."""
    return await chat_service.handle_message(request, user, chat_id)


@chat_router.get("/list", response_model=list[Chat])
async def get_chat_list(
    user: Annotated[User, Depends(extract_user_from_request)],
) -> list[Chat]:
    """Get all chats for the authenticated user."""
    return await chat_service.get_user_chats(user.id)


@chat_router.post("/new", response_model=Chat)
async def create_new_chat(
    user: Annotated[User, Depends(extract_user_from_request)],
) -> Chat:
    """Create a new chat for the authenticated user."""
    return await chat_service.create_chat(user.id)


@chat_router.get("/latest", response_model=Chat)
async def get_latest_chat(
    user: Annotated[User, Depends(extract_user_from_request)],
) -> Chat:
    """Get the most recently updated chat for the authenticated user."""
    return await chat_service.get_latest_chat(user.id)


@chat_router.get("/{chat_id}", response_model=Chat)
async def get_chat(
    chat_id: int,
    user: Annotated[User, Depends(extract_user_from_request)],
) -> Chat:
    """Get a specific chat by ID."""
    return await chat_service.get_chat(chat_id, user.id)


@chat_router.get("/{chat_id}/messages", response_model=list[ChatMessage])
async def get_chat_messages(
    chat_id: int,
    user: Annotated[User, Depends(extract_user_from_request)],
) -> list[ChatMessage]:
    """Get all messages for a specific chat."""
    return await chat_service.get_chat_messages(chat_id, user.id)


@chat_router.post("/{chat_id}/messages", response_model=ChatMessage)
async def create_message(
    chat_id: int,
    message_request: ChatMessageRequest,
    user: Annotated[User, Depends(extract_user_from_request)],
) -> ChatMessage:
    """Add a new message to a chat."""
    return await chat_service.create_message(chat_id, user.id, message_request)
