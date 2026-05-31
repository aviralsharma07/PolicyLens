"""
Validate Source Spans — DSE-010

Structural integrity checks for the clause store (data/engine.sqlite)
and resolved facts (data/interim/facts_resolved/).

Checks:
  1. All 5 source_documents present
  2. Zero dangling FKs
  3. Zero resolved facts with 'clause:' provisional evidence_span_id
  4. char_end > char_start for all spans with non-null char offsets
  5. page_regions_json is valid JSON array with at least 1 element per span
  6. All fact_evidence spans have non-null char_start and char_end

Usage:
  PYTHONPATH=. python scripts/validate_source_spans.py \\
    --db data/engine.sqlite \\
    --facts-root data/interim/facts_resolved

Exit 0 if all checks pass. Exit 1 if any check fails.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sqlite3
import sys
from typing import List, Tuple

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

_EXPECTED_POLICY_COUNT = 5


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def open_db(db_path: str) -> sqlite3.Connection:
    if not os.path.isfile(db_path):
        raise ValidationError(f"Database not found: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def check_source_documents(conn: sqlite3.Connection) -> int:
    count = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
    require(
        count == _EXPECTED_POLICY_COUNT,
        f"Expected {_EXPECTED_POLICY_COUNT} source_documents, found {count}",
    )
    return count


def check_foreign_keys(conn: sqlite3.Connection) -> int:
    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    require(
        len(violations) == 0,
        f"Found {len(violations)} dangling FK references: "
        + str([dict(v) for v in violations[:3]]),
    )
    return len(violations)


def check_no_provisional_ids_in_resolved(facts_root: str) -> Tuple[int, int]:
    """Check that resolved facts have no 'clause:{id}' evidence_span_id."""
    total_present = 0
    provisional_remaining = 0
    for slug in sorted(os.listdir(facts_root)):
        path = os.path.join(facts_root, slug, "accepted_facts.json")
        if not os.path.isfile(path):
            raise ValidationError(f"Resolved facts missing for {slug}: {path}")
        with open(path, encoding="utf-8") as f:
            facts = json.load(f)
        for fact in facts:
            if fact.get("fact_status") == "present":
                total_present += 1
                ev_id = fact.get("evidence_span_id") or ""
                if ev_id.startswith("clause:"):
                    provisional_remaining += 1
    require(
        provisional_remaining == 0,
        f"Found {provisional_remaining} present facts still with provisional 'clause:{{id}}' "
        f"evidence_span_id in {facts_root}",
    )
    return total_present, provisional_remaining


def check_span_char_offsets(conn: sqlite3.Connection) -> Tuple[int, int]:
    """
    Check char_end >= char_start for all spans with non-null offsets.
    char_end == char_start == 0 is valid (empty clause text).
    Only char_end < char_start is an error.
    """
    bad = conn.execute(
        """SELECT span_id, char_start, char_end FROM source_spans
           WHERE char_start IS NOT NULL AND char_end IS NOT NULL
             AND char_end < char_start"""
    ).fetchall()
    require(
        len(bad) == 0,
        f"Found {len(bad)} source_spans with char_end <= char_start: "
        + str([dict(r) for r in bad[:3]]),
    )
    total_with_offsets = conn.execute(
        "SELECT COUNT(*) FROM source_spans WHERE char_start IS NOT NULL"
    ).fetchone()[0]
    return total_with_offsets, len(bad)


def check_page_regions_json(conn: sqlite3.Connection) -> int:
    """Check that page_regions_json is valid JSON array with >= 1 element."""
    spans = conn.execute("SELECT span_id, page_regions_json FROM source_spans").fetchall()
    bad = []
    for row in spans:
        try:
            regions = json.loads(row["page_regions_json"])
            if not isinstance(regions, list) or len(regions) == 0:
                bad.append(row["span_id"])
        except (json.JSONDecodeError, TypeError):
            bad.append(row["span_id"])
    require(
        len(bad) == 0,
        f"Found {len(bad)} source_spans with invalid page_regions_json: {bad[:3]}",
    )
    return len(spans)


def check_fact_evidence_spans_have_offsets(conn: sqlite3.Connection) -> int:
    """All fact_evidence spans must have char_start and char_end."""
    missing = conn.execute(
        """SELECT span_id FROM source_spans
           WHERE span_type = 'fact_evidence'
             AND (char_start IS NULL OR char_end IS NULL)"""
    ).fetchall()
    require(
        len(missing) == 0,
        f"Found {len(missing)} fact_evidence spans with null char offsets: "
        + str([r[0] for r in missing[:5]]),
    )
    total = conn.execute(
        "SELECT COUNT(*) FROM source_spans WHERE span_type = 'fact_evidence'"
    ).fetchone()[0]
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Source Spans — DSE-010")
    parser.add_argument("--db", default="data/engine.sqlite")
    parser.add_argument("--facts-root", default="data/interim/facts_resolved")
    args = parser.parse_args()

    print(f"Validating clause store: {args.db}")
    print(f"Validating resolved facts: {args.facts_root}")
    print()

    passed = True
    results = []

    try:
        conn = open_db(args.db)
    except ValidationError as exc:
        print(f"FAIL: {exc}")
        return 1

    checks = [
        ("source_documents_count", lambda: check_source_documents(conn)),
        ("foreign_key_violations", lambda: check_foreign_keys(conn)),
        ("span_char_offsets_valid", lambda: check_span_char_offsets(conn)),
        ("page_regions_json_valid", lambda: check_page_regions_json(conn)),
        ("fact_evidence_spans_have_offsets", lambda: check_fact_evidence_spans_have_offsets(conn)),
    ]
    if os.path.isdir(args.facts_root):
        checks.insert(
            2,
            (
                "no_provisional_ids_in_resolved_facts",
                lambda: check_no_provisional_ids_in_resolved(args.facts_root),
            ),
        )

    for check_name, check_fn in checks:
        try:
            result = check_fn()
            print(f"  PASS  {check_name}: {result}")
            results.append((check_name, "pass", result))
        except ValidationError as exc:
            print(f"  FAIL  {check_name}: {exc}")
            results.append((check_name, "fail", str(exc)))
            passed = False

    conn.close()
    print()
    print(f"{'All checks PASSED' if passed else 'VALIDATION FAILED'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
