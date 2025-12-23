import re
from typing import List


def extract_target_cell(message: str) -> List[str]:
    pattern = r"<target>(.*?)</target>"
    matches = re.findall(pattern, message, flags=re.DOTALL)
    stripped_matches = [m.strip() for m in matches]
    return stripped_matches
