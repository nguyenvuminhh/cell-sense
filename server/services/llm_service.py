from typing import Type

from google.genai.errors import ServerError

from server.constants import JinjaPromptTemplatesNames, LLMModels
from server.middleware import InternalServerError
from server.models.exception_models import InternalServerErrorPublic
from server.models.message_models import MessageRequest, MessageResponse
from server.utils import get_llm_client, parse_to_jinja_prompt


def generate_response(
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    response_schema: Type[MessageResponse] | None,
) -> str:
    # Implementation for generating response using LLM
    client = get_llm_client(
        llm_provider=message_request.llm_provider,
        llm_model=message_request.llm_model,
    )
    prompt = parse_to_jinja_prompt(
        request=message_request, template_name=template_name
    )
    if response_schema:
        config = {
            "response_mime_type": "application/json",
            "response_schema": response_schema.model_json_schema(),
        }
    else:
        config = {
            "response_mime_type": "text/plain",
        }
    try:
        response = client.models.generate_content(
            model=LLMModels.GOOGLE_GEMINI_2_5_PRO,  # message_request.llm_model.value,
            contents=prompt,
            config=config,  # type: ignore
        )
        if response.text is None:
            raise InternalServerError(f"LLM request failed: {response}")
        return response.text
    except ServerError as e:
        if e.code == 503:
            raise InternalServerErrorPublic(
                "LLM service is currently unavailable. Please try again later."
            )
        else:
            raise InternalServerError(f"LLM request failed: {e.message}")
