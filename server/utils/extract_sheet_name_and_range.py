import re

from server.models.exception_models import BadRequestError


def extract_sheet_name_and_range(sheet_name_and_range: str):
    from server.utils import validate_a1_range_notation

    """
    Split a string like "Sheet1!A1:B5" or "'My Sheet'!C2:D10"
    into (sheet_name, range_a1).
    """

    # Remove extra whitespace
    stripped = sheet_name_and_range.strip()
    if not validate_a1_range_notation(stripped):
        raise BadRequestError(
            f"Invalid A1 range notation: {sheet_name_and_range}"
        )

    # Regex handles quoted sheet names like 'My Sheet'!A1:B5
    match = re.match(r"^'?([^'!]+)'?! ?(.*)$", stripped)
    if not match:
        raise BadRequestError(
            f"Invalid sheet reference format: {sheet_name_and_range}"
        )

    sheet_name = match.group(1).strip()
    range_a1 = match.group(2).strip()

    return sheet_name, range_a1
