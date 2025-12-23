from fastapi import APIRouter, HTTPException

from server.middleware import (
    BadRequestError,
    InternalServerError,
    NotFoundError,
)

error_router = APIRouter()


@error_router.get("/500")
def get_error_500():
    raise InternalServerError("You should not see this message.")


@error_router.get("/404")
def get_error_404():
    raise NotFoundError("This is a custom not found message.")


@error_router.get("/400")
def get_error_400():
    raise BadRequestError("This is a custom bad request message.")


@error_router.get("/http_exception")
def get_error_http_exception():
    raise HTTPException(
        status_code=418, detail="This is a custom HTTP exception."
    )


@error_router.get("/unexpected_exception")
def get_unexpected_exception():
    raise ValueError("This is an unexpected exception.")
