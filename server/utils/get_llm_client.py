from google import genai

from server.config import GEMINI_API_KEY
from server.constants import LLMModels, LLMProviders, LLMProvidersToModels
from server.middleware import InternalServerError


def get_llm_client(
    llm_provider: LLMProviders, llm_model: LLMModels
) -> genai.Client:
    if llm_model not in LLMProvidersToModels[llm_provider]:
        raise InternalServerError(
            f"Model {llm_model} is not supported by provider {llm_provider}."
        )

    if llm_provider == LLMProviders.GOOGLE:
        api_key = GEMINI_API_KEY
        if not api_key:
            raise InternalServerError(
                "GEMINI_API_KEY is not set in the environment variables."
            )
        return genai.Client(api_key=api_key)
    else:
        raise InternalServerError(
            f"LLM provider {llm_provider} is not supported."
        )
