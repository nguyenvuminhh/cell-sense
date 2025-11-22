from fastapi import Request
from fastapi.responses import JSONResponse

from server.models.exception_models import (
    BadRequestError,
    InternalServerError,
    InternalServerErrorPublic,
    NotFoundError,
)
from server.utils import get_logger

logger = get_logger()


async def handle_http_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except (NotFoundError, BadRequestError, InternalServerErrorPublic) as e:
        # Re-raise known HTTP errors so FastAPI handles them
        logger.error("An unexpected error occurred.")

        return e()
    except InternalServerError as e:
        # Log internal server errors
        logger.error(
            f"An internal server error occurred: {e.detail}", exc_info=True
        )
        e.detail = "Something went wrong!"
        return e()

    except Exception:
        # Log and handle unexpected errors
        logger.error("An unexpected error occurred.", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Something went wrong!"},
        )
