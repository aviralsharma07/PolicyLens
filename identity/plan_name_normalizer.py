import logging
import re
from difflib import SequenceMatcher
from typing import List, Optional

logger = logging.getLogger(__name__)

COMMON_SUFFIXES = [
    r"_IRDAI\b",
    r"_IRDDA\b",
    r"_website\b",
    r"_policy_wording\b",
    r"_kis\b",
    r"_Policy\b",
    r"_Policy_Document\b",
    r"_Policy_Terms\b",
    r"_Policy_Terms_and_Conditions\b",
    r"_Policy_Terms_\&\s*Conditions\b",
    r"_Prospectus\b",
    r"_Brochure\b",
    r"_Sales_Literature\b",
    r"_Prospectus_cum_Sales_Literature\b",
    r"_Terms_and_Conditions\b",
    r"_T\&\s*C\b",
    r"_Product\b",
    r"_Document\b",
    r"_Policy_Wording\b",
    r"_\d{4}\b",
    r"\.pdf$",
]

INSUFFICIENT_NAMES = {
    "health insurance policy document",
    "health insurance policy",
    "insurance policy document",
    "policy document",
    "insurance policy",
    "policy wording",
    "policy",
    "prospectus",
    "brochure",
}


def extract_plan_name(filename: str, insurer_prefixes: Optional[List[str]] = None) -> str:
    name = filename.strip()
    for suffix in COMMON_SUFFIXES:
        name = re.sub(suffix, "", name, flags=re.IGNORECASE)
    if insurer_prefixes:
        for prefix in sorted(insurer_prefixes, key=len, reverse=True):
            pattern = re.compile(r"^" + re.escape(prefix) + r"[_\s]", re.IGNORECASE)
            if pattern.match(name):
                name = pattern.sub("", name, count=1)
                break
    name = name.strip()
    name = re.sub(r"__+", "_", name)
    name = name.strip("_ \t-")
    return name


def normalize(name: str) -> str:
    cleaned = name.lower()
    cleaned = re.sub(r"[_-]", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9\s]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def is_sufficient(name: str) -> bool:
    normalized = normalize(name)
    if not normalized or len(normalized) < 5:
        return False
    if normalized in INSUFFICIENT_NAMES:
        return False
    return True


def fuzzy_score(name1: str, name2: str) -> float:
    if not name1 or not name2:
        return 0.0
    n1 = normalize(name1)
    n2 = normalize(name2)
    return SequenceMatcher(None, n1, n2).ratio()


def best_match_score(extracted: str, candidates: List[str]) -> float:
    if not is_sufficient(extracted):
        return 0.0
    scores = [fuzzy_score(extracted, c) for c in candidates]
    return max(scores) if scores else 0.0
