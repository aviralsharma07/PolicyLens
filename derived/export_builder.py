"""
Export builder — DSE-013

Builds the three Product B consumable JSON files per policy:
  policy_features.json
  policy_fact_sources.json
  policy_clauses_minimal.json

Reads from data/engine.sqlite. Writes to data/export/{policy_id}/.
"""

from __future__ import annotations

import json
import sqlite3
import time
from typing import Any, Dict, List, Optional

from derived.field_mapping import (
    ALL_EXPORT_CONCEPTS,
    CONCEPT_FIELD_MAP,
    extract_scalar_value,
    get_export_field_name,
    get_unit,
)

_CLAUSE_TEXT_MAX = 500
_EXPORT_SCHEMA_VERSION = "1.0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _json_parse(val: Any) -> Any:
    """Parse a JSON string or return as-is if already parsed or None."""
    if val is None:
        return None
    if isinstance(val, str):
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return val
    return val


def _evidence_page_from_span(conn: sqlite3.Connection, span_id: Optional[str]) -> Optional[int]:
    """Extract the first page number from a source_span's page_regions_json."""
    if not span_id:
        return None
    row = conn.execute(
        "SELECT page_regions_json FROM source_spans WHERE span_id = ?",
        (span_id,),
    ).fetchone()
    if not row:
        return None
    try:
        regions = json.loads(row[0])
        if regions and isinstance(regions, list):
            return regions[0].get("page")
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def _clause_info(conn: sqlite3.Connection, clause_id: Optional[str]) -> Dict[str, Any]:
    """
    Get clause reference and title from policy_clauses.

    Fallback chain for evidence_clause (contract requires non-null for present facts):
      1. clause_number if not null (e.g., "4.1")
      2. source_clause_id as fallback (e.g., "clause_0050")
    """
    if not clause_id:
        return {"number": None, "title": None}
    row = conn.execute(
        "SELECT clause_number, title, source_clause_id FROM policy_clauses WHERE clause_id = ?",
        (clause_id,),
    ).fetchone()
    if row:
        number = row["clause_number"] or row["source_clause_id"]
        return {"number": number, "title": row["title"]}
    return {"number": None, "title": None}


# ---------------------------------------------------------------------------
# policy_features.json
# ---------------------------------------------------------------------------


def build_policy_features(
    conn: sqlite3.Connection,
    document_id: str,
    policy_id: str,
    pipeline_run_id: str,
) -> dict:
    """
    Build policy_features.json per export_contract.md.

    All 20 concepts emitted. Present facts have values and evidence.
    Not-found concepts have null values and null evidence.
    """
    # Source document block
    doc_row = conn.execute(
        """SELECT sd.source_pdf_path, sd.file_hash, sd.page_count,
                  p.normalized_insurer, p.normalized_plan_name, p.uin_base,
                  pv.full_uin
           FROM source_documents sd
           JOIN products p ON p.product_id = sd.policy_id
           JOIN product_versions pv ON pv.version_id = sd.version_id
           WHERE sd.document_id = ?""",
        (document_id,),
    ).fetchone()

    source_document = {
        "filename": doc_row["source_pdf_path"].split("/")[-1] if doc_row else None,
        "file_hash": doc_row["file_hash"] if doc_row else None,
        "source_domain": "policy_wording",
        "page_count": doc_row["page_count"] if doc_row else None,
    }

    product_identity = {
        "insurer": doc_row["normalized_insurer"] if doc_row else None,
        "plan_name": doc_row["normalized_plan_name"] if doc_row else None,
        "uin": doc_row["full_uin"] if doc_row else None,
        "uin_base": doc_row["uin_base"] if doc_row else None,
    }

    # Build features for all 20 concepts
    facts_cursor = conn.execute(
        """SELECT concept, value_json, normalized_value_json, fact_status,
                  confidence, extraction_method, evidence_span_id, clause_id,
                  scope_json, condition_json
           FROM extracted_facts WHERE document_id = ?""",
        (document_id,),
    )
    facts_by_concept: Dict[str, dict] = {}
    for row in facts_cursor.fetchall():
        facts_by_concept[row["concept"]] = dict(row)

    features: Dict[str, dict] = {}
    concepts_resolved = 0
    concepts_not_found = 0
    concepts_not_applicable = 0
    total_confidence = 0.0
    confidence_count = 0
    unresolved_concepts: List[str] = []

    for concept in ALL_EXPORT_CONCEPTS:
        field_name = get_export_field_name(concept)
        unit = get_unit(concept)

        fact = facts_by_concept.get(concept)

        if fact:
            status = fact["fact_status"]
            norm_val = _json_parse(fact["normalized_value_json"])
            scalar_val = extract_scalar_value(concept, norm_val)
            confidence = fact["confidence"]
            method = fact["extraction_method"]
            span_id = fact["evidence_span_id"]
            clause_id = fact["clause_id"]
            scope = _json_parse(fact["scope_json"])
            condition = _json_parse(fact["condition_json"])

            evidence_page = _evidence_page_from_span(conn, span_id)
            clause = _clause_info(conn, clause_id)

            # Get evidence text from source_span
            evidence_text = None
            if span_id:
                span_row = conn.execute(
                    "SELECT text FROM source_spans WHERE span_id = ?", (span_id,)
                ).fetchone()
                if span_row:
                    evidence_text = span_row[0]

            features[field_name] = {
                "value": scalar_val,
                "unit": unit,
                "fact_status": status,
                "confidence": confidence,
                "method": method,
                "evidence": evidence_text,
                "evidence_page": evidence_page,
                "evidence_clause": clause["number"],
                "scope": scope,
                "condition": condition,
                "source_span_id": span_id,
            }

            if status == "present":
                concepts_resolved += 1
                if confidence is not None:
                    total_confidence += confidence
                    confidence_count += 1
            elif status == "explicitly_not_covered":
                concepts_resolved += 1
            elif status == "not_applicable":
                concepts_not_applicable += 1
        else:
            # Not found — no extractor produced a fact for this concept
            features[field_name] = {
                "value": None,
                "unit": unit,
                "fact_status": "not_found",
                "confidence": None,
                "method": None,
                "evidence": None,
                "evidence_page": None,
                "evidence_clause": None,
                "scope": None,
                "condition": None,
                "source_span_id": None,
            }
            concepts_not_found += 1
            unresolved_concepts.append(concept)

    avg_confidence = round(total_confidence / confidence_count, 2) if confidence_count else None
    fill_rate = round(concepts_resolved / len(ALL_EXPORT_CONCEPTS), 2)

    return {
        "policy_id": policy_id,
        "export_schema_version": _EXPORT_SCHEMA_VERSION,
        "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pipeline_run_id": pipeline_run_id,
        "source_document": source_document,
        "product_identity": product_identity,
        "features": features,
        "unresolved_concepts": unresolved_concepts,
        "parse_quality": {
            "total_concepts_attempted": len(ALL_EXPORT_CONCEPTS),
            "concepts_resolved": concepts_resolved,
            "concepts_not_found": concepts_not_found,
            "concepts_not_applicable": concepts_not_applicable,
            "overall_fill_rate": fill_rate,
            "average_confidence": avg_confidence,
        },
    }


# ---------------------------------------------------------------------------
# policy_fact_sources.json
# ---------------------------------------------------------------------------


def build_policy_fact_sources(
    conn: sqlite3.Connection,
    document_id: str,
    policy_id: str,
    pipeline_run_id: str,
) -> dict:
    """
    Build policy_fact_sources.json with full provenance for each concept.

    Lists ALL candidates (accepted + rejected) per concept.
    """
    # Get all candidates for this document
    candidates = conn.execute(
        """SELECT source_candidate_id, concept, candidate_value_json,
                  normalized_value_json, fact_status, confidence, score,
                  accepted, rejection_reason, extractor_name, pattern_id,
                  evidence_span_id, evidence_text, evidence_page,
                  source_clause_id, clause_id
           FROM extracted_fact_candidates
           WHERE document_id = ?
           ORDER BY concept, score DESC""",
        (document_id,),
    ).fetchall()

    # Get accepted facts for linking
    accepted_facts = conn.execute(
        "SELECT concept, source_candidate_id FROM extracted_facts WHERE document_id = ?",
        (document_id,),
    ).fetchall()
    accepted_by_concept = {r["concept"]: r["source_candidate_id"] for r in accepted_facts}

    # Get conflicts
    conflicts = conn.execute(
        """SELECT concept, fact_a_id, fact_b_id, conflict_type,
                  resolution, resolved_by, resolution_notes
           FROM fact_conflicts WHERE document_id = ?""",
        (document_id,),
    ).fetchall()

    # Group candidates by concept
    from collections import defaultdict

    cands_by_concept: Dict[str, List[dict]] = defaultdict(list)
    for c in candidates:
        clause = _clause_info(conn, c["clause_id"])

        # For accepted candidates with a source_span, derive page from the span
        # (same source of truth as policy_features.json) to avoid cross-file disagreement.
        # For rejected candidates without spans, fall back to stale candidate evidence_page.
        page = c["evidence_page"]
        if c["accepted"] and c["evidence_span_id"]:
            span_page = _evidence_page_from_span(conn, c["evidence_span_id"])
            if span_page is not None:
                page = span_page

        cands_by_concept[c["concept"]].append(
            {
                "candidate_id": c["source_candidate_id"],
                "clause_number": clause["number"],
                "clause_title": clause["title"],
                "evidence_text_snippet": (c["evidence_text"] or "")[:300],
                "page": page,
                "extraction_method": "deterministic",
                "extractor_name": c["extractor_name"],
                "pattern_id": c["pattern_id"],
                "candidate_score": c["score"],
                "confidence": c["confidence"],
                "accepted": bool(c["accepted"]),
                "rejection_reason": c["rejection_reason"],
                "pipeline_run_id": pipeline_run_id,
            }
        )

    sources: Dict[str, dict] = {}
    for concept in ALL_EXPORT_CONCEPTS:
        provenance = cands_by_concept.get(concept, [])
        accepted_id = accepted_by_concept.get(concept)
        sources[concept] = {
            "provenance": provenance,
            "accepted_candidate_id": accepted_id,
        }

    resolved_conflicts = [
        {
            "concept": c["concept"],
            "fact_a_id": c["fact_a_id"],
            "fact_b_id": c["fact_b_id"],
            "conflict_type": c["conflict_type"],
            "resolution": c["resolution"],
            "resolved_by": c["resolved_by"],
            "resolution_notes": c["resolution_notes"],
        }
        for c in conflicts
        if c["resolution"] != "unresolved"
    ]
    unresolved_conflicts = [
        {
            "concept": c["concept"],
            "fact_a_id": c["fact_a_id"],
            "fact_b_id": c["fact_b_id"],
            "conflict_type": c["conflict_type"],
        }
        for c in conflicts
        if c["resolution"] == "unresolved"
    ]

    return {
        "policy_id": policy_id,
        "pipeline_run_id": pipeline_run_id,
        "sources": sources,
        "conflicts_resolved": resolved_conflicts,
        "unresolved_conflicts": unresolved_conflicts,
    }


# ---------------------------------------------------------------------------
# policy_clauses_minimal.json
# ---------------------------------------------------------------------------


def build_policy_clauses_minimal(
    conn: sqlite3.Connection,
    document_id: str,
    policy_id: str,
) -> dict:
    """
    Lightweight section/clause tree for Product B.
    No spans, no bbox, no line IDs. Clause text truncated to 500 chars.
    """
    sections = conn.execute(
        """SELECT section_id, source_section_id, section_number, title,
                  level, page_start, page_end
           FROM document_sections
           WHERE document_id = ?
           ORDER BY page_start, section_id""",
        (document_id,),
    ).fetchall()

    clauses = conn.execute(
        """SELECT clause_id, source_clause_id, section_id,
                  clause_number, title, raw_text, page_start
           FROM policy_clauses
           WHERE document_id = ?
           ORDER BY page_start, clause_id""",
        (document_id,),
    ).fetchall()

    # Group clauses by section
    from collections import defaultdict

    clauses_by_section: Dict[str, List[dict]] = defaultdict(list)
    for c in clauses:
        text = c["raw_text"] or ""
        clauses_by_section[c["section_id"]].append(
            {
                "number": c["clause_number"],
                "title": c["title"],
                "text": text[:_CLAUSE_TEXT_MAX] + ("..." if len(text) > _CLAUSE_TEXT_MAX else ""),
                "page": c["page_start"],
            }
        )

    section_list = []
    for s in sections:
        section_clauses = clauses_by_section.get(s["section_id"], [])
        if not section_clauses and s["level"] > 2:
            continue  # skip deep empty sections
        section_list.append(
            {
                "number": s["section_number"],
                "title": s["title"],
                "level": s["level"],
                "page_start": s["page_start"],
                "page_end": s["page_end"],
                "clauses": section_clauses,
            }
        )

    return {
        "policy_id": policy_id,
        "total_sections": len(section_list),
        "total_clauses": sum(len(s["clauses"]) for s in section_list),
        "sections": section_list,
    }
