from fastapi.responses import JSONResponse


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
