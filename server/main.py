from fastapi import FastAPI

from server.constants import LLMModels, LLMProviders
from server.middleware import (
    handle_http_exceptions,
    log_request_body,
    remove_trailing_slash,
    verify_signature_from_apps_script,
    verify_timestamps,
)
from server.routers import chat_router, error_router, user_router

app = FastAPI(redirect_slashes=False)

# ------------------------- Middleware -------------------------
app.middleware("http")(verify_timestamps)
app.middleware("http")(verify_signature_from_apps_script)
app.middleware("http")(handle_http_exceptions)
app.middleware("http")(remove_trailing_slash)
app.middleware("http")(log_request_body)


# ------------------------- Health Check -------------------------
@app.get("/ping")
def ping():
    return "pong"


@app.get("/")
def get_root():
    return "Hi"


@app.get(
    "/supported-models", response_model=list[tuple[LLMProviders, LLMModels]]
)
def get_supported_models() -> list[tuple[LLMProviders, LLMModels]]:

    gemini_models = [
        LLMModels.GOOGLE_GEMINI_2_5_FLASH,
        LLMModels.GOOGLE_GEMINI_2_5_FLASH_LITE,
        LLMModels.GOOGLE_GEMINI_2_5_PRO,
    ]
    result = [(LLMProviders.GOOGLE, model) for model in gemini_models]
    return result


# ------------------------- Routers -------------------------
app.include_router(chat_router, prefix="/chat")
app.include_router(error_router, prefix="/error")
app.include_router(user_router, prefix="/user")
