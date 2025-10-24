from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from server.utils.get_logger import get_logger

logger = get_logger()

class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        self.log_detail = detail  # Store the original detail for logging
        logger.error(f"❌ Detail: {self.log_detail}")

class NotFoundError(CustomHTTPException):
    def __init__(self, detail: str = "Resource not found."):
        super().__init__(status_code=404, detail=detail)

class BadRequestError(CustomHTTPException):
    def __init__(self, detail: str = "Bad request."):
        super().__init__(status_code=400, detail=detail)

class InternalServerError(CustomHTTPException):
    def __init__(self, detail: str = "Something went wrong."):
        super().__init__(status_code=500, detail="Something went wrong.")
        self.log_detail = detail  # Store the original detail for logging

CustomError = (NotFoundError, BadRequestError, InternalServerError)

async def handle_http_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except CustomError as e:
        # Re-raise known HTTP errors so FastAPI handles them
        raise e
    except HTTPException as e:
        # Re-raise existing FastAPI exceptions
        raise e
    except Exception:
        # Log and handle unexpected errors
        return JSONResponse(
            status_code=500,
            content={"detail": "Something went wrong."},
        )
