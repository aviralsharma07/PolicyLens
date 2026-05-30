from __future__ import annotations

import re
from typing import Dict, List

from normalizers.indian_number_words import NUMBER_WORD_PATTERN, parse_number, to_int_if_whole


AGE_TOKEN = rf"\d+(?:\.\d+)?|(?:{NUMBER_WORD_PATTERN})(?:[\s-]+(?:{NUMBER_WORD_PATTERN}))*"
AGE_RE = re.compile(
    rf"(?P<prefix>\baged?\s+|\bage\s+|\bbeyond\s+|\babove\s+|\bover\s+|\bat\s+least\s+)?"
    rf"(?P<age>{AGE_TOKEN})\s*(?P<unit>years?|yrs?)"
    rf"(?P<suffix>\s+or\s+above|\s+and\s+above|\s+or\s+more)?",
    re.IGNORECASE,
)


def _comparator(prefix: str | None, suffix: str | None) -> str:
    prefix_lower = (prefix or "").strip().lower()
    suffix_lower = (suffix or "").strip().lower()
    if prefix_lower in {"beyond", "above", "over"}:
        return "gt"
    if prefix_lower == "at least" or suffix_lower in {"or above", "and above", "or more"}:
        return "gte"
    return "eq"


def find_ages(text: str) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for match in AGE_RE.finditer(text):
        parsed = parse_number(match.group("age"))
        if parsed is None:
            continue
        age = to_int_if_whole(parsed)
        comparator = _comparator(match.group("prefix"), match.group("suffix"))
        results.append(
            {
                "value": age,
                "normalized": {"age_years": age, "comparator": comparator},
                "span": match.span(),
                "text": match.group(0),
                "unit": "years",
                "comparator": comparator,
                "value_type": "age",
            }
        )
    return results

