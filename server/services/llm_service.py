from typing import Any

from server.constants import JinjaPromptTemplatesNames
from server.middleware import InternalServerError
from server.models.chat_models import MessageRequest
from server.utils import get_llm_client, parse_to_jinja_prompt


def generate_response(
    message_request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
    response_schema: dict[str, Any],
) -> str:
    # Implementation for generating response using LLM
    client = get_llm_client(
        llm_provider=message_request.llm_provider,
        llm_model=message_request.llm_model,
    )
    prompt = parse_to_jinja_prompt(
        request=message_request, template_name=template_name
    )
    response = client.models.generate_content(
        model=message_request.llm_model.value,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": response_schema,
        },
    )

    if response.text is None:
        raise InternalServerError(f"LLM request failed: {response}")
    return response.text
