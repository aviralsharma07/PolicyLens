from __future__ import annotations

import re
from typing import Dict


NOT_COVERED_RE = re.compile(
    r"\b(not\s+covered|not\s+admissible|excluded|not\s+payable|no\s+coverage)\b",
    re.IGNORECASE,
)
CONDITIONAL_RE = re.compile(
    r"\b(covered\s+after|payable\s+after|subject\s+to|covered\s+subject\s+to|after\s+waiting\s+period)\b",
    re.IGNORECASE,
)
COVERED_ACTUALS_RE = re.compile(r"\b(up\s+to\s+actuals|actuals|as\s+charged)\b", re.IGNORECASE)
COVERED_RE = re.compile(r"\b(covered|payable|admissible|indemnify|reimburse)\b", re.IGNORECASE)


def normalize_coverage_status(text: str) -> Dict[str, object]:
    if NOT_COVERED_RE.search(text):
        status = "not_covered"
    elif COVERED_ACTUALS_RE.search(text):
        status = "covered_with_actuals"
    elif CONDITIONAL_RE.search(text):
        status = "conditional"
    elif COVERED_RE.search(text):
        status = "covered"
    else:
        status = "unknown"
    return {
        "value": status,
        "normalized": {"coverage_status": status},
        "span": (0, len(text)),
        "text": text,
        "value_type": "coverage_status",
    }

