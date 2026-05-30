from __future__ import annotations

import re
from typing import Dict, List

from normalizers.indian_number_words import NUMBER_WORD_PATTERN, parse_number, to_int_if_whole

PERCENTAGE_RE = re.compile(
    rf"(?<!\w)(?P<value>\d+(?:\.\d+)?|(?:{NUMBER_WORD_PATTERN})(?:[\s-]+(?:{NUMBER_WORD_PATTERN}))*)\s*"
    r"(?:%|percent\b|per\s+cent\b)",
    re.IGNORECASE,
)


def normalize_percentage(value: float) -> Dict[str, float | int]:
    if value.is_integer():
        return {"percentage": int(value)}
    return {"percentage": value}


def find_percentages(text: str) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for match in PERCENTAGE_RE.finditer(text):
        parsed = parse_number(match.group("value"))
        if parsed is None:
            continue
        value = float(parsed)
        results.append(
            {
                "value": to_int_if_whole(parsed),
                "normalized": normalize_percentage(value),
                "span": match.span(),
                "text": match.group(0),
            }
        )
    return results
