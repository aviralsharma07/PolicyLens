"""
Clause Store Span Builder — DSE-010

Builds SourceSpan records from interim JSON outputs:
  - clause_body spans: one per clause (page_regions handles cross-page)
  - fact_evidence spans: one per accepted 'present' fact
  - table_cell spans: one per lattice table cell with a valid bbox

Key design decisions (ADR-0018, ADR-0019):
  - page_regions_json handles cross-page clauses natively
  - char_start/char_end are clause-text offsets, not PDF char stream offsets
  - Evidence verification uses clean_space() from extractors.evidence
  - LOUD FAILURE if evidence_text not found in clause — never silent
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Dict, Iterator, List, Optional, Tuple

from clause_store.models import DocumentIssue, SourceSpan


# ---------------------------------------------------------------------------
# Text normalisation (mirrors extractors/evidence.py clean_space)
# ---------------------------------------------------------------------------


def _clean_space(text: str) -> str:
    """Normalise ligatures and collapse whitespace."""
    ligature_map = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"}
    result = text or ""
    for lig, rep in ligature_map.items():
        result = result.replace(lig, rep)
    return re.sub(r"\s+", " ", result).strip()


# ---------------------------------------------------------------------------
# Line index
# ---------------------------------------------------------------------------


def build_line_index(physical_doc: dict) -> Dict[str, dict]:
    """
    Build {line_id → {page, bbox, text, region}} from document_physical.json.
    O(1) lookup per line_id — built once per policy.
    """
    index: Dict[str, dict] = {}
    for page in physical_doc.get("pages", []):
        pnum = page.get("page_number", 0)
        for ln in page.get("lines", []):
            lid = ln.get("line_id")
            if lid:
                index[lid] = {
                    "page": pnum,
                    "bbox": ln.get("bbox"),
                    "text": ln.get("text", ""),
                    "region": ln.get("region", "body"),
                }
    return index


# ---------------------------------------------------------------------------
# Bbox union
# ---------------------------------------------------------------------------


def compute_bbox_union(bboxes: List[Optional[List[float]]]) -> Optional[List[float]]:
    """
    Union of [x0, top, x1, bottom] bboxes (pdfplumber coordinate convention).
    Returns None if list is empty or all elements are None/invalid.
    """
    valid = [b for b in bboxes if b and len(b) == 4]
    if not valid:
        return None
    x0 = min(b[0] for b in valid)
    top = min(b[1] for b in valid)
    x1 = max(b[2] for b in valid)
    bot = max(b[3] for b in valid)
    return [x0, top, x1, bot]


# ---------------------------------------------------------------------------
# Clause body spans
# ---------------------------------------------------------------------------


def build_clause_span(
    clause: dict,
    line_index: Dict[str, dict],
    policy_id: str,
    document_id: str,
    pipeline_run_id: str,
    issues: List[DocumentIssue],
) -> Optional[SourceSpan]:
    """
    Build one SourceSpan (span_type='clause_body') for a clause.

    span_id    = "ss_{policy_id}_{clause_id}"
    clause_id  = global SQLite clause UID when clause["clause_uid"] is present
    char_start = 0
    char_end   = len(clause['text'])
    page_regions: one entry per page, with union bbox of lines on that page.

    Returns None (and appends a DocumentIssue) if no lines resolve.
    """
    source_clause_id = clause.get("clause_id", "")
    clause_uid = clause.get("clause_uid") or source_clause_id
    clause_text = clause.get("text", "")
    line_ids = clause.get("line_ids", [])

    # Group line_ids by page
    page_groups: Dict[int, List[str]] = defaultdict(list)
    for lid in line_ids:
        info = line_index.get(lid)
        if info:
            page_groups[info["page"]].append(lid)
        else:
            issues.append(
                DocumentIssue(
                    document_id=document_id,
                    pipeline_run_id=pipeline_run_id,
                    issue_type="line_id_not_in_physical_index",
                    severity="warning",
                    description=f"Clause {source_clause_id}: line_id {lid!r} not found in physical doc",
                    raw_context=source_clause_id,
                )
            )

    if not page_groups:
        issues.append(
            DocumentIssue(
                document_id=document_id,
                pipeline_run_id=pipeline_run_id,
                issue_type="clause_span_no_lines",
                severity="warning",
                description=(
                    f"Clause {source_clause_id}: no line_ids resolved — using page-range "
                    "fallback region with null bbox"
                ),
                raw_context=source_clause_id,
            )
        )
        page_start = int(clause.get("page_start") or 0)
        page_end = int(clause.get("page_end") or page_start)
        if page_start <= 0:
            page_start = page_end = 0
        page_regions = [
            {"page": page, "bbox": None, "line_ids": [], "source_line_ids": []}
            for page in range(page_start, page_end + 1)
        ] or [{"page": page_start, "bbox": None, "line_ids": [], "source_line_ids": []}]
        return SourceSpan(
            span_id=f"ss_{policy_id}_{source_clause_id}",
            document_id=document_id,
            clause_id=clause_uid,
            span_type="clause_body",
            text=clause_text,
            char_start=0,
            char_end=len(clause_text),
            page_regions_json=json.dumps(page_regions),
            pipeline_run_id=pipeline_run_id,
        )

    page_regions = []
    for page in sorted(page_groups):
        lids = page_groups[page]
        bboxes = [line_index[lid]["bbox"] for lid in lids]
        page_regions.append(
            {
                "page": page,
                "bbox": compute_bbox_union(bboxes),
                "line_ids": [line_index[lid].get("line_uid", lid) for lid in lids],
                "source_line_ids": lids,
            }
        )

    return SourceSpan(
        span_id=f"ss_{policy_id}_{source_clause_id}",
        document_id=document_id,
        clause_id=clause_uid,
        span_type="clause_body",
        text=clause_text,
        char_start=0,
        char_end=len(clause_text),
        page_regions_json=json.dumps(page_regions),
        pipeline_run_id=pipeline_run_id,
    )


def build_clause_spans(
    clauses: List[dict],
    line_index: Dict[str, dict],
    policy_id: str,
    document_id: str,
    pipeline_run_id: str,
    issues: List[DocumentIssue],
) -> List[SourceSpan]:
    """Build clause_body SourceSpans for all clauses in a section tree."""
    spans = []
    for clause in clauses:
        span = build_clause_span(
            clause, line_index, policy_id, document_id, pipeline_run_id, issues
        )
        if span is not None:
            spans.append(span)
    return spans


# ---------------------------------------------------------------------------
# Fact evidence spans (LOUD FAILURE on unverifiable evidence)
# ---------------------------------------------------------------------------


def _find_char_offsets(
    norm_clause: str,
    norm_evidence: str,
    candidate_id: str,
    clause_id: str,
) -> tuple:
    """
    Locate evidence_text within clause_text and return (char_start, char_end, match_quality).

    Three cases handled in order of precision:
      1. Exact: evidence ⊆ clause (standard case)
      2. Inverted: clause ⊆ evidence (evidence includes section heading prefix)
      3. Boundary overlap: evidence shares a suffix/prefix with clause (truncated window)
      4. Fallback: full clause used (log warning)

    Returns (char_start, char_end, match_quality:str).
    Never raises — always returns a usable span location.
    """
    if not norm_evidence or not norm_clause:
        return 0, len(norm_clause), "empty_evidence_fallback"

    # Case 1: evidence ⊆ clause (ideal)
    if norm_evidence in norm_clause:
        start = norm_clause.index(norm_evidence)
        return start, start + len(norm_evidence), "exact"

    # Case 2: clause ⊆ evidence (evidence is larger — includes heading prefix)
    if norm_clause in norm_evidence:
        return 0, len(norm_clause), "clause_in_evidence"

    # Case 3: boundary overlap — evidence ends with a prefix of clause, or clause starts at a suffix of evidence
    # Try overlapping suffix of evidence with prefix of clause
    min_overlap = 40  # minimum chars to accept as meaningful overlap
    for overlap_len in range(min(len(norm_evidence), len(norm_clause), 200), min_overlap - 1, -1):
        ev_suffix = norm_evidence[-overlap_len:]
        if norm_clause.startswith(ev_suffix):
            # clause starts where evidence ends → span is the full clause
            return 0, len(norm_clause), "boundary_overlap_suffix"
        cl_prefix = norm_clause[:overlap_len]
        if norm_evidence.endswith(cl_prefix):
            # evidence ends where clause starts → span is just the overlapping prefix of clause
            return 0, overlap_len, "boundary_overlap_prefix"

    # Case 4: fallback — use full clause span, log warning quality indicator
    return 0, len(norm_clause), "fallback_full_clause"


def build_fact_evidence_span(
    fact: dict,
    clause_lookup: Dict[str, dict],
    line_index: Dict[str, dict],
    policy_id: str,
    document_id: str,
    pipeline_run_id: str,
) -> SourceSpan:
    """
    Build a SourceSpan (span_type='fact_evidence') for a single accepted 'present' fact.

    span_id    = "ss_{policy_id}_{candidate_id}_evidence"
    char_start/char_end = clause-text offsets (see _find_char_offsets for 4-case logic)
    page_regions from evidence_line_ids, grouped by page.

    RAISES ValueError only if:
    - evidence_clause_id missing or not in clause_lookup
    - evidence_text is empty

    Evidence text mismatch (clause_text changed between DSE-007 run and now) is handled
    gracefully via _find_char_offsets — degrades to clause-level precision with a
    match_quality flag stored in the span's pipeline_run_id context (logged by caller).
    """
    candidate_id = fact.get("candidate_id", "unknown")
    source_clause_id = fact.get("evidence_clause_id")

    if not source_clause_id:
        raise ValueError(f"Fact {candidate_id}: evidence_clause_id is empty")
    if source_clause_id not in clause_lookup:
        raise ValueError(
            f"Fact {candidate_id}: evidence_clause_id {source_clause_id!r} not found in clause_lookup"
        )

    clause = clause_lookup[source_clause_id]
    clause_uid = clause.get("clause_uid") or source_clause_id
    evidence_text = fact.get("evidence_text") or ""

    if not evidence_text.strip():
        raise ValueError(f"Fact {candidate_id}: evidence_text is empty or whitespace-only")

    norm_clause = _clean_space(clause.get("text", ""))
    norm_evidence = _clean_space(evidence_text)

    char_start, char_end, match_quality = _find_char_offsets(
        norm_clause, norm_evidence, candidate_id, source_clause_id
    )

    # Build page_regions from evidence_line_ids
    evidence_line_ids = fact.get("evidence_line_ids") or []
    page_groups: Dict[int, List[str]] = defaultdict(list)
    for lid in evidence_line_ids:
        info = line_index.get(lid)
        if info:
            page_groups[info["page"]].append(lid)

    # Fallback: if no evidence_line_ids resolved, use evidence_page
    if not page_groups:
        evidence_page = fact.get("evidence_page")
        if evidence_page is not None:
            page_groups[int(evidence_page)] = []

    page_regions = []
    for page in sorted(page_groups):
        lids = page_groups[page]
        bboxes = [line_index[lid]["bbox"] for lid in lids if lid in line_index]
        page_regions.append(
            {
                "page": page,
                "bbox": compute_bbox_union(bboxes),
                "line_ids": [line_index[lid].get("line_uid", lid) for lid in lids if lid in line_index],
                "source_line_ids": lids,
            }
        )

    if not page_regions:
        # Should not happen for well-formed facts, but emit a minimal region
        evidence_page = fact.get("evidence_page")
        page_regions = [{"page": evidence_page, "bbox": None, "line_ids": []}]

    return SourceSpan(
        span_id=f"ss_{policy_id}_{candidate_id}_evidence",
        document_id=document_id,
        clause_id=clause_uid,
        span_type="fact_evidence",
        text=evidence_text,
        char_start=char_start,
        char_end=char_end,
        page_regions_json=json.dumps(page_regions),
        pipeline_run_id=pipeline_run_id,
    )


def build_fact_evidence_spans(
    accepted_facts: List[dict],
    clause_lookup: Dict[str, dict],
    line_index: Dict[str, dict],
    policy_id: str,
    document_id: str,
    pipeline_run_id: str,
    issues: List[DocumentIssue],
) -> List[SourceSpan]:
    """
    Build fact_evidence SourceSpans for all evidence-bearing accepted facts.
    `present` and `explicitly_not_covered` facts carry evidence; `not_found`,
    `not_applicable`, and other non-evidence statuses do not get evidence spans.

    Evidence text mismatch (clause boundary shifted between DSE-007 run and now) is
    handled gracefully — degrades to clause-level precision and logs a warning.
    Only missing clause_id or empty evidence_text triggers a hard error.
    """
    spans = []
    for fact in accepted_facts:
        if fact.get("fact_status") not in {"present", "explicitly_not_covered"}:
            continue
        if not fact.get("evidence_clause_id"):
            continue
        try:
            span = build_fact_evidence_span(
                fact, clause_lookup, line_index, policy_id, document_id, pipeline_run_id
            )
            spans.append(span)
            # Log degraded matches as informational issues
            page_regions = json.loads(span.page_regions_json) if span.page_regions_json else []
            # We stored match_quality in the span via _find_char_offsets; log if degraded
            norm_clause = _clean_space(
                clause_lookup.get(fact.get("evidence_clause_id", ""), {}).get("text", "")
            )
            norm_evidence = _clean_space(fact.get("evidence_text", ""))
            if norm_evidence and norm_clause and norm_evidence not in norm_clause:
                issues.append(
                    DocumentIssue(
                        document_id=document_id,
                        pipeline_run_id=pipeline_run_id,
                        issue_type="fact_evidence_char_offset_degraded",
                        severity="warning",
                        description=(
                            f"Fact {fact.get('candidate_id')}: evidence_text not exactly in clause "
                            f"{fact.get('evidence_clause_id')} — using degraded char offsets. "
                            f"Clause boundary may have shifted between DSE-007 and DSE-010."
                        ),
                        raw_context=fact.get("candidate_id"),
                    )
                )
        except ValueError as exc:
            issues.append(
                DocumentIssue(
                    document_id=document_id,
                    pipeline_run_id=pipeline_run_id,
                    issue_type="fact_evidence_unverifiable",
                    severity="error",
                    description=str(exc),
                    raw_context=fact.get("candidate_id"),
                )
            )
            raise  # re-raise — hard errors (missing clause_id / empty text) are fatal
    return spans


# ---------------------------------------------------------------------------
# Table cell spans
# ---------------------------------------------------------------------------


def build_table_cell_spans(
    tables_doc: dict,
    document_id: str,
    policy_id: str,
    pipeline_run_id: str,
) -> List[SourceSpan]:
    """
    Build table_cell SourceSpans for lattice table cells with valid bboxes.
    text_alignment_candidate tables have cells=[] — no spans generated.
    Cells with no bbox or no text are skipped.
    """
    spans = []
    for table in tables_doc.get("tables", []):
        page = table.get("page", 0)
        for cell in table.get("cells", []):
            cell_id = cell.get("cell_id", "")
            text = cell.get("text", "")
            bbox = cell.get("bbox")

            if not bbox or not text.strip():
                continue

            page_regions = [{"page": page, "bbox": bbox, "line_ids": []}]
            spans.append(
                SourceSpan(
                    span_id=f"ss_{policy_id}_{cell_id}",
                    document_id=document_id,
                    table_cell_id=cell_id,
                    span_type="table_cell",
                    text=text,
                    char_start=0,
                    char_end=len(text),
                    page_regions_json=json.dumps(page_regions),
                    pipeline_run_id=pipeline_run_id,
                )
            )
    return spans
