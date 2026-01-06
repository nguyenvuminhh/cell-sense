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
    OPENAI = "openai"


class LLMModels(StrEnum):
    GOOGLE_GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GOOGLE_GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite"
    GOOGLE_GEMINI_2_5_PRO = "gemini-2.5-pro"

    OPENAI_GPT_5 = "gpt-5"
    OPENAI_GPT_5_PRO = "gpt-5-pro"
    OPENAI_GPT_5_MINI = "gpt-5-mini"
    OPENAI_GPT_5_NANO = "gpt-5-nano"


LLMProvidersToModels = {
    LLMProviders.GOOGLE: [
        LLMModels.GOOGLE_GEMINI_2_5_FLASH,
        LLMModels.GOOGLE_GEMINI_2_5_FLASH_LITE,
        LLMModels.GOOGLE_GEMINI_2_5_PRO,
    ],
    LLMProviders.OPENAI: [
        LLMModels.OPENAI_GPT_5,
        LLMModels.OPENAI_GPT_5_PRO,
        LLMModels.OPENAI_GPT_5_MINI,
        LLMModels.OPENAI_GPT_5_NANO,
    ],
}


class GeminiHistoryRoles(StrEnum):
    USER = "user"
    MODEL = "model"


class ChatGPTHistoryRoles(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    DEVELOPER = "developer"


DEFAULT_CHAT_NAME = "New Chat"

actual_names = get_all_prompt_template_names()
for name in JinjaPromptTemplatesNames.__members__.values():
    assert (
        name.value in actual_names
    ), f"Template '{name.value}' not found in {actual_names}."
