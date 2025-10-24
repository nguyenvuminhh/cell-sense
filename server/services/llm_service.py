from typing import Any

from server.constants import JinjaPromptTemplatesNames
from server.middleware.handle_http_exceptions import InternalServerError
from server.models.chat_models import MessageRequest
from server.utils.get_llm_client import get_llm_client
from server.utils.parse_to_jinja_prompt import parse_to_jinja_prompt


def generate_response(message_request: MessageRequest, template_name: JinjaPromptTemplatesNames, response_schema: dict[str, Any]) -> str:
    # Implementation for generating response using LLM
    client = get_llm_client(
        llm_provider=message_request.llm_provider,
        llm_model=message_request.llm_model
    )
    prompt = parse_to_jinja_prompt(
        request=message_request,
        template_name=template_name
    )
    response = client.models.generate_content(
        model=message_request.llm_model.value,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": response_schema
        }
    )

    if response.text is None:
        raise InternalServerError(f"LLM request failed: {response}")
    return response.text

if __name__ == "__main__":
    # Example usage
    from server.constants import LLMModels, LLMProviders
    from server.models.chat_models import MessageRequest, Range, SelectedRange
    example_request = MessageRequest(
        message="Sum of the two left cells",
        selected_ranges=[SelectedRange(sheet_name_and_range="Sheet1!A1:B2", cell_values=[[1, 2], [3, 4]])],
        target_range=Range(sheet_name_and_range="Sheet1!C1:C2"),
        llm_provider=LLMProviders.GOOGLE,
        llm_model=LLMModels.GOOGLE_GEMINI_2_5_FLASH_LITE
    )
    # response = generate_response(example_request)
    # print(response)
