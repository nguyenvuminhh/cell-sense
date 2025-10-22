import re


def extract_sheet_name_and_range(sheet_name_and_range: str):
    """
    Split a string like "Sheet1!A1:B5" or "'My Sheet'!C2:D10"
    into (sheet_name, range_a1).
    """
    # Remove extra whitespace
    stripped = sheet_name_and_range.strip()

    # Regex handles quoted sheet names like 'My Sheet'!A1:B5
    match = re.match(r"^'?([^'!]+)'?!?(.*)$", stripped)
    if not match:
        raise ValueError(f"Invalid sheet reference format: {sheet_name_and_range}")

    sheet_name = match.group(1).strip()
    range_a1 = match.group(2).strip()

    return sheet_name, range_a1
