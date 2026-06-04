from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from extractors.evidence import clean_space
from normalizers.duration import find_durations


def clean_lower(text: str) -> str:
    return clean_space(text).lower()


def has_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def evidence_window(text: str, start: int, end: int, radius: int = 220) -> str:
    cleaned = clean_space(text)
    left = max(0, start - radius)
    right = min(len(cleaned), end + radius)
    return cleaned[left:right].strip(" ,;:")


def near_terms(text: str, start: int, end: int, terms: Iterable[str], radius: int = 220) -> bool:
    window = evidence_window(text, start, end, radius)
    window_lower = window.lower()
    return any(term.lower() in window_lower for term in terms)


def reject_if_context(
    text: str,
    start: int,
    end: int,
    reject_terms: Iterable[str],
    radius: int = 220,
) -> Optional[str]:
    window = evidence_window(text, start, end, radius)
    window_lower = window.lower()
    for term in reject_terms:
        if term.lower() in window_lower:
            return f"context_contains_{term.lower().replace(' ', '_')}"
    return None


def find_duration_near_terms(
    text: str,
    terms: Iterable[str],
    allowed_units: Optional[set[str]] = None,
    radius: int = 260,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    cleaned = clean_space(text)
    for duration in find_durations(cleaned):
        unit = duration.get("unit", "")
        if allowed_units and unit not in allowed_units:
            continue
        dur_start, dur_end = duration["span"]
        if near_terms(cleaned, dur_start, dur_end, terms, radius):
            results.append(duration)
    return results


def schedule_dependent_value(reason: str) -> Dict[str, Any]:
    return {"schedule_dependent": True, "basis": reason}


def coverage_value(status: str = "covered", **extra: Any) -> Dict[str, Any]:
    if status == "covered":
        return {"coverage_status": "covered", **extra}
    elif status == "conditional":
        return {"coverage_status": "conditional", **extra}
    else:
        raise ValueError(f"Unsupported coverage status: {status}")
