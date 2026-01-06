from anthropic import Anthropic
from google import genai
from openai import OpenAI


def get_google_gemini_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def get_openai_chatgpt_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)


def get_anthropic_claude_client(api_key: str) -> Anthropic:
    return Anthropic(api_key=api_key)
