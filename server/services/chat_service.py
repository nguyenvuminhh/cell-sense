from fastapi import HTTPException

from server.config import GEMINI_API_KEY
from server.constants import (
    DEFAULT_CHAT_NAME,
    JinjaPromptTemplatesNames,
    LLMProviders,
)
from server.crud import chats_crud, free_user_quota_crud
from server.middleware import NotFoundError
from server.models.chat_models import Chat, ChatMessage, ChatMessageRequest
from server.models.exception_models import BadRequestError, InternalServerError
from server.models.free_user_quota_models import FreeUserQuota
from server.models.message_models import (
    MessageRequest,
    MessageResponse,
    TitleNamingResponse,
)
from server.models.user_models import User
from server.services import llm_service


async def handle_message(
    request: MessageRequest,
    free_user_quota: FreeUserQuota,
    user: User,
    chat_id: int,
) -> MessageResponse:
    # Check if chat has not messages
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")

    if chat.title == DEFAULT_CHAT_NAME:
        title = await _get_chat_title(request)
        if title is not None and title != "":
            await chats_crud.update_chat(chat.id, title)

    prompt_and_response = await llm_service.generate_response(
        request,
        template_name=JinjaPromptTemplatesNames.LLM_REQUEST_PROMPT,
        response_schema=MessageResponse,
        api_key=await _get_api_key(request, user),
        chat_id=chat_id,
    )
    response_model = MessageResponse.model_validate_json(
        prompt_and_response.full_model_response
    )
    user_message_request = ChatMessageRequest(
        chat_id=chat_id,
        content=request.decoded_message,
        is_from_user=True,
        model_name=request.llm_model,
        full_user_prompt=prompt_and_response.full_user_prompt,
    )
    llm_message_request = ChatMessageRequest(
        chat_id=chat_id,
        content=response_model.message,
        is_from_user=False,
        model_name=request.llm_model,
        full_model_response=prompt_and_response.full_model_response,
    )
    await chats_crud.create_message(user_message_request)
    await chats_crud.create_message(llm_message_request)
    return response_model


async def get_user_chats(user: User) -> list[Chat]:
    chat_list = await chats_crud.get_chats_by_user(user.id)

    # Delete chats with 0 messages
    empty_chat_ids = [chat.id for chat in chat_list if len(chat.messages) == 0]
    await chats_crud.delete_chats(empty_chat_ids)

    filtered_chats = [chat for chat in chat_list if len(chat.messages) > 0]
    return filtered_chats


async def create_chat(user: User) -> Chat:
    return await chats_crud.create_chat(user.id)


async def get_latest_chat(user: User) -> Chat:
    chats = await chats_crud.get_chats_by_user(user.id)
    if not chats:
        chat = await chats_crud.create_chat(user.id)
        return chat
    # Chats are ordered by updated_at desc in the CRUD function
    return chats[0]


async def get_chat(chat_id: int, user: User) -> Chat:
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    if chat.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return chat


async def delete_chat(chat_id: int, user: User) -> bool:
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    if chat.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    success = await chats_crud.delete_chat(chat_id)
    if not success:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    return success


async def get_chat_messages(chat_id: int, user: User) -> list[ChatMessage]:
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    if chat.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return await chats_crud.get_messages_by_chat(chat_id)


async def create_message(
    chat_id: int, user: User, message_request: ChatMessageRequest
) -> ChatMessage:
    chat = await chats_crud.get_chat(chat_id)
    if not chat:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    if chat.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if message_request.chat_id != chat_id:
        raise HTTPException(
            status_code=400,
            detail="chat_id in request body must match URL parameter",
        )
    return await chats_crud.create_message(message_request)


async def delete_message(message_id: int) -> bool:
    success = await chats_crud.delete_message(message_id)
    if not success:
        raise NotFoundError(f"Message with id {message_id} not found")
    return success


async def _get_chat_title(message: MessageRequest) -> str:
    system_api_key = GEMINI_API_KEY
    if not system_api_key:
        raise InternalServerError(
            "GEMINI_API_KEY is not set in the environment variables."
        )
    prompt_and_response = await llm_service.generate_response(
        message,
        template_name=JinjaPromptTemplatesNames.LLM_TITLE_NAMING_PROMPT,
        response_schema=TitleNamingResponse,
        api_key=system_api_key,
        chat_id=None,
    )
    response = TitleNamingResponse.model_validate_json(
        prompt_and_response.full_model_response
    )
    new_title = (
        response.title.strip().strip('"').strip("'")
        if not response.message_is_unclear
        else ""
    )
    return new_title


async def _get_api_key(request: MessageRequest, user: User) -> str:
    if request.llm_provider == LLMProviders.GOOGLE:
        if not user.gemini_api_key:
            quota_model, success = (
                await free_user_quota_crud.decrement_free_user_quota(user.id)
            )
            if not quota_model:
                raise NotFoundError("Free user quota not found.")
            if not success:
                raise BadRequestError("No quota is left.")
            if not GEMINI_API_KEY:
                raise InternalServerError(
                    "GEMINI_API_KEY is not set in the environment variables."
                )
            return GEMINI_API_KEY
        return user.gemini_api_key
    else:
        raise InternalServerError(
            f"Unsupported LLM provider: {request.llm_provider}"
        )
