from fastapi import Request, Response

from server.config import ENV
from server.constants import Environments
from server.utils import get_logger

logger = get_logger()


async def log_request_body(request: Request, call_next) -> Response:
    if ENV == Environments.DEVELOPMENT:
        body = await request.body()
        logger.info(f"Request Body: {body.decode('utf-8')}")
    response = await call_next(request)
    return response
