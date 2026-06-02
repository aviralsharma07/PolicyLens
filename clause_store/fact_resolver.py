"""
Fact Resolver — DSE-010

Replaces provisional evidence_span_id ("clause:{id}") in accepted facts
with real SourceSpan IDs built by span_builder.py.

DSE-007 accepted_facts.json is NEVER overwritten (ADR-0020).
DSE-010 writes resolved facts to data/interim/facts_resolved/{slug}/accepted_facts.json.

Rules:
  - fact_status in {"present", "explicitly_not_covered"} with evidence must resolve
    → evidence_resolution_status = "resolved"
  - fact_status without evidence (not_found, not_applicable, etc.) gets
    evidence_resolution_status = "not_applicable"
  - Missing evidence span for an evidence-bearing fact → LOUD failure, not silent
"""

from __future__ import annotations

import copy
import json
from typing import Dict, List, Tuple

from clause_store.models import SourceSpan


def resolve_facts(
    accepted_facts: List[dict],
    evidence_spans_by_candidate: Dict[str, SourceSpan],
    policy_id: str,
) -> Tuple[List[dict], List[str]]:
    """
    Resolve provisional evidence_span_id values to real source span IDs.

    Args:
        accepted_facts: list from accepted_facts.json (not mutated).
        evidence_spans_by_candidate: {candidate_id → SourceSpan} built by span_builder.
        policy_id: for constructing span IDs.

    Returns:
        (resolved_facts, warning_messages)

    Raises:
        ValueError if a 'present' fact has no corresponding evidence span.
    """
    resolved: List[dict] = []
    warnings: List[str] = []

    for fact in accepted_facts:
        rf = copy.deepcopy(fact)
        status = fact.get("fact_status", "not_found")
        candidate_id = fact.get("candidate_id", "")

        evidence_bearing = status in {"present", "explicitly_not_covered"}

        if evidence_bearing and fact.get("evidence_clause_id"):
            span = evidence_spans_by_candidate.get(candidate_id)
            if span is None:
                raise ValueError(
                    f"Fact {candidate_id} (status={status}) has no evidence span. "
                    f"This means span_builder.build_fact_evidence_spans() "
                    f"did not produce a span for this candidate. "
                    f"Check for prior errors."
                )
            # Preserve provisional ID for audit trail
            rf["provisional_evidence_span_id"] = fact.get("evidence_span_id")
            rf["evidence_span_id"] = span.span_id
            rf["evidence_clause_uid"] = span.clause_id
            rf["evidence_document_id"] = span.document_id
            rf["evidence_resolution_status"] = "resolved"
            try:
                regions = json.loads(span.page_regions_json or "[]")
            except json.JSONDecodeError:
                regions = []
            evidence_line_uids = []
            evidence_source_line_ids = []
            for region in regions:
                evidence_line_uids.extend(region.get("line_ids") or [])
                evidence_source_line_ids.extend(region.get("source_line_ids") or [])
            rf["evidence_line_uids"] = evidence_line_uids
            if evidence_source_line_ids:
                rf["evidence_source_line_ids"] = evidence_source_line_ids

        elif not evidence_bearing:
            # not_found / not_applicable / etc. — no evidence span expected
            rf["provisional_evidence_span_id"] = fact.get("evidence_span_id")
            rf["evidence_resolution_status"] = "not_applicable"

        else:
            # evidence-bearing but no evidence_clause_id — shouldn't happen for valid output
            warnings.append(
                f"Fact {candidate_id}: status={status} but no evidence_clause_id — not resolved"
            )
            rf["provisional_evidence_span_id"] = fact.get("evidence_span_id")
            rf["evidence_resolution_status"] = "unresolved_no_clause_id"

        resolved.append(rf)

    return resolved, warnings
