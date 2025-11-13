from fastapi import HTTPException

from server.constants import JinjaPromptTemplatesNames
from server.crud import chats_crud
from server.middleware import NotFoundError
from server.models.chat_models import (
    Chat,
    ChatMessage,
    ChatMessageRequest,
    ChatRequest,
)
from server.models.message_models import MessageRequest, MessageResponse
from server.models.user_models import User
from server.services import llm_service


def handle_message(request: MessageRequest, user: User) -> MessageResponse:
    response = llm_service.generate_response(
        request,
        template_name=JinjaPromptTemplatesNames.LLM_REQUEST_PROMPT,
        response_schema=MessageResponse.model_json_schema(),
    )
    return MessageResponse.model_validate_json(response)


async def get_user_chats(user_id: int) -> list[Chat]:
    """Get all chats for a user."""
    return await chats_crud.get_chats_by_user(user_id)


async def create_chat(user_id: int, chat_request: ChatRequest) -> Chat:
    """Create a new chat for a user."""
    return await chats_crud.create_chat(user_id, chat_request)


async def get_chat(chat_id: int, user_id: int) -> Chat:
    """Get a chat by ID with authorization check."""
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    if chat.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return chat


async def update_chat(
    chat_id: int, user_id: int, chat_update: ChatRequest
) -> Chat:
    """Update a chat's title with authorization check."""
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    if chat.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    updated_chat = await chats_crud.update_chat(chat_id, chat_update)
    if not updated_chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    return updated_chat


async def delete_chat(chat_id: int, user_id: int) -> bool:
    """Delete a chat with authorization check."""
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    if chat.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    success = await chats_crud.delete_chat(chat_id)
    if not success:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    return success


async def get_chat_messages(chat_id: int, user_id: int) -> list[ChatMessage]:
    """Get all messages for a chat with authorization check."""
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    if chat.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return await chats_crud.get_messages_by_chat(chat_id)


async def create_message(
    chat_id: int, user_id: int, message_request: ChatMessageRequest
) -> ChatMessage:
    """Create a message in a chat with authorization check."""
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    if chat.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if message_request.chat_id != chat_id:
        raise HTTPException(
            status_code=400,
            detail="chat_id in request body must match URL parameter",
        )
    return await chats_crud.create_message(message_request)


async def delete_message(message_id: int) -> bool:
    """Delete a message."""
    success = await chats_crud.delete_message(message_id)
    if not success:
        raise NotFoundError(f"Message with id {message_id} not found")
    return success
