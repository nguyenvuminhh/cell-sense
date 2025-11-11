from pydantic import BaseModel

from server.models import BaseSchemaInPydantic


class UserRequest(BaseModel):
    email: str
    gemini_api_key: str | None = None


class User(BaseSchemaInPydantic, UserRequest):
    pass
