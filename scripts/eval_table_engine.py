#!/usr/bin/env python3
"""
Eval Table Engine — DSE-009.

This eval intentionally separates "page has any detected table" from "gold table
matched by type/content". The first is useful diagnostics; the second is the gate.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
_PRIORITY_TYPES = {"waiting_period", "schedule_of_benefits"}
_MATCH_SCORE_THRESHOLD = 0.35
_BBOX_IOU_THRESHOLD = 0.70

_LEGACY_TABLE_DISPOSITIONS = {
    "care_health_care_plus_table_001": ("prose_summary_not_table", "Waiting period summary is clause prose, not a physical cell grid."),
    "care_health_care_plus_table_002": ("prose_summary_not_table", "Room-rent schedule dependency is prose/schedule reference, not a physical table on the labelled page."),
    "care_health_care_plus_table_003": ("deferred_needs_pdf_review", "Premium region exists but cells were not annotated in DSE-003."),
    "care_health_care_plus_table_004": ("deferred_needs_pdf_review", "Claims-documents region requires physical bbox/header review."),
    "care_health_care_plus_table_005": ("physical_table_eval", "Mapped to network-list physical label."),
    "hdfc_arogya_sanjeevani_table_001": ("prose_summary_not_table", "Room-rent/SOB values are prose/product-summary facts, not the physical table on page 24."),
    "hdfc_arogya_sanjeevani_table_002": ("prose_summary_not_table", "Waiting-period definition is prose; no reliable physical table cells."),
    "hdfc_arogya_sanjeevani_table_003": ("prose_summary_not_table", "Room-rent value is prose/fact summary."),
    "hdfc_arogya_sanjeevani_table_004": ("deferred_needs_pdf_review", "Premium/product-summary table not part of priority physical gate."),
    "hdfc_arogya_sanjeevani_table_005": ("physical_table_eval", "Mapped to claim timeline physical table."),
    "hdfc_arogya_sanjeevani_table_006": ("wrong_page_or_wrong_type", "Legacy network-list label points to page content that is not a network-list physical table."),
    "icici_family_shield_table_001": ("prose_summary_not_table", "Waiting period is a policy wording fact, not a physical table."),
    "icici_family_shield_table_002": ("deferred_needs_pdf_review", "Policy certificate/premium-like page needs separate physical schedule review."),
    "icici_family_shield_table_003": ("deferred_needs_pdf_review", "Claims-documents region requires physical bbox/header review."),
    "icici_family_shield_table_004": ("wrong_page_or_wrong_type", "Legacy network-list label is not a network-list physical table."),
    "new_india_floater_table_001": ("prose_summary_not_table", "Waiting period is prose/definition content, not a physical waiting-period table."),
    "new_india_floater_table_002": ("prose_summary_not_table", "Room-rent fact is extracted from benefit-clause prose/table rows, not a legacy room-rent table."),
    "new_india_floater_table_003": ("physical_table_eval", "Mapped to premium retention physical table."),
    "new_india_floater_table_004": ("deferred_needs_pdf_review", "Claims-documents region requires physical bbox/header review."),
    "new_india_floater_table_005": ("wrong_page_or_wrong_type", "Legacy network-list label points to non-network-list page content."),
    "star_medi_classic_accident_table_001": ("prose_summary_not_table", "SOB facts are embedded in policy summary/prose, not a clean physical SOB grid."),
    "star_medi_classic_accident_table_002": ("prose_summary_not_table", "Waiting-period facts are prose; page 2 physical table is policy-summary/coverage index."),
    "star_medi_classic_accident_table_003": ("prose_summary_not_table", "Room-rent fact is prose/scope text, not a physical room-rent grid."),
    "star_medi_classic_accident_table_004": ("physical_table_eval", "Mapped to premium retention physical table."),
    "star_medi_classic_accident_table_005": ("deferred_needs_pdf_review", "Claims-documents label needs source/bbox review."),
    "star_medi_classic_accident_table_006": ("wrong_page_or_wrong_type", "Legacy network-list label points to non-network-list page content."),
}


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_gold_tables(gold_corpus: str, slug: str) -> List[dict]:
    path = os.path.join(gold_corpus, "policies", slug, "tables.json")
    if not os.path.isfile(path):
        return []
    return _load_json(path)


def _load_physical_table_labels(gold_corpus: str, slug: str) -> List[dict]:
    path = os.path.join(gold_corpus, "policies", slug, "physical_table_labels.json")
    if not os.path.isfile(path):
        return []
    return _load_json(path)


def _load_extracted_doc(tables_root: str, slug: str) -> dict:
    path = os.path.join(tables_root, slug, "document_tables.json")
    if not os.path.isfile(path):
        return {}
    return _load_json(path)


def _load_extracted_cells(tables_root: str, slug: str) -> List[dict]:
    path = os.path.join(tables_root, slug, "document_table_cells.json")
    if not os.path.isfile(path):
        return []
    return _load_json(path)


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        return f"unknown: {exc}"
    return result.stdout.strip()


def _tokens(text: str) -> List[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", (text or "").lower())
        if len(token) > 2 or token.isdigit()
    ]


def _table_text(table: dict, all_cells: List[dict]) -> str:
    parts = []
    for cell in all_cells:
        if cell.get("table_id") == table.get("table_id"):
            parts.append(cell.get("text", ""))
    for line in table.get("raw_lines", []):
        parts.append(line.get("text", ""))
    return " ".join(parts)


def _gold_text(gold_table: dict) -> str:
    parts = list(gold_table.get("headers") or [])
    for row in gold_table.get("rows") or []:
        parts.extend(str(item) for item in row)
    if not parts:
        parts.append(gold_table.get("table_type", ""))
    return " ".join(parts)


def _token_overlap(gold_text: str, extracted_text: str) -> float:
    gold_tokens = set(_tokens(gold_text))
    if not gold_tokens:
        return 0.0
    extracted_tokens = set(_tokens(extracted_text))
    if not extracted_tokens:
        return 0.0
    return len(gold_tokens & extracted_tokens) / len(gold_tokens)


def _bbox_iou(a: Optional[List[float]], b: Optional[List[float]]) -> float:
    if not a or not b or len(a) != 4 or len(b) != 4:
        return 0.0
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    intersection = (x1 - x0) * (y1 - y0)
    area_a = max(0.0, (a[2] - a[0]) * (a[3] - a[1]))
    area_b = max(0.0, (b[2] - b[0]) * (b[3] - b[1]))
    union = area_a + area_b - intersection
    return intersection / union if union else 0.0


def _header_lineage(gold_table: dict, matched_table: Optional[dict], all_cells: List[dict]) -> dict:
    gold_headers = gold_table.get("headers") or []
    if not matched_table:
        return {
            "required": bool(gold_headers),
            "passed": not gold_headers,
            "gold_headers": gold_headers,
            "extracted_headers": [],
            "match_rate": None,
            "note": "no matched table",
        }
    header_cells = [
        cell.get("text", "")
        for cell in all_cells
        if cell.get("table_id") == matched_table.get("table_id") and cell.get("is_header")
    ]
    if not header_cells:
        header_cells = matched_table.get("column_headers", [])
    if not gold_headers:
        return {
            "required": False,
            "passed": True,
            "gold_headers": [],
            "extracted_headers": header_cells,
            "match_rate": None,
            "note": "gold headers not annotated",
        }
    match_rate = _token_overlap(" ".join(gold_headers), " ".join(header_cells))
    return {
        "required": True,
        "passed": match_rate >= 0.5,
        "gold_headers": gold_headers,
        "extracted_headers": header_cells,
        "match_rate": round(match_rate, 4),
        "note": "header tokens matched" if match_rate >= 0.5 else "header tokens missing",
    }


def _cell_accuracy(gold_table: dict, matched_table: Optional[dict], all_cells: List[dict]) -> dict:
    gold_rows = gold_table.get("rows") or []
    if not gold_rows:
        return {"required": False, "row_match_rate": None, "rows_matched": 0, "rows_total": 0}
    if not matched_table:
        return {"required": True, "row_match_rate": 0.0, "rows_matched": 0, "rows_total": len(gold_rows)}
    table_text = _table_text(matched_table, all_cells)
    matched = 0
    for row in gold_rows:
        if _token_overlap(" ".join(str(item) for item in row), table_text) >= 0.35:
            matched += 1
    return {
        "required": True,
        "row_match_rate": round(matched / len(gold_rows), 4),
        "rows_matched": matched,
        "rows_total": len(gold_rows),
    }


def _score_candidate(gold_table: dict, table: dict, all_cells: List[dict]) -> dict:
    extracted_text = _table_text(table, all_cells)
    signature_overlap = _token_overlap(_gold_text(gold_table), extracted_text)
    type_ok = table.get("table_type") == gold_table.get("table_type")
    method = table.get("extraction_method")
    bbox_iou = _bbox_iou(gold_table.get("bbox"), table.get("bbox"))
    structured_bonus = 0.1 if method in {"pdfplumber_lattice", "pdfplumber_text"} and table.get("cells") else 0.0
    score = (0.55 * bbox_iou) + (0.20 if type_ok else 0.0) + (0.20 * signature_overlap) + structured_bonus
    return {
        "table": table,
        "score": round(score, 4),
        "type_ok": type_ok,
        "signature_overlap": round(signature_overlap, 4),
        "bbox_iou": round(bbox_iou, 4),
        "structured_match": method in {"pdfplumber_lattice", "pdfplumber_text"} and bool(table.get("cells")),
    }


def _match_gold_to_extracted(
    gold_table: dict,
    extracted_tables: List[dict],
    all_cells: List[dict],
    used_table_ids: Optional[set[str]] = None,
) -> dict:
    used_table_ids = used_table_ids or set()
    on_page = [
        table
        for table in extracted_tables
        if table.get("page") == gold_table.get("page") and table.get("table_id") not in used_table_ids
    ]
    if not on_page:
        return {
            "page_region_detected": False,
            "detected": False,
            "type_ok": False,
            "matched_table": None,
            "match_score": 0.0,
            "signature_overlap": 0.0,
            "bbox_iou": 0.0,
            "match_reason": "no_extracted_table_on_gold_page",
        }

    scored = [_score_candidate(gold_table, table, all_cells) for table in on_page]
    scored.sort(key=lambda item: item["score"], reverse=True)
    best = scored[0]
    detected = (
        best["bbox_iou"] >= _BBOX_IOU_THRESHOLD
        or best["score"] >= _MATCH_SCORE_THRESHOLD
    ) and (
        best["type_ok"] or best["signature_overlap"] >= 0.25
    )
    return {
        "page_region_detected": True,
        "detected": detected,
        "type_ok": best["type_ok"] if detected else False,
        "matched_table": best["table"] if detected else best["table"],
        "match_score": best["score"],
        "signature_overlap": best["signature_overlap"],
        "bbox_iou": best["bbox_iou"],
        "match_reason": "bbox_type_or_signature_match" if detected else "same_page_without_type_or_content_match",
    }


def _unrecorded_missing_cell_bbox_count(extracted_tables: List[dict], all_cells: List[dict]) -> int:
    issues_by_table = {
        table.get("table_id"): table.get("issues", [])
        for table in extracted_tables
    }
    count = 0
    for cell in all_cells:
        if cell.get("bbox") is not None:
            continue
        issues = issues_by_table.get(cell.get("table_id"), [])
        if not any(str(issue).startswith("cell_bbox_missing:") for issue in issues):
            count += 1
    return count


def evaluate_policy(slug: str, gold_corpus: str, tables_root: str) -> dict:
    gold_tables = _load_physical_table_labels(gold_corpus, slug)
    doc = _load_extracted_doc(tables_root, slug)
    all_cells = _load_extracted_cells(tables_root, slug)

    if not gold_tables:
        return {"slug": slug, "status": "no_gold_tables", "tables": []}
    if not doc:
        return {"slug": slug, "status": "no_extracted_output", "tables": []}

    extracted_tables = doc.get("tables", [])
    table_results = []
    missing_cell_bbox_tables = [
        table
        for table in extracted_tables
        if any(issue.startswith("cell_bbox_missing:") for issue in table.get("issues", []))
    ]
    unrecorded_missing_cell_bboxes = _unrecorded_missing_cell_bbox_count(extracted_tables, all_cells)

    used_table_ids: set[str] = set()
    for gold_table in gold_tables:
        match = _match_gold_to_extracted(gold_table, extracted_tables, all_cells, used_table_ids)
        matched_table = match["matched_table"]
        if match["detected"] and matched_table:
            used_table_ids.add(matched_table["table_id"])
        header_lineage = _header_lineage(gold_table, matched_table if match["detected"] else None, all_cells)
        cell_accuracy = _cell_accuracy(gold_table, matched_table if match["detected"] else None, all_cells)
        result = {
            "table_id": gold_table["label_id"],
            "source_table_id": gold_table["source_table_id"],
            "gold_page": gold_table["page"],
            "gold_type": gold_table["table_type"],
            "gold_annotation_status": "physical_table_label",
            "is_priority": bool(gold_table.get("priority")),
            "page_region_detected": match["page_region_detected"],
            "detected": match["detected"],
            "type_ok": match["type_ok"],
            "match_score": match["match_score"],
            "signature_overlap": match["signature_overlap"],
            "bbox_iou": match["bbox_iou"],
            "match_reason": match["match_reason"],
            "extracted_table_id": matched_table.get("table_id") if matched_table else None,
            "extracted_type": matched_table.get("table_type") if matched_table else None,
            "extraction_method": matched_table.get("extraction_method") if matched_table else None,
            "extracted_bbox": matched_table.get("bbox") if matched_table else None,
            "header_lineage": header_lineage,
            "cell_accuracy": cell_accuracy,
        }
        table_results.append(result)

    total = len(table_results)
    detected_count = sum(1 for row in table_results if row["detected"])
    page_region_detected_count = sum(1 for row in table_results if row["page_region_detected"])
    type_ok_count = sum(1 for row in table_results if row["type_ok"])
    priority_tables = [row for row in table_results if row["is_priority"]]
    priority_detected = sum(1 for row in priority_tables if row["detected"])
    priority_page_region_detected = sum(1 for row in priority_tables if row["page_region_detected"])
    priority_type_ok = sum(1 for row in priority_tables if row["type_ok"])
    header_required = [row for row in table_results if row["header_lineage"]["required"]]
    header_passed = sum(1 for row in header_required if row["header_lineage"]["passed"])

    return {
        "slug": slug,
        "status": "ok",
        "policy_metrics": {
            "total_gold_tables": total,
            "detected": detected_count,
            "detection_recall": round(detected_count / total, 4) if total else 0,
            "page_region_detected": page_region_detected_count,
            "page_region_recall": round(page_region_detected_count / total, 4) if total else 0,
            "type_ok": type_ok_count,
            "type_accuracy": round(type_ok_count / detected_count, 4) if detected_count else 0,
            "priority_total": len(priority_tables),
            "priority_detected": priority_detected,
            "priority_detection_recall": round(priority_detected / len(priority_tables), 4)
            if priority_tables
            else 0,
            "priority_page_region_detected": priority_page_region_detected,
            "priority_page_region_recall": round(priority_page_region_detected / len(priority_tables), 4)
            if priority_tables
            else 0,
            "priority_type_ok": priority_type_ok,
            "header_required": len(header_required),
            "header_passed": header_passed,
            "header_lineage_pass_rate": round(header_passed / len(header_required), 4)
            if header_required
            else 1.0,
            "structured_tables_extracted": doc.get("structured_tables", 0),
            "candidate_tables_extracted": doc.get("candidate_tables", 0),
            "total_tables_extracted": doc.get("tables_found", 0),
            "tables_with_missing_cell_bboxes": len(missing_cell_bbox_tables),
            "unrecorded_missing_cell_bboxes": unrecorded_missing_cell_bboxes,
            "false_positive_tables": max(0, len(extracted_tables) - detected_count),
        },
        "tables": table_results,
    }


def _write_json(path: str, payload: Any) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def _build_bbox_review(policy_results: List[dict]) -> List[dict]:
    rows = []
    for policy in policy_results:
        for row in policy.get("tables", []):
            rows.append(
                {
                    "policy_slug": policy["slug"],
                    "gold_table_id": row["table_id"],
                    "gold_page": row["gold_page"],
                    "gold_type": row["gold_type"],
                    "predicted_table_id": row["extracted_table_id"] if row["detected"] else None,
                    "predicted_type": row["extracted_type"] if row["detected"] else None,
                    "extraction_method": row["extraction_method"] if row["detected"] else None,
                    "predicted_bbox": row["extracted_bbox"] if row["detected"] else None,
                    "match_score": row["match_score"],
                    "signature_overlap": row["signature_overlap"],
                    "bbox_iou": row["bbox_iou"],
                    "needs_manual_review": not row["detected"] or not row["type_ok"],
                    "notes": row["match_reason"],
                }
            )
    return rows


def _build_legacy_source_review(gold_corpus: str) -> List[dict]:
    rows = []
    policies_dir = os.path.join(gold_corpus, "policies")
    for slug in sorted(os.listdir(policies_dir)):
        metadata_path = os.path.join(policies_dir, slug, "metadata.json")
        if not os.path.isfile(metadata_path):
            continue
        for table in _load_gold_tables(gold_corpus, slug):
            disposition, reason = _LEGACY_TABLE_DISPOSITIONS.get(
                table["table_id"],
                ("deferred_needs_pdf_review", "No explicit disposition recorded."),
            )
            rows.append(
                {
                    "policy_slug": slug,
                    "legacy_table_id": table["table_id"],
                    "legacy_page": table["page"],
                    "legacy_type": table["table_type"],
                    "classification": disposition,
                    "reason": reason,
                }
            )
    return rows


def _write_source_review_markdown(path: str, rows: List[dict]) -> None:
    lines = [
        "# DSE-009 Gold Table Source Review",
        "",
        "This report classifies legacy DSE-003 `tables.json` rows for the DSE-009 physical table gate.",
        "",
        "| Policy | Legacy table | Page | Type | Classification | Reason |",
        "|---|---|---:|---|---|---|",
    ]
    for row in rows:
        reason = row["reason"].replace("|", "/")
        lines.append(
            f"| {row['policy_slug']} | {row['legacy_table_id']} | {row['legacy_page']} | "
            f"{row['legacy_type']} | {row['classification']} | {reason} |"
        )
    _write_text(path, "\n".join(lines) + "\n")


def _write_text(path: str, payload: str) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(payload)


def _build_header_review(policy_results: List[dict]) -> List[dict]:
    rows = []
    for policy in policy_results:
        for row in policy.get("tables", []):
            if not row["header_lineage"]["required"]:
                continue
            rows.append(
                {
                    "policy_slug": policy["slug"],
                    "gold_table_id": row["table_id"],
                    "gold_headers": row["header_lineage"]["gold_headers"],
                    "extracted_table_id": row["extracted_table_id"] if row["detected"] else None,
                    "extracted_headers": row["header_lineage"]["extracted_headers"],
                    "passed": row["header_lineage"]["passed"],
                    "match_rate": row["header_lineage"]["match_rate"],
                    "note": row["header_lineage"]["note"],
                }
            )
    return rows


def _build_gold_annotation_audit(policy_results: List[dict]) -> List[dict]:
    rows = []
    for policy in policy_results:
        for row in policy.get("tables", []):
            if row["detected"] and row["type_ok"] and row["header_lineage"]["passed"]:
                continue
            review_reason = []
            if not row["page_region_detected"]:
                review_reason.append("no_physical_table_or_candidate_on_gold_page")
            elif not row["detected"]:
                review_reason.append("same_page_table_without_gold_content_signature")
            if row["detected"] and not row["type_ok"]:
                review_reason.append("matched_content_but_type_disagrees")
            if row["header_lineage"]["required"] and not row["header_lineage"]["passed"]:
                review_reason.append("gold_headers_not_preserved_in_extracted_header_cells")
            rows.append(
                {
                    "policy_slug": policy["slug"],
                    "gold_table_id": row["table_id"],
                    "gold_page": row["gold_page"],
                    "gold_type": row["gold_type"],
                    "gold_annotation_status": row["gold_annotation_status"],
                    "is_priority": row["is_priority"],
                    "page_region_detected": row["page_region_detected"],
                    "content_detected": row["detected"],
                    "type_ok": row["type_ok"],
                    "header_lineage_passed": row["header_lineage"]["passed"],
                    "review_reason": review_reason,
                    "recommended_action": (
                        "source_pdf_manual_review_before_hard_gate"
                        if row["gold_annotation_status"]
                        == "table_region_with_manual_header_row_summary"
                        else "inspect_extractor_or_gold_bbox_in_dse012"
                    ),
                }
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Eval Table Engine — DSE-009")
    parser.add_argument("--gold-corpus", default="gold_corpus", help="Gold corpus directory")
    parser.add_argument("--tables-root", default="data/interim/tables")
    parser.add_argument(
        "--output",
        default=f"runs/evals/{time.strftime('%Y-%m-%d')}-table-engine-dse009-v3.json",
    )
    parser.add_argument("--report-dir", default="data/reports")
    args = parser.parse_args()

    policies_dir = os.path.join(args.gold_corpus, "policies")
    if not os.path.isdir(policies_dir):
        print(f"ERROR: gold corpus policies dir not found: {policies_dir}", file=sys.stderr)
        return 1

    policy_results = []
    for slug in sorted(os.listdir(policies_dir)):
        if not os.path.isfile(os.path.join(policies_dir, slug, "metadata.json")):
            continue
        try:
            policy_results.append(evaluate_policy(slug, args.gold_corpus, args.tables_root))
        except Exception as exc:
            print(f"ERROR evaluating {slug}: {exc}", file=sys.stderr)
            policy_results.append({"slug": slug, "status": "eval_error", "error": str(exc), "tables": []})

    all_rows = [row for policy in policy_results for row in policy.get("tables", [])]
    priority_rows = [row for row in all_rows if row["is_priority"]]
    header_rows = [row for row in all_rows if row["header_lineage"]["required"]]
    total_gold = len(all_rows)
    total_detected = sum(1 for row in all_rows if row["detected"])
    page_region_detected = sum(1 for row in all_rows if row["page_region_detected"])
    type_ok = sum(1 for row in all_rows if row["type_ok"])
    priority_detected = sum(1 for row in priority_rows if row["detected"])
    priority_page_region_detected = sum(1 for row in priority_rows if row["page_region_detected"])
    priority_type_ok = sum(1 for row in priority_rows if row["type_ok"])
    header_passed = sum(1 for row in header_rows if row["header_lineage"]["passed"])
    missing_cell_bbox_tables = sum(
        policy.get("policy_metrics", {}).get("tables_with_missing_cell_bboxes", 0)
        for policy in policy_results
    )
    unrecorded_missing_cell_bboxes = sum(
        policy.get("policy_metrics", {}).get("unrecorded_missing_cell_bboxes", 0)
        for policy in policy_results
    )
    false_positive_tables = sum(
        policy.get("policy_metrics", {}).get("false_positive_tables", 0)
        for policy in policy_results
    )
    legacy_source_review = _build_legacy_source_review(args.gold_corpus)
    undocumented_legacy_rows = [
        row for row in legacy_source_review if row["classification"] == "deferred_needs_pdf_review" and row["reason"] == "No explicit disposition recorded."
    ]

    priority_detection_recall = round(priority_detected / len(priority_rows), 4) if priority_rows else 0
    priority_page_region_recall = (
        round(priority_page_region_detected / len(priority_rows), 4) if priority_rows else 0
    )
    header_lineage_pass_rate = round(header_passed / len(header_rows), 4) if header_rows else 1.0
    type_accuracy = round(type_ok / total_detected, 4) if total_detected else 0

    failures = []
    if len([p for p in policy_results if p.get("status") == "ok"]) != 5:
        failures.append("not_all_5_policies_evaluated")
    if len(priority_rows) == 0:
        failures.append("no_priority_physical_table_labels")
    if priority_detection_recall < 0.85:
        failures.append("priority_content_detection_recall_below_85pct")
    if header_lineage_pass_rate < 0.85:
        failures.append("header_lineage_pass_rate_below_85pct")
    if type_accuracy < 0.80:
        failures.append("type_accuracy_below_80pct")
    if unrecorded_missing_cell_bboxes != 0:
        failures.append("unrecorded_missing_cell_bboxes")
    if undocumented_legacy_rows:
        failures.append("legacy_gold_rows_without_disposition")

    result_doc = {
        "eval_name": "table-engine-dse009-v3",
        "date": time.strftime("%Y-%m-%d"),
        "task_id": "DSE-009",
        "git_commit": _git_commit(),
        "input_manifest": "gold_corpus physical_table_labels.json (5 policies)",
        "hard_gates": {
            "policies_evaluated_target": 5,
            "policies_evaluated_actual": len([p for p in policy_results if p.get("status") == "ok"]),
            "priority_physical_detection_recall_target": 0.85,
            "priority_physical_detection_recall_actual": priority_detection_recall,
            "header_lineage_pass_rate_target": 0.85,
            "header_lineage_pass_rate_actual": header_lineage_pass_rate,
            "type_accuracy_target": 0.80,
            "type_accuracy_actual": type_accuracy,
            "unrecorded_missing_cell_bboxes_target": 0,
            "unrecorded_missing_cell_bboxes_actual": unrecorded_missing_cell_bboxes,
            "legacy_gold_rows_without_disposition_target": 0,
            "legacy_gold_rows_without_disposition_actual": len(undocumented_legacy_rows),
        },
        "metrics": {
            "total_physical_table_labels": total_gold,
            "total_detected": total_detected,
            "physical_table_detection_recall_all": round(total_detected / total_gold, 4)
            if total_gold
            else 0,
            "page_region_detected": page_region_detected,
            "page_region_recall_all": round(page_region_detected / total_gold, 4)
            if total_gold
            else 0,
            "type_accuracy_on_content_detected": type_accuracy,
            "priority_physical_tables_total": len(priority_rows),
            "priority_physical_tables_detected": priority_detected,
            "priority_physical_detection_recall": priority_detection_recall,
            "priority_page_region_detected": priority_page_region_detected,
            "priority_page_region_recall": priority_page_region_recall,
            "priority_type_accuracy": round(priority_type_ok / len(priority_rows), 4)
            if priority_rows
            else 0,
            "header_lineage_required": len(header_rows),
            "header_lineage_passed": header_passed,
            "header_lineage_pass_rate": header_lineage_pass_rate,
            "tables_with_missing_cell_bboxes_recorded": missing_cell_bbox_tables,
            "unrecorded_missing_cell_bboxes": unrecorded_missing_cell_bboxes,
            "false_positive_tables": false_positive_tables,
            "legacy_gold_rows_documented": len(legacy_source_review),
        },
        "per_policy": {
            policy["slug"]: policy.get("policy_metrics", {})
            for policy in policy_results
            if policy.get("status") == "ok"
        },
        "policies": policy_results,
        "passed": not failures,
        "failures": failures,
        "notes": (
            "v3 evaluates DSE-009 physical_table_labels.json only. Legacy semantic tables.json "
            "rows are documented in the source review and excluded from hard gates."
        ),
        "known_limitations": [
            "Legacy DSE-003 tables.json still includes conceptual/non-physical table summaries.",
            "text_alignment_candidate tables preserve raw lines and cells=[] when split is unreliable.",
            "Physical labels cover the initial 5-policy gold set; DSE-012 should expand and review more bboxes.",
            "parent_clause_id assignment remains provisional until DSE-010 bbox/source-span overlap.",
        ],
    }

    _write_json(args.output, result_doc)
    _write_json(
        os.path.join(args.report_dir, "dse009_table_bbox_review_candidates.json"),
        _build_bbox_review(policy_results),
    )
    _write_json(
        os.path.join(args.report_dir, "dse009_header_lineage_review.json"),
        _build_header_review(policy_results),
    )
    _write_json(
        os.path.join(args.report_dir, "dse009_gold_table_annotation_audit.json"),
        _build_gold_annotation_audit(policy_results),
    )
    _write_json(
        os.path.join(args.report_dir, "dse009_gold_table_source_review.json"),
        legacy_source_review,
    )
    _write_source_review_markdown(
        os.path.join(args.report_dir, "dse009_gold_table_source_review.md"),
        legacy_source_review,
    )

    print(json.dumps({"passed": result_doc["passed"], "metrics": result_doc["metrics"], "failures": failures}, indent=2))
    return 0 if result_doc["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
