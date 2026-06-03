"""
Run Export — DSE-013

Batch CLI: read from data/engine.sqlite, produce policy_features.json,
policy_fact_sources.json, and policy_clauses_minimal.json per policy
under data/export/{policy_id}/.

Also persists each export to the derived_policy_features SQLite table.

Usage:
  PYTHONPATH=. python scripts/run_export.py \\
    --db data/engine.sqlite \\
    --output-root data/export

Exit 0 if all policies exported and validated. Exit 1 on validation failure.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import subprocess
import sys
import time
from typing import Any

from clause_store.repository import init_db, insert_pipeline_run, update_pipeline_run_finished
from clause_store.models import PipelineRun
from derived.export_builder import (
    build_policy_clauses_minimal,
    build_policy_fact_sources,
    build_policy_features,
)
from derived.schema_validator import validate_policy_features

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("run_export")

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _git_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(_PROJECT_ROOT),
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Derived Export — DSE-013")
    parser.add_argument("--db", default="data/engine.sqlite")
    parser.add_argument("--output-root", default="data/export")
    parser.add_argument("--pipeline-run-id")
    parser.add_argument("--summary-output", default="data/reports/dse013_export_summary.json")
    args = parser.parse_args()

    if not os.path.isfile(args.db):
        logger.error("Database not found: %s", args.db)
        return 1

    pipeline_run_id = args.pipeline_run_id or f"dse013_v1_{int(time.time())}"
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S")

    conn = init_db(args.db)
    insert_pipeline_run(conn, PipelineRun(id=pipeline_run_id, started_at=started_at))

    # Get all source documents
    docs = conn.execute(
        "SELECT document_id, policy_id FROM source_documents ORDER BY policy_id"
    ).fetchall()

    results = []
    had_failure = False

    for doc in docs:
        document_id = doc["document_id"]
        policy_id = doc["policy_id"]
        logger.info("Exporting %s", policy_id)

        try:
            # Build all 3 files
            features = build_policy_features(conn, document_id, policy_id, pipeline_run_id)
            fact_sources = build_policy_fact_sources(conn, document_id, policy_id, pipeline_run_id)
            clauses_minimal = build_policy_clauses_minimal(conn, document_id, policy_id)

            # Validate features
            errors = validate_policy_features(features)
            if errors:
                logger.error("  %s: VALIDATION FAILED: %s", policy_id, errors)
                had_failure = True
                results.append(
                    {"policy_id": policy_id, "status": "validation_failed", "errors": errors}
                )
                continue

            # Write to export directory
            out_dir = os.path.join(args.output_root, policy_id)
            _write_json(os.path.join(out_dir, "policy_features.json"), features)
            _write_json(os.path.join(out_dir, "policy_fact_sources.json"), fact_sources)
            _write_json(os.path.join(out_dir, "policy_clauses_minimal.json"), clauses_minimal)

            # Persist to derived_policy_features table
            conn.execute(
                """INSERT OR REPLACE INTO derived_policy_features
                   (id, document_id, pipeline_run_id, feature_json,
                    feature_schema_version, created_at, export_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"{document_id}:export_v1",
                    document_id,
                    pipeline_run_id,
                    json.dumps(features, ensure_ascii=False),
                    "1.0",
                    time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "exported",
                ),
            )
            conn.commit()

            pq = features["parse_quality"]
            logger.info(
                "  %s: %d resolved, %d not_found, fill_rate=%.0f%%",
                policy_id,
                pq["concepts_resolved"],
                pq["concepts_not_found"],
                pq["overall_fill_rate"] * 100,
            )
            results.append(
                {
                    "policy_id": policy_id,
                    "status": "ok",
                    "concepts_resolved": pq["concepts_resolved"],
                    "concepts_not_found": pq["concepts_not_found"],
                    "fill_rate": pq["overall_fill_rate"],
                    "validation_errors": 0,
                }
            )

        except Exception as exc:
            logger.exception("FATAL error exporting %s: %s", policy_id, exc)
            results.append({"policy_id": policy_id, "status": "fatal_error", "error": str(exc)})
            had_failure = True

    finished_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    success_count = sum(1 for r in results if r["status"] == "ok")
    update_pipeline_run_finished(
        conn,
        pipeline_run_id,
        "completed" if not had_failure else "partial_failure",
        finished_at,
        success_count,
        len(docs) - success_count,
    )
    conn.close()

    # Write summary
    summary = {
        "pipeline_run_id": pipeline_run_id,
        "git_commit": _git_commit(),
        "date": time.strftime("%Y-%m-%d"),
        "output_root": args.output_root,
        "policies_exported": success_count,
        "policies_total": len(docs),
        "policy_results": results,
    }
    _write_json(args.summary_output, summary)
    logger.info("Summary written to %s", args.summary_output)
    logger.info("Done: %d/%d policies exported", success_count, len(docs))

    return 1 if had_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
