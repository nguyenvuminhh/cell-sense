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

DATABASE_DIALECT = os.getenv("DATABASE_DIALECT")
DATABASE_DRIVER = os.getenv("DATABASE_DRIVER")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"{DATABASE_DIALECT}+{DATABASE_DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{POSTGRES_DB}"

SIGNATURE_PUBLIC_KEY_PATH = "assets/public.pem"

MAX_TIMESTAMP_DIFF_SECONDS = 60  # 1 minute
SKIP_AUTH_PATHS = ["/ping", "/error/", "/docs", "/openapi.json"]
FREE_USER_DAILY_QUOTA = 10
