#!/usr/bin/env python3
"""Run DSE-020 per-policy pipeline stages with resumable progress logging."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Tuple

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


STAGES = ("physical", "heading", "section", "tables", "facts")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _load_summary(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {"policy_results": {}, "events_count": 0}
    return _read_json(path)


def _stage_names(stage: str) -> Tuple[str, ...]:
    if stage == "all":
        return STAGES
    if stage not in STAGES:
        raise ValueError(f"unknown stage: {stage}")
    return (stage,)


def classify_failure(stage: str, error: str) -> str:
    if "pdf not found" in error.lower() or "no such file" in error.lower():
        return "identity_data_issue"
    if stage in {"physical", "heading", "section"}:
        return "parser_fix"
    if stage == "tables":
        return "table_fix"
    if stage == "facts":
        return "extractor_fix"
    return "human_review"


def _build_line_index(pages: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    index = {}
    for page in pages:
        for line in page.get("lines", []):
            lid = line.get("line_id", "")
            if lid:
                index[lid] = line
    return index


def _build_line_to_idx_mapping(pages: List[Dict[str, Any]]) -> Dict[str, int]:
    mapping = {}
    idx = 0
    for page in pages:
        for line in page.get("lines", []):
            lid = line.get("line_id", "")
            if lid:
                mapping[lid] = idx
                idx += 1
    return mapping


def run_physical(policy: Dict[str, Any], pdf_path: Path, output_root: Path, pipeline_run_id: str) -> Dict[str, Any]:
    from pdf_parser.layout_extractor import extract_pdf, save_document

    doc = extract_pdf(str(pdf_path), policy["slug"], pipeline_run_id)
    out_path = save_document(doc, str(output_root / "physical"), policy["slug"])
    return {"output_path": out_path, "page_count": doc.page_count, "line_count": sum(len(p.lines) for p in doc.pages)}


def run_heading(policy: Dict[str, Any], output_root: Path) -> Dict[str, Any]:
    from structure_parser.heading_scorer import HeadingScorer

    slug = policy["slug"]
    physical_path = output_root / "physical" / slug / "document_physical.json"
    doc = _read_json(physical_path)
    result = HeadingScorer().score_document(doc)
    out_path = output_root / "logical" / slug / "heading_candidates.json"
    _write_json(out_path, result)
    return {
        "output_path": str(out_path),
        "total_lines_scored": result.get("total_lines_scored", 0),
        "total_headings": result.get("total_headings", 0),
    }


def run_section(policy: Dict[str, Any], output_root: Path) -> Dict[str, Any]:
    from structure_parser.clause_segmenter import ClauseSegmenter
    from structure_parser.section_tree import SectionTreeBuilder

    slug = policy["slug"]
    physical_path = output_root / "physical" / slug / "document_physical.json"
    heading_path = output_root / "logical" / slug / "heading_candidates.json"
    doc = _read_json(physical_path)
    candidates_data = _read_json(heading_path)
    physical_pages = doc.get("pages", [])
    heading_candidates = candidates_data.get("candidates", [])
    pipeline_run_id = candidates_data.get("config", {}).get("pipeline_run_id") or doc.get(
        "pipeline_run_id", ""
    )

    builder = SectionTreeBuilder(
        heading_candidates=heading_candidates,
        physical_pages=physical_pages,
        policy_id=slug,
        pipeline_run_id=pipeline_run_id,
    )
    result = builder.build()
    segmenter = ClauseSegmenter(
        physical_pages=physical_pages,
        line_index=_build_line_index(physical_pages),
        line_to_idx=_build_line_to_idx_mapping(physical_pages),
    )
    clauses = segmenter.segment_document(result["sections"])

    out_tree = {
        "schema_version": "section_tree.v1",
        "parser_version": "section_tree_builder.v2",
        "document_id": candidates_data.get("document_id") or doc.get("document_id"),
        "policy_id": candidates_data.get("policy_id") or doc.get("policy_id") or slug,
        "pipeline_run_id": pipeline_run_id,
        "config": {
            "heading_threshold": candidates_data.get("config", {}).get("threshold", 0.5),
            "synthetic_detection": "compact_numbered_iterative_v2",
            "clause_segmentation": "numbered_prefix_and_paragraph_gap_v2",
        },
        "source_paths": {
            "physical": str(physical_path),
            "heading_candidates": str(heading_path),
        },
        "issues": [],
        "total_sections": len(result["sections"]),
        "total_clauses": len(clauses),
        "total_visual_headings": sum(1 for s in result["sections"] if s.get("heading_type") == "visual"),
        "total_synthetic_sections": sum(
            1 for s in result["sections"] if str(s.get("heading_type", "")).startswith("synthetic_")
        ),
        "sections": result["sections"],
        "section_tree": result["section_tree"],
        "clauses": clauses,
    }
    out_path = output_root / "logical" / slug / "section_tree.json"
    _write_json(out_path, out_tree)
    return {
        "output_path": str(out_path),
        "total_sections": out_tree["total_sections"],
        "total_clauses": out_tree["total_clauses"],
        "total_visual_headings": out_tree["total_visual_headings"],
    }


def run_tables(policy: Dict[str, Any], pdf_path: Path, output_root: Path, pipeline_run_id: str) -> Dict[str, Any]:
    import pdfplumber
    from table_engine.models import ExtractionMethod, TableDocument, TableType
    from table_engine.table_detector import extract_tables_from_page
    from table_engine.table_type_classifier import classify
    from table_engine.text_alignment_detector import try_page

    slug = policy["slug"]
    physical_path = output_root / "physical" / slug / "document_physical.json"
    phys = _read_json(physical_path)
    document_id = phys.get("document_id", "")
    all_tables = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_num, plumber_page in enumerate(pdf.pages, start=1):
            page_table_counter = 1
            page_tables, page_table_counter = extract_tables_from_page(
                page=plumber_page,
                page_num=page_num,
                policy_id=slug,
                document_id=document_id,
                page_table_counter=page_table_counter,
            )
            if not page_tables:
                phys_lines = []
                for page in phys.get("pages", []):
                    if page.get("page_number") == page_num:
                        phys_lines = [
                            {
                                "line_id": line.get("line_id", ""),
                                "text": line.get("text", ""),
                                "bbox": line.get("bbox", []),
                                "region": line.get("region", "body"),
                            }
                            for line in page.get("lines", [])
                        ]
                        break
                if phys_lines:
                    fallback, page_table_counter = try_page(
                        phys_lines, page_num, slug, document_id, page_table_counter
                    )
                    page_tables.extend(fallback)

            for table in page_tables:
                raw_grid = table.__dict__.get("_raw_grid") or []
                heading_ctx = table.__dict__.get("_heading_context") or ""
                if raw_grid:
                    table_type, confidence = classify(raw_grid, heading_ctx)
                else:
                    table_type, confidence = TableType.unknown, 0.0
                table.table_type = table_type
                table.table_type_confidence = confidence
            all_tables.extend(page_tables)

    structured = sum(1 for table in all_tables if table.extraction_method == ExtractionMethod.pdfplumber_lattice)
    candidates = sum(
        1 for table in all_tables if table.extraction_method == ExtractionMethod.text_alignment_candidate
    )
    table_doc = TableDocument(
        pipeline_run_id=pipeline_run_id,
        document_id=document_id,
        policy_id=slug,
        source_pdf_path=policy.get("file_path", ""),
        page_count=phys.get("page_count", 0),
        tables_found=len(all_tables),
        structured_tables=structured,
        candidate_tables=candidates,
        tables=all_tables,
    )

    out_dir = output_root / "tables" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(out_dir / "document_tables.json", json.loads(table_doc.model_dump_json(exclude_none=True)))
    all_cells = []
    for table in all_tables:
        for cell in table.cells:
            all_cells.append(json.loads(cell.model_dump_json(exclude_none=True)))
    _write_json(out_dir / "document_table_cells.json", all_cells)
    return {
        "output_path": str(out_dir / "document_tables.json"),
        "tables_found": len(all_tables),
        "structured_tables": structured,
        "candidate_tables": candidates,
        "table_cells": len(all_cells),
    }


def run_facts(policy: Dict[str, Any], output_root: Path) -> Dict[str, Any]:
    sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))
    from run_fact_extractors import process_policy

    section_tree_path = output_root / "logical" / policy["slug"] / "section_tree.json"
    result = process_policy(section_tree_path, output_root / "facts")
    return {
        "output_path": str(output_root / "facts" / policy["slug"]),
        "candidate_count": result.get("candidate_count", 0),
        "accepted_count": result.get("accepted_count", 0),
        "status_counts": result.get("status_counts", {}),
    }


def run_stage(
    stage: str,
    policy: Dict[str, Any],
    pdf_path: Path,
    output_root: Path,
    pipeline_run_id: str,
) -> Dict[str, Any]:
    runners: Dict[str, Callable[..., Dict[str, Any]]] = {
        "physical": lambda: run_physical(policy, pdf_path, output_root, pipeline_run_id),
        "heading": lambda: run_heading(policy, output_root),
        "section": lambda: run_section(policy, output_root),
        "tables": lambda: run_tables(policy, pdf_path, output_root, pipeline_run_id),
        "facts": lambda: run_facts(policy, output_root),
    }
    started = time.time()
    try:
        details = runners[stage]()
        return {
            "stage": stage,
            "status": "ok",
            "elapsed_seconds": round(time.time() - started, 3),
            "details": details,
        }
    except Exception as exc:
        error = str(exc)
        return {
            "stage": stage,
            "status": "failed",
            "elapsed_seconds": round(time.time() - started, 3),
            "error": error,
            "traceback_tail": traceback.format_exc()[-1200:],
            "classification_candidate": classify_failure(stage, error),
        }


def filter_policies(policies: List[Dict[str, Any]], args: argparse.Namespace, prior_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    selected = list(policies)
    if args.slug:
        wanted = set(args.slug)
        selected = [policy for policy in selected if policy["slug"] in wanted]
    if args.insurer:
        selected = [policy for policy in selected if policy.get("insurer") == args.insurer]
    if args.start_index is not None:
        selected = selected[args.start_index - 1 :]
    if args.end_index is not None:
        selected = selected[: args.end_index]
    if args.only_failed:
        prior = prior_summary.get("policy_results", {})
        selected = [
            policy
            for policy in selected
            if prior.get(policy["slug"], {}).get("status") not in {"ok", "skipped"}
        ]
    if args.limit is not None:
        selected = selected[: args.limit]
    return selected


def should_skip_for_resume(policy: Dict[str, Any], stages: Tuple[str, ...], prior_summary: Dict[str, Any]) -> bool:
    prior = prior_summary.get("policy_results", {}).get(policy["slug"])
    if not prior:
        return False
    if prior.get("status") != "ok":
        return False
    prior_stages = {stage["stage"]: stage["status"] for stage in prior.get("stages", [])}
    return all(prior_stages.get(stage) == "ok" for stage in stages)


def update_summary(summary_path: Path, summary: Dict[str, Any]) -> None:
    policy_results = summary.get("policy_results", {})
    stage_counts = {
        stage: {
            "ok": sum(1 for result in policy_results.values() for s in result.get("stages", []) if s["stage"] == stage and s["status"] == "ok"),
            "failed": sum(1 for result in policy_results.values() for s in result.get("stages", []) if s["stage"] == stage and s["status"] == "failed"),
        }
        for stage in STAGES
    }
    summary["stage_counts"] = stage_counts
    summary["policies_ok"] = sum(1 for result in policy_results.values() if result.get("status") == "ok")
    summary["policies_failed"] = sum(1 for result in policy_results.values() if result.get("status") == "failed")
    summary["policies_partial"] = sum(1 for result in policy_results.values() if result.get("status") == "partial")
    summary["policies_skipped"] = sum(1 for result in policy_results.values() if result.get("status") == "skipped")
    _write_json_atomic(summary_path, summary)


def main() -> int:
    parser = argparse.ArgumentParser(description="DSE-020 per-policy scale-run batch runner")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--policy-data-root", type=Path, default=Path("../policy_data"))
    parser.add_argument("--output-root", type=Path, default=Path("data/interim/dse020"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--start-index", type=int)
    parser.add_argument("--end-index", type=int)
    parser.add_argument("--slug", action="append")
    parser.add_argument("--insurer")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--only-failed", action="store_true")
    parser.add_argument("--stage", choices=("all",) + STAGES, default="all")
    parser.add_argument("--pipeline-run-id")
    args = parser.parse_args()

    if "dse020" not in str(args.output_root):
        print(f"ERROR: output root must be DSE-020 namespaced: {args.output_root}")
        return 2

    manifest = _read_json(args.manifest)
    policies = manifest.get("policies", [])
    if manifest.get("policy_count") != 647 or len(policies) != 647:
        print(f"ERROR: expected 647 manifest policies, got {len(policies)}")
        return 2
    if len({policy["slug"] for policy in policies}) != len(policies):
        print("ERROR: manifest slugs are not unique")
        return 2

    progress_root = args.output_root / "progress"
    events_path = progress_root / "events.jsonl"
    summary_path = progress_root / "summary.json"
    summary = _load_summary(summary_path)
    summary.setdefault("schema_version", "dse020_progress_summary.v1")
    summary.setdefault("task_id", "DSE-020")
    summary.setdefault("manifest", str(args.manifest))
    summary.setdefault("output_root", str(args.output_root))
    summary.setdefault("policy_results", {})
    summary["free_disk_bytes_at_start"] = shutil.disk_usage(args.output_root.parent if args.output_root.parent.exists() else Path(".")).free

    selected = filter_policies(policies, args, summary)
    stages = _stage_names(args.stage)
    pipeline_run_id = args.pipeline_run_id or f"dse020_{int(time.time())}"

    print(
        f"DSE-020 batch: selected={len(selected)} stage={args.stage} "
        f"output_root={args.output_root}"
    )

    for index, policy in enumerate(selected, start=1):
        slug = policy["slug"]
        policy_start = time.time()
        if args.resume and should_skip_for_resume(policy, stages, summary):
            event = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "slug": slug,
                "status": "skipped",
                "reason": "resume_already_ok",
            }
            _append_jsonl(events_path, event)
            continue

        if policy.get("skip_reason"):
            result = {
                "slug": slug,
                "status": "skipped",
                "skip_reason": policy["skip_reason"],
                "stages": [],
                "elapsed_seconds": 0.0,
            }
            summary["policy_results"][slug] = result
            _append_jsonl(events_path, {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), **result})
            update_summary(summary_path, summary)
            continue

        pdf_path = args.policy_data_root / policy["file_path"]
        if not pdf_path.is_file():
            result = {
                "slug": slug,
                "status": "skipped",
                "skip_reason": "pdf_not_found",
                "stages": [],
                "elapsed_seconds": 0.0,
            }
            summary["policy_results"][slug] = result
            _append_jsonl(events_path, {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), **result})
            update_summary(summary_path, summary)
            continue

        print(f"[{index}/{len(selected)}] {slug}")
        stage_results = []
        for stage in stages:
            stage_result = run_stage(stage, policy, pdf_path, args.output_root, pipeline_run_id)
            stage_results.append(stage_result)
            _append_jsonl(
                events_path,
                {
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "slug": slug,
                    "stage": stage,
                    **stage_result,
                },
            )
            if stage_result["status"] != "ok":
                print(f"  {stage}: failed — {stage_result.get('error')}")
            else:
                print(f"  {stage}: ok")

        ok_count = sum(1 for stage in stage_results if stage["status"] == "ok")
        if ok_count == len(stage_results):
            status = "ok"
        elif ok_count:
            status = "partial"
        else:
            status = "failed"
        summary["policy_results"][slug] = {
            "slug": slug,
            "status": status,
            "stages": stage_results,
            "elapsed_seconds": round(time.time() - policy_start, 3),
        }
        update_summary(summary_path, summary)

    update_summary(summary_path, summary)
    print(f"Progress summary written to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
