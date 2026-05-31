"""
Eval Clause Store — DSE-010

Hard-gate evaluation and metric computation for the clause store and source spans.

Hard gates (any failure blocks merge):
  1. policies_ingested == 5
  2. dangling_fk_count == 0
  3. unresolved_present_facts == 0
  4. clauses_with_spans / total_clauses >= 0.95
  5. no_provisional_ids_in_resolved_facts == 0
  6. db_size_bytes < 30MB

Reported-only (not blocking):
  - tables with bbox-resolved parent_clause_id
  - avg_iou of resolved parent clauses
  - span char_offset coverage
  - cross-page clause count

Usage:
  PYTHONPATH=. python scripts/eval_clause_store.py \\
    --db data/engine.sqlite \\
    --facts-root data/interim/facts_resolved \\
    --gold-corpus gold_corpus \\
    --output runs/evals/2026-05-31-clause-store-dse010-v1.json

Exit 0 if all hard gates pass. Exit 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sqlite3
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
_DB_SIZE_LIMIT_BYTES = 30 * 1024 * 1024  # 30 MB
_SPAN_COVERAGE_TARGET = 0.95


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(_PROJECT_ROOT),
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def _load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def open_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# Gate computations
# ---------------------------------------------------------------------------


def compute_policies_ingested(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]


def compute_dangling_fks(conn: sqlite3.Connection) -> int:
    return len(conn.execute("PRAGMA foreign_key_check").fetchall())


def compute_unresolved_present_facts(facts_root: str) -> Tuple[int, int]:
    """Returns (total_present, unresolved_present)."""
    if not os.path.isdir(facts_root):
        return 0, 0
    total_present = 0
    unresolved = 0
    for slug in os.listdir(facts_root):
        path = os.path.join(facts_root, slug, "accepted_facts.json")
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            facts = json.load(f)
        for fact in facts:
            if fact.get("fact_status") == "present":
                total_present += 1
                ev_id = fact.get("evidence_span_id") or ""
                if ev_id.startswith("clause:") or not ev_id:
                    unresolved += 1
    return total_present, unresolved


def compute_span_coverage(conn: sqlite3.Connection) -> Tuple[int, int, float]:
    """Returns (clauses_with_spans, total_clauses, coverage_rate)."""
    total_clauses = conn.execute("SELECT COUNT(*) FROM policy_clauses").fetchone()[0]
    clauses_with_spans = conn.execute(
        """SELECT COUNT(DISTINCT clause_id) FROM source_spans
           WHERE span_type = 'clause_body' AND clause_id IS NOT NULL"""
    ).fetchone()[0]
    rate = clauses_with_spans / total_clauses if total_clauses else 0.0
    return clauses_with_spans, total_clauses, round(rate, 4)


def compute_no_provisional_in_resolved(facts_root: str) -> int:
    """Returns count of resolved facts with provisional 'clause:' evidence_span_id."""
    if not os.path.isdir(facts_root):
        return 0
    count = 0
    for slug in os.listdir(facts_root):
        path = os.path.join(facts_root, slug, "accepted_facts.json")
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            facts = json.load(f)
        for fact in facts:
            ev_id = fact.get("evidence_span_id") or ""
            if ev_id.startswith("clause:"):
                count += 1
    return count


def compute_db_size(db_path: str) -> int:
    return pathlib.Path(db_path).stat().st_size


# ---------------------------------------------------------------------------
# Reported-only metrics
# ---------------------------------------------------------------------------


def compute_table_parent_clause_metrics(conn: sqlite3.Connection) -> dict:
    total_tables = conn.execute("SELECT COUNT(*) FROM document_tables").fetchone()[0]
    tables_with_parent = conn.execute(
        "SELECT COUNT(*) FROM document_tables WHERE parent_clause_id IS NOT NULL"
    ).fetchone()[0]
    tables_with_confidence = conn.execute(
        "SELECT parent_clause_confidence FROM document_tables WHERE parent_clause_confidence IS NOT NULL"
    ).fetchall()
    avg_iou = (
        sum(r[0] for r in tables_with_confidence) / len(tables_with_confidence)
        if tables_with_confidence
        else 0.0
    )
    return {
        "total_tables": total_tables,
        "tables_with_bbox_resolved_parent": tables_with_parent,
        "tables_pct_resolved": round(tables_with_parent / total_tables, 4) if total_tables else 0,
        "avg_iou_resolved_parents": round(avg_iou, 4),
    }


def compute_span_char_coverage(conn: sqlite3.Connection) -> dict:
    total_spans = conn.execute("SELECT COUNT(*) FROM source_spans").fetchone()[0]
    spans_with_offsets = conn.execute(
        "SELECT COUNT(*) FROM source_spans WHERE char_start IS NOT NULL"
    ).fetchone()[0]
    return {
        "total_source_spans": total_spans,
        "spans_with_char_offsets": spans_with_offsets,
        "char_offset_coverage_rate": round(spans_with_offsets / total_spans, 4)
        if total_spans
        else 0,
    }


def compute_cross_page_clause_metrics(conn: sqlite3.Connection) -> dict:
    cross_page_clauses = conn.execute(
        "SELECT COUNT(*) FROM policy_clauses WHERE page_end > page_start"
    ).fetchone()[0]
    total_clauses = conn.execute("SELECT COUNT(*) FROM policy_clauses").fetchone()[0]
    # Cross-page spans have > 1 page_region
    cross_page_spans = 0
    span_rows = conn.execute(
        "SELECT page_regions_json FROM source_spans WHERE span_type = 'clause_body'"
    ).fetchall()
    for row in span_rows:
        try:
            regions = json.loads(row[0])
            if len(regions) > 1:
                cross_page_spans += 1
        except Exception:
            pass
    return {
        "cross_page_clauses": cross_page_clauses,
        "total_clauses": total_clauses,
        "cross_page_clause_spans": cross_page_spans,
    }


def compute_span_type_distribution(conn: sqlite3.Connection) -> dict:
    rows = conn.execute(
        "SELECT span_type, COUNT(*) c FROM source_spans GROUP BY span_type"
    ).fetchall()
    return {row[0]: row[1] for row in rows}


def compute_evidence_degradation_stats(conn: sqlite3.Connection) -> dict:
    """Count fact_evidence spans by char_start offset (exact match has char_start != 0)."""
    exact = conn.execute(
        """SELECT COUNT(*) FROM source_spans
           WHERE span_type = 'fact_evidence' AND char_start > 0"""
    ).fetchone()[0]
    fallback = conn.execute(
        """SELECT COUNT(*) FROM source_spans
           WHERE span_type = 'fact_evidence' AND char_start = 0"""
    ).fetchone()[0]
    total = exact + fallback
    return {
        "fact_evidence_spans_total": total,
        "evidence_exact_match": exact,
        "evidence_clause_level_precision": fallback,
    }


def compute_row_counts(conn: sqlite3.Connection) -> dict:
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    return {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tables}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Eval Clause Store — DSE-010")
    parser.add_argument("--db", default="data/engine.sqlite")
    parser.add_argument("--facts-root", default="data/interim/facts_resolved")
    parser.add_argument("--gold-corpus", default="gold_corpus")
    parser.add_argument(
        "--output",
        default=f"runs/evals/{time.strftime('%Y-%m-%d')}-clause-store-dse010-v1.json",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.db):
        print(f"ERROR: Database not found: {args.db}", file=sys.stderr)
        return 1

    conn = open_db(args.db)

    # -----------------------------------------------------------------------
    # Gate computations
    # -----------------------------------------------------------------------
    policies_ingested = compute_policies_ingested(conn)
    dangling_fks = compute_dangling_fks(conn)
    total_present, unresolved_present = compute_unresolved_present_facts(args.facts_root)
    clauses_with_spans, total_clauses, span_coverage = compute_span_coverage(conn)
    provisional_in_resolved = compute_no_provisional_in_resolved(args.facts_root)
    db_size_bytes = compute_db_size(args.db)

    # -----------------------------------------------------------------------
    # Reported-only metrics
    # -----------------------------------------------------------------------
    table_parent_metrics = compute_table_parent_clause_metrics(conn)
    char_coverage = compute_span_char_coverage(conn)
    cross_page = compute_cross_page_clause_metrics(conn)
    span_types = compute_span_type_distribution(conn)
    evidence_degradation = compute_evidence_degradation_stats(conn)
    row_counts = compute_row_counts(conn)
    conn.close()

    # -----------------------------------------------------------------------
    # Hard gate evaluation
    # -----------------------------------------------------------------------
    failures = []
    if policies_ingested != 5:
        failures.append(f"policies_ingested={policies_ingested} (expected 5)")
    if dangling_fks != 0:
        failures.append(f"dangling_fk_count={dangling_fks} (expected 0)")
    if unresolved_present != 0:
        failures.append(f"unresolved_present_facts={unresolved_present} (expected 0)")
    if span_coverage < _SPAN_COVERAGE_TARGET:
        failures.append(
            f"clause_span_coverage={span_coverage:.1%} (target >= {_SPAN_COVERAGE_TARGET:.0%})"
        )
    if provisional_in_resolved != 0:
        failures.append(f"provisional_ids_in_resolved={provisional_in_resolved} (expected 0)")
    if db_size_bytes >= _DB_SIZE_LIMIT_BYTES:
        failures.append(f"db_size={db_size_bytes / 1024 / 1024:.1f}MB (limit 30MB)")

    passed = len(failures) == 0

    # -----------------------------------------------------------------------
    # Output
    # -----------------------------------------------------------------------
    result_doc = {
        "eval_name": "clause-store-dse010-v1",
        "date": time.strftime("%Y-%m-%d"),
        "task_id": "DSE-010",
        "git_commit": _git_commit(),
        "hard_gates": {
            "policies_ingested_target": 5,
            "policies_ingested_actual": policies_ingested,
            "dangling_fk_count_target": 0,
            "dangling_fk_count_actual": dangling_fks,
            "unresolved_present_facts_target": 0,
            "unresolved_present_facts_actual": unresolved_present,
            "total_present_facts": total_present,
            "clause_span_coverage_target": _SPAN_COVERAGE_TARGET,
            "clause_span_coverage_actual": span_coverage,
            "provisional_ids_in_resolved_target": 0,
            "provisional_ids_in_resolved_actual": provisional_in_resolved,
            "db_size_limit_bytes": _DB_SIZE_LIMIT_BYTES,
            "db_size_bytes_actual": db_size_bytes,
        },
        "metrics": {
            "clauses_with_spans": clauses_with_spans,
            "total_clauses": total_clauses,
            "clause_span_coverage": span_coverage,
            "span_type_distribution": span_types,
            "table_parent_clause": table_parent_metrics,
            "span_char_offset_coverage": char_coverage,
            "cross_page_clauses": cross_page,
            "evidence_degradation": evidence_degradation,
            "db_size_mb": round(db_size_bytes / 1024 / 1024, 2),
        },
        "table_row_counts": row_counts,
        "passed": passed,
        "failures": failures,
        "notes": (
            "ADR-0017: document_text_spans not populated (char-level spans deferred). "
            "ADR-0018: page_regions_json handles cross-page clauses. "
            "ADR-0019: char_start/char_end are clause-text offsets. "
            "ADR-0020: resolved facts written to data/interim/facts_resolved/ (DSE-007 output unchanged). "
            "Degraded fact evidence char offsets occur when DSE-007 evidence_text boundaries "
            "differ from current clause segmentation — location (clause, page, bbox) is correct."
        ),
        "known_limitations": [
            "document_text_spans not populated (ADR-0017)",
            "One block per page (physical parser limitation)",
            "fact_evidence char offsets may be clause-level (not subspan-level) when evidence_text predates current clause boundaries",
            "parent_clause_id for tables uses bbox IoU threshold 0.10 — tables fully outside any clause bbox retain null",
            "extracted_facts, fact_conflicts, derived_policy_features not populated (DSE-011/013)",
        ],
    }

    _write_json(args.output, result_doc)

    # Print summary
    print(
        json.dumps(
            {
                "passed": passed,
                "hard_gates": result_doc["hard_gates"],
                "metrics": {
                    k: v for k, v in result_doc["metrics"].items() if k != "span_type_distribution"
                },
                "failures": failures,
            },
            indent=2,
        )
    )

    print(f"\nEval artifact written to: {args.output}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
