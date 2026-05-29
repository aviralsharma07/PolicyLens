#!/usr/bin/env python3
"""Validate DSE-003 gold corpus annotations."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
GOLD_ROOT = REPO_ROOT / "gold_corpus"

EXPECTED_POLICIES = {
    "new_india_floater",
    "star_medi_classic_accident",
    "hdfc_arogya_sanjeevani",
    "icici_family_shield",
    "care_health_care_plus",
}

EXPECTED_FILES = {
    "metadata.json",
    "sections.json",
    "clauses.json",
    "tables.json",
    "facts.json",
    "heading_labels.json",
}

GENERATED_DOCLING_POLICIES = {
    "star_medi_classic_accident",
    "care_health_care_plus",
}

GENERATED_DOCLING_PASS_ID = "pass_4_generated_docling_crosscheck_missing_policies"

FACT_STATUSES = {
    "present",
    "explicitly_not_covered",
    "not_applicable",
    "not_found",
    "ambiguous",
    "conflicting",
    "requires_manual_review",
}

REQUIRED_FACT_FIELDS = {
    "concept",
    "value_json",
    "normalized_value_json",
    "fact_status",
    "scope_json",
    "condition_json",
    "extraction_method",
    "confidence",
    "evidence_span_id",
    "pipeline_run_id",
    "evidence_page",
    "evidence_text",
    "source_document",
}

EXPECTED_CONCEPTS = {
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
}


class ValidationError(Exception):
    """Raised when a gold corpus invariant fails."""


def load_json(path: Path) -> Any:
    try:
        with path.open() as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc
    except OSError as exc:
        raise ValidationError(f"{path}: failed to read file: {exc}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_page_ref(path: Path, field: str, value: Any, page_count: int) -> None:
    require(isinstance(value, int), f"{path}: {field} must be an integer")
    require(1 <= value <= page_count, f"{path}: {field}={value} outside 1..{page_count}")


def validate_page_refs(path: Path, refs: Any, page_count: int) -> None:
    require(isinstance(refs, list) and refs, f"{path}: source_page_refs must be a non-empty list")
    for page in refs:
        validate_page_ref(path, "source_page_refs[]", page, page_count)


def validate_metadata(policy_dir: Path) -> dict[str, Any]:
    path = policy_dir / "metadata.json"
    metadata = load_json(path)
    required = {
        "policy_id",
        "policy_slug",
        "insurer",
        "plan_name",
        "uin",
        "source_pdf_path",
        "file_hash",
        "page_count",
        "source_domain",
        "document_type",
        "corpus_status",
        "annotation_date",
        "pipeline_run_id",
        "annotation_status",
        "counts",
    }
    missing = sorted(required - metadata.keys())
    require(not missing, f"{path}: missing required fields: {missing}")
    require(metadata["policy_slug"] == policy_dir.name, f"{path}: policy_slug must match folder name")
    require(metadata["document_type"] == "policy_wording", f"{path}: document_type must be policy_wording")
    require(metadata["corpus_status"] == "active", f"{path}: corpus_status must be active")
    require(isinstance(metadata["page_count"], int) and metadata["page_count"] > 0, f"{path}: invalid page_count")
    passes = metadata.get("annotation_passes")
    require(isinstance(passes, list) and len(passes) >= 2, f"{path}: annotation_passes must include pass 2 and pass 3")
    pass_ids = {p.get("pass_id") for p in passes if isinstance(p, dict)}
    require("pass_2_structure_docling_crosscheck" in pass_ids, f"{path}: missing pass_2_structure_docling_crosscheck")
    require("pass_3_fact_precision_review" in pass_ids, f"{path}: missing pass_3_fact_precision_review")
    if policy_dir.name in GENERATED_DOCLING_POLICIES:
        require(GENERATED_DOCLING_PASS_ID in pass_ids, f"{path}: missing {GENERATED_DOCLING_PASS_ID}")
    require(metadata.get("docling_markdown_available") is True, f"{path}: docling_markdown_available must be true")
    docling_path_value = metadata.get("docling_markdown_path")
    require(isinstance(docling_path_value, str) and docling_path_value, f"{path}: docling_markdown_path is required")
    docling_path = REPO_ROOT / docling_path_value
    if not docling_path.exists():
        docling_path = REPO_ROOT.parent / docling_path_value
    require(docling_path.exists(), f"{path}: docling markdown does not exist: {docling_path_value}")
    if policy_dir.name in GENERATED_DOCLING_POLICIES:
        try:
            docling_text = docling_path.read_text(errors="replace")
        except OSError as exc:
            raise ValidationError(f"{path}: failed to read docling markdown {docling_path}: {exc}") from exc
        require("data:image" not in docling_text, f"{path}: generated markdown must not embed images")
        require("base64," not in docling_text, f"{path}: generated markdown must not embed base64 image data")
    source_pdf = REPO_ROOT.parent / "policy_data" / metadata["source_pdf_path"]
    require(source_pdf.exists(), f"{path}: source PDF does not exist: {source_pdf}")
    return metadata


def validate_sections(policy_dir: Path, page_count: int) -> int:
    path = policy_dir / "sections.json"
    sections = load_json(path)
    require(isinstance(sections, list) and sections, f"{path}: must be a non-empty array")
    ids: set[str] = set()
    for item in sections:
        for field in ("section_id", "title", "level", "page_start", "page_end", "source_page_refs"):
            require(field in item, f"{path}: section missing {field}")
        require(item["section_id"] not in ids, f"{path}: duplicate section_id {item['section_id']}")
        ids.add(item["section_id"])
        validate_page_ref(path, "page_start", item["page_start"], page_count)
        validate_page_ref(path, "page_end", item["page_end"], page_count)
        require(item["page_start"] <= item["page_end"], f"{path}: section page_start > page_end")
        validate_page_refs(path, item["source_page_refs"], page_count)
        parent = item.get("parent_id")
        require(parent is None or isinstance(parent, str), f"{path}: parent_id must be string/null")
    return len(sections)


def validate_clauses(policy_dir: Path, page_count: int) -> int:
    path = policy_dir / "clauses.json"
    clauses = load_json(path)
    require(isinstance(clauses, list) and clauses, f"{path}: must be a non-empty array")
    ids: set[str] = set()
    for item in clauses:
        for field in ("clause_id", "section_id", "page_start", "page_end", "source_page_refs", "raw_text"):
            require(field in item, f"{path}: clause missing {field}")
        require(item["clause_id"] not in ids, f"{path}: duplicate clause_id {item['clause_id']}")
        ids.add(item["clause_id"])
        validate_page_ref(path, "page_start", item["page_start"], page_count)
        validate_page_ref(path, "page_end", item["page_end"], page_count)
        require(item["page_start"] <= item["page_end"], f"{path}: clause page_start > page_end")
        validate_page_refs(path, item["source_page_refs"], page_count)
        require(isinstance(item["raw_text"], str) and item["raw_text"].strip(), f"{path}: empty raw_text")
    return len(clauses)


def validate_tables(policy_dir: Path, page_count: int) -> int:
    path = policy_dir / "tables.json"
    tables = load_json(path)
    require(isinstance(tables, list), f"{path}: must be an array")
    ids: set[str] = set()
    for item in tables:
        for field in ("table_id", "page", "table_type", "headers", "rows", "source_page_refs", "annotation_status"):
            require(field in item, f"{path}: table missing {field}")
        require(item["table_id"] not in ids, f"{path}: duplicate table_id {item['table_id']}")
        ids.add(item["table_id"])
        validate_page_ref(path, "page", item["page"], page_count)
        validate_page_refs(path, item["source_page_refs"], page_count)
        require(isinstance(item["headers"], list), f"{path}: headers must be an array")
        require(isinstance(item["rows"], list), f"{path}: rows must be an array")
        if item.get("annotation_status") == "table_region_with_manual_header_row_summary":
            require(item["headers"], f"{path}: manually summarized table must include headers")
            require("cell_coordinates_status" in item, f"{path}: table missing cell_coordinates_status")
    return len(tables)


def validate_facts(policy_dir: Path, page_count: int) -> tuple[int, dict[str, int]]:
    path = policy_dir / "facts.json"
    facts = load_json(path)
    require(isinstance(facts, list), f"{path}: must be an array")
    concepts = [fact.get("concept") for fact in facts]
    require(set(concepts) == EXPECTED_CONCEPTS, f"{path}: fact concepts do not match expected 20 concepts")
    require(len(concepts) == len(set(concepts)), f"{path}: duplicate fact concepts")

    status_counts = {status: 0 for status in FACT_STATUSES}
    for fact in facts:
        missing = sorted(REQUIRED_FACT_FIELDS - fact.keys())
        require(not missing, f"{path}: fact {fact.get('concept')} missing fields: {missing}")
        status = fact["fact_status"]
        require(status in FACT_STATUSES, f"{path}: invalid fact_status {status}")
        status_counts[status] += 1
        require(fact["extraction_method"] == "manual", f"{path}: extraction_method must be manual")
        require(fact["pipeline_run_id"], f"{path}: pipeline_run_id is required")
        require(isinstance(fact["source_document"], dict), f"{path}: source_document must be object")
        require("human_review_priority" in fact, f"{path}: {fact['concept']} missing human_review_priority")
        quality_passes = fact.get("quality_passes")
        require(isinstance(quality_passes, list) and quality_passes, f"{path}: {fact['concept']} missing quality_passes")
        quality_pass_ids = {p.get("pass_id") for p in quality_passes if isinstance(p, dict)}
        require(
            "pass_3_fact_precision_review" in quality_pass_ids,
            f"{path}: {fact['concept']} missing pass_3_fact_precision_review",
        )

        if fact["evidence_page"] is not None:
            validate_page_ref(path, "evidence_page", fact["evidence_page"], page_count)
        additional_evidence = fact.get("additional_evidence")
        if additional_evidence is not None:
            require(isinstance(additional_evidence, list), f"{path}: {fact['concept']} additional_evidence must be an array")
            for idx, item in enumerate(additional_evidence):
                require(isinstance(item, dict), f"{path}: {fact['concept']} additional_evidence[{idx}] must be an object")
                validate_page_ref(path, f"{fact['concept']}.additional_evidence[{idx}].page", item.get("page"), page_count)
                require(
                    isinstance(item.get("text"), str) and item["text"].strip(),
                    f"{path}: {fact['concept']} additional_evidence[{idx}] missing text",
                )
        if status in {"present", "explicitly_not_covered"}:
            require(fact["evidence_page"] is not None, f"{path}: {fact['concept']} missing evidence_page")
            require(
                isinstance(fact["evidence_text"], str) and fact["evidence_text"].strip(),
                f"{path}: {fact['concept']} missing evidence_text",
            )
            require(fact["value_json"] is not None or status == "explicitly_not_covered", f"{path}: present fact has null value")
    return len(facts), {k: v for k, v in status_counts.items() if v}


def validate_heading_labels(policy_dir: Path, page_count: int) -> int:
    path = policy_dir / "heading_labels.json"
    labels = load_json(path)
    require(isinstance(labels, list) and labels, f"{path}: must be a non-empty array")
    ids: set[str] = set()
    line_refs: set[tuple[int, str]] = set()
    for item in labels:
        required = {
            "label_id",
            "source_section_id",
            "page",
            "expected_text",
            "label_type",
            "is_visual_heading",
            "line_id",
            "reviewer_note",
        }
        missing = sorted(required - item.keys())
        require(not missing, f"{path}: heading label missing fields: {missing}")
        require(item["label_id"] not in ids, f"{path}: duplicate label_id {item['label_id']}")
        ids.add(item["label_id"])
        validate_page_ref(path, "page", item["page"], page_count)
        require(
            isinstance(item["expected_text"], str) and item["expected_text"].strip(),
            f"{path}: empty expected_text",
        )
        require(item["label_type"] == "visual_heading", f"{path}: label_type must be visual_heading")
        require(item["is_visual_heading"] is True, f"{path}: is_visual_heading must be true")
        require(isinstance(item["line_id"], str) and item["line_id"], f"{path}: line_id is required")
        require(
            item["source_section_id"] is None or isinstance(item["source_section_id"], str),
            f"{path}: source_section_id must be string/null",
        )
        require(
            isinstance(item["reviewer_note"], str) and item["reviewer_note"].strip(),
            f"{path}: reviewer_note is required",
        )
        line_ref = (item["page"], item["line_id"])
        require(line_ref not in line_refs, f"{path}: duplicate page/line_id label {line_ref}")
        line_refs.add(line_ref)
    return len(labels)


def validate_gold_corpus() -> dict[str, Any]:
    require(GOLD_ROOT.exists(), f"gold corpus directory not found: {GOLD_ROOT}")
    policies_dir = GOLD_ROOT / "policies"
    require(policies_dir.exists(), f"policies directory not found: {policies_dir}")

    found = {p.name for p in policies_dir.iterdir() if p.is_dir()}
    require(found == EXPECTED_POLICIES, f"policy folders mismatch: expected {sorted(EXPECTED_POLICIES)}, found {sorted(found)}")

    totals = {
        "policies": 0,
        "json_files": 0,
        "sections": 0,
        "clauses": 0,
        "tables": 0,
        "facts": 0,
        "heading_labels": 0,
        "status_counts": {},
    }

    for policy_name in sorted(EXPECTED_POLICIES):
        policy_dir = policies_dir / policy_name
        files = {p.name for p in policy_dir.iterdir() if p.is_file()}
        require(EXPECTED_FILES <= files, f"{policy_dir}: missing files {sorted(EXPECTED_FILES - files)}")
        metadata = validate_metadata(policy_dir)
        page_count = metadata["page_count"]
        totals["policies"] += 1
        totals["json_files"] += len(EXPECTED_FILES)
        totals["sections"] += validate_sections(policy_dir, page_count)
        totals["clauses"] += validate_clauses(policy_dir, page_count)
        totals["tables"] += validate_tables(policy_dir, page_count)
        fact_count, status_counts = validate_facts(policy_dir, page_count)
        totals["facts"] += fact_count
        totals["heading_labels"] += validate_heading_labels(policy_dir, page_count)
        for status, count in status_counts.items():
            totals["status_counts"][status] = totals["status_counts"].get(status, 0) + count

    require(totals["policies"] == 5, "expected exactly 5 policies")
    require(totals["json_files"] == 30, "expected exactly 30 policy JSON files")
    require(totals["facts"] == 100, "expected exactly 100 fact annotations")
    require(totals["heading_labels"] >= 25, "expected visual heading labels for every policy")
    require(totals["status_counts"].get("requires_manual_review", 0) == 0, "gold corpus still has requires_manual_review facts")
    return totals


def main() -> int:
    try:
        totals = validate_gold_corpus()
    except ValidationError as exc:
        print(f"Gold corpus validation FAILED: {exc}", file=sys.stderr)
        return 1
    print("Gold corpus validation passed.")
    print(json.dumps(totals, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
