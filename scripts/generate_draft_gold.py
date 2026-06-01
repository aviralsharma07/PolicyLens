"""
Generate Draft Gold Annotations — DSE-012

Converts pipeline interim outputs into draft gold annotation files.
Every generated file is marked label_status=draft, annotation_method=pipeline_draft.

Does NOT modify existing reviewed gold policies.

Usage:
  PYTHONPATH=. python scripts/generate_draft_gold.py \\
    --manifest data/manifests/dse012_gold_expansion_candidates_v1.json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import time
from typing import Any, Dict, List, Optional

from identity.uin_utils import extract_uin_base
from identity.insurer_registry import get_display_name
from identity.plan_normalizer import clean_plan_name

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("generate_draft_gold")

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

# The 20 priority concepts (same order as existing gold)
_ALL_CONCEPTS = [
    "ped_waiting_period",
    "initial_waiting_period",
    "specific_disease_waiting_periods",
    "room_rent_limit",
    "icu_limit",
    "co_pay",
    "deductible",
    "cumulative_bonus_ncb",
    "restoration_benefit",
    "ayush_coverage",
    "modern_treatment_coverage",
    "maternity_waiting",
    "newborn_coverage",
    "organ_donor_coverage",
    "ambulance_coverage",
    "free_look_period",
    "grace_period",
    "renewability",
    "claim_intimation_timeline",
    "claim_settlement_timeline",
]


def _load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _detect_known_issues(policy: dict, phys: dict, tree: Optional[dict]) -> List[str]:
    """Detect known issues for the review report."""
    issues = []
    if tree:
        if tree.get("total_sections", 0) <= 1:
            issues.append("section_tree_failed_or_degenerate")
        if tree.get("total_clauses", 0) == 0:
            issues.append("no_clauses_segmented")
    return issues


# ---------------------------------------------------------------------------
# metadata.json
# ---------------------------------------------------------------------------


def generate_metadata(
    policy: dict, phys: dict, tree: Optional[dict], known_issues: List[str]
) -> dict:
    insurer = policy["insurer_display"]
    raw_plan = policy["plan_name_raw"]
    # Re-clean plan name to pick up NBSP normalization fix (DSE-012)
    clean = clean_plan_name(raw_plan, insurer)

    return {
        "policy_id": policy["slug"],
        "policy_slug": policy["slug"],
        "insurer": insurer,
        "plan_name": clean,
        "uin": policy["uin"],
        "uin_base": policy["uin_base"],
        "lifecycle_product_name": raw_plan,
        "match_status": "verified",
        "match_confidence": "high",
        "source_pdf_path": policy["file_path"],
        "raw_pdf_policy": "read_only_external_reference",
        "file_hash": policy.get("file_hash", ""),
        "document_id": phys.get("document_id", policy.get("file_hash", "")),
        "page_count": phys.get("page_count", policy.get("page_count", 0)),
        "source_domain": policy.get("source_domain", ""),
        "document_type": "policy_wording",
        "corpus_status": "active",
        "triage_flags": [],
        "annotator": "pipeline_draft",
        "human_reviewer": None,
        "annotation_date": time.strftime("%Y-%m-%d"),
        "pipeline_run_id": phys.get("pipeline_run_id", "dse012_batch"),
        "annotation_status": "pipeline_draft",
        "label_status": "draft",
        "review_status": "needs_human_review",
        "known_issues": known_issues,
        "annotation_method": "pipeline_draft",
        "counts": {
            "sections": tree.get("total_sections", 0) if tree else 0,
            "clauses": tree.get("total_clauses", 0) if tree else 0,
            "tables": 0,  # filled below
            "facts": 20,
        },
        "annotation_passes": [
            {
                "pass_id": "dse012_pipeline_draft",
                "date": time.strftime("%Y-%m-%d"),
                "tools": [
                    "pdfplumber",
                    "heading_scorer",
                    "section_tree_builder",
                    "table_engine",
                    "fact_extractors",
                ],
                "changes": "Automated pipeline draft. Requires human review before promotion to gold.",
            }
        ],
    }


# ---------------------------------------------------------------------------
# sections.json
# ---------------------------------------------------------------------------


def generate_sections(tree: Optional[dict], slug: str) -> List[dict]:
    if not tree:
        return [
            {
                "section_id": f"{slug}_sec_000",
                "section_number": None,
                "title": "Document root",
                "level": 0,
                "parent_id": None,
                "page_start": 1,
                "page_end": 1,
                "source_page_refs": [1],
                "heading_text": None,
                "annotation_status": "pipeline_draft",
                "notes": "Section tree degenerate — heading scorer found no visual headings.",
                "source_tools": ["pipeline_draft"],
            }
        ]

    sections = []
    for sec in tree.get("sections", []):
        sections.append(
            {
                "section_id": sec.get("section_id", ""),
                "section_number": sec.get("number"),
                "title": sec.get("title", ""),
                "level": sec.get("level", 0),
                "parent_id": sec.get("parent_id"),
                "page_start": sec.get("page_start", 0),
                "page_end": sec.get("page_end", 0),
                "source_page_refs": list(
                    range(sec.get("page_start", 1), sec.get("page_end", 1) + 1)
                ),
                "heading_text": sec.get("title"),
                "annotation_status": "pipeline_draft",
                "notes": "",
                "source_tools": ["pipeline_draft"],
            }
        )
    return sections


# ---------------------------------------------------------------------------
# clauses.json
# ---------------------------------------------------------------------------


def generate_clauses(tree: Optional[dict]) -> List[dict]:
    if not tree:
        return []

    clauses = []
    for cl in tree.get("clauses", []):
        text = cl.get("text", "")
        clauses.append(
            {
                "clause_id": cl.get("clause_id", ""),
                "section_id": cl.get("section_id", ""),
                "clause_number": cl.get("clause_number"),
                "title": cl.get("title", ""),
                "page_start": cl.get("page_start", 0),
                "page_end": cl.get("page_end", 0),
                "source_page_refs": list(range(cl.get("page_start", 1), cl.get("page_end", 1) + 1)),
                "raw_text": text,
                "annotation_status": "pipeline_draft",
                "notes": "",
                "source_tools": ["pipeline_draft"],
            }
        )
    return clauses


# ---------------------------------------------------------------------------
# tables.json
# ---------------------------------------------------------------------------


def generate_tables(slug: str) -> List[dict]:
    tables_path = f"data/interim/tables/{slug}/document_tables.json"
    if not os.path.isfile(tables_path):
        return []

    doc = _load_json(tables_path)
    tables = []
    for t in doc.get("tables", []):
        if t.get("extraction_method") == "text_alignment_candidate":
            continue  # only include lattice tables as gold candidates
        tables.append(
            {
                "table_id": t.get("table_id", ""),
                "page": t.get("page", 0),
                "bbox": t.get("bbox"),
                "table_type": t.get("table_type", "unknown"),
                "headers": [],
                "rows": [],
                "parent_clause_id": t.get("parent_clause_id"),
                "source_page_refs": [t.get("page", 0)],
                "evidence_text": None,
                "annotation_status": "pipeline_draft",
                "notes": "",
                "cell_coordinates_status": "pipeline_detected",
                "source_tools": ["pipeline_draft"],
            }
        )
    return tables


# ---------------------------------------------------------------------------
# facts.json
# ---------------------------------------------------------------------------


def generate_facts(slug: str, phys: dict) -> List[dict]:
    """Generate 20-concept fact annotations from pipeline output."""
    facts_path = f"data/interim/facts/{slug}/accepted_facts.json"
    extracted = {}
    if os.path.isfile(facts_path):
        for f in _load_json(facts_path):
            extracted[f["concept"]] = f

    source_doc = phys.get("file_hash", phys.get("document_id", ""))
    facts = []

    for concept in _ALL_CONCEPTS:
        ext = extracted.get(concept)

        if ext and ext.get("fact_status") == "present":
            facts.append(
                {
                    "concept": concept,
                    "value_json": ext.get("value_json"),
                    "normalized_value_json": ext.get("normalized_value_json"),
                    "fact_status": "present",
                    "scope_json": ext.get("scope_json"),
                    "condition_json": ext.get("condition_json"),
                    "extraction_method": ext.get("extraction_method", "deterministic"),
                    "confidence": ext.get("confidence", 0.0),
                    "evidence_span_id": ext.get("evidence_span_id"),
                    "pipeline_run_id": ext.get("pipeline_run_id", "dse012_batch"),
                    "evidence_page": ext.get("evidence_page"),
                    "evidence_text": ext.get("evidence_text"),
                    "source_document": source_doc,
                    "value_type": ext.get("value_type"),
                    "annotator": "pipeline_draft",
                    "review_status": "needs_human_review",
                    "notes": "Pipeline-extracted. Requires human verification of value and evidence.",
                    "source_tools": ["pipeline_draft"],
                }
            )
        elif ext and ext.get("fact_status") == "not_found":
            facts.append(
                {
                    "concept": concept,
                    "value_json": None,
                    "normalized_value_json": None,
                    "fact_status": "not_found",
                    "scope_json": None,
                    "condition_json": None,
                    "extraction_method": "deterministic",
                    "confidence": None,
                    "evidence_span_id": None,
                    "pipeline_run_id": ext.get("pipeline_run_id", "dse012_batch"),
                    "evidence_page": None,
                    "evidence_text": None,
                    "source_document": source_doc,
                    "value_type": None,
                    "annotator": "pipeline_draft",
                    "review_status": "needs_human_review",
                    "notes": "Extractor searched but did not find this concept. May need manual search.",
                    "source_tools": ["pipeline_draft"],
                }
            )
        else:
            # No extractor for this concept — mark as not_found with explanation
            facts.append(
                {
                    "concept": concept,
                    "value_json": None,
                    "normalized_value_json": None,
                    "fact_status": "not_found",
                    "scope_json": None,
                    "condition_json": None,
                    "extraction_method": None,
                    "confidence": None,
                    "evidence_span_id": None,
                    "pipeline_run_id": "dse012_batch",
                    "evidence_page": None,
                    "evidence_text": None,
                    "source_document": source_doc,
                    "value_type": None,
                    "annotator": "pipeline_draft",
                    "review_status": "needs_human_review",
                    "notes": "No extractor implemented for this concept. Requires manual annotation.",
                    "source_tools": ["pipeline_draft"],
                }
            )

    return facts


# ---------------------------------------------------------------------------
# heading_labels.json
# ---------------------------------------------------------------------------


def generate_heading_labels(slug: str) -> List[dict]:
    heading_path = f"data/interim/logical/{slug}/heading_candidates.json"
    if not os.path.isfile(heading_path):
        return []

    data = _load_json(heading_path)
    candidates = data.get("candidates", [])

    labels = []
    for i, cand in enumerate(candidates):
        if cand.get("score", 0) < 0.5:
            continue  # only include accepted headings
        labels.append(
            {
                "label_id": f"{slug}_heading_{i:04d}",
                "source_section_id": None,
                "page": cand.get("page_number", 0),
                "expected_text": cand.get("text", ""),
                "label_type": "visual_heading",
                "is_visual_heading": True,
                "line_id": cand.get("line_id", ""),
                "reviewer_note": "pipeline_draft",
            }
        )
    return labels


# ---------------------------------------------------------------------------
# physical_table_labels.json
# ---------------------------------------------------------------------------


def generate_physical_table_labels(slug: str) -> List[dict]:
    tables_path = f"data/interim/tables/{slug}/document_tables.json"
    if not os.path.isfile(tables_path):
        return []

    doc = _load_json(tables_path)
    labels = []
    for i, t in enumerate(doc.get("tables", [])):
        if t.get("extraction_method") != "pdfplumber_lattice":
            continue
        if not t.get("bbox"):
            continue
        labels.append(
            {
                "label_id": f"{slug}_phys_table_{i:04d}",
                "source_table_id": t.get("table_id", ""),
                "page": t.get("page", 0),
                "bbox": t.get("bbox"),
                "table_type": t.get("table_type", "unknown"),
                "headers": [],
                "rows": [],
                "header_rows": [],
                "column_count": t.get("col_count", 0),
                "row_count": t.get("row_count", 0),
                "priority": t.get("table_type") in ("waiting_period", "schedule_of_benefits"),
                "reviewer_note": "pipeline_draft",
            }
        )
    return labels


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def generate_policy(policy: dict) -> dict:
    """Generate all 7 draft gold files for one policy."""
    slug = policy["slug"]
    logger.info("Generating draft gold for %s", slug)

    # Load interim outputs
    phys_path = f"data/interim/physical/{slug}/document_physical.json"
    tree_path = f"data/interim/logical/{slug}/section_tree.json"

    phys = _load_json(phys_path) if os.path.isfile(phys_path) else {}
    tree = _load_json(tree_path) if os.path.isfile(tree_path) else None

    known_issues = _detect_known_issues(policy, phys, tree)

    # Generate all 7 files
    metadata = generate_metadata(policy, phys, tree, known_issues)
    sections = generate_sections(tree, slug)
    clauses = generate_clauses(tree)
    tables = generate_tables(slug)
    facts = generate_facts(slug, phys)
    heading_labels = generate_heading_labels(slug)
    physical_table_labels = generate_physical_table_labels(slug)

    # Update metadata counts
    metadata["counts"]["tables"] = len(tables)
    metadata["counts"]["sections"] = len(sections)
    metadata["counts"]["clauses"] = len(clauses)

    # Write to gold_corpus/policies/{slug}/
    out_dir = f"gold_corpus/policies/{slug}"
    _write_json(f"{out_dir}/metadata.json", metadata)
    _write_json(f"{out_dir}/sections.json", sections)
    _write_json(f"{out_dir}/clauses.json", clauses)
    _write_json(f"{out_dir}/tables.json", tables)
    _write_json(f"{out_dir}/facts.json", facts)
    _write_json(f"{out_dir}/heading_labels.json", heading_labels)
    _write_json(f"{out_dir}/physical_table_labels.json", physical_table_labels)

    logger.info(
        "  %s: %d sections, %d clauses, %d tables, %d facts, %d heading_labels, %d physical_table_labels, issues=%s",
        slug,
        len(sections),
        len(clauses),
        len(tables),
        len(facts),
        len(heading_labels),
        len(physical_table_labels),
        known_issues or "none",
    )

    return {
        "slug": slug,
        "status": "draft_generated",
        "files_written": 7,
        "sections": len(sections),
        "clauses": len(clauses),
        "tables": len(tables),
        "facts": len(facts),
        "heading_labels": len(heading_labels),
        "physical_table_labels": len(physical_table_labels),
        "known_issues": known_issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Draft Gold — DSE-012")
    parser.add_argument(
        "--manifest", default="data/manifests/dse012_gold_expansion_candidates_v1.json"
    )
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    policies = manifest.get("policies", [])

    results = []
    for policy in policies:
        result = generate_policy(policy)
        results.append(result)

    _write_json(
        "data/reports/dse012_draft_gold_summary.json",
        {
            "date": time.strftime("%Y-%m-%d"),
            "total_policies": len(results),
            "results": results,
        },
    )
    logger.info("Draft gold generation complete: %d policies", len(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
