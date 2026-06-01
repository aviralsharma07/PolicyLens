"""
Eval Fact Scoring — DSE-011 / DSE-017

Hard-gate evaluation for the fact candidate scoring and conflict resolution layer.

Hard gates (any failure blocks merge):
  1.  policies_evaluated == reviewed gold count (corpus-driven)
  2.  candidate_persistence_parity == 100% (per-document, JSON == SQLite)
  3.  fact_persistence_parity == 100% (per-document, resolved present == SQLite)
  4.  FK violations == 0
  5.  deterministic_precision >= 95% (present facts match gold)
  6.  fact_status_accuracy >= 95% (correct status for 5 concepts × N policies)
  7.  normalized_value_accuracy >= 95% (present fact values match gold)
  8.  evidence_accuracy >= 95% (every present fact has valid evidence_span_id in SQLite)
  9.  false_present_count == 0
  10. conflicts_resolved_or_zero
  11. no_cross_document_fact_links
  12. accepted_candidate_min_score >= 0.85

Usage:
  PYTHONPATH=. python scripts/eval_fact_scoring.py \\
    --db data/engine.sqlite \\
    --candidates-root data/interim/facts \\
    --resolved-root data/interim/facts_resolved \\
    --gold-corpus gold_corpus \\
    --output runs/evals/YYYY-MM-DD-fact-scoring-dse011-v1.json
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
_TARGET_CONCEPTS = [
    "free_look_period",
    "grace_period",
    "ped_waiting_period",
    "initial_waiting_period",
    "co_pay",
]


def _count_reviewed_policies(gold_corpus: str) -> int:
    """Count reviewed policy directories in gold_corpus."""
    policies_dir = os.path.join(gold_corpus, "policies")
    if not os.path.isdir(policies_dir):
        return 0
    return sum(
        1
        for slug in os.listdir(policies_dir)
        if os.path.isfile(os.path.join(policies_dir, slug, "metadata.json"))
    )


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


def _load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _norm_json(obj: Any) -> str:
    if obj is None:
        return "{}"
    if isinstance(obj, str):
        try:
            return json.dumps(json.loads(obj), sort_keys=True, separators=(",", ":"))
        except (json.JSONDecodeError, TypeError):
            return obj
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _json_obj(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except (json.JSONDecodeError, TypeError):
            return obj
    return obj


def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        normalized = {}
        for key, item in sorted(value.items()):
            if key == "components" and isinstance(item, list):
                normalized[key] = sorted(
                    (_canonical(x) for x in item), key=lambda x: json.dumps(x, sort_keys=True)
                )
            else:
                normalized[key] = _canonical(item)
        return normalized
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    return value


def _is_subset_value(expected: Any, actual: Any) -> bool:
    if isinstance(expected, dict) and isinstance(actual, dict):
        return all(key in actual and _is_subset_value(value, actual[key]) for key, value in expected.items())
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return False
        unmatched = list(actual)
        for expected_item in expected:
            match_idx = next(
                (idx for idx, actual_item in enumerate(unmatched) if _is_subset_value(expected_item, actual_item)),
                None,
            )
            if match_idx is None:
                return False
            unmatched.pop(match_idx)
        return True
    return expected == actual


def _values_match(expected: Any, actual: Any) -> bool:
    expected_c = _canonical(_json_obj(expected))
    actual_c = _canonical(_json_obj(actual))
    return expected_c == actual_c or _is_subset_value(expected_c, actual_c)


def open_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# Gate computations
# ---------------------------------------------------------------------------


def compute_candidate_parity(
    conn: sqlite3.Connection,
    candidates_root: str,
    gold_corpus: str,
) -> Tuple[bool, List[dict]]:
    """Per-document: JSON candidate count == SQLite candidate count."""
    details = []
    all_pass = True
    policies_dir = os.path.join(gold_corpus, "policies")
    for slug in sorted(os.listdir(policies_dir)):
        meta_path = os.path.join(policies_dir, slug, "metadata.json")
        if not os.path.isfile(meta_path):
            continue
        physical = _load_json(os.path.join("data/interim/physical", slug, "document_physical.json"))
        doc_id = physical["document_id"]

        json_path = os.path.join(candidates_root, slug, "fact_candidates.json")
        json_count = len(_load_json(json_path)) if os.path.isfile(json_path) else 0

        db_count = conn.execute(
            "SELECT COUNT(*) FROM extracted_fact_candidates WHERE document_id = ?",
            (doc_id,),
        ).fetchone()[0]

        ok = json_count == db_count
        if not ok:
            all_pass = False
        details.append({"slug": slug, "json": json_count, "db": db_count, "ok": ok})
    return all_pass, details


def compute_fact_parity(
    conn: sqlite3.Connection,
    resolved_root: str,
    gold_corpus: str,
) -> Tuple[bool, List[dict]]:
    """Per-document: resolved present fact count == SQLite extracted_facts count."""
    details = []
    all_pass = True
    policies_dir = os.path.join(gold_corpus, "policies")
    for slug in sorted(os.listdir(policies_dir)):
        meta_path = os.path.join(policies_dir, slug, "metadata.json")
        if not os.path.isfile(meta_path):
            continue
        physical = _load_json(os.path.join("data/interim/physical", slug, "document_physical.json"))
        doc_id = physical["document_id"]

        resolved_path = os.path.join(resolved_root, slug, "accepted_facts.json")
        resolved = _load_json(resolved_path) if os.path.isfile(resolved_path) else []
        json_present = sum(
            1
            for f in resolved
            if f.get("fact_status") in ("present", "explicitly_not_covered")
            and f.get("candidate_id")
            and f.get("evidence_clause_id")
        )

        db_count = conn.execute(
            "SELECT COUNT(*) FROM extracted_facts WHERE document_id = ?",
            (doc_id,),
        ).fetchone()[0]

        ok = json_present == db_count
        if not ok:
            all_pass = False
        details.append({"slug": slug, "json_present": json_present, "db": db_count, "ok": ok})
    return all_pass, details


def compute_gold_comparison(
    conn: sqlite3.Connection,
    gold_corpus: str,
) -> dict:
    """Compare extracted facts against gold for the 5 target concepts."""
    total_pairs = 0
    status_correct = 0
    value_correct = 0
    false_present = 0
    false_not_found = 0
    evidence_valid = 0
    evidence_checked = 0
    per_policy = []

    policies_dir = os.path.join(gold_corpus, "policies")
    for slug in sorted(os.listdir(policies_dir)):
        meta_path = os.path.join(policies_dir, slug, "metadata.json")
        if not os.path.isfile(meta_path):
            continue
        physical = _load_json(os.path.join("data/interim/physical", slug, "document_physical.json"))
        doc_id = physical["document_id"]

        gold_facts = _load_json(os.path.join(policies_dir, slug, "facts.json"))
        gold_by_concept = {f["concept"]: f for f in gold_facts}

        db_facts = conn.execute(
            """SELECT concept, fact_status, normalized_value_json, evidence_span_id
               FROM extracted_facts WHERE document_id = ?""",
            (doc_id,),
        ).fetchall()
        db_by_concept = {r["concept"]: dict(r) for r in db_facts}

        policy_results = []
        for concept in _TARGET_CONCEPTS:
            total_pairs += 1
            gold = gold_by_concept.get(concept)
            ext = db_by_concept.get(concept)

            if not gold:
                continue

            g_status = gold["fact_status"]
            e_status = ext["fact_status"] if ext else "not_found"

            status_ok = g_status == e_status
            if status_ok:
                status_correct += 1

            # False present: gold=not_found but extracted=present
            if g_status in ("not_found",) and e_status in ("present", "explicitly_not_covered"):
                false_present += 1

            # False not_found: gold=present but no extracted fact
            if g_status == "present" and not ext:
                false_not_found += 1

            # Value comparison for present facts
            val_ok = None
            if g_status == "present" and ext and e_status == "present":
                val_ok = _values_match(
                    gold.get("normalized_value_json"),
                    ext.get("normalized_value_json"),
                )
                if val_ok:
                    value_correct += 1

            # Evidence validity for present facts
            if ext and e_status == "present":
                evidence_checked += 1
                span_id = ext.get("evidence_span_id")
                if span_id:
                    span_row = conn.execute(
                        "SELECT span_id FROM source_spans WHERE span_id = ?",
                        (span_id,),
                    ).fetchone()
                    if span_row:
                        evidence_valid += 1

            policy_results.append(
                {
                    "concept": concept,
                    "gold_status": g_status,
                    "extracted_status": e_status,
                    "status_ok": status_ok,
                    "value_ok": val_ok,
                }
            )

        per_policy.append({"slug": slug, "results": policy_results})

    present_pairs = sum(
        1
        for p in per_policy
        for r in p["results"]
        if r["gold_status"] == "present" and r["extracted_status"] == "present"
    )

    return {
        "total_concept_policy_pairs": total_pairs,
        "status_correct": status_correct,
        "status_accuracy": round(status_correct / total_pairs, 4) if total_pairs else 0,
        "value_correct": value_correct,
        "value_accuracy": round(value_correct / present_pairs, 4) if present_pairs else 0,
        "false_present": false_present,
        "false_not_found": false_not_found,
        "evidence_checked": evidence_checked,
        "evidence_valid": evidence_valid,
        "evidence_accuracy": round(evidence_valid / evidence_checked, 4) if evidence_checked else 0,
        "per_policy": per_policy,
    }


def compute_cross_document_fact_links(conn: sqlite3.Connection) -> int:
    """Extracted facts must point to clauses in the same document."""
    bad = conn.execute(
        """SELECT COUNT(*)
           FROM extracted_facts f
           JOIN policy_clauses c ON c.clause_id = f.clause_id
           WHERE f.document_id != c.document_id"""
    ).fetchone()[0]
    return bad


def compute_conflicts_status(conn: sqlite3.Connection) -> dict:
    total = conn.execute("SELECT COUNT(*) FROM fact_conflicts").fetchone()[0]
    unresolved = conn.execute(
        "SELECT COUNT(*) FROM fact_conflicts WHERE resolution = 'unresolved'"
    ).fetchone()[0]
    return {"total": total, "unresolved": unresolved}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Eval Fact Scoring — DSE-011")
    parser.add_argument("--db", default="data/engine.sqlite")
    parser.add_argument("--candidates-root", default="data/interim/facts")
    parser.add_argument("--resolved-root", default="data/interim/facts_resolved")
    parser.add_argument("--gold-corpus", default="gold_corpus")
    parser.add_argument(
        "--output",
        default=f"runs/evals/{time.strftime('%Y-%m-%d')}-fact-scoring-dse011-v2.json",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.db):
        print(f"ERROR: DB not found: {args.db}", file=sys.stderr)
        return 1

    conn = open_db(args.db)

    # Gate computations
    cand_parity_ok, cand_parity_detail = compute_candidate_parity(
        conn, args.candidates_root, args.gold_corpus
    )
    fact_parity_ok, fact_parity_detail = compute_fact_parity(
        conn, args.resolved_root, args.gold_corpus
    )
    fk_violations = len(conn.execute("PRAGMA foreign_key_check").fetchall())
    gold_cmp = compute_gold_comparison(conn, args.gold_corpus)
    cross_doc_links = compute_cross_document_fact_links(conn)
    conflicts = compute_conflicts_status(conn)

    policies_evaluated = len(cand_parity_detail)
    total_db_cands = conn.execute("SELECT COUNT(*) FROM extracted_fact_candidates").fetchone()[0]
    total_db_facts = conn.execute("SELECT COUNT(*) FROM extracted_facts").fetchone()[0]

    # Gate 12: accepted candidate minimum composite score
    _min_score_row = conn.execute(
        "SELECT MIN(score) FROM extracted_fact_candidates WHERE accepted = 1"
    ).fetchone()
    accepted_min_score = (
        float(_min_score_row[0]) if _min_score_row and _min_score_row[0] is not None else None
    )

    conn.close()

    # Hard gate evaluation
    expected_policy_count = _count_reviewed_policies(args.gold_corpus)
    failures = []
    if policies_evaluated != expected_policy_count:
        failures.append(
            f"policies_evaluated={policies_evaluated} (expected {expected_policy_count})"
        )
    if not cand_parity_ok:
        failures.append(f"candidate_parity FAIL: {[d for d in cand_parity_detail if not d['ok']]}")
    if not fact_parity_ok:
        failures.append(f"fact_parity FAIL: {[d for d in fact_parity_detail if not d['ok']]}")
    if fk_violations != 0:
        failures.append(f"fk_violations={fk_violations}")
    if gold_cmp["status_accuracy"] < 0.95:
        failures.append(f"fact_status_accuracy={gold_cmp['status_accuracy']:.2%} (target >= 95%)")
    if gold_cmp["value_accuracy"] < 0.95:
        failures.append(
            f"normalized_value_accuracy={gold_cmp['value_accuracy']:.2%} (target >= 95%)"
        )
    if gold_cmp["evidence_accuracy"] < 0.95:
        failures.append(f"evidence_accuracy={gold_cmp['evidence_accuracy']:.2%} (target >= 95%)")
    if gold_cmp["false_present"] != 0:
        failures.append(f"false_present_count={gold_cmp['false_present']}")
    if conflicts["unresolved"] != 0:
        failures.append(f"unresolved_conflicts={conflicts['unresolved']}")
    if cross_doc_links != 0:
        failures.append(f"cross_document_fact_links={cross_doc_links}")
    if accepted_min_score is not None and accepted_min_score < 0.85:
        failures.append(f"accepted_candidate_min_score={accepted_min_score:.4f} (target >= 0.85)")

    passed = len(failures) == 0

    result_doc = {
        "eval_name": "fact-scoring-dse011-v2",
        "date": time.strftime("%Y-%m-%d"),
        "task_id": "DSE-011",
        "git_commit": _git_commit(),
        "hard_gates": {
            "policies_evaluated": policies_evaluated,
            "candidate_persistence_parity": cand_parity_ok,
            "fact_persistence_parity": fact_parity_ok,
            "fk_violations": fk_violations,
            "fact_status_accuracy": gold_cmp["status_accuracy"],
            "normalized_value_accuracy": gold_cmp["value_accuracy"],
            "evidence_accuracy": gold_cmp["evidence_accuracy"],
            "false_present_count": gold_cmp["false_present"],
            "conflicts_total": conflicts["total"],
            "conflicts_unresolved": conflicts["unresolved"],
            "cross_document_fact_links": cross_doc_links,
            "accepted_candidate_min_score": accepted_min_score,
        },
        "metrics": {
            "total_db_candidates": total_db_cands,
            "total_db_facts": total_db_facts,
            "total_concept_policy_pairs": gold_cmp["total_concept_policy_pairs"],
            "status_correct": gold_cmp["status_correct"],
            "value_correct": gold_cmp["value_correct"],
            "evidence_valid": gold_cmp["evidence_valid"],
            "false_not_found": gold_cmp["false_not_found"],
            "candidate_parity": cand_parity_detail,
            "fact_parity": fact_parity_detail,
        },
        "gold_comparison": gold_cmp["per_policy"],
        "passed": passed,
        "failures": failures,
    }

    _write_json(args.output, result_doc)

    # Print summary
    print(f"\n{'=' * 60}")
    print("DSE-011 Fact Scoring Eval")
    print(f"{'=' * 60}")
    print(f"Policies evaluated:          {policies_evaluated}")
    print(f"Total candidates in DB:      {total_db_cands}")
    print(f"Total facts in DB:           {total_db_facts}")
    print(f"Candidate parity:            {'PASS' if cand_parity_ok else 'FAIL'}")
    print(f"Fact parity:                 {'PASS' if fact_parity_ok else 'FAIL'}")
    print(f"FK violations:               {fk_violations}")
    print(
        f"Fact status accuracy:        {gold_cmp['status_accuracy']:.1%} ({gold_cmp['status_correct']}/{gold_cmp['total_concept_policy_pairs']})"
    )
    print(
        f"Normalized value accuracy:   {gold_cmp['value_accuracy']:.1%} ({gold_cmp['value_correct']}/{gold_cmp['evidence_checked']})"
    )
    print(
        f"Evidence accuracy:           {gold_cmp['evidence_accuracy']:.1%} ({gold_cmp['evidence_valid']}/{gold_cmp['evidence_checked']})"
    )
    print(f"False present:               {gold_cmp['false_present']}")
    print(
        f"Conflicts:                   {conflicts['total']} total, {conflicts['unresolved']} unresolved"
    )
    print(f"Cross-document fact links:   {cross_doc_links}")
    print(
        f"Accepted min score:          {accepted_min_score:.4f}"
        if accepted_min_score is not None
        else "Accepted min score:          N/A (no accepted candidates)"
    )
    print()
    print(f"RESULT: {'ALL GATES PASS' if passed else 'FAILED'}")
    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
    print(f"\nEval artifact written to: {args.output}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
