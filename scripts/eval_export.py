"""
Eval Export — DSE-013

Hard-gate evaluation for the derived 20-concept export.

Hard gates (any failure blocks merge):
  1.  policies_exported == 5
  2.  all_20_concepts_present_per_policy
  3.  schema_validation_errors == 0
  4.  present_facts_have_evidence (evidence + evidence_page + evidence_clause + source_span_id non-null)
  5.  not_found_facts_have_null_value
  6.  no_invalid_fact_status
  7.  evidence_span_ids_exist_in_db
  8.  gold_value_match_for_5_concepts >= 95%
  9.  gold_status_match_for_5_concepts >= 95%
  10. false_present_for_gold_not_found == 0
  11. export_schema_version_present ("1.0")
  12. derived_policy_features_parity == 5
  13. present_missing_evidence_clause == 0
  14. cross_file_page_disagreement == 0

Usage:
  PYTHONPATH=. python scripts/eval_export.py \\
    --db data/engine.sqlite \\
    --export-root data/export \\
    --gold-corpus gold_corpus \\
    --output runs/evals/YYYY-MM-DD-export-dse013-v1.json
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
from typing import Any, Dict, List, Tuple

from derived.field_mapping import ALL_EXPORT_CONCEPTS, CONCEPT_FIELD_MAP, VALID_FACT_STATUSES
from derived.schema_validator import validate_policy_features

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
_TARGET_CONCEPTS_5 = [
    "free_look_period",
    "grace_period",
    "ped_waiting_period",
    "initial_waiting_period",
    "co_pay",
]


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
        return "null"
    if isinstance(obj, str):
        try:
            return json.dumps(json.loads(obj), sort_keys=True, separators=(",", ":"))
        except (json.JSONDecodeError, TypeError):
            return obj
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def open_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def evaluate_exports(
    db_path: str,
    export_root: str,
    gold_corpus: str,
) -> dict:
    conn = open_db(db_path)

    # Collect all exported policy_features.json files
    policies_dir = os.path.join(gold_corpus, "policies")
    slugs = sorted(
        s
        for s in os.listdir(policies_dir)
        if os.path.isfile(os.path.join(policies_dir, s, "metadata.json"))
    )

    # Map slug → policy_id (from source_documents)
    slug_to_policy = {}
    slug_to_doc_id = {}
    for slug in slugs:
        physical = _load_json(os.path.join("data/interim/physical", slug, "document_physical.json"))
        doc_id = physical["document_id"]
        row = conn.execute(
            "SELECT policy_id FROM source_documents WHERE document_id = ?", (doc_id,)
        ).fetchone()
        if row:
            slug_to_policy[slug] = row["policy_id"]
            slug_to_doc_id[slug] = doc_id

    # Gate 1: policies exported
    exported_policies = []
    for slug, policy_id in slug_to_policy.items():
        feat_path = os.path.join(export_root, policy_id, "policy_features.json")
        if os.path.isfile(feat_path):
            exported_policies.append(policy_id)

    # Gate 3: schema validation
    schema_errors_total = 0
    schema_details = []
    features_by_policy: Dict[str, dict] = {}
    for policy_id in exported_policies:
        feat = _load_json(os.path.join(export_root, policy_id, "policy_features.json"))
        features_by_policy[policy_id] = feat
        errors = validate_policy_features(feat)
        schema_errors_total += len(errors)
        if errors:
            schema_details.append({"policy_id": policy_id, "errors": errors})

    # Gate 2: all 20 concepts present
    expected_fields = {CONCEPT_FIELD_MAP[c]["field"] for c in ALL_EXPORT_CONCEPTS}
    concepts_missing = 0
    for policy_id, feat in features_by_policy.items():
        actual = set(feat.get("features", {}).keys())
        if actual != expected_fields:
            concepts_missing += len(expected_fields - actual)

    # Gates 4-6: present/not_found/status validation
    present_missing_evidence = 0
    present_missing_evidence_clause = 0
    not_found_with_value = 0
    invalid_status_count = 0
    for policy_id, feat in features_by_policy.items():
        for field_name, feature in feat.get("features", {}).items():
            status = feature.get("fact_status")
            if status not in VALID_FACT_STATUSES:
                invalid_status_count += 1
            if status == "present":
                for ev in ("evidence", "evidence_page", "source_span_id", "evidence_clause"):
                    if feature.get(ev) is None:
                        present_missing_evidence += 1
                        break
                if feature.get("evidence_clause") is None:
                    present_missing_evidence_clause += 1
            if status == "not_found" and feature.get("value") is not None:
                not_found_with_value += 1

    # Gate 7: evidence span IDs exist in DB
    span_ids_missing = 0
    span_ids_checked = 0
    for policy_id, feat in features_by_policy.items():
        for field_name, feature in feat.get("features", {}).items():
            span_id = feature.get("source_span_id")
            if span_id:
                span_ids_checked += 1
                row = conn.execute(
                    "SELECT span_id FROM source_spans WHERE span_id = ?", (span_id,)
                ).fetchone()
                if not row:
                    span_ids_missing += 1

    # Gate: cross-file page consistency
    cross_file_page_disagreement = 0
    for policy_id in exported_policies:
        feat = features_by_policy[policy_id]
        sources_path = os.path.join(export_root, policy_id, "policy_fact_sources.json")
        if not os.path.isfile(sources_path):
            continue
        sources = _load_json(sources_path)
        # Reverse-map field_name → concept for lookup into sources
        field_to_concept = {v["field"]: k for k, v in CONCEPT_FIELD_MAP.items()}
        for field_name, feature in feat.get("features", {}).items():
            if feature.get("fact_status") != "present":
                continue
            concept = field_to_concept.get(field_name)
            if not concept:
                continue
            feat_page = feature.get("evidence_page")
            src = sources.get("sources", {}).get(concept, {})
            accepted_id = src.get("accepted_candidate_id")
            src_page = None
            for prov in src.get("provenance", []):
                if prov.get("candidate_id") == accepted_id:
                    src_page = prov.get("page")
                    break
            if feat_page is not None and src_page is not None and feat_page != src_page:
                cross_file_page_disagreement += 1

    # Gates 8-10: gold comparison for 5 implemented concepts
    gold_status_total = 0
    gold_status_correct = 0
    gold_value_total = 0
    gold_value_correct = 0
    false_present = 0
    gold_details = []

    for slug in slugs:
        policy_id = slug_to_policy.get(slug)
        if not policy_id or policy_id not in features_by_policy:
            continue
        gold_facts = _load_json(os.path.join(policies_dir, slug, "facts.json"))
        gold_by_concept = {f["concept"]: f for f in gold_facts}
        feat = features_by_policy[policy_id]

        for concept in _TARGET_CONCEPTS_5:
            gold = gold_by_concept.get(concept)
            if not gold:
                continue
            field_name = CONCEPT_FIELD_MAP[concept]["field"]
            exported = feat.get("features", {}).get(field_name, {})

            g_status = gold["fact_status"]
            e_status = exported.get("fact_status", "not_found")

            gold_status_total += 1
            if g_status == e_status:
                gold_status_correct += 1

            if (
                g_status in ("not_found", "not_applicable", "explicitly_not_covered")
                and e_status == "present"
            ):
                false_present += 1

            if g_status == "present" and e_status == "present":
                gold_value_total += 1
                from derived.field_mapping import extract_scalar_value

                g_val = _norm_json(extract_scalar_value(concept, gold.get("normalized_value_json")))
                e_val = _norm_json(exported.get("value"))
                if g_val == e_val:
                    gold_value_correct += 1
                gold_details.append(
                    {
                        "slug": slug,
                        "concept": concept,
                        "gold_value": g_val,
                        "export_value": e_val,
                        "match": g_val == e_val,
                    }
                )

    # Gate 11: schema version
    schema_version_ok = all(
        feat.get("export_schema_version") == "1.0" for feat in features_by_policy.values()
    )

    # Gate 12: derived_policy_features parity
    dpf_count = conn.execute("SELECT COUNT(*) FROM derived_policy_features").fetchone()[0]

    conn.close()

    return {
        "policies_exported": len(exported_policies),
        "concepts_missing_fields": concepts_missing,
        "schema_errors_total": schema_errors_total,
        "schema_details": schema_details,
        "present_missing_evidence": present_missing_evidence,
        "not_found_with_value": not_found_with_value,
        "invalid_status_count": invalid_status_count,
        "span_ids_checked": span_ids_checked,
        "span_ids_missing": span_ids_missing,
        "gold_status_total": gold_status_total,
        "gold_status_correct": gold_status_correct,
        "gold_status_accuracy": round(gold_status_correct / gold_status_total, 4)
        if gold_status_total
        else 0,
        "gold_value_total": gold_value_total,
        "gold_value_correct": gold_value_correct,
        "gold_value_accuracy": round(gold_value_correct / gold_value_total, 4)
        if gold_value_total
        else 0,
        "false_present": false_present,
        "schema_version_ok": schema_version_ok,
        "derived_policy_features_count": dpf_count,
        "present_missing_evidence_clause": present_missing_evidence_clause,
        "cross_file_page_disagreement": cross_file_page_disagreement,
        "gold_value_details": gold_details,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Eval Export — DSE-013")
    parser.add_argument("--db", default="data/engine.sqlite")
    parser.add_argument("--export-root", default="data/export")
    parser.add_argument("--gold-corpus", default="gold_corpus")
    parser.add_argument(
        "--output",
        default=f"runs/evals/{time.strftime('%Y-%m-%d')}-export-dse013-v1.json",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.db):
        print(f"ERROR: DB not found: {args.db}", file=sys.stderr)
        return 1

    results = evaluate_exports(args.db, args.export_root, args.gold_corpus)

    # Hard gate evaluation
    failures = []
    if results["policies_exported"] != 5:
        failures.append(f"policies_exported={results['policies_exported']} (expected 5)")
    if results["concepts_missing_fields"] != 0:
        failures.append(f"concepts_missing_fields={results['concepts_missing_fields']}")
    if results["schema_errors_total"] != 0:
        failures.append(
            f"schema_validation_errors={results['schema_errors_total']}: {results['schema_details']}"
        )
    if results["present_missing_evidence"] != 0:
        failures.append(f"present_missing_evidence={results['present_missing_evidence']}")
    if results["not_found_with_value"] != 0:
        failures.append(f"not_found_with_value={results['not_found_with_value']}")
    if results["invalid_status_count"] != 0:
        failures.append(f"invalid_fact_status_count={results['invalid_status_count']}")
    if results["span_ids_missing"] != 0:
        failures.append(f"evidence_span_ids_missing_from_db={results['span_ids_missing']}")
    if results["gold_value_accuracy"] < 0.95:
        failures.append(f"gold_value_accuracy={results['gold_value_accuracy']:.2%} (target >= 95%)")
    if results["gold_status_accuracy"] < 0.95:
        failures.append(
            f"gold_status_accuracy={results['gold_status_accuracy']:.2%} (target >= 95%)"
        )
    if results["false_present"] != 0:
        failures.append(f"false_present={results['false_present']}")
    if not results["schema_version_ok"]:
        failures.append("export_schema_version not '1.0' in all exports")
    if results["derived_policy_features_count"] != 5:
        failures.append(
            f"derived_policy_features_count={results['derived_policy_features_count']} (expected 5)"
        )
    if results["present_missing_evidence_clause"] != 0:
        failures.append(
            f"present_missing_evidence_clause={results['present_missing_evidence_clause']}"
        )
    if results["cross_file_page_disagreement"] != 0:
        failures.append(f"cross_file_page_disagreement={results['cross_file_page_disagreement']}")

    passed = len(failures) == 0

    result_doc = {
        "eval_name": "export-dse013-v2",
        "date": time.strftime("%Y-%m-%d"),
        "task_id": "DSE-013",
        "git_commit": _git_commit(),
        "hard_gates": {
            "policies_exported": results["policies_exported"],
            "concepts_missing_fields": results["concepts_missing_fields"],
            "schema_validation_errors": results["schema_errors_total"],
            "present_missing_evidence": results["present_missing_evidence"],
            "not_found_with_value": results["not_found_with_value"],
            "invalid_fact_status_count": results["invalid_status_count"],
            "span_ids_missing_from_db": results["span_ids_missing"],
            "gold_value_accuracy": results["gold_value_accuracy"],
            "gold_status_accuracy": results["gold_status_accuracy"],
            "false_present": results["false_present"],
            "schema_version_ok": results["schema_version_ok"],
            "derived_policy_features_count": results["derived_policy_features_count"],
            "present_missing_evidence_clause": results["present_missing_evidence_clause"],
            "cross_file_page_disagreement": results["cross_file_page_disagreement"],
        },
        "metrics": {
            "span_ids_checked": results["span_ids_checked"],
            "gold_status_total": results["gold_status_total"],
            "gold_status_correct": results["gold_status_correct"],
            "gold_value_total": results["gold_value_total"],
            "gold_value_correct": results["gold_value_correct"],
        },
        "gold_value_details": results["gold_value_details"],
        "passed": passed,
        "failures": failures,
    }

    _write_json(args.output, result_doc)

    # Print summary
    print(f"\n{'=' * 60}")
    print("DSE-013 Derived Export Eval")
    print(f"{'=' * 60}")
    print(f"Policies exported:           {results['policies_exported']}")
    print(f"Concepts per policy:         20/20 (missing: {results['concepts_missing_fields']})")
    print(f"Schema validation errors:    {results['schema_errors_total']}")
    print(f"Present missing evidence:    {results['present_missing_evidence']}")
    print(f"Not-found with value:        {results['not_found_with_value']}")
    print(f"Invalid fact statuses:       {results['invalid_status_count']}")
    print(
        f"Span IDs missing from DB:    {results['span_ids_missing']}/{results['span_ids_checked']}"
    )
    print(
        f"Gold status accuracy (5):    {results['gold_status_accuracy']:.1%} ({results['gold_status_correct']}/{results['gold_status_total']})"
    )
    print(
        f"Gold value accuracy (5):     {results['gold_value_accuracy']:.1%} ({results['gold_value_correct']}/{results['gold_value_total']})"
    )
    print(f"False present:               {results['false_present']}")
    print(f"Schema version OK:           {results['schema_version_ok']}")
    print(f"Derived features in DB:      {results['derived_policy_features_count']}")
    print(f"Evidence clause missing:     {results['present_missing_evidence_clause']}")
    print(f"Cross-file page disagree:    {results['cross_file_page_disagreement']}")
    print()
    print(f"RESULT: {'ALL GATES PASS' if passed else 'FAILED'}")
    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
    print(f"\nEval artifact written to: {args.output}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
