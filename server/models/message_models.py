import html
from typing import Any, List

from pydantic import BaseModel, computed_field

from server.constants import (
    ChatGPTHistoryRoles,
    GeminiHistoryRoles,
    LLMModels,
    LLMProviders,
)
from server.utils import extract_sheet_name_and_range, extract_target_cell


# ----- Request Models -----
class Range(BaseModel):
    sheet_name_and_range: str

    @computed_field
    @property
    def sheet_name(self) -> str:
        sheet_name, _ = extract_sheet_name_and_range(self.sheet_name_and_range)
        return sheet_name

    @computed_field
    @property
    def range(self) -> str:
        _, range = extract_sheet_name_and_range(self.sheet_name_and_range)
        return range


class SelectedRange(Range):
    cell_values: List[List[Any]]


class MessageRequest(BaseModel):
    message: str
    # sheet: List[List[Any]]
    selected_ranges: List[SelectedRange]

    llm_provider: LLMProviders = LLMProviders.GOOGLE
    llm_model: LLMModels = LLMModels.GOOGLE_GEMINI_2_5_FLASH_LITE

    @computed_field
    @property
    def decoded_message(self) -> str:
        return html.unescape(self.message)

    @computed_field
    @property
    def target_ranges(self) -> List[Range]:
        string_repr = extract_target_cell(self.decoded_message)
        return [Range(sheet_name_and_range=m) for m in string_repr]


# ----- Response Models -----
class FilledRange(BaseModel):
    sheet_name: str
    range: str
    r1c1_value: str


class MessageResponse(BaseModel):
    message: str
    filled_ranges: list[FilledRange]


class UserPromptAndModelResponse(BaseModel):
    full_user_prompt: str
    full_model_response: str


# ----- Title Naming Models -----
class TitleNamingResponse(BaseModel):
    title: str
    message_is_unclear: bool


# ----- Gemini History Models -----
class GeminiHistoryPart(BaseModel):
    text: str


class GeminiHistoryEntry(BaseModel):
    role: GeminiHistoryRoles
    parts: list[GeminiHistoryPart]


# ----- ChatGPT History Models -----
class ChatGPTHistoryEntry(BaseModel):
    role: ChatGPTHistoryRoles
    content: str
