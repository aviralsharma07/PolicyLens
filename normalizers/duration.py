from __future__ import annotations

import re
from typing import Dict, List, Optional

from normalizers.indian_number_words import NUMBER_WORD_PATTERN, parse_number, to_int_if_whole


NUMBER_TOKEN = rf"\d+(?:\.\d+)?|(?:{NUMBER_WORD_PATTERN})(?:[\s-]+(?:{NUMBER_WORD_PATTERN}))*"

DURATION_RE = re.compile(
    rf"\b(?P<num>{NUMBER_TOKEN})(?:\s*-\s*|\s+)"
    r"(?:(?:calendar|consecutive|continuous|completed|fixed)\s+)?"
    r"(?P<unit>day|days|month|months|year|years|yr|yrs)\b",
    re.IGNORECASE,
)


def parse_number_token(value: str) -> Optional[int]:
    parsed = parse_number(value)
    if parsed is None:
        return None
    return int(parsed)


def parse_number_phrase(first: str, second: Optional[str] = None) -> Optional[int]:
    phrase = f"{first} {second}" if second else first
    parsed = parse_number(phrase)
    if parsed is None:
        return None
    return int(parsed)


def normalize_duration(value: int, unit: str) -> Dict[str, int]:
    unit_lower = unit.lower()
    if unit_lower.startswith("day"):
        return {"days": value}
    if unit_lower.startswith("month"):
        return {"months": value}
    if unit_lower.startswith("year") or unit_lower in {"yr", "yrs"}:
        return {"months": value * 12}
    raise ValueError(f"Unsupported duration unit: {unit}")


def find_durations(text: str) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for match in DURATION_RE.finditer(text):
        parsed = parse_number(match.group("num"))
        if parsed is None:
            continue
        value = int(to_int_if_whole(parsed))
        if value is None:
            continue
        unit = match.group("unit")
        results.append(
            {
                "value": value,
                "unit": unit.lower(),
                "normalized": normalize_duration(value, unit),
                "span": match.span(),
                "text": match.group(0),
            }
        )
    return results
