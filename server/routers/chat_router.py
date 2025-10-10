from fastapi import APIRouter

from server.models.chat_models import DummyMessageRequest, DummyMessageResponse

chat_router = APIRouter()

@chat_router.post("/")
def dummy_message(
    request: DummyMessageRequest
):
    row_count = len(request.sheet)
    column_count = len(request.sheet[0]) if row_count else 0
    selection_summary = ""
    if request.selected_ranges:
        selection_summary = (
            f" First selection: {request.selected_ranges[0].range} "
            f"({len(request.selected_ranges[0].values)} row(s))."
        )

    reply = (
        f"Received sheet '{request.sheet_name or 'Untitled'}' "
        f"with {row_count} row(s) and {column_count} column(s). "
        f"Updated the sheet!{selection_summary}"
    )
    return DummyMessageResponse(reply=reply)
