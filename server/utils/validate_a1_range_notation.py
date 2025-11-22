import re


def validate_a1_range_notation(value: str) -> bool:
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
