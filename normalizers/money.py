from __future__ import annotations

import re
from decimal import Decimal
from typing import Dict, List

from normalizers.indian_number_words import (
    MAGNITUDE_PATTERN,
    NUMBER_WORD_PATTERN,
    apply_indian_multiplier,
    parse_number,
    to_int_if_whole,
)


AMOUNT_TOKEN = rf"\d[\d,]*(?:\.\d+)?|(?:{NUMBER_WORD_PATTERN})(?:[\s-]+(?:{NUMBER_WORD_PATTERN}))*"
MONEY_RE = re.compile(
    rf"(?P<currency>₹|rs\.?|inr)?\s*(?P<amount>{AMOUNT_TOKEN})\s*(?P<magnitude>{MAGNITUDE_PATTERN})?",
    re.IGNORECASE,
)
SPECIAL_RE = re.compile(r"\b(?P<special>actuals|as\s+charged|subject\s+to\s+limit)\b", re.IGNORECASE)


def normalize_money_amount(amount: Decimal, magnitude: str | None = None) -> Dict[str, object]:
    normalized_amount = apply_indian_multiplier(amount, magnitude)
    return {"amount": to_int_if_whole(normalized_amount), "currency": "INR"}


def find_money_values(text: str) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for match in MONEY_RE.finditer(text):
        has_currency = bool(match.group("currency"))
        has_magnitude = bool(match.group("magnitude"))
        if not has_currency and not has_magnitude:
            continue
        parsed = parse_number(match.group("amount"))
        if parsed is None:
            continue
        normalized = normalize_money_amount(parsed, match.group("magnitude"))
        results.append(
            {
                "value": normalized["amount"],
                "normalized": normalized,
                "span": match.span(),
                "text": match.group(0).strip(),
                "currency": "INR",
                "magnitude": match.group("magnitude").lower() if match.group("magnitude") else None,
                "value_type": "money",
            }
        )

    for match in SPECIAL_RE.finditer(text):
        special = "_".join(match.group("special").lower().split())
        results.append(
            {
                "value": special,
                "normalized": {"special_value": special, "currency": "INR"},
                "span": match.span(),
                "text": match.group(0),
                "currency": "INR",
                "magnitude": None,
                "value_type": "special_money_value",
            }
        )
    return sorted(results, key=lambda result: result["span"])

