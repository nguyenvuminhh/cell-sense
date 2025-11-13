from pydantic import BaseModel

from server.models import BaseSchemaInPydantic


class ChatRequest(BaseModel):
    title: str = "New Chat"
    user_id: int


class Chat(BaseSchemaInPydantic, ChatRequest):
    pass


class ChatMessageRequest(BaseModel):
    chat_id: int
    content: str
    is_from_user: bool
    model_name: str | None = None

    def model_post_init(self, __context):
        if not self.is_from_user and self.model_name is None:
            raise ValueError(
                "model_name must be provided when is_from_user is False"
            )


class ChatMessage(BaseSchemaInPydantic, ChatMessageRequest):
    pass
