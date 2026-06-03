"""
Validate Source Spans — DSE-010

Structural integrity checks for the clause store (data/engine.sqlite)
and resolved facts (data/interim/facts_resolved/).

Checks:
  1. All 5 source_documents present
  2. Zero dangling FKs
  3. Zero resolved facts with 'clause:' provisional evidence_span_id
  4. SQLite row counts match source JSON line/section/clause counts
  5. char_end > char_start for all spans with non-null char offsets
  6. page_regions_json is valid JSON array with at least 1 element per span
  7. All fact_evidence spans have non-null char_start and char_end
  8. source_spans do not cross document boundaries
  9. Every resolved present fact points to an existing source_span

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
from typing import Dict, List, Optional, Tuple

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

_EXPECTED_POLICY_COUNT = None  # Derived dynamically from gold_corpus at runtime


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


def check_source_documents(conn: sqlite3.Connection, expected_count: int) -> int:
    count = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
    require(
        count == expected_count,
        f"Expected {expected_count} source_documents, found {count}",
    )
    return count


def _load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect_source_counts(
    gold_corpus: str, physical_root: str, logical_root: str
) -> Dict[str, dict]:
    """Collect expected per-document row counts from source artifacts."""
    policies_dir = os.path.join(gold_corpus, "policies")
    counts: Dict[str, dict] = {}
    for slug in sorted(os.listdir(policies_dir)):
        meta_path = os.path.join(policies_dir, slug, "metadata.json")
        physical_path = os.path.join(physical_root, slug, "document_physical.json")
        logical_path = os.path.join(logical_root, slug, "section_tree.json")
        if not os.path.isfile(meta_path):
            continue
        if not os.path.isfile(physical_path):
            raise ValidationError(f"Missing physical artifact for {slug}: {physical_path}")
        if not os.path.isfile(logical_path):
            raise ValidationError(f"Missing logical artifact for {slug}: {logical_path}")
        physical = _load_json(physical_path)
        logical = _load_json(logical_path)
        document_id = physical["document_id"]
        counts[document_id] = {
            "slug": slug,
            "lines": sum(len(page.get("lines", [])) for page in physical.get("pages", [])),
            "sections": len(logical.get("sections", [])),
            "clauses": len(logical.get("clauses", [])),
        }
    return counts


def collect_source_counts_from_manifest(
    manifest_path: str,
    physical_root: str,
    logical_root: str,
    slugs_filter: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> Dict[str, dict]:
    """Collect expected source row counts for manifest-driven DSE-020 runs."""
    manifest = _load_json(manifest_path)
    policies = [p for p in manifest.get("policies", []) if not p.get("skip_reason")]
    if slugs_filter:
        wanted = set(slugs_filter)
        policies = [p for p in policies if p.get("slug") in wanted]
    if limit is not None:
        policies = policies[:limit]

    counts: Dict[str, dict] = {}
    for policy in policies:
        slug = policy["slug"]
        physical_path = os.path.join(physical_root, slug, "document_physical.json")
        logical_path = os.path.join(logical_root, slug, "section_tree.json")
        if not os.path.isfile(physical_path):
            raise ValidationError(f"Missing physical artifact for {slug}: {physical_path}")
        if not os.path.isfile(logical_path):
            raise ValidationError(f"Missing logical artifact for {slug}: {logical_path}")
        physical = _load_json(physical_path)
        logical = _load_json(logical_path)
        document_id = physical["document_id"]
        counts[document_id] = {
            "slug": slug,
            "lines": sum(len(page.get("lines", [])) for page in physical.get("pages", [])),
            "sections": len(logical.get("sections", [])),
            "clauses": len(logical.get("clauses", [])),
        }
    return counts


def check_source_count_parity(
    conn: sqlite3.Connection, expected: Dict[str, dict]
) -> Dict[str, dict]:
    """Check DB rows equal source artifact rows globally and per document."""
    actual: Dict[str, dict] = {}
    for document_id in expected:
        actual[document_id] = {
            "lines": conn.execute(
                "SELECT COUNT(*) FROM document_lines WHERE document_id = ?", (document_id,)
            ).fetchone()[0],
            "sections": conn.execute(
                "SELECT COUNT(*) FROM document_sections WHERE document_id = ?", (document_id,)
            ).fetchone()[0],
            "clauses": conn.execute(
                "SELECT COUNT(*) FROM policy_clauses WHERE document_id = ?", (document_id,)
            ).fetchone()[0],
        }

    failures = []
    for document_id, exp in expected.items():
        got = actual[document_id]
        for key in ("lines", "sections", "clauses"):
            if got[key] != exp[key]:
                failures.append(
                    f"{exp['slug']} {key}: db={got[key]} source={exp[key]} document_id={document_id}"
                )

    require(
        not failures,
        "Source artifact count parity failed: " + "; ".join(failures[:10]),
    )
    return {
        "expected_totals": {
            "lines": sum(v["lines"] for v in expected.values()),
            "sections": sum(v["sections"] for v in expected.values()),
            "clauses": sum(v["clauses"] for v in expected.values()),
        },
        "actual_totals": {
            "lines": sum(v["lines"] for v in actual.values()),
            "sections": sum(v["sections"] for v in actual.values()),
            "clauses": sum(v["clauses"] for v in actual.values()),
        },
        "per_document": actual,
    }


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


def check_source_span_document_consistency(conn: sqlite3.Connection) -> Tuple[int, int]:
    """Every linked source_span must point to a clause/table cell in the same document."""
    bad_clause = conn.execute(
        """SELECT s.span_id, s.document_id AS span_document_id, c.document_id AS clause_document_id
           FROM source_spans s
           LEFT JOIN policy_clauses c ON c.clause_id = s.clause_id
           WHERE s.clause_id IS NOT NULL
             AND (c.clause_id IS NULL OR c.document_id != s.document_id)"""
    ).fetchall()
    bad_cell = conn.execute(
        """SELECT s.span_id, s.document_id AS span_document_id, t.document_id AS table_document_id
           FROM source_spans s
           LEFT JOIN document_table_cells cell ON cell.cell_id = s.table_cell_id
           LEFT JOIN document_tables t ON t.table_id = cell.table_id
           WHERE s.table_cell_id IS NOT NULL
             AND (cell.cell_id IS NULL OR t.document_id != s.document_id)"""
    ).fetchall()
    require(
        len(bad_clause) == 0 and len(bad_cell) == 0,
        "Found source_spans linked across documents or to missing parents: "
        f"clause={[dict(r) for r in bad_clause[:3]]}, "
        f"table_cell={[dict(r) for r in bad_cell[:3]]}",
    )
    return len(bad_clause), len(bad_cell)


def check_resolved_fact_spans_exist(conn: sqlite3.Connection, facts_root: str) -> Tuple[int, int]:
    """Every present resolved fact evidence_span_id must exist and match its document/clause UID."""
    total_present = 0
    bad = []
    for slug in sorted(os.listdir(facts_root)):
        path = os.path.join(facts_root, slug, "accepted_facts.json")
        if not os.path.isfile(path):
            raise ValidationError(f"Resolved facts missing for {slug}: {path}")
        facts = _load_json(path)
        for fact in facts:
            if fact.get("fact_status") != "present":
                continue
            total_present += 1
            span_id = fact.get("evidence_span_id")
            row = conn.execute(
                "SELECT span_id, document_id, clause_id, text FROM source_spans WHERE span_id = ?",
                (span_id,),
            ).fetchone()
            if row is None:
                bad.append(f"{slug}:{fact.get('concept')} missing span {span_id}")
                continue
            if (
                fact.get("evidence_document_id")
                and fact["evidence_document_id"] != row["document_id"]
            ):
                bad.append(f"{slug}:{fact.get('concept')} evidence_document_id mismatch")
            if fact.get("evidence_clause_uid") and fact["evidence_clause_uid"] != row["clause_id"]:
                bad.append(f"{slug}:{fact.get('concept')} evidence_clause_uid mismatch")
            evidence_text = fact.get("evidence_text") or ""
            if evidence_text and evidence_text != row["text"]:
                bad.append(f"{slug}:{fact.get('concept')} evidence_text mismatch")
    require(
        not bad,
        "Resolved fact span validation failed: " + "; ".join(bad[:10]),
    )
    return total_present, len(bad)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Source Spans — DSE-010")
    parser.add_argument("--db", default="data/engine.sqlite")
    parser.add_argument("--facts-root", default="data/interim/facts_resolved")
    parser.add_argument("--gold-corpus", default="gold_corpus")
    parser.add_argument(
        "--manifest", help="Optional DSE-020 manifest; overrides gold-corpus policy discovery"
    )
    parser.add_argument("--physical-root", default="data/interim/physical")
    parser.add_argument("--logical-root", default="data/interim/logical")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--slug", action="append")
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

    if args.manifest:
        expected_counts = collect_source_counts_from_manifest(
            args.manifest,
            args.physical_root,
            args.logical_root,
            slugs_filter=args.slug,
            limit=args.limit,
        )
        manifest = _load_json(args.manifest)
        total_entries = len([p for p in manifest.get("policies", []) if not p.get("skip_reason")])
        unique_docs = len(expected_counts)
        if unique_docs < total_entries:
            print(
                f"  NOTE: manifest has {total_entries} entries but {unique_docs} unique document_ids "
                f"({total_entries - unique_docs} entries share document hashes)"
            )
    else:
        expected_counts = collect_source_counts(
            args.gold_corpus, args.physical_root, args.logical_root
        )
    expected_policy_count = len(expected_counts)
    print(f"  Expected source_documents: {expected_policy_count}")

    checks = [
        ("source_documents_count", lambda: check_source_documents(conn, expected_policy_count)),
        ("foreign_key_violations", lambda: check_foreign_keys(conn)),
        ("source_artifact_count_parity", lambda: check_source_count_parity(conn, expected_counts)),
        ("span_char_offsets_valid", lambda: check_span_char_offsets(conn)),
        ("page_regions_json_valid", lambda: check_page_regions_json(conn)),
        ("fact_evidence_spans_have_offsets", lambda: check_fact_evidence_spans_have_offsets(conn)),
        ("source_span_document_consistency", lambda: check_source_span_document_consistency(conn)),
    ]
    if os.path.isdir(args.facts_root):
        checks.insert(
            2,
            (
                "no_provisional_ids_in_resolved_facts",
                lambda: check_no_provisional_ids_in_resolved(args.facts_root),
            ),
        )
        checks.append(
            (
                "resolved_fact_spans_exist",
                lambda: check_resolved_fact_spans_exist(conn, args.facts_root),
            )
        )
    else:
        print(f"  FAIL  facts_root_exists: missing directory {args.facts_root}")
        return 1

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
