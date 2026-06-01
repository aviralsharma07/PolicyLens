#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from extractors.evidence import contains_evidence
from extractors.models import TARGET_CONCEPTS
from scripts.run_fact_extractors import build_extraction_clauses


GOLD_POLICIES = {
    "hdfc_arogya_sanjeevani",
    "new_india_floater",
    "care_health_care_plus",
    "star_medi_classic_accident",
    "icici_family_shield",
}


def _discover_reviewed_policies(gold_corpus: Path) -> set:
    """Discover all reviewed policy slugs from gold_corpus/policies/."""
    policies_dir = gold_corpus / "policies"
    if not policies_dir.is_dir():
        return GOLD_POLICIES
    return {
        slug
        for slug in sorted(d.name for d in policies_dir.iterdir() if d.is_dir())
        if (policies_dir / slug / "metadata.json").is_file()
    }


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _gold_by_concept(path: Path) -> Dict[str, Dict[str, Any]]:
    facts = _read_json(path)
    return {fact["concept"]: fact for fact in facts if fact.get("concept") in TARGET_CONCEPTS}


def _accepted_by_concept(path: Path) -> Dict[str, Dict[str, Any]]:
    facts = _read_json(path)
    return {fact["concept"]: fact for fact in facts}


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


def _values_match(predicted: Any, gold: Any) -> bool:
    predicted_c = _canonical(predicted)
    gold_c = _canonical(gold)
    if predicted_c == gold_c:
        return True
    return _is_subset_value(gold_c, predicted_c)


def _is_subset_value(expected: Any, actual: Any) -> bool:
    """Allow predicted values to carry extra metadata while preserving gold value equality."""
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


def _load_clause_texts(section_root: Path, slug: str) -> Dict[str, str]:
    section_tree_path = section_root / slug / "section_tree.json"
    if not section_tree_path.exists():
        return {}
    clauses = build_extraction_clauses(_read_json(section_tree_path))
    return {clause["clause_id"]: clause.get("text", "") for clause in clauses}


def _evidence_verified(fact: Dict[str, Any], clause_texts: Dict[str, str]) -> bool:
    if fact.get("fact_status") != "present":
        return True
    evidence_text = fact.get("evidence_text")
    clause_id = fact.get("evidence_clause_id")
    if not evidence_text or not clause_id:
        return False
    return contains_evidence(clause_texts.get(clause_id, ""), evidence_text)


def evaluate_policy(
    *,
    slug: str,
    facts_root: Path,
    gold_corpus: Path,
    section_root: Path,
) -> Dict[str, Any]:
    gold_path = gold_corpus / "policies" / slug / "facts.json"
    accepted_path = facts_root / slug / "accepted_facts.json"
    policy = {
        "policy_slug": slug,
        "passed": False,
        "errors": [],
        "concepts": {},
        "metrics": {},
    }
    if not gold_path.exists():
        policy["errors"].append(f"Missing gold facts: {gold_path}")
        return policy
    if not accepted_path.exists():
        policy["errors"].append(f"Missing accepted facts: {accepted_path}")
        return policy

    gold = _gold_by_concept(gold_path)
    predicted = _accepted_by_concept(accepted_path)
    clause_texts = _load_clause_texts(section_root, slug)

    counts = {
        "gold_present": 0,
        "present_tp": 0,
        "present_fp": 0,
        "present_fn": 0,
        "status_correct": 0,
        "status_total": 0,
        "value_correct": 0,
        "value_total": 0,
        "evidence_verified": 0,
        "evidence_total": 0,
        "false_present_for_gold_not_found": 0,
    }

    for concept in TARGET_CONCEPTS:
        gold_fact = gold.get(concept)
        pred_fact = predicted.get(concept)
        result: Dict[str, Any] = {
            "gold_status": gold_fact.get("fact_status") if gold_fact else None,
            "predicted_status": pred_fact.get("fact_status") if pred_fact else None,
            "gold_normalized_value": gold_fact.get("normalized_value_json") if gold_fact else None,
            "predicted_normalized_value": pred_fact.get("normalized_value_json")
            if pred_fact
            else None,
            "status_match": False,
            "value_match": False,
            "evidence_verified": False,
            "issues": [],
        }
        if not gold_fact:
            result["issues"].append("missing_gold_target_concept")
            policy["concepts"][concept] = result
            continue
        if not pred_fact:
            result["issues"].append("missing_predicted_target_concept")
            policy["concepts"][concept] = result
            continue

        counts["status_total"] += 1
        status_match = pred_fact.get("fact_status") == gold_fact.get("fact_status")
        result["status_match"] = status_match
        if status_match:
            counts["status_correct"] += 1

        gold_present = gold_fact.get("fact_status") == "present"
        pred_present = pred_fact.get("fact_status") == "present"
        if gold_present:
            counts["gold_present"] += 1
            if pred_present:
                counts["value_total"] += 1
                value_match = _values_match(
                    pred_fact.get("normalized_value_json"),
                    gold_fact.get("normalized_value_json"),
                )
                result["value_match"] = value_match
                if value_match:
                    counts["value_correct"] += 1
                    counts["present_tp"] += 1
                else:
                    counts["present_fp"] += 1
                    counts["present_fn"] += 1
                    result["issues"].append("normalized_value_mismatch")
            else:
                counts["present_fn"] += 1
                result["issues"].append("gold_present_predicted_not_present")
        elif pred_present:
            counts["present_fp"] += 1
            if gold_fact.get("fact_status") == "not_found":
                counts["false_present_for_gold_not_found"] += 1
                result["issues"].append("false_present_for_gold_not_found")

        if pred_present:
            counts["evidence_total"] += 1
            verified = _evidence_verified(pred_fact, clause_texts)
            result["evidence_verified"] = verified
            if verified:
                counts["evidence_verified"] += 1
            else:
                result["issues"].append("evidence_not_verified")

        policy["concepts"][concept] = result

    precision = _safe_div(counts["present_tp"], counts["present_tp"] + counts["present_fp"])
    recall = _safe_div(counts["present_tp"], counts["gold_present"])
    value_accuracy = _safe_div(counts["value_correct"], counts["value_total"])
    status_accuracy = _safe_div(counts["status_correct"], counts["status_total"])
    evidence_accuracy = _safe_div(counts["evidence_verified"], counts["evidence_total"])
    attempted_all = set(predicted.keys()) >= set(TARGET_CONCEPTS)
    policy["metrics"] = {
        **counts,
        "deterministic_present_precision": precision,
        "deterministic_present_recall": recall,
        "normalized_value_accuracy": value_accuracy,
        "status_accuracy": status_accuracy,
        "evidence_accuracy": evidence_accuracy,
        "attempted_all_target_concepts": attempted_all,
    }
    policy["passed"] = (
        not policy["errors"]
        and attempted_all
        and counts["false_present_for_gold_not_found"] == 0
        and evidence_accuracy >= 0.95
        and precision >= 0.95
        and value_accuracy >= 0.95
        and recall >= 0.60
    )
    return policy


def _safe_div(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 1.0
    return round(numerator / denominator, 6)


def _aggregate(policy_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    totals = {
        "gold_present": 0,
        "present_tp": 0,
        "present_fp": 0,
        "present_fn": 0,
        "status_correct": 0,
        "status_total": 0,
        "value_correct": 0,
        "value_total": 0,
        "evidence_verified": 0,
        "evidence_total": 0,
        "false_present_for_gold_not_found": 0,
    }
    for policy in policy_results:
        for key in totals:
            totals[key] += policy.get("metrics", {}).get(key, 0)
    return {
        **totals,
        "policy_count": len(policy_results),
        "policies_passed": sum(1 for policy in policy_results if policy.get("passed")),
        "deterministic_present_precision": _safe_div(
            totals["present_tp"], totals["present_tp"] + totals["present_fp"]
        ),
        "deterministic_present_recall": _safe_div(totals["present_tp"], totals["gold_present"]),
        "normalized_value_accuracy": _safe_div(totals["value_correct"], totals["value_total"]),
        "status_accuracy": _safe_div(totals["status_correct"], totals["status_total"]),
        "evidence_accuracy": _safe_div(totals["evidence_verified"], totals["evidence_total"]),
    }


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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate DSE-007 fact extraction against gold facts."
    )
    parser.add_argument("--facts-root", type=Path, required=True)
    parser.add_argument("--gold-corpus", type=Path, required=True)
    parser.add_argument("--section-root", type=Path, default=Path("data/interim/logical"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    policies = sorted(_discover_reviewed_policies(args.gold_corpus))
    results = [
        evaluate_policy(
            slug=slug,
            facts_root=args.facts_root,
            gold_corpus=args.gold_corpus,
            section_root=args.section_root,
        )
        for slug in policies
    ]
    metrics = _aggregate(results)
    expected_count = len(policies)
    failures = []
    if len(results) != expected_count:
        failures.append(f"Expected {expected_count} gold policies evaluated, got {len(results)}")
    if metrics["policies_passed"] != expected_count:
        failures.append(f"Only {metrics['policies_passed']}/{expected_count} policies passed")
    if metrics["false_present_for_gold_not_found"] != 0:
        failures.append("False present emitted for at least one gold not_found fact")
    if metrics["deterministic_present_precision"] < 0.95:
        failures.append("deterministic_present_precision below 0.95")
    if metrics["evidence_accuracy"] < 0.95:
        failures.append("evidence_accuracy below 0.95")
    if metrics["normalized_value_accuracy"] < 0.95:
        failures.append("normalized_value_accuracy below 0.95")
    if metrics["deterministic_present_recall"] < 0.60:
        failures.append("deterministic_present_recall below 0.60")

    output = {
        "eval_name": "fact-extraction-dse007-v1",
        "date": date.today().isoformat(),
        "task_id": "DSE-007",
        "git_commit": _git_commit(),
        "input_manifest": "data/interim/logical/*/section_tree.json",
        "target_concepts": TARGET_CONCEPTS,
        "metrics": metrics,
        "policies": results,
        "passed": not failures,
        "failures": failures,
        "notes": (
            "DSE-007 evaluates first five deterministic extractors. Evidence is verified "
            "against DSE-006 clause text enriched with section heading context because "
            "true source spans are deferred to DSE-010."
        ),
    }
    _write_json(args.output, output)
    print(
        json.dumps({"passed": output["passed"], "metrics": metrics, "failures": failures}, indent=2)
    )
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
