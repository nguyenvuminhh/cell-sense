from typing import Type

from google.genai.errors import ServerError

from server.constants import (
    GeminiHistoryRoles,
    JinjaPromptTemplatesNames,
    LLMModels,
    LLMProviders,
)
from server.crud import chats_crud
from server.middleware import InternalServerError
from server.models.exception_models import InternalServerErrorPublic
from server.models.message_models import (
    GeminiHistoryEntry,
    GeminiHistoryPart,
    MessageRequest,
    MessageResponse,
    TitleNamingResponse,
    UserPromptAndModelResponse,
)
from server.utils import get_llm_client, parse_to_jinja_prompt


async def generate_response(
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    response_schema: Type[MessageResponse] | Type[TitleNamingResponse],
    api_key: str,
    chat_id: int | None = None,
) -> UserPromptAndModelResponse:
    if message_request.llm_provider == LLMProviders.GOOGLE:
        return await _generate_response_for_gemini(
            message_request=message_request,
            template_name=template_name,
            response_schema=response_schema,
            api_key=api_key,
            chat_id=chat_id,
        )
    else:
        raise InternalServerError(
            f"Unsupported LLM provider: {message_request.llm_provider}"
        )


async def _generate_response_for_gemini(
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    response_schema: Type[MessageResponse] | Type[TitleNamingResponse],
    api_key: str,
    chat_id: int | None,
) -> UserPromptAndModelResponse:
    # Implementation for generating response using LLM
    client = get_llm_client(
        llm_provider=message_request.llm_provider,
        llm_model=message_request.llm_model,
        api_key=api_key,
    )

    content_history = await _build_gemini_content_history(
        message_request=message_request,
        template_name=template_name,
        chat_id=chat_id,
    )
    print("Content History for Gemini:", content_history)
    try:
        response = client.models.generate_content(
            model=LLMModels.GOOGLE_GEMINI_2_5_FLASH_LITE,  # message_request.llm_model.value,
            contents=content_history,
            config={
                "response_mime_type": "application/json",
                "response_schema": response_schema.model_json_schema(),
            },
        )
        if response.text is None:
            raise InternalServerError(f"LLM request failed: {response}")
        print("LLM Response:", response.text)
        return UserPromptAndModelResponse(
            full_user_prompt=content_history[-1].parts[0].text,
            full_model_response=response.text,
        )
    except ServerError as e:
        if e.code == 503:
            raise InternalServerErrorPublic(
                "LLM service is currently unavailable. Please try again later."
            )
        else:
            raise InternalServerError(f"LLM request failed: {e.message}")


async def _build_gemini_content_history(
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    chat_id: int | None,
) -> list[GeminiHistoryEntry]:

    history = []
    prompt = parse_to_jinja_prompt(
        request=message_request, template_name=template_name
    )
    if chat_id is None:
        history = [
            GeminiHistoryEntry(
                role=GeminiHistoryRoles.USER,
                parts=[GeminiHistoryPart(text=prompt)],
            )
        ]
    else:
        messages = await chats_crud.get_messages_by_chat(chat_id)
        for message in messages:
            role = (
                GeminiHistoryRoles.USER
                if message.is_from_user
                else GeminiHistoryRoles.MODEL
            )
            history.append(
                GeminiHistoryEntry(
                    role=role, parts=[GeminiHistoryPart(text=message.content)]
                )
            )
        history.append(
            GeminiHistoryEntry(
                role=GeminiHistoryRoles.USER,
                parts=[GeminiHistoryPart(text=prompt)],
            )
        )

    return [entry for entry in history]
