#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict, List

from normalizers.age import find_ages
from normalizers.coverage_status import normalize_coverage_status
from normalizers.duration import find_durations
from normalizers.indian_number_words import MULTIPLIERS
from normalizers.money import find_money_values
from normalizers.percentage import find_percentages


VectorFn = Callable[[str], Dict[str, Any]]


def _first_normalized(find_fn: Callable[[str], List[Dict[str, Any]]]) -> VectorFn:
    def wrapper(text: str) -> Dict[str, Any]:
        results = find_fn(text)
        if not results:
            return {}
        return results[0]["normalized"]

    return wrapper


def _coverage(text: str) -> Dict[str, Any]:
    return normalize_coverage_status(text)["normalized"]


def _magnitude(text: str) -> Dict[str, Any]:
    return {"multiplier": MULTIPLIERS[text]}


VECTORS = {
    "money": [
        ("₹5 lakh", {"amount": 500000, "currency": "INR"}),
        ("Rs. 5,00,000", {"amount": 500000, "currency": "INR"}),
        ("INR 5 lakhs", {"amount": 500000, "currency": "INR"}),
        ("1 crore", {"amount": 10000000, "currency": "INR"}),
        ("50 lacs", {"amount": 5000000, "currency": "INR"}),
        ("₹ 1,00,000", {"amount": 100000, "currency": "INR"}),
        ("Rs. 2.5 lakhs", {"amount": 250000, "currency": "INR"}),
        ("actuals", {"special_value": "actuals", "currency": "INR"}),
        ("as charged", {"special_value": "as_charged", "currency": "INR"}),
        ("subject to limit", {"special_value": "subject_to_limit", "currency": "INR"}),
    ],
    "duration": [
        ("36 months", {"months": 36}),
        ("2 years", {"months": 24}),
        ("90 days", {"days": 90}),
        ("thirty days", {"days": 30}),
        ("one year", {"months": 12}),
        ("1 yr", {"months": 12}),
    ],
    "percentage": [
        ("20%", {"percentage": 20}),
        ("20 per cent", {"percentage": 20}),
        ("twenty percent", {"percentage": 20}),
        ("1% of SI", {"percentage": 1}),
        ("20% of claim", {"percentage": 20}),
    ],
    "age": [
        ("60 years", {"age_years": 60, "comparator": "eq"}),
        ("18 yrs", {"age_years": 18, "comparator": "eq"}),
        ("aged 61 years", {"age_years": 61, "comparator": "eq"}),
        ("beyond 60 years", {"age_years": 60, "comparator": "gt"}),
        ("61 years or above", {"age_years": 61, "comparator": "gte"}),
    ],
    "coverage_status": [
        ("covered", {"coverage_status": "covered"}),
        ("not covered", {"coverage_status": "not_covered"}),
        ("covered after waiting period", {"coverage_status": "conditional"}),
        ("up to actuals", {"coverage_status": "covered_with_actuals"}),
        ("not admissible", {"coverage_status": "not_covered"}),
    ],
    "indian_number_words": [
        ("lakh", {"multiplier": 100000}),
        ("lac", {"multiplier": 100000}),
        ("crore", {"multiplier": 10000000}),
        ("thousand", {"multiplier": 1000}),
    ],
}

NORMALIZERS: Dict[str, VectorFn] = {
    "money": _first_normalized(find_money_values),
    "duration": _first_normalized(find_durations),
    "percentage": _first_normalized(find_percentages),
    "age": _first_normalized(find_ages),
    "coverage_status": _coverage,
    "indian_number_words": _magnitude,
}


def _git_commit() -> str:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        return f"unknown: {exc}"
    return result.stdout.strip()


def evaluate() -> Dict[str, Any]:
    cases = []
    passed = 0
    total = 0
    by_group: Dict[str, Dict[str, int]] = {}
    for group, vectors in VECTORS.items():
        by_group[group] = {"passed": 0, "total": 0}
        normalizer = NORMALIZERS[group]
        for text, expected in vectors:
            actual = normalizer(text)
            ok = actual == expected
            total += 1
            by_group[group]["total"] += 1
            if ok:
                passed += 1
                by_group[group]["passed"] += 1
            cases.append(
                {
                    "group": group,
                    "input": text,
                    "expected": expected,
                    "actual": actual,
                    "passed": ok,
                }
            )
    return {
        "eval_name": "normalizers-dse008-v1",
        "date": date.today().isoformat(),
        "task_id": "DSE-008",
        "git_commit": _git_commit(),
        "metrics": {
            "total_vectors": total,
            "passed_vectors": passed,
            "pass_rate": round(passed / total, 6) if total else 0,
            "by_group": by_group,
        },
        "passed": passed == total,
        "failures": [case for case in cases if not case["passed"]],
        "cases": cases,
        "notes": "DSE-008 fixed-vector eval for reusable normalizers. Hard gate is 100% vector pass rate.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate DSE-008 normalizer vectors.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = evaluate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "metrics": result["metrics"], "failures": result["failures"]}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

