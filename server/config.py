import os

from dotenv import load_dotenv

from server.constants import Environments

ENV = os.getenv("ENV", "development")

# Load the right .env file
if ENV == Environments.TEST:
    load_dotenv(".env.test")
elif ENV == Environments.DEVELOPMENT:
    load_dotenv(".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")

DATABASE_URL = os.getenv("DATABASE_URL")

SIGNATURE_PUBLIC_KEY_PATH = os.getenv("SIGNATURE_PUBLIC_KEY_PATH")

MAX_TIMESTAMP_DIFF_SECONDS = 60  # 1 minute
SKIP_AUTH_PATHS = ["/ping", "/error/", "/docs", "/openapi.json", "/db"]
FREE_USER_DAILY_QUOTA = 10
CONTEXT_WINDOW_SIZE = 30  # Number of messages to consider for context in chat
