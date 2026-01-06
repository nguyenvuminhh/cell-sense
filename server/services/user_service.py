from sqlalchemy.ext.asyncio import AsyncSession

from server.crud import users_crud
from server.models.exception_models import BadRequestError
from server.models.user_models import ApiKeyUpdateRequest, User


async def update_api_key(
    session: AsyncSession,
    request: ApiKeyUpdateRequest,
    user: User,
) -> User:
    updated_user_model = user
    if request.gemini_api_key is not None:
        updated_user_model.gemini_api_key = request.gemini_api_key
    if request.chatgpt_api_key is not None:
        updated_user_model.chatgpt_api_key = request.chatgpt_api_key
    if request.claude_api_key is not None:
        updated_user_model.claude_api_key = request.claude_api_key

    result = await users_crud.update_user(session, user.id, updated_user_model)
    if not result:
        raise BadRequestError("Failed to update API key.")
    return result
