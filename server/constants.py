from enum import StrEnum

from server.prompts import get_all_prompt_template_names


class Environments(StrEnum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"
    TEST = "test"


class JinjaPromptTemplatesNames(StrEnum):
    LLM_REQUEST_PROMPT = "llm_request_prompt.md"
    LLM_TITLE_NAMING_PROMPT = "llm_title_naming_prompt.md"


class LLMProviders(StrEnum):
    GOOGLE = "google"


class LLMModels(StrEnum):
    GOOGLE_GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GOOGLE_GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite"
    GOOGLE_GEMINI_2_5_PRO = "gemini-2.5-pro"


LLMProvidersToModels = {
    LLMProviders.GOOGLE: [
        LLMModels.GOOGLE_GEMINI_2_5_FLASH,
        LLMModels.GOOGLE_GEMINI_2_5_FLASH_LITE,
        LLMModels.GOOGLE_GEMINI_2_5_PRO,
    ],
}


class GeminiHistoryRoles(StrEnum):
    USER = "user"
    MODEL = "model"


DEFAULT_CHAT_NAME = "New Chat"

actual_names = get_all_prompt_template_names()
for name in JinjaPromptTemplatesNames.__members__.values():
    assert (
        name.value in actual_names
    ), f"Template '{name.value}' not found in {actual_names}."
