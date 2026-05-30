import re
from typing import Dict, List, Optional


NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fourty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

NUMBER_TOKEN = (
    r"\d+|"
    r"zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|"
    r"thirty|forty|fourty|fifty|sixty|seventy|eighty|ninety"
)

DURATION_RE = re.compile(
    rf"\b(?P<num>{NUMBER_TOKEN})(?:[\s-]+(?P<num2>{NUMBER_TOKEN}))?\s+"
    r"(?P<unit>day|days|month|months|year|years)\b",
    re.IGNORECASE,
)


def parse_number_token(value: str) -> Optional[int]:
    token = value.strip().lower()
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


def parse_number_phrase(first: str, second: Optional[str] = None) -> Optional[int]:
    first_value = parse_number_token(first)
    if first_value is None:
        return None
    if not second:
        return first_value
    second_value = parse_number_token(second)
    if second_value is None:
        return first_value
    if first_value >= 20 and first_value % 10 == 0 and 0 < second_value < 10:
        return first_value + second_value
    return first_value


def normalize_duration(value: int, unit: str) -> Dict[str, int]:
    unit_lower = unit.lower()
    if unit_lower.startswith("day"):
        return {"days": value}
    if unit_lower.startswith("month"):
        return {"months": value}
    if unit_lower.startswith("year"):
        return {"months": value * 12}
    raise ValueError(f"Unsupported duration unit: {unit}")


def find_durations(text: str) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for match in DURATION_RE.finditer(text):
        value = parse_number_phrase(match.group("num"), match.group("num2"))
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
