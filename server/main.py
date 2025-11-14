from fastapi import FastAPI

from server.middleware import (
    handle_http_exceptions,
    log_request_body,
    remove_trailing_slash,
    verify_signature_from_apps_script,
)
from server.routers import chat_router, error_router

app = FastAPI(redirect_slashes=False)

app.middleware("http")(verify_signature_from_apps_script)
app.middleware("http")(handle_http_exceptions)
app.middleware("http")(remove_trailing_slash)
app.middleware("http")(log_request_body)


@app.get("/ping")
def ping():
    return "pong"


@app.get("/")
def get_root():
    return "Hi"


app.include_router(chat_router, prefix="/chat")
app.include_router(error_router, prefix="/error")
