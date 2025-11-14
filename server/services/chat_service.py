from fastapi import HTTPException

from server.constants import DEFAULT_CHAT_NAME, JinjaPromptTemplatesNames
from server.crud import chats_crud
from server.middleware import NotFoundError
from server.models.chat_models import Chat, ChatMessage, ChatMessageRequest
from server.models.message_models import MessageRequest, MessageResponse
from server.models.user_models import User
from server.services import llm_service


async def handle_message(
    request: MessageRequest, user: User, chat_id: int
) -> MessageResponse:
    # Check if chat has not messages
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")

    if chat.title == DEFAULT_CHAT_NAME:
        title = await get_chat_title(request)
        if title is not None and title != "":
            await chats_crud.update_chat(chat.id, title)

    response = llm_service.generate_response(
        request,
        template_name=JinjaPromptTemplatesNames.LLM_REQUEST_PROMPT,
        response_schema=MessageResponse,
    )
    response_model = MessageResponse.model_validate_json(response)
    user_message_request = ChatMessageRequest(
        chat_id=chat_id,
        content=request.decoded_message,
        is_from_user=True,
        model_name=request.llm_model,
    )
    llm_message_request = ChatMessageRequest(
        chat_id=chat_id,
        content=response_model.message,
        is_from_user=False,
        model_name=request.llm_model,
    )
    await chats_crud.create_message(user_message_request)
    await chats_crud.create_message(llm_message_request)
    return response_model


async def get_user_chats(user_id: int) -> list[Chat]:
    """Get all chats for a user."""
    chat_list = await chats_crud.get_chats_by_user(user_id)

    # Delete chats with 0 messages
    empty_chat_ids = [chat.id for chat in chat_list if len(chat.messages) == 0]
    await chats_crud.delete_chats(empty_chat_ids)

    filtered_chats = [chat for chat in chat_list if len(chat.messages) > 0]
    return filtered_chats


async def create_chat(user_id: int) -> Chat:
    """Create a new chat for a user."""
    return await chats_crud.create_chat(user_id)


async def get_latest_chat(user_id: int) -> Chat:
    """Get the most recently updated chat for a user."""
    chats = await chats_crud.get_chats_by_user(user_id)
    if not chats:
        chat = await chats_crud.create_chat(user_id)
        return chat
    # Chats are ordered by updated_at desc in the CRUD function
    return chats[0]


async def get_chat(chat_id: int, user_id: int) -> Chat:
    """Get a chat by ID with authorization check."""
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    if chat.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return chat


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


async def get_chat_title(message: MessageRequest) -> str:
    response = llm_service.generate_response(
        message,
        template_name=JinjaPromptTemplatesNames.LLM_TITLE_NAMING_PROMPT,
        response_schema=None,
    )
    new_title = response.strip().strip('"').strip("'")
    return new_title
