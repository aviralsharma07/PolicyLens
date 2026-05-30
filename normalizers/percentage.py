from __future__ import annotations

import re
from typing import Dict, List


PERCENTAGE_RE = re.compile(
    r"(?<!\w)(?P<value>\d+(?:\.\d+)?)\s*(?:%|percent\b|per\s+cent\b)",
    re.IGNORECASE,
)


def normalize_percentage(value: float) -> Dict[str, float | int]:
    if value.is_integer():
        return {"percentage": int(value)}
    return {"percentage": value}


def find_percentages(text: str) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for match in PERCENTAGE_RE.finditer(text):
        value = float(match.group("value"))
        results.append(
            {
                "value": int(value) if value.is_integer() else value,
                "normalized": normalize_percentage(value),
                "span": match.span(),
                "text": match.group(0),
            }
        )
    return results
