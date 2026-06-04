#!/usr/bin/env python3
"""Generate DSE-020 scale triage reports from manifest, progress, DB, and exports."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


FAILURE_CATEGORIES = {
    "identity_data_issue",
    "parser_fix",
    "extractor_fix",
    "table_fix",
    "storage_source_span_fix",
    "export_fix",
    "human_review",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for root, _, files in os.walk(path):
        for name in files:
            try:
                total += (Path(root) / name).stat().st_size
            except OSError:
                continue
    return total


def _load_progress(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {"policy_results": {}}
    return _read_json(path)


def _load_parser_target_overrides(path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
    if path is None or not path.is_file():
        return {}
    payload = _read_json(path)
    overrides = {}
    for override in payload.get("overrides", []):
        if override.get("parser_target") is False:
            slug = override.get("slug")
            if slug:
                overrides[slug] = override
    return overrides


def _db_counts(db_path: Path) -> Dict[str, Any]:
    if not db_path.is_file():
        return {"exists": False}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    tables = [
        "source_documents",
        "document_lines",
        "document_sections",
        "policy_clauses",
        "source_spans",
        "document_tables",
        "document_table_cells",
        "extracted_fact_candidates",
        "extracted_facts",
        "derived_policy_features",
    ]
    counts = {}
    for table in tables:
        try:
            counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except sqlite3.Error:
            counts[table] = None
    fk_violations = len(conn.execute("PRAGMA foreign_key_check").fetchall())
    conn.close()
    return {
        "exists": True,
        "path": str(db_path),
        "size_bytes": db_path.stat().st_size,
        "size_mb": round(db_path.stat().st_size / 1024 / 1024, 2),
        "table_counts": counts,
        "foreign_key_violations": fk_violations,
    }


def _export_stats(export_root: Path) -> Dict[str, Any]:
    from derived.field_mapping import CONCEPT_FIELD_MAP

    field_to_concept = {mapping["field"]: concept for concept, mapping in CONCEPT_FIELD_MAP.items()}
    if not export_root.is_dir():
        return {
            "exists": False,
            "exported_policy_count": 0,
            "not_found_by_concept": {},
            "fill_rates": [],
        }
    not_found = Counter()
    fill_rates = []
    exported = 0
    for feature_path in sorted(export_root.glob("*/policy_features.json")):
        exported += 1
        payload = _read_json(feature_path)
        features = payload.get("features", {})
        resolved = 0
        for field_name, feature in features.items():
            concept = field_to_concept.get(field_name, field_name)
            status = feature.get("fact_status")
            if status == "not_found":
                not_found[concept] += 1
            elif status in {"present", "explicitly_not_covered"}:
                resolved += 1
        total = len(features) or 1
        fill_rates.append(
            {
                "policy_id": payload.get("policy_id", feature_path.parent.name),
                "resolved": resolved,
                "total": len(features),
                "fill_rate": round(resolved / total, 4),
            }
        )
    return {
        "exists": True,
        "exported_policy_count": exported,
        "not_found_by_concept": dict(not_found.most_common()),
        "fill_rates": fill_rates,
    }


def _stage_failure_category(stage: str, stage_result: Dict[str, Any]) -> str:
    if stage_result.get("classification_candidate") in FAILURE_CATEGORIES:
        return stage_result["classification_candidate"]
    if stage in {"physical", "heading", "section"}:
        return "parser_fix"
    if stage == "tables":
        return "table_fix"
    if stage == "facts":
        return "extractor_fix"
    return "human_review"


def _analyze_progress(
    manifest: Dict[str, Any],
    progress: Dict[str, Any],
    output_root: Path,
    parser_target_overrides: Dict[str, Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    manifest_by_slug = {policy["slug"]: policy for policy in manifest.get("policies", [])}
    results = progress.get("policy_results", {})
    parser_target_overrides = parser_target_overrides or {}

    per_stage = defaultdict(lambda: {"ok": 0, "failed": 0})
    failure_by_category = Counter()
    failure_by_insurer = Counter()
    failure_by_exception = Counter()
    zero_headings = []
    zero_clauses = []
    zero_facts = []
    table_failures = []
    excluded_parser_targets = []

    for slug, result in results.items():
        policy = manifest_by_slug.get(slug, {})
        insurer = policy.get("insurer", "unknown")
        parser_override = parser_target_overrides.get(slug)
        parser_excluded = parser_override is not None
        if parser_excluded:
            excluded_parser_targets.append(
                {
                    "slug": slug,
                    "file_path": parser_override.get("file_path") or policy.get("file_path"),
                    "file_hash": parser_override.get("file_hash") or policy.get("file_hash"),
                    "reason_code": parser_override.get("reason_code"),
                    "classification": parser_override.get("classification"),
                    "reviewer_note": parser_override.get("reviewer_note"),
                }
            )
        for stage_result in result.get("stages", []):
            stage = stage_result.get("stage")
            status = stage_result.get("status")
            per_stage[stage][status] += 1
            if status != "ok":
                category = _stage_failure_category(stage, stage_result)
                failure_by_category[category] += 1
                failure_by_insurer[insurer] += 1
                failure_by_exception[stage_result.get("error", "unknown")] += 1
                if stage == "tables":
                    table_failures.append(slug)

        heading_path = output_root / "logical" / slug / "heading_candidates.json"
        if heading_path.is_file():
            heading = _read_json(heading_path)
            if heading.get("total_headings", 0) == 0 and not parser_excluded:
                zero_headings.append(slug)

        section_path = output_root / "logical" / slug / "section_tree.json"
        if section_path.is_file():
            section = _read_json(section_path)
            if section.get("total_clauses", 0) == 0 and not parser_excluded:
                zero_clauses.append(slug)

        facts_path = output_root / "facts" / slug / "fact_candidates.json"
        if facts_path.is_file():
            facts = _read_json(facts_path)
            if len(facts) == 0:
                zero_facts.append(slug)

    return {
        "attempted_count": len(results),
        "skipped_count": sum(1 for result in results.values() if result.get("status") == "skipped"),
        "completed_all_per_policy_stages": sum(
            1 for result in results.values() if result.get("status") == "ok"
        ),
        "per_stage": dict(per_stage),
        "failure_by_category": dict(failure_by_category.most_common()),
        "failure_by_insurer": dict(failure_by_insurer.most_common()),
        "failure_by_exception": dict(failure_by_exception.most_common(20)),
        "zero_headings": zero_headings,
        "zero_clauses": zero_clauses,
        "zero_facts": zero_facts,
        "table_failures": table_failures,
        "excluded_parser_targets": excluded_parser_targets,
    }


def _recommend_fixes(progress_analysis: Dict[str, Any], exports: Dict[str, Any], db: Dict[str, Any]) -> List[str]:
    recommendations = []
    if progress_analysis["zero_clauses"]:
        recommendations.append(
            f"Fix parser/section-tree failures for {len(progress_analysis['zero_clauses'])} policies with zero clauses."
        )
    if progress_analysis["zero_headings"]:
        recommendations.append(
            f"Audit heading scorer for {len(progress_analysis['zero_headings'])} policies with zero headings."
        )
    if progress_analysis["zero_facts"]:
        recommendations.append(
            f"Audit extractor recall/parser inputs for {len(progress_analysis['zero_facts'])} policies with zero candidates."
        )
    if exports.get("not_found_by_concept"):
        concept, count = next(iter(exports["not_found_by_concept"].items()))
        recommendations.append(f"Prioritize extractor/LLM strategy for top not_found concept `{concept}` ({count}).")
    if db.get("foreign_key_violations"):
        recommendations.append(f"Fix SQLite FK integrity: {db['foreign_key_violations']} violations.")
    while len(recommendations) < 5:
        recommendations.append("Continue full-corpus run and classify the next largest failure cluster.")
    return recommendations[:5]


def _markdown_report(report: Dict[str, Any]) -> str:
    metrics = report["metrics"]
    lines = [
        "# DSE-020 Scale Triage Report",
        "",
        f"Date: {report['date']}",
        f"Manifest policies: {metrics['manifest_policy_count']}",
        f"Attempted: {metrics['attempted_count']}",
        f"Per-policy completed: {metrics['completed_all_per_policy_stages']}",
        f"Exports: {metrics['exported_policy_count']}",
        f"DB size MB: {metrics['db'].get('size_mb')}",
        "",
        "## Per-Stage Counts",
        "",
        "```json",
        json.dumps(metrics["per_stage"], indent=2),
        "```",
        "",
        "## Top Not Found Concepts",
        "",
        "```json",
        json.dumps(metrics["not_found_by_concept"], indent=2),
        "```",
        "",
        "## Structural Warnings",
        "",
        f"- Zero headings: {len(metrics['zero_headings'])}",
        f"- Zero clauses: {len(metrics['zero_clauses'])}",
        f"- Excluded parser targets: {len(metrics.get('excluded_parser_targets', []))}",
        f"- Zero fact candidates: {len(metrics['zero_facts'])}",
        "",
        "## Top Recommended Fixes",
        "",
    ]
    lines.extend(f"{idx}. {text}" for idx, text in enumerate(report["top_recommended_fixes"], start=1))
    lines.append("")
    return "\n".join(lines)


def build_report(args: argparse.Namespace) -> Dict[str, Any]:
    manifest = _read_json(args.manifest)
    progress = _load_progress(args.progress_summary)
    parser_target_overrides = _load_parser_target_overrides(
        getattr(args, "parser_target_overrides", None)
    )
    progress_analysis = _analyze_progress(
        manifest, progress, args.output_root, parser_target_overrides
    )
    db = _db_counts(args.db)
    exports = _export_stats(args.export_root)
    output_size = _directory_size(args.output_root)
    export_size = _directory_size(args.export_root)

    metrics = {
        "manifest_policy_count": len(manifest.get("policies", [])),
        **progress_analysis,
        "exported_policy_count": exports["exported_policy_count"],
        "not_found_by_concept": exports["not_found_by_concept"],
        "fill_rates": exports["fill_rates"],
        "db": db,
        "output_size_bytes": output_size,
        "output_size_mb": round(output_size / 1024 / 1024, 2),
        "export_size_bytes": export_size,
        "export_size_mb": round(export_size / 1024 / 1024, 2),
    }
    return {
        "schema_version": "dse020_scale_triage_report.v1",
        "task_id": "DSE-020",
        "date": args.date,
        "inputs": {
            "manifest": str(args.manifest),
            "progress_summary": str(args.progress_summary),
            "output_root": str(args.output_root),
            "db": str(args.db),
            "export_root": str(args.export_root),
            "parser_target_overrides": (
                str(args.parser_target_overrides)
                if getattr(args, "parser_target_overrides", None)
                else None
            ),
        },
        "metrics": metrics,
        "top_recommended_fixes": _recommend_fixes(progress_analysis, exports, db),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate DSE-020 scale triage report")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--progress-summary", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("data/interim/dse020"))
    parser.add_argument("--db", type=Path, default=Path("data/engine_dse020.sqlite"))
    parser.add_argument("--export-root", type=Path, default=Path("data/export/dse020"))
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--md-output", type=Path, required=True)
    parser.add_argument("--parser-target-overrides", type=Path)
    parser.add_argument("--date", default="2026-06-03")
    args = parser.parse_args()

    report = build_report(args)
    _write_json(args.json_output, report)
    _write_text(args.md_output, _markdown_report(report))
    print(f"Wrote {args.json_output}")
    print(f"Wrote {args.md_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
