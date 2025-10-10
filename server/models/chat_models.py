from typing import Any, List, Optional

from pydantic import BaseModel, Field

class SelectedRange(BaseModel):
    range: str
    values: List[List[Any]] = Field(default_factory=list)


class DummyMessageRequest(BaseModel):
    message: str
    sheet: List[List[Any]] = Field(default_factory=list)
    sheet_name: Optional[str] = None
    selected_ranges: List[SelectedRange] = Field(default_factory=list)

class DummyMessageResponse(BaseModel):
    reply: str
