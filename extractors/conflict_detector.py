"""
Fact conflict detector — DSE-011

Detects same-concept/same-document candidates with different accepted values.

ADR-0026: Conflict detection logic.

Conflict types:
  value_disagreement  — same concept, different normalized_value_json
  status_disagreement — same concept, one present, another explicitly_not_covered
  scope_disagreement  — same concept+value, different scope_json

Expected: 0 production conflicts for the current 5-concept single-extractor pipeline.
The machinery is proven correct via synthetic test data.
"""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from clause_store.models import FactConflict


def _norm_json(value: Optional[str]) -> str:
    """Normalize a JSON string for comparison (sorted keys, no whitespace)."""
    if not value:
        return "{}"
    try:
        return json.dumps(json.loads(value), sort_keys=True, separators=(",", ":"))
    except (json.JSONDecodeError, TypeError):
        return value or "{}"


def detect_conflicts(
    candidates: List[Dict],
    document_id: str,
    pipeline_run_id: str,
) -> List[FactConflict]:
    """
    Detect conflicts among accepted candidates for the same document.

    A conflict occurs when two or more accepted candidates for the same concept
    have different normalized values, different statuses, or different scopes.

    Args:
        candidates: list of candidate dicts (from fact_candidates.json or SQLite).
                    Must have: 'id' (global UID), 'concept', 'accepted',
                    'normalized_value_json', 'fact_status', 'scope_json'.
        document_id: the document these candidates belong to.
        pipeline_run_id: for the conflict record.

    Returns:
        List of FactConflict records. Empty if no conflicts.
    """
    # Group accepted candidates by concept
    by_concept: Dict[str, List[Dict]] = defaultdict(list)
    for cand in candidates:
        if cand.get("accepted"):
            by_concept[cand["concept"]].append(cand)

    conflicts: List[FactConflict] = []

    for concept, accepted_cands in by_concept.items():
        if len(accepted_cands) < 2:
            continue

        # Compare each pair
        for i in range(len(accepted_cands)):
            for j in range(i + 1, len(accepted_cands)):
                a = accepted_cands[i]
                b = accepted_cands[j]

                conflict_type = _detect_conflict_type(a, b)
                if conflict_type:
                    conflicts.append(
                        FactConflict(
                            document_id=document_id,
                            concept=concept,
                            fact_a_id=a["id"],
                            fact_b_id=b["id"],
                            conflict_type=conflict_type,
                            pipeline_run_id=pipeline_run_id,
                        )
                    )

    return conflicts


def _detect_conflict_type(a: Dict, b: Dict) -> Optional[str]:
    """Determine conflict type between two accepted candidates, or None if no conflict."""
    a_status = a.get("fact_status", "present")
    b_status = b.get("fact_status", "present")

    if a_status != b_status:
        return "status_disagreement"

    a_val = _norm_json(a.get("normalized_value_json"))
    b_val = _norm_json(b.get("normalized_value_json"))

    if a_val != b_val:
        return "value_disagreement"

    a_scope = _norm_json(a.get("scope_json"))
    b_scope = _norm_json(b.get("scope_json"))

    if a_scope != b_scope:
        return "scope_disagreement"

    return None  # Same value, same status, same scope → no conflict


def resolve_conflict(
    conflict: FactConflict,
    candidates_by_id: Dict[str, Dict],
    strategy: str = "higher_score_wins",
) -> FactConflict:
    """
    Apply a resolution strategy to a conflict.

    Strategies:
      higher_score_wins — pick the candidate with higher composite score
      manual_review_required — flag for human review

    Returns a new FactConflict with resolution filled.
    """
    if strategy == "higher_score_wins":
        a = candidates_by_id.get(conflict.fact_a_id, {})
        b = candidates_by_id.get(conflict.fact_b_id, {})
        a_score = float(a.get("score", 0.0))
        b_score = float(b.get("score", 0.0))
        winner_id = conflict.fact_a_id if a_score >= b_score else conflict.fact_b_id
        return FactConflict(
            document_id=conflict.document_id,
            concept=conflict.concept,
            fact_a_id=conflict.fact_a_id,
            fact_b_id=conflict.fact_b_id,
            conflict_type=conflict.conflict_type,
            pipeline_run_id=conflict.pipeline_run_id,
            resolution="higher_score_wins",
            resolved_by="scoring_engine",
            resolution_notes=f"Winner: {winner_id} (score_a={a_score:.4f}, score_b={b_score:.4f})",
        )
    else:
        return FactConflict(
            document_id=conflict.document_id,
            concept=conflict.concept,
            fact_a_id=conflict.fact_a_id,
            fact_b_id=conflict.fact_b_id,
            conflict_type=conflict.conflict_type,
            pipeline_run_id=conflict.pipeline_run_id,
            resolution="manual_review_required",
            resolved_by=None,
            resolution_notes=f"Strategy '{strategy}' requires manual review",
        )
