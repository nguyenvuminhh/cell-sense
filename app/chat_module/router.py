from fastapi import APIRouter

from app.chat_module.models import DummyMessageRequest, DummyMessageResponse

chat_router = APIRouter()

@chat_router.post("/")
def dummy_message(
    request: DummyMessageRequest
):
    return DummyMessageResponse(message=request.message)