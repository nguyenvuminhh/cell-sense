from typing import Type

from anthropic.types.beta.beta_message_param import BetaMessageParam
from google.genai.errors import ClientError, ServerError
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)
from sqlalchemy.ext.asyncio.session import AsyncSession

from server.constants import ChatRoles, JinjaPromptTemplatesNames, LLMProviders
from server.crud import chats_crud
from server.middleware import InternalServerError
from server.models.exception_models import (
    BadRequestError,
    InternalServerErrorPublic,
)
from server.models.message_models import (
    ChatGPTHistoryEntry,
    ClaudeHistoryEntry,
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
from server.utils.get_llm_client import get_anthropic_claude_client


# ------ Entry point for generating LLM responses ------ #
async def generate_response(
    session: AsyncSession,
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    response_schema: Type[MessageResponse] | Type[TitleNamingResponse],
    api_key: str,
    chat_id: int | None = None,
) -> UserPromptAndModelResponse:
    if message_request.llm_provider == LLMProviders.GOOGLE:
        result = await _generate_response_for_gemini(
            session=session,
            message_request=message_request,
            template_name=template_name,
            response_schema=response_schema,
            api_key=api_key,
            chat_id=chat_id,
        )
    elif message_request.llm_provider == LLMProviders.OPENAI:
        result = await _generate_response_for_chatgpt(
            session=session,
            message_request=message_request,
            template_name=template_name,
            response_schema=response_schema,
            api_key=api_key,
            chat_id=chat_id,
        )
    elif message_request.llm_provider == LLMProviders.ANTHROPIC:
        result = await _generate_response_for_anthropic(
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

    return result


# ------ Generate response functions for each LLM provider ------ #
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
            messages=_parse_chatgpt_content_history(content_history),
            response_format=response_schema,
        )
        if response.choices[0].message.parsed is None:
            raise InternalServerError(f"LLM request failed: {response}")

        return UserPromptAndModelResponse(
            full_user_prompt=content_history[-1].content,
            full_model_response=response.choices[
                0
            ].message.parsed.model_dump_json(),
        )
    except Exception as e:
        raise InternalServerError(f"LLM request failed: {str(e)}")


async def _generate_response_for_anthropic(
    session: AsyncSession,
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    response_schema: Type[MessageResponse] | Type[TitleNamingResponse],
    api_key: str,
    chat_id: int | None,
) -> UserPromptAndModelResponse:
    client = get_anthropic_claude_client(api_key=api_key)
    content_history = await _build_claude_content_history(
        message_request=message_request,
        template_name=template_name,
        chat_id=chat_id,
        session=session,
    )
    try:
        response = client.beta.messages.parse(
            model=message_request.llm_model.value,
            betas=["structured-outputs-2025-11-13"],
            max_tokens=1024,
            messages=_parse_claude_content_history(content_history),
            output_format=response_schema,
        )
        return UserPromptAndModelResponse(
            full_user_prompt=content_history[-1].content,
            full_model_response=response.content[0].text,  # type: ignore
        )
    except Exception as e:
        raise InternalServerError(f"LLM request failed: {str(e)}")


# ------ Build content history for each LLM provider ------ #
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
            role = ChatRoles.USER if message.is_from_user else ChatRoles.MODEL
            history.append(
                GeminiHistoryEntry(
                    role=role, parts=[GeminiHistoryPart(text=message.content)]
                )
            )
    history.append(
        GeminiHistoryEntry(
            role=ChatRoles.USER,
            parts=[GeminiHistoryPart(text=prompt)],
        )
    )

    return history


async def _build_chatgpt_content_history(
    session: AsyncSession,
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    chat_id: int | None,
) -> list[ChatGPTHistoryEntry]:

    history = []
    prompt = parse_to_jinja_prompt(
        request=message_request, template_name=template_name
    )
    if chat_id is not None:
        messages = await chats_crud.get_messages_by_chat(session, chat_id)
        for message in messages[:30]:
            if message.is_from_user:
                history.append(
                    ChatGPTHistoryEntry(
                        content=message.content,
                        role=ChatRoles.USER,
                    )
                )
            else:
                history.append(
                    ChatGPTHistoryEntry(
                        content=message.content,
                        role=ChatRoles.ASSISTANT,
                    )
                )
    history.append(
        ChatGPTHistoryEntry(
            role=ChatRoles.USER,
            content=prompt,
        )
    )
    return history


def _parse_chatgpt_content_history(
    content_history_pydantic: list[ChatGPTHistoryEntry],
) -> list[ChatCompletionMessageParam]:
    parsed_content_history = []
    for entry in content_history_pydantic:
        if entry.role == ChatRoles.USER:
            parsed_content_history.append(
                ChatCompletionUserMessageParam(
                    role=entry.role.value, content=entry.content
                )
            )
        elif entry.role == ChatRoles.ASSISTANT:
            parsed_content_history.append(
                ChatCompletionAssistantMessageParam(
                    role=entry.role.value, content=entry.content
                )
            )
        else:
            raise InternalServerError(
                f"Unsupported chat role in history: {entry.role}"
            )

    return parsed_content_history


async def _build_claude_content_history(
    session: AsyncSession,
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    chat_id: int | None,
) -> list[ClaudeHistoryEntry]:
    history = []
    prompt = parse_to_jinja_prompt(
        request=message_request, template_name=template_name
    )
    if chat_id is not None:
        messages = await chats_crud.get_messages_by_chat(session, chat_id)
        for message in messages[:30]:
            if message.is_from_user:
                history.append(
                    ChatGPTHistoryEntry(
                        content=message.content,
                        role=ChatRoles.USER,
                    )
                )
            else:
                history.append(
                    ChatGPTHistoryEntry(
                        content=message.content,
                        role=ChatRoles.ASSISTANT,
                    )
                )
    history.append(
        ChatGPTHistoryEntry(
            role=ChatRoles.USER,
            content=prompt,
        )
    )
    return history


def _parse_claude_content_history(
    content_history_pydantic: list[ClaudeHistoryEntry],
) -> list[BetaMessageParam]:
    parsed_content_history = []
    for entry in content_history_pydantic:
        if entry.role == ChatRoles.USER:
            parsed_content_history.append(
                BetaMessageParam(role=entry.role.value, content=entry.content)
            )
        elif entry.role == ChatRoles.ASSISTANT:
            parsed_content_history.append(
                BetaMessageParam(role=entry.role.value, content=entry.content)
            )
        else:
            raise InternalServerError(
                f"Unsupported chat role in history: {entry.role}"
            )

    return parsed_content_history
