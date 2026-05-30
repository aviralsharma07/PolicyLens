import re
from typing import Dict, Iterable, Optional


def clean_space(text: str) -> str:
    ligature_fixed = (
        (text or "")
        .replace("ﬁ", "fi")
        .replace("ﬂ", "fl")
        .replace("ﬀ", "ff")
        .replace("ﬃ", "ffi")
        .replace("ﬄ", "ffl")
    )
    return re.sub(r"\s+", " ", ligature_fixed).strip()


def contains_evidence(clause_text: str, evidence_text: str) -> bool:
    if not evidence_text:
        return False
    return clean_space(evidence_text) in clean_space(clause_text)


def evidence_window(text: str, keywords: Iterable[str], *, radius: int = 180) -> Optional[str]:
    compact = clean_space(text)
    if not compact:
        return None
    lower = compact.lower()
    positions = [lower.find(k.lower()) for k in keywords if k and lower.find(k.lower()) >= 0]
    if not positions:
        return compact[: min(len(compact), radius * 2)]
    center = min(positions)
    start = max(0, center - radius)
    end = min(len(compact), center + radius)
    return compact[start:end].strip()


def clause_source(clause: Dict[str, object]) -> str:
    return f"clause:{clause.get('clause_id')}"
