import html
from typing import Any, List

from pydantic import BaseModel, computed_field

from utils.extract_sheet_name_and_range import extract_sheet_name_and_range


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
    target_range: Range

    @computed_field
    @property
    def decoded_message(self) -> str:
        return html.unescape(self.message)

# ----- Response Models -----
class FilledRange(BaseModel):
    sheet_name: str
    range: str
    r1c1_value: str

class MessageResponse(BaseModel):
    message: str
    filled_range: FilledRange
