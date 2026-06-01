"""
Fact candidate composite scoring — DSE-011

Computes a weighted composite score for each fact candidate from:
  confidence (extractor-assigned)       — weight 0.50
  evidence quality                      — weight 0.30
  pattern specificity                   — weight 0.15
  source type priority                  — weight 0.05

ADR-0025: Composite scoring formula.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Weights
# ---------------------------------------------------------------------------

W_CONFIDENCE = 0.50
W_EVIDENCE = 0.30
W_PATTERN = 0.15
W_SOURCE = 0.05

# Minimum composite score for automatic acceptance
ACCEPT_THRESHOLD = 0.85

# ---------------------------------------------------------------------------
# Pattern specificity scores (known DSE-007 pattern_ids)
# ---------------------------------------------------------------------------

PATTERN_SPECIFICITY: Dict[str, float] = {
    # High specificity — pattern targets a single concrete value form
    "free_look_15_days": 1.0,
    "free_look_30_days": 1.0,
    "renewal_grace_days": 1.0,
    "ped_waiting_duration": 1.0,
    "ped_schedule_dependent": 0.8,
    "initial_wait_30_days": 1.0,
    "copay_percentage": 1.0,
    "star_age_based_copay": 1.0,
    "care_smart_select_copay_components": 1.0,
    "copay_schedule_dependent": 0.8,
    # Medium specificity — generic or non-primary
    "free_look_non_primary_duration": 0.5,
    "care_age_schedule_copay_component": 0.5,
    # Low specificity — definition-only or weak signal
    "copay_definition_only": 0.2,
    "ped_definition_only": 0.2,
}

_DEFAULT_PATTERN_SPECIFICITY = 0.5


# ---------------------------------------------------------------------------
# Evidence quality
# ---------------------------------------------------------------------------


def compute_evidence_quality(candidate: Dict[str, Any]) -> float:
    """
    1.0 — evidence_text non-empty AND evidence_clause_id non-null AND no rejection for evidence
    0.5 — evidence_text present but clause_id missing or rejection related to evidence
    0.0 — no evidence_text
    """
    evidence_text = candidate.get("evidence_text") or ""
    clause_id = candidate.get("evidence_clause_id") or ""
    rejection = candidate.get("rejection_reason") or ""

    if not evidence_text.strip():
        return 0.0

    if not clause_id:
        return 0.3

    if "evidence" in rejection.lower():
        return 0.5

    return 1.0


# ---------------------------------------------------------------------------
# Pattern specificity
# ---------------------------------------------------------------------------


def compute_pattern_specificity(pattern_id: Optional[str]) -> float:
    """Look up pattern specificity from the known map. Default 0.5 for unknown patterns."""
    if not pattern_id:
        return _DEFAULT_PATTERN_SPECIFICITY
    return PATTERN_SPECIFICITY.get(pattern_id, _DEFAULT_PATTERN_SPECIFICITY)


# ---------------------------------------------------------------------------
# Source type priority
# ---------------------------------------------------------------------------


def compute_source_priority(candidate: Dict[str, Any]) -> float:
    """
    1.0 — clause source (direct text extraction)
    0.7 — table cell source
    0.3 — inferred / other
    """
    source = candidate.get("source", "")
    if "clause" in source.lower():
        return 1.0
    if "table" in source.lower():
        return 0.7
    return 0.3


# ---------------------------------------------------------------------------
# Composite score
# ---------------------------------------------------------------------------


def compute_composite_score(candidate: Dict[str, Any]) -> float:
    """
    Weighted composite of confidence, evidence quality, pattern specificity, source priority.
    Returns float clamped to [0.0, 1.0].
    """
    confidence = float(candidate.get("confidence", 0.0))
    evidence_q = compute_evidence_quality(candidate)
    pattern_s = compute_pattern_specificity(candidate.get("pattern_id"))
    source_p = compute_source_priority(candidate)

    raw = (
        W_CONFIDENCE * confidence
        + W_EVIDENCE * evidence_q
        + W_PATTERN * pattern_s
        + W_SOURCE * source_p
    )
    return max(0.0, min(1.0, round(raw, 4)))


# ---------------------------------------------------------------------------
# Score and rank candidates
# ---------------------------------------------------------------------------


def score_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compute composite_score for each candidate. Returns the same list
    with 'score' field populated. Does NOT modify acceptance — that is
    done by the run script which applies threshold + rejection_reason logic.
    """
    for cand in candidates:
        cand["score"] = compute_composite_score(cand)
    return candidates
