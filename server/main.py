from fastapi import FastAPI

from server.middleware.handle_http_exceptions import (
    BadRequestError,
    InternalServerError,
    NotFoundError,
    handle_http_exceptions,
)
from server.middleware.remove_training_slash import remove_trailing_slash
from server.routers.chat_router import chat_router

app = FastAPI(redirect_slashes=False)

app.middleware("http")(remove_trailing_slash)
app.middleware("http")(handle_http_exceptions)


@app.get("/ping")
def ping():
    return "pong"

@app.get("/")
def get_root():
    return "Hi"

@app.get("/error/500")
def get_error_500():
    raise InternalServerError("You should not see this message.")

@app.get("/error/404")
def get_error_404():
    raise NotFoundError("This is a custom not found message.")

@app.get("/error/400")
def get_error_400():
    raise BadRequestError("This is a custom bad request message.")

app.include_router(chat_router, prefix="/chat")
