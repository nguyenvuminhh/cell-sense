

from server.constants import JinjaPromptTemplatesNames
from server.models.chat_models import FilledRange, MessageRequest, MessageResponse
from utils.parse_to_jinja_prompt import parse_to_jinja_prompt


def handle_message(
    request: MessageRequest
):
    target_cells = request.target_range
    # Dummy implementation for demonstration purposes
    print("DEBUG", JinjaPromptTemplatesNames.LLM_REQUEST_PROMPT)
    parsed_prompt = parse_to_jinja_prompt(
        request=request,
        template_name=JinjaPromptTemplatesNames.LLM_REQUEST_PROMPT,
    )
    print("DEBUG", parsed_prompt)
    response = MessageResponse(
        message=f"Prompt: {parsed_prompt}",
        filled_range=FilledRange(
            range=target_cells.range,
            sheet_name=target_cells.sheet_name,
            r1c1_value="=SUM(RC[1]:RC[10])"
        )
    )
    return response
