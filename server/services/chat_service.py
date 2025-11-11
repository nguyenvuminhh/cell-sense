from server.constants import JinjaPromptTemplatesNames
from server.models.chat_models import MessageRequest, MessageResponse
from server.models.user_models import User
from server.services import llm_service


def handle_message(request: MessageRequest, user: User) -> MessageResponse:
    response = llm_service.generate_response(
        request,
        template_name=JinjaPromptTemplatesNames.LLM_REQUEST_PROMPT,
        response_schema=MessageResponse.model_json_schema(),
    )
    return MessageResponse.model_validate_json(response)
