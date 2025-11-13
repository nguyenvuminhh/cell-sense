from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from server.middleware import extract_user_from_request
from server.models.chat_models import (
    Chat,
    ChatMessage,
    ChatMessageRequest,
    ChatRequest,
)
from server.models.message_models import MessageRequest
from server.models.user_models import User
from server.services import chat_service

chat_router = APIRouter()


@chat_router.post("/send-message")
def send_message(
    request: MessageRequest,
    user: Annotated[User, Depends(extract_user_from_request)],
):
    return chat_service.handle_message(request, user)


@chat_router.get("/list")
async def get_chat_list(
    user: Annotated[User, Depends(extract_user_from_request)],
) -> list[Chat]:
    """Get all chats for the authenticated user."""
    return await chat_service.get_user_chats(user.id)


@chat_router.post("/new")
async def create_new_chat(
    chat_request: ChatRequest,
    user: Annotated[User, Depends(extract_user_from_request)],
) -> Chat:
    """Create a new chat for the authenticated user."""
    return await chat_service.create_chat(user.id, chat_request)


@chat_router.get("/{chat_id}")
async def get_chat(
    chat_id: int,
    user: Annotated[User, Depends(extract_user_from_request)],
) -> Chat:
    """Get a specific chat by ID."""
    return await chat_service.get_chat(chat_id, user.id)


@chat_router.put("/{chat_id}")
async def update_chat(
    chat_id: int,
    chat_update: ChatRequest,
    user: Annotated[User, Depends(extract_user_from_request)],
) -> Chat:
    """Update a chat's title."""
    return await chat_service.update_chat(chat_id, user.id, chat_update)


@chat_router.delete("/{chat_id}")
async def delete_chat(
    chat_id: int,
    user: Annotated[User, Depends(extract_user_from_request)],
) -> dict:
    """Delete a chat and all its messages."""
    await chat_service.delete_chat(chat_id, user.id)
    return {"message": "Chat deleted successfully"}


@chat_router.get("/{chat_id}/messages")
async def get_chat_messages(
    chat_id: int,
    user: Annotated[User, Depends(extract_user_from_request)],
) -> list[ChatMessage]:
    """Get all messages for a specific chat."""
    return await chat_service.get_chat_messages(chat_id, user.id)


@chat_router.post("/{chat_id}/messages")
async def create_message(
    chat_id: int,
    message_request: ChatMessageRequest,
    user: Annotated[User, Depends(extract_user_from_request)],
) -> ChatMessage:
    """Add a new message to a chat."""
    return await chat_service.create_message(chat_id, user.id, message_request)


@chat_router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    user: Annotated[User, Depends(extract_user_from_request)],
) -> dict:
    """Delete a specific message."""
    await chat_service.delete_message(message_id)
    return {"message": "Message deleted successfully"}
