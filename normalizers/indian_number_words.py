from __future__ import annotations

import re
from decimal import Decimal
from typing import Optional


ONES = {
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
}

TENS = {
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

MULTIPLIERS = {
    "hundred": 100,
    "thousand": 1000,
    "lakh": 100000,
    "lakhs": 100000,
    "lac": 100000,
    "lacs": 100000,
    "crore": 10000000,
    "crores": 10000000,
}

NUMBER_WORDS = {**ONES, **TENS}
NUMBER_WORD_PATTERN = "|".join(sorted(NUMBER_WORDS, key=len, reverse=True))
MAGNITUDE_PATTERN = "|".join(sorted(MULTIPLIERS, key=len, reverse=True))


def clean_numeric_token(value: str) -> str:
    return value.replace(",", "").strip()


def parse_numeric_token(value: str) -> Optional[Decimal]:
    cleaned = clean_numeric_token(value)
    if not re.fullmatch(r"\d+(?:\.\d+)?", cleaned):
        return None
    return Decimal(cleaned)


def parse_number_word_phrase(value: str) -> Optional[int]:
    tokens = [token for token in re.split(r"[\s-]+", value.lower().strip()) if token and token != "and"]
    if not tokens:
        return None

    total = 0
    current = 0
    found = False
    for token in tokens:
        if token in ONES:
            current += ONES[token]
            found = True
        elif token in TENS:
            current += TENS[token]
            found = True
        elif token == "hundred":
            current = max(current, 1) * 100
            found = True
        elif token in {"thousand", "lakh", "lakhs", "lac", "lacs", "crore", "crores"}:
            total += max(current, 1) * MULTIPLIERS[token]
            current = 0
            found = True
        else:
            return None
    if not found:
        return None
    return total + current


def parse_number(value: str) -> Optional[Decimal]:
    numeric = parse_numeric_token(value)
    if numeric is not None:
        return numeric
    word_value = parse_number_word_phrase(value)
    if word_value is None:
        return None
    return Decimal(word_value)


def apply_indian_multiplier(value: Decimal, magnitude: Optional[str]) -> Decimal:
    if not magnitude:
        return value
    multiplier = MULTIPLIERS[magnitude.lower()]
    return value * Decimal(multiplier)


def to_int_if_whole(value: Decimal) -> int | float:
    if value == value.to_integral_value():
        return int(value)
    return float(value)

