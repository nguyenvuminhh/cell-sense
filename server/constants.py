from enum import StrEnum

from server.prompts import get_all_prompt_template_names


class JinjaPromptTemplatesNames(StrEnum):
    LLM_REQUEST_PROMPT = "llm_request_prompt.md"

actual_names = get_all_prompt_template_names()
for name in JinjaPromptTemplatesNames.__members__.values():
    assert name.value in actual_names, f"Template '{name.value}' not found in {actual_names}."
