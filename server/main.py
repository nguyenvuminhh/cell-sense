from fastapi import FastAPI

from server import routers
from server.middleware.handle_http_exceptions import handle_http_exceptions
from server.middleware.log_request_body import log_request_body
from server.middleware.remove_training_slash import remove_trailing_slash

app = FastAPI(redirect_slashes=False)

app.middleware("http")(handle_http_exceptions)
app.middleware("http")(remove_trailing_slash)
app.middleware("http")(log_request_body)


@app.get("/ping")
def ping():
    return "pong"


@app.get("/")
def get_root():
    return "Hi"


app.include_router(routers.chat_router, prefix="/chat")
app.include_router(routers.error_router, prefix="/error")
