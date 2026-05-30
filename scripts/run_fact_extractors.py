#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from extractors.models import TARGET_CONCEPTS
from extractors.registry import run_extractors


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def _write_json(path: Path, payload: Dict[str, Any] | List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _section_lookup(section_tree: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        section["section_id"]: section
        for section in section_tree.get("sections", [])
        if section.get("section_id")
    }


def build_extraction_clauses(section_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return clause records enriched with section heading text for DSE-006 title-carried facts."""
    sections = _section_lookup(section_tree)
    enriched: List[Dict[str, Any]] = []
    for clause in section_tree.get("clauses", []):
        section = sections.get(clause.get("section_id"), {})
        title = section.get("title") or ""
        text = clause.get("text") or ""
        heading_line_id = section.get("heading_line_id")
        line_ids = list(clause.get("line_ids") or [])
        if heading_line_id and heading_line_id not in line_ids:
            line_ids = [heading_line_id] + line_ids
        extraction_text = " ".join(part for part in [title, text] if part).strip()
        enriched_clause = dict(clause)
        enriched_clause["text"] = extraction_text or text
        enriched_clause["line_ids"] = line_ids
        enriched_clause["extraction_context"] = {
            "uses_section_heading": bool(title),
            "section_id": clause.get("section_id"),
        }
        enriched.append(enriched_clause)
    return enriched


def process_policy(section_tree_path: Path, output_root: Path) -> Dict[str, Any]:
    section_tree = _read_json(section_tree_path)
    slug = section_tree_path.parent.name
    policy_output = output_root / slug
    pipeline_run_id = section_tree.get("pipeline_run_id") or "unknown_pipeline_run"
    clauses = build_extraction_clauses(section_tree)
    candidates, accepted = run_extractors(clauses, pipeline_run_id)

    _write_json(policy_output / "fact_candidates.json", candidates)
    _write_json(policy_output / "accepted_facts.json", accepted)

    attempted = sorted(fact["concept"] for fact in accepted)
    return {
        "policy_slug": slug,
        "section_tree_path": str(section_tree_path),
        "output_dir": str(policy_output),
        "pipeline_run_id": pipeline_run_id,
        "clauses_scanned": len(clauses),
        "candidate_count": len(candidates),
        "accepted_count": len(accepted),
        "attempted_concepts": attempted,
        "missing_concepts": sorted(set(TARGET_CONCEPTS) - set(attempted)),
        "status_counts": _status_counts(accepted),
    }


def _status_counts(facts: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for fact in facts:
        status = fact.get("fact_status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DSE-007 deterministic fact extractors.")
    parser.add_argument("--section-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--policy", action="append", help="Optional policy slug to process. Can repeat.")
    args = parser.parse_args()

    requested = set(args.policy or [])
    section_paths = sorted(args.section_root.glob("*/section_tree.json"))
    if requested:
        section_paths = [path for path in section_paths if path.parent.name in requested]
        found = {path.parent.name for path in section_paths}
        missing = sorted(requested - found)
        if missing:
            print(f"ERROR: missing section_tree.json for requested policies: {', '.join(missing)}")
            return 2

    if not section_paths:
        print(f"ERROR: no section_tree.json files found under {args.section_root}")
        return 2

    processed = []
    errors = []
    for section_tree_path in section_paths:
        try:
            processed.append(process_policy(section_tree_path, args.output_root))
        except Exception as exc:
            errors.append({"path": str(section_tree_path), "error": str(exc)})

    summary = {
        "schema_version": "dse_fact_extraction_run_summary_v1",
        "task_id": "DSE-007",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "section_root": str(args.section_root),
        "output_root": str(args.output_root),
        "target_concepts": TARGET_CONCEPTS,
        "processed_count": len(processed),
        "error_count": len(errors),
        "processed": processed,
        "errors": errors,
    }
    _write_json(args.output_root / "fact_extraction_run_summary.json", summary)

    if errors:
        print(f"ERROR: fact extraction completed with {len(errors)} error(s)")
        return 1
    print(f"Processed {len(processed)} policies into {args.output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

