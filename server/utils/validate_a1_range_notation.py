import re


def validate_a1_range_notation(value: str) -> bool:
    """
    Validate if the given string is in valid A1 range notation.

    Valid examples:
        "A1"
        "B2:C3"
        "Sheet1!A1"
        "Sheet1!A1:B5"
        "'My Sheet'!A1"
        "'Data 2025'!A1:B10"

    Invalid examples:
        "A0"
        "1A"
        "Sheet1!A"
        "A1:B"
        "Sheet!A1:B"
        "Sheet!A1:B C3"
    """
    if not value or not isinstance(value, str):
        return False

    # Reject immediately if spaces exist outside quoted sheet names
    if " " in value and not re.match(r"^'[^']+'!.*$", value):
        return False

    # Regex for A1 range notation
    pattern = re.compile(
        r"^(?:'[^']+'|[^'!]+)?!?"  # optional sheet name (quoted or unquoted)
        r"([A-Z]+[1-9][0-9]*"  # first cell ref (e.g. A1)
        r"(?::[A-Z]+[1-9][0-9]*)?)$",  # optional second cell ref
        re.IGNORECASE,
    )

    return bool(pattern.match(value))
