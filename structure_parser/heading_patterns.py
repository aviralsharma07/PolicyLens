import re
from typing import List, Set

NUMBERING_PATTERNS = [
    re.compile(r"^SECTION\s+[A-Z0-9]", re.IGNORECASE),
    re.compile(r"^PART\s+[A-Z0-9]", re.IGNORECASE),
    re.compile(r"^(?:I|II|III|IV|V|VI|VII|VIII|IX|X)[\.\)]\s"),
    re.compile(r"^\d+\s+\w+"),
    re.compile(r"^\d+\.[\d\.]*\s+\w+"),
    re.compile(r"^\d+[\.\)]\s+[A-Z]"),
    re.compile(r"^\d+\.[A-Z]"),
    re.compile(r"^\d+\.[a-z]"),
    re.compile(r"^\d+\.\d+[A-Z]"),
    re.compile(r"^\d+\.\d+\.\d+[A-Za-z]"),
    re.compile(r"^[A-Z]\.\s+(?!No\b|no\b)[^\t]"),
]

TOC_DOT_PATTERN = re.compile(r"\.\s*\.\s*\.\s*\.\s*\.")

LONG_TEXT_THRESHOLD = 120

HEADING_DICTIONARY: Set[str] = {
    "preamble",
    "definitions",
    "coverage",
    "exclusions",
    "waiting period",
    "conditions",
    "renewal",
    "claims",
    "premium",
    "deductible",
    "co-payment",
    "limitations",
    "general terms",
    "schedule",
    "benefits",
    "moratorium",
    "miscellaneous",
    "free look",
    "portability",
    "migration",
    "cumulative bonus",
    "hospitalization",
    "operative clause",
    "claim procedure",
    "period of cover",
    "policy period",
    "sum insured",
    "policy schedule",
    "specific waiting period",
    "pre-existing disease",
    "permanent total disablement",
    "insured event",
    "emergency care",
    "medical expenses",
    "hospital",
    "in-patient care",
    "day care treatment",
    "grace period",
    "network provider",
    "notification of claim",
    "reasonable and customary",
    "surgery",
    "subrogation",
    "indemnity",
    "nominee",
    "room rent",
    "comprehensive",
    "policy",
    "section",
    "part",
    "family shield",
    "accident",
    "age",
    "illness",
    "injury",
    "treatment",
    "charges",
    "expenses",
    "disablement",
    "disease",
    "care",
    "cover",
    "optional",
    "additional",
    "benefit",
}


def matches_numbering(text: str) -> bool:
    for pattern in NUMBERING_PATTERNS:
        if pattern.search(text):
            return True
    return False


def has_toc_dots(text: str) -> bool:
    return bool(TOC_DOT_PATTERN.search(text))


def _strip_leading_number(text: str) -> str:
    return re.sub(r"^[\d\.\s\)]+", "", text).strip()


def matches_heading_dict(text: str) -> bool:
    stripped = _strip_leading_number(text).lower()
    for term in HEADING_DICTIONARY:
        if stripped.startswith(term):
            return True
    return False


def is_bold_line(spans: list) -> bool:
    return any(s.get("is_bold") is True or getattr(s, "is_bold", None) is True for s in spans)


def is_all_caps(text: str) -> bool:
    clean = text.strip()
    if len(clean) < 3:
        return False
    alpha_chars = [c for c in clean if c.isalpha()]
    if len(alpha_chars) < 3:
        return False
    return all(c.isupper() for c in alpha_chars)


def is_sentence_case(text: str) -> bool:
    stripped = _strip_leading_number(text)
    if len(stripped) < 5:
        return False
    words = stripped.split()
    if len(words) < 2:
        return False
    first_word_upper = words[0][0].isupper() if words[0] and words[0][0].isalpha() else False
    rest_lower = any(w[0].islower() for w in words[1:] if w and w[0].isalpha())
    return first_word_upper and rest_lower


def normalize_heading_text(text: str) -> str:
    text = re.sub(r"\.\s*\.\s*\.+\s*\.*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()
