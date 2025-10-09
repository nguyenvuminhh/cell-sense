from fastapi import FastAPI

from app.chat_module.router import chat_router

app = FastAPI()

@app.get("/ping")
def ping():
    return "pong"

@app.get("/")
def get_root():
    return "Hi"

app.include_router(chat_router, prefix="/chat")