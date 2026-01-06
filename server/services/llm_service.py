from typing import Type

from google.genai.errors import ClientError, ServerError
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)
from sqlalchemy.ext.asyncio.session import AsyncSession

from server.constants import (
    ChatGPTHistoryRoles,
    GeminiHistoryRoles,
    JinjaPromptTemplatesNames,
    LLMProviders,
)
from server.crud import chats_crud
from server.middleware import InternalServerError
from server.models.exception_models import (
    BadRequestError,
    InternalServerErrorPublic,
)
from server.models.message_models import (
    ChatGPTHistoryEntry,
    GeminiHistoryEntry,
    GeminiHistoryPart,
    MessageRequest,
    MessageResponse,
    TitleNamingResponse,
    UserPromptAndModelResponse,
)
from server.utils import (
    get_google_gemini_client,
    get_openai_chatgpt_client,
    parse_to_jinja_prompt,
)


async def generate_response(
    session: AsyncSession,
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    response_schema: Type[MessageResponse] | Type[TitleNamingResponse],
    api_key: str,
    chat_id: int | None = None,
) -> UserPromptAndModelResponse:
    if message_request.llm_provider == LLMProviders.GOOGLE:
        return await _generate_response_for_gemini(
            session=session,
            message_request=message_request,
            template_name=template_name,
            response_schema=response_schema,
            api_key=api_key,
            chat_id=chat_id,
        )
    elif message_request.llm_provider == LLMProviders.OPENAI:
        return await _generate_response_for_chatgpt(
            session=session,
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
    session: AsyncSession,
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    response_schema: Type[MessageResponse] | Type[TitleNamingResponse],
    api_key: str,
    chat_id: int | None,
) -> UserPromptAndModelResponse:
    client = get_google_gemini_client(api_key=api_key)

    content_history = await _build_gemini_content_history(
        message_request=message_request,
        template_name=template_name,
        chat_id=chat_id,
        session=session,
    )

    try:
        response = client.models.generate_content(
            model=message_request.llm_model.value,
            contents=content_history,
            config={
                "response_mime_type": "application/json",
                "response_schema": response_schema.model_json_schema(),
            },
        )
        if response.text is None:
            raise InternalServerError(f"LLM request failed: {response}")

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
    except ClientError as e:
        if e.code == 400:
            raise BadRequestError(f"LLM request failed: {e.message}")
        else:
            raise InternalServerError(f"LLM request failed: {e.message}")


async def _generate_response_for_chatgpt(
    session: AsyncSession,
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    response_schema: Type[MessageResponse] | Type[TitleNamingResponse],
    api_key: str,
    chat_id: int | None,
) -> UserPromptAndModelResponse:
    client = get_openai_chatgpt_client(api_key=api_key)
    content_history = await _build_chatgpt_content_history(
        message_request=message_request,
        template_name=template_name,
        chat_id=chat_id,
        session=session,
    )
    try:
        response = client.chat.completions.parse(
            model=message_request.llm_model.value,
            messages=content_history,
            response_format=response_schema,
        )
        if response.choices[0].message.parsed is None:
            raise InternalServerError(f"LLM request failed: {response}")

        full_user_prompt = content_history[-1].get("content", "")
        if not full_user_prompt or not isinstance(full_user_prompt, str):
            raise InternalServerError(
                "Failed to extract full user prompt from history."
            )

        return UserPromptAndModelResponse(
            full_user_prompt=full_user_prompt,
            full_model_response=response.choices[
                0
            ].message.parsed.model_dump_json(),
        )
    except ServerError as e:
        if e.code == 503:
            raise InternalServerErrorPublic(
                "LLM service is currently unavailable. Please try again later."
            )
        else:
            raise InternalServerError(f"LLM request failed: {e.message}")
    except ClientError as e:
        if e.code == 400:
            raise BadRequestError(f"LLM request failed: {e.message}")
        else:
            raise InternalServerError(f"LLM request failed: {e.message}")


async def _build_gemini_content_history(
    session: AsyncSession,
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    chat_id: int | None,
) -> list[GeminiHistoryEntry]:

    history = []
    prompt = parse_to_jinja_prompt(
        request=message_request, template_name=template_name
    )
    if chat_id is not None:
        messages = await chats_crud.get_messages_by_chat(session, chat_id)
        for message in messages[:30]:
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

    return history


async def _build_chatgpt_content_history(
    session: AsyncSession,
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    chat_id: int | None,
) -> list[ChatCompletionMessageParam]:

    history = []
    prompt = parse_to_jinja_prompt(
        request=message_request, template_name=template_name
    )
    if chat_id is not None:
        messages = await chats_crud.get_messages_by_chat(session, chat_id)
        for message in messages[:30]:
            if message.is_from_user:
                history.append(
                    ChatCompletionUserMessageParam(
                        content=message.content,
                        role=ChatGPTHistoryRoles.USER.value,
                    )
                )
            else:
                history.append(
                    ChatCompletionAssistantMessageParam(
                        content=message.content,
                        role=ChatGPTHistoryRoles.ASSISTANT.value,
                    )
                )
    history.append(
        ChatGPTHistoryEntry(
            role=ChatGPTHistoryRoles.USER,
            content=prompt,
        )
    )

    return history
