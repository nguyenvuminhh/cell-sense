from fastapi import Request
from fastapi.responses import JSONResponse

from server.utils import get_logger

logger = get_logger()


class CustomHTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

    def __call__(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code, content={"detail": self.detail}
        )


class NotFoundError(CustomHTTPException):
    def __init__(self, detail: str = "Resource not found."):
        self.status_code = 404
        self.detail = detail


class BadRequestError(CustomHTTPException):
    def __init__(self, detail: str = "Bad request."):
        self.status_code = 400
        self.detail = detail


class InternalServerError(CustomHTTPException):
    def __init__(self, detail: str = "Something went wrong."):
        self.status_code = 500
        self.detail = detail


async def handle_http_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except (NotFoundError, BadRequestError) as e:
        # Re-raise known HTTP errors so FastAPI handles them
        logger.error("An unexpected error occurred.", exc_info=True)

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
