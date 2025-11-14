from pydantic import BaseModel, model_validator

from server.constants import DEFAULT_CHAT_NAME, LLMModels
from server.models import BaseSchemaInPydantic


class ChatMessageRequest(BaseModel):
    chat_id: int
    content: str
    is_from_user: bool
    model_name: LLMModels | None = None

    @model_validator(mode="after")
    def check_model_name(self):
        """
        When is_from_user=False (LLM response), model_name must be provided.
        """
        if not self.is_from_user and self.model_name is None:
            raise ValueError(
                "model_name must be provided when is_from_user is False"
            )
        return self


class ChatMessage(BaseSchemaInPydantic, ChatMessageRequest):
    pass


class Chat(BaseSchemaInPydantic):
    title: str = DEFAULT_CHAT_NAME
    user_id: int
    messages: list["ChatMessage"] = []
