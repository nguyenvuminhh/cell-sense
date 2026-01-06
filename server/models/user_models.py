from pydantic import BaseModel, model_validator

from server.models import BaseSchemaInPydantic


class UserRequest(BaseModel):
    email: str
    gemini_api_key: str | None = None
    chatgpt_api_key: str | None = None
    claude_api_key: str | None = None


class User(BaseSchemaInPydantic, UserRequest):
    pass


class UserWithTruncatedApiKey(User):

    @model_validator(mode="after")
    def truncate_api_key(self):
        if self.gemini_api_key:
            truncated_key = (
                self.gemini_api_key[:4] + "..." + self.gemini_api_key[-4:]
            )
            self.gemini_api_key = truncated_key
        if self.chatgpt_api_key:
            truncated_key = (
                self.chatgpt_api_key[:4] + "..." + self.chatgpt_api_key[-4:]
            )
            self.chatgpt_api_key = truncated_key
        if self.claude_api_key:
            truncated_key = (
                self.claude_api_key[:4] + "..." + self.claude_api_key[-4:]
            )
            self.claude_api_key = truncated_key
        return self


class ApiKeyUpdateRequest(BaseModel):
    gemini_api_key: str | None = None
    chatgpt_api_key: str | None = None
    claude_api_key: str | None = None
