from fastapi import APIRouter

from server.models.chat_models import MessageRequest
from server.services import chat_service

chat_router = APIRouter()

@chat_router.post("/")
def handle_message(
    request: MessageRequest
):
    return chat_service.handle_message(request)
