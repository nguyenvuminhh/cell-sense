from pydantic import BaseModel

class DummyMessageRequest(BaseModel):
    message: str

class DummyMessageResponse(BaseModel):
    message: str