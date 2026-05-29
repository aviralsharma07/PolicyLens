import argparse
import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple


def _get_git_commit() -> Optional[str]:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except Exception:
        return None


def _get_git_dirty() -> Optional[bool]:
    try:
        subprocess.check_call(
            ["git", "diff", "--quiet"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.check_call(
            ["git", "diff", "--cached", "--quiet"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return False
    except subprocess.CalledProcessError:
        return True
    except Exception:
        return None


def normalize_text(text: str) -> str:
    text = re.sub(r"\.\s*\.\s*\.\s*\.\s*\.+", "", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip().lower().rstrip(".")
    return text


def compact_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_text(text))


def _candidate_label_score(candidate: Dict[str, Any], label: Dict[str, Any]) -> float:
    if candidate.get("page_number") != label.get("page"):
        return 0.0

    label_line_id = label.get("line_id")
    if label_line_id and candidate.get("line_id") == label_line_id:
        return 1.0

    cand_norm = normalize_text(candidate.get("text", ""))
    label_norm = normalize_text(label.get("expected_text", ""))
    if cand_norm == label_norm:
        return 0.98

    cand_compact = compact_text(candidate.get("text", ""))
    label_compact = compact_text(label.get("expected_text", ""))
    if cand_compact and cand_compact == label_compact:
        return 0.95

    if min(len(cand_compact), len(label_compact)) >= 12:
        if cand_compact.startswith(label_compact) or label_compact.startswith(cand_compact):
            length_ratio = min(len(cand_compact), len(label_compact)) / max(
                len(cand_compact), len(label_compact)
            )
            if length_ratio >= 0.75:
                return 0.85
    return 0.0


def _load_visual_labels(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    labels = data if isinstance(data, list) else data.get("labels", [])
    visual = [label for label in labels if label.get("is_visual_heading") is True]
    return visual


def compute_metrics(
    candidates: List[Dict[str, Any]],
    heading_labels: List[Dict[str, Any]],
) -> Dict[str, Any]:

    candidate_headings = [c for c in candidates if c.get("decision") == "heading"]
    candidate_indices = set(range(len(candidate_headings)))
    label_indices = set(range(len(heading_labels)))
    scored_pairs: List[Tuple[float, int, int]] = []

    for cand_idx, candidate in enumerate(candidate_headings):
        for label_idx, label in enumerate(heading_labels):
            score = _candidate_label_score(candidate, label)
            if score > 0:
                scored_pairs.append((score, cand_idx, label_idx))

    matched_pairs = []
    used_candidates = set()
    used_labels = set()
    for score, cand_idx, label_idx in sorted(scored_pairs, reverse=True):
        if cand_idx in used_candidates or label_idx in used_labels:
            continue
        matched_pairs.append((score, candidate_headings[cand_idx], heading_labels[label_idx]))
        used_candidates.add(cand_idx)
        used_labels.add(label_idx)

    false_positives = [
        candidate_headings[idx] for idx in sorted(candidate_indices - used_candidates)
    ]
    missed_gold = [heading_labels[idx] for idx in sorted(label_indices - used_labels)]

    total_candidate = len(candidate_headings)
    total_gold = len(heading_labels)
    true_positives = len(matched_pairs)

    precision = (true_positives / total_candidate * 100) if total_candidate > 0 else 0.0
    recall = (true_positives / total_gold * 100) if total_gold > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "total_candidates_above_threshold": total_candidate,
        "total_gold_visual_headings": total_gold,
        "true_positives": true_positives,
        "false_positives": len(false_positives),
        "false_negatives": len(missed_gold),
        "count_invariant_ok": true_positives + len(missed_gold) == total_gold,
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "f1_score": round(f1, 2),
        "matched_examples": [
            {
                "candidate_text": cand.get("text", "")[:100],
                "label_text": label.get("expected_text", "")[:100],
                "page": cand.get("page_number"),
                "line_id": cand.get("line_id"),
                "match_score": round(score, 3),
            }
            for score, cand, label in matched_pairs[:20]
        ],
        "false_positive_examples": [
            {
                "text": fp.get("text", "")[:80],
                "page": fp.get("page_number"),
                "line_id": fp.get("line_id"),
                "score": fp.get("score"),
                "features": fp.get("features", {}),
            }
            for fp in false_positives[:20]
        ],
        "missed_heading_examples": [
            {
                "expected_text": mg.get("expected_text", "")[:80],
                "page": mg.get("page"),
                "line_id": mg.get("line_id"),
                "source_section_id": mg.get("source_section_id"),
            }
            for mg in missed_gold[:20]
        ],
    }


def evaluate_policy(
    slug: str,
    candidates_root: str,
    gold_corpus_root: str,
) -> Optional[Dict[str, Any]]:
    cand_path = os.path.join(candidates_root, slug, "heading_candidates.json")
    labels_path = os.path.join(gold_corpus_root, "policies", slug, "heading_labels.json")

    if not os.path.isfile(cand_path):
        return {"slug": slug, "status": "missing_candidates"}
    if not os.path.isfile(labels_path):
        return {"slug": slug, "status": "missing_heading_labels"}

    with open(cand_path, "r", encoding="utf-8") as f:
        cand_data = json.load(f)

    candidates = cand_data.get("candidates", [])
    heading_labels = _load_visual_labels(labels_path)

    metrics = compute_metrics(candidates, heading_labels)

    precision_gate = metrics["precision"] >= 90.0
    recall_gate = metrics["recall"] >= 80.0
    count_gate = metrics["count_invariant_ok"] is True
    gates_passed = precision_gate and recall_gate and count_gate

    return {
        "slug": slug,
        "status": "passed" if gates_passed else "failed",
        "threshold": cand_data.get("config", {}).get("threshold", 0.5),
        "body_font_mode": cand_data.get("config", {}).get("body_font_mode"),
        "total_lines_scored": cand_data.get("total_lines_scored", 0),
        "metrics": metrics,
        "gates": {
            "precision_ge_90": precision_gate,
            "recall_ge_80": recall_gate,
            "tp_plus_fn_equals_gold": count_gate,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="DSE-005 Heading Scorer Eval")
    parser.add_argument("--candidates-root", required=True)
    parser.add_argument("--gold-corpus", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    policies_dir = os.path.join(args.gold_corpus, "policies")
    slugs = sorted(os.listdir(policies_dir))
    results = []

    for slug in slugs:
        print(f"Evaluating {slug} ...")
        result = evaluate_policy(
            slug=slug,
            candidates_root=args.candidates_root,
            gold_corpus_root=args.gold_corpus,
        )
        results.append(result)
        if result["status"] == "passed":
            print(
                f"  PASS: P={result['metrics']['precision']}% "
                f"R={result['metrics']['recall']}% "
                f"F1={result['metrics']['f1_score']}%"
            )
        else:
            m = result.get("metrics", {})
            fp_count = m.get("false_positives", 0)
            fn_count = m.get("false_negatives", 0)
            print(
                f"  FAIL: P={m.get('precision')}% R={m.get('recall')}% FP={fp_count} FN={fn_count}"
            )

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = len(results) - passed

    eval_result = {
        "eval_name": "heading-scorer-v2",
        "date": "2026-05-30",
        "task_id": "DSE-005",
        "git_commit": _get_git_commit(),
        "git_dirty": _get_git_dirty(),
        "input_manifest": "gold_corpus (5 policies)",
        "metrics": {
            "policies_processed": len(results),
            "passed": passed,
            "failed": failed,
        },
        "policy_results": results,
        "passed": failed == 0,
        "failures": [r["slug"] for r in results if r["status"] != "passed"],
        "notes": "Heading scorer v2 eval on 5 gold PDFs. Gates: precision >= 90%, recall >= 80%, one-to-one page-aware visual-heading label matching, and TP+FN=count(gold visual headings). DSE-006 handles logical section tree and clause boundaries separately.",
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(eval_result, f, indent=2)

    print(f"\nEval written to {args.output}")
    print(f"Passed: {passed}/{len(results)}")
    print(f"Overall: {'PASS' if eval_result['passed'] else 'FAIL'}")

    sys.exit(0 if eval_result["passed"] else 1)


if __name__ == "__main__":
    main()
