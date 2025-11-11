from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from server.middleware import extract_user_from_request
from server.models.chat_models import MessageRequest
from server.models.user_models import User
from server.services import chat_service

chat_router = APIRouter()


@chat_router.post("")
def handle_message(
    request: MessageRequest,
    user: Annotated[User, Depends(extract_user_from_request)],
):
    return chat_service.handle_message(request, user)
