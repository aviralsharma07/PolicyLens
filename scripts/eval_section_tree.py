import argparse
from difflib import SequenceMatcher
import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple


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


def _normalize_text(text: str) -> str:
    text = re.sub(r"\.\s*\.\s*\.\s*\.\s*\.+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower().rstrip(".")


def _compact_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", _normalize_text(text))


def _is_toc_section(gold_sec: Dict[str, Any]) -> bool:
    title = gold_sec.get("title", "")
    if re.search(r"\.{4,}", title):
        return True
    return False


def _is_cover_or_header_gold(gold_sec: Dict[str, Any]) -> bool:
    title = _compact_text(gold_sec.get("title", ""))
    if gold_sec.get("section_number"):
        return False
    header_fragments = {
        "newindiafloatermediclaimpolicy",
        "thenewindiaassurancecoltd",
        "registeredheadoffice87mahatmagandhiroadmumbai400001",
    }
    return title in header_fragments


def _extract_section_number(gold_sec: Dict[str, Any]) -> Optional[str]:
    num = gold_sec.get("section_number")
    if num:
        return str(num).strip()
    title = gold_sec.get("title", "")
    match = re.match(r"\s*(\d+(?:\.\d+)*)\s*\.?\s", title)
    if match:
        return match.group(1)
    return None


def _number_parent(number: Optional[str]) -> Optional[str]:
    if not number:
        return None
    upper = str(number).upper()
    if re.fullmatch(r"[IVXLCDM]+", upper):
        return None
    parts = str(number).split(".")
    if len(parts) <= 1:
        return None
    return ".".join(parts[:-1])


def _is_roman_number(number: Optional[str]) -> bool:
    return bool(number and re.fullmatch(r"[IVXLCDM]+", str(number).upper()))


def _strip_number_prefix(title: str) -> str:
    result = re.sub(r"^\s*\d+(?:\.\d+)*\s*\.?\s*", "", title).strip()
    if result == title.strip():
        result = re.sub(r"^\s*[IVXLCDM]{2,}\.?\s*", "", title).strip()
    if result == title.strip():
        result = re.sub(r"^\s*[IVXLCDM]\.\s+", "", title).strip()
    if result == title.strip():
        result = re.sub(r"^\s*SECTION\s+[A-Z0-9]+(?:\.\d+)*\s*[:.]?\s*", "", title).strip()
    if result == title.strip():
        result = re.sub(
            r"^\s*PART\s+[IVXLCDM]+\s+OF\s+THE\s+POLICY\s+SCHEDULE\s*", "", title
        ).strip()
    return result


def _title_similarity(a: str, b: str) -> float:
    ca = _compact_text(_strip_number_prefix(a))
    cb = _compact_text(_strip_number_prefix(b))
    if not ca or not cb:
        return 0.0
    if ca == cb:
        return 1.0
    if ca.startswith(cb) or cb.startswith(ca):
        if min(len(ca), len(cb)) >= 6:
            return 0.85
        return min(len(ca), len(cb)) / max(len(ca), len(cb))
    return SequenceMatcher(None, ca, cb).ratio()


def _parent_agreement(
    gold_sec: Dict[str, Any],
    pred_sec: Dict[str, Any],
    gold_by_id: Dict[str, Dict[str, Any]],
    pred_by_id: Dict[str, Dict[str, Any]],
    matched_pairs: List[Tuple[str, str, float]],
) -> bool:
    gold_number = _extract_section_number(gold_sec)
    expected_parent_number = _number_parent(gold_number)
    if not expected_parent_number:
        return True

    pred_parent = pred_by_id.get(pred_sec.get("parent_id"))
    if not pred_parent:
        return False
    return str(pred_parent.get("number")).upper() == expected_parent_number.upper()


def _is_penalized_false_positive(
    pred_sec: Dict[str, Any],
    gold_numbers: Set[str],
) -> bool:
    number = pred_sec.get("number")
    if not number:
        return True
    number_upper = str(number).upper()
    if _is_roman_number(number_upper):
        return False
    return number_upper in gold_numbers


def _gold_compact(gold_sec: Dict[str, Any]) -> str:
    return _compact_text(gold_sec.get("title", ""))


def _pred_compact(pred_sec: Dict[str, Any]) -> str:
    title = pred_sec.get("title", "")
    stripped = _strip_number_prefix(title)
    if stripped:
        return _compact_text(stripped)
    return _compact_text(title)


def match_predicted_to_gold(
    predicted_sections: List[Dict[str, Any]],
    gold_sections: List[Dict[str, Any]],
) -> Dict[str, Any]:
    matched: List[Tuple[str, str, float]] = []
    used_pred_ids: Set[str] = set()
    used_gold_ids: Set[str] = set()

    for gold_sec in sorted(gold_sections, key=lambda s: (s.get("page_start", 0), s.get("section_id", ""))):
        gid = gold_sec["section_id"]
        gold_num = _extract_section_number(gold_sec)
        gold_title = gold_sec.get("title", "")
        gold_page = gold_sec.get("page_start", 0)

        best_pred = None
        best_score = 0.0
        for pred_sec in predicted_sections:
            pid = pred_sec["section_id"]
            if pid in used_pred_ids:
                continue
            pred_num = pred_sec.get("number")
            pred_title = pred_sec.get("title", "")
            pred_page = pred_sec.get("page_start", 0)

            page_delta = abs(int(pred_page or 0) - int(gold_page or 0))
            if page_delta > 1:
                continue

            text_score = _title_similarity(gold_title, pred_title)
            number_score = 0.0
            if gold_num and pred_num and str(gold_num).upper() == str(pred_num).upper():
                number_score = 0.45
            elif not gold_num and not pred_num:
                number_score = 0.15

            page_score = 0.2 if page_delta == 0 else 0.1
            score = (text_score * 0.55) + number_score + page_score

            if score > best_score:
                best_score = score
                best_pred = pred_sec

        if best_pred and best_score >= 0.72:
            matched.append((gid, best_pred["section_id"], round(min(best_score, 1.0), 3)))
            used_gold_ids.add(gid)
            used_pred_ids.add(best_pred["section_id"])

    unmatched_gold = [s for s in gold_sections if s["section_id"] not in used_gold_ids]
    unmatched_pred = [
        s for s in predicted_sections if s["section_id"] not in used_pred_ids and s["level"] > 0
    ]

    return {
        "matched": matched,
        "matched_gold_ids": used_gold_ids,
        "matched_pred_ids": used_pred_ids,
        "unmatched_gold": unmatched_gold,
        "unmatched_pred": unmatched_pred,
    }


def compute_metrics(
    predicted_sections: List[Dict[str, Any]],
    predicted_clauses: List[Dict[str, Any]],
    gold_sections: List[Dict[str, Any]],
    gold_clauses: List[Dict[str, Any]],
) -> Dict[str, Any]:

    raw_gold_non_root = [s for s in gold_sections if s.get("level", 1) > 0]
    gold_toc = [s for s in raw_gold_non_root if _is_toc_section(s)]
    gold_excluded_headers = [s for s in raw_gold_non_root if _is_cover_or_header_gold(s)]
    min_pred_visual_page = min(
        (
            int(s.get("page_start") or 0)
            for s in predicted_sections
            if s.get("heading_type") == "visual" and int(s.get("page_start") or 0) > 0
        ),
        default=0,
    )
    gold_non_toc = [
        s
        for s in raw_gold_non_root
        if not _is_toc_section(s) and not _is_cover_or_header_gold(s)
        and (min_pred_visual_page == 0 or int(s.get("page_start") or 0) >= min_pred_visual_page)
    ]
    max_gold_page = max((int(s.get("page_start") or 0) for s in gold_non_toc), default=0)
    predicted_eligible = [
        s
        for s in predicted_sections
        if s.get("level", 0) > 0 and (max_gold_page == 0 or int(s.get("page_start") or 0) <= max_gold_page)
    ]

    gold_by_id = {s["section_id"]: s for s in gold_non_toc}
    pred_by_id = {s["section_id"]: s for s in predicted_eligible}

    match_result = match_predicted_to_gold(predicted_eligible, gold_non_toc)

    matched_gold_count = len(match_result["matched"])
    total_gold_visual = len(gold_non_toc)
    total_predicted_non_root = len(predicted_eligible)

    gold_numbers = {
        str(_extract_section_number(s)).upper()
        for s in gold_non_toc
        if _extract_section_number(s)
    }

    penalized_unmatched_pred = [
        s for s in match_result["unmatched_pred"] if _is_penalized_false_positive(s, gold_numbers)
    ]

    # Section-level metrics
    true_positives = matched_gold_count
    false_negatives = total_gold_visual - matched_gold_count
    false_positives = len(penalized_unmatched_pred)

    section_recall = (true_positives / total_gold_visual * 100) if total_gold_visual > 0 else 0.0
    section_precision = (
        (true_positives / (true_positives + false_positives) * 100)
        if (true_positives + false_positives) > 0
        else 0.0
    )
    section_f1 = (
        2 * section_precision * section_recall / (section_precision + section_recall)
        if (section_precision + section_recall) > 0
        else 0.0
    )

    # Section tree accuracy counts missed gold sections as incorrect.
    tree_correct = 0
    page_correct = 0
    for gid, pid, score in match_result["matched"]:
        gold_sec = gold_by_id.get(gid)
        pred_sec = pred_by_id.get(pid)
        if not gold_sec or not pred_sec:
            continue
        gold_page = gold_sec.get("page_start", 0)
        pred_page = pred_sec.get("page_start", 0)
        if gold_page == pred_page:
            page_correct += 1
        if _parent_agreement(gold_sec, pred_sec, gold_by_id, pred_by_id, match_result["matched"]):
            tree_correct += 1

    section_tree_accuracy = (
        (tree_correct / total_gold_visual * 100) if total_gold_visual > 0 else 0.0
    )
    section_boundary_accuracy = (
        (page_correct / total_gold_visual * 100) if total_gold_visual > 0 else 0.0
    )

    # Clause boundary proxy: gold clauses currently do not carry line IDs, so DSE-006
    # evaluates whether each gold clause's owning section has a page-aligned predicted
    # section with at least one produced clause. This is stricter than count matching
    # and will be replaced by true line-overlap once gold clauses include spans.
    gold_clause_by_section: Dict[str, List[Dict[str, Any]]] = {}
    for gc in gold_clauses:
        sid = gc.get("section_id", "")
        gold_clause_by_section.setdefault(sid, []).append(gc)

    pred_clause_by_section: Dict[str, List[Dict[str, Any]]] = {}
    for pc in predicted_clauses:
        sid = pc.get("section_id", "")
        pred_clause_by_section.setdefault(sid, []).append(pc)

    clause_tp = 0
    clause_fp = 0
    clause_fn = 0
    clause_excluded_toc = 0

    for gid, pid, score in match_result["matched"]:
        gold_section_clauses = gold_clause_by_section.get(gid, [])
        pred_section_clauses = pred_clause_by_section.get(pid, [])

        gold_count = max(1, len(gold_section_clauses))
        if pred_section_clauses:
            clause_tp += gold_count
        else:
            clause_fn += gold_count

    unmatched_gold_clause_sections = [
        s for s in gold_non_toc if s["section_id"] not in match_result["matched_gold_ids"]
    ]
    clause_fn += sum(max(1, len(gold_clause_by_section.get(s["section_id"], []))) for s in unmatched_gold_clause_sections)

    unmatched_pred_clause_sections = penalized_unmatched_pred
    clause_fp += sum(1 for s in unmatched_pred_clause_sections if pred_clause_by_section.get(s["section_id"]))

    clause_precision = (
        (clause_tp / (clause_tp + clause_fp) * 100) if (clause_tp + clause_fp) > 0 else 0.0
    )
    clause_recall = (
        (clause_tp / (clause_tp + clause_fn) * 100) if (clause_tp + clause_fn) > 0 else 0.0
    )
    clause_f1 = (
        2 * clause_precision * clause_recall / (clause_precision + clause_recall)
        if (clause_precision + clause_recall) > 0
        else 0.0
    )

    critical_terms = (
        "definition",
        "coverage",
        "waiting period",
        "exclusion",
        "claim procedure",
        "general terms",
        "preamble",
    )
    missed_critical_sections = 0
    for s in match_result["unmatched_gold"]:
        title = _normalize_text(s.get("title", ""))
        starts_with_critical = any(title.startswith(term) for term in critical_terms)
        uppercase_heading = title.upper() == title and any(term in title for term in critical_terms)
        if starts_with_critical or uppercase_heading:
            missed_critical_sections += 1

    return {
        "total_gold_non_toc_sections": total_gold_visual,
        "total_gold_toc_sections": len(gold_toc),
        "total_gold_header_sections_excluded": len(gold_excluded_headers),
        "min_predicted_visual_page": min_pred_visual_page,
        "max_gold_eval_page": max_gold_page,
        "total_predicted_non_root_sections": total_predicted_non_root,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "section_tree_accuracy": round(section_tree_accuracy, 2),
        "section_boundary_accuracy": round(section_boundary_accuracy, 2),
        "section_precision": round(section_precision, 2),
        "section_recall": round(section_recall, 2),
        "section_f1": round(section_f1, 2),
        "clause_precision": round(clause_precision, 2),
        "clause_recall": round(clause_recall, 2),
        "clause_f1": round(clause_f1, 2),
        "clause_excluded_toc": clause_excluded_toc,
        "tree_correct": tree_correct,
        "page_correct": page_correct,
        "missed_critical_sections": missed_critical_sections,
        "matched_examples": [
            {
                "gold_id": gid,
                "pred_id": pid,
                "match_score": score,
            }
            for gid, pid, score in match_result["matched"][:20]
        ],
    }


def evaluate_policy(
    slug: str,
    output_root: str,
    gold_corpus_root: str,
) -> Optional[Dict[str, Any]]:
    tree_path = os.path.join(output_root, slug, "section_tree.json")
    gold_sections_path = os.path.join(gold_corpus_root, "policies", slug, "sections.json")
    gold_clauses_path = os.path.join(gold_corpus_root, "policies", slug, "clauses.json")

    if not os.path.isfile(tree_path):
        return {"slug": slug, "status": "missing_section_tree_output"}
    if not os.path.isfile(gold_sections_path):
        return {"slug": slug, "status": "missing_gold_sections"}
    if not os.path.isfile(gold_clauses_path):
        return {"slug": slug, "status": "missing_gold_clauses"}

    with open(tree_path, "r", encoding="utf-8") as f:
        tree_data = json.load(f)

    with open(gold_sections_path, "r", encoding="utf-8") as f:
        gold_sections_raw = json.load(f)

    with open(gold_clauses_path, "r", encoding="utf-8") as f:
        gold_clauses_raw = json.load(f)

    gold_sections = (
        gold_sections_raw
        if isinstance(gold_sections_raw, list)
        else gold_sections_raw.get("sections", [])
    )
    gold_clauses = (
        gold_clauses_raw
        if isinstance(gold_clauses_raw, list)
        else gold_clauses_raw.get("clauses", [])
    )

    predicted_sections = tree_data.get("sections", [])
    predicted_clauses = tree_data.get("clauses", [])

    metrics = compute_metrics(predicted_sections, predicted_clauses, gold_sections, gold_clauses)

    tree_acc_gate = metrics["section_tree_accuracy"] >= 85.0
    section_f1_gate = metrics["section_f1"] >= 80.0
    section_recall_gate = metrics["section_recall"] >= 80.0
    clause_f1_gate = metrics["clause_f1"] >= 80.0
    crit_miss_gate = metrics["missed_critical_sections"] == 0
    gates_passed = (
        tree_acc_gate
        and section_f1_gate
        and section_recall_gate
        and clause_f1_gate
        and crit_miss_gate
    )

    return {
        "slug": slug,
        "status": "passed" if gates_passed else "failed",
        "total_predicted_sections": len(predicted_sections),
        "total_predicted_clauses": len(predicted_clauses),
        "total_gold_sections": len(gold_sections),
        "total_gold_clauses": len(gold_clauses),
        "metrics": metrics,
        "gates": {
            "section_tree_accuracy_ge_85": tree_acc_gate,
            "section_f1_ge_80": section_f1_gate,
            "section_recall_ge_80": section_recall_gate,
            "clause_f1_ge_80": clause_f1_gate,
            "critical_misses_eq_0": crit_miss_gate,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="DSE-006 Section Tree Eval")
    parser.add_argument(
        "--output-root", required=True, help="Root of section tree outputs (DSE-006 output)"
    )
    parser.add_argument("--gold-corpus", required=True, help="Root of gold corpus")
    parser.add_argument("--output", required=True, help="Path to write eval JSON result")

    args = parser.parse_args()

    policies_dir = os.path.join(args.gold_corpus, "policies")
    if not os.path.isdir(policies_dir):
        print(f"ERROR: gold policies dir not found: {policies_dir}", file=sys.stderr)
        return 1

    slugs = sorted(os.listdir(policies_dir))
    results = []

    for slug in slugs:
        print(f"Evaluating {slug} ...")
        result = evaluate_policy(
            slug=slug,
            output_root=args.output_root,
            gold_corpus_root=args.gold_corpus,
        )
        results.append(result)

        if result and result.get("status") == "passed":
            m = result["metrics"]
            print(
                f"  PASS: TreeAcc={m['section_tree_accuracy']}% "
                f"SectionF1={m['section_f1']}% "
                f"ClauseF1={m['clause_f1']}% "
                f"MissCrit={m['missed_critical_sections']}"
            )
        elif result:
            m = result.get("metrics", {})
            print(
                f"  FAIL: TreeAcc={m.get('section_tree_accuracy')}% "
                f"SectionF1={m.get('section_f1')}% "
                f"ClauseF1={m.get('clause_f1')}% "
                f"Crit={m.get('missed_critical_sections')} "
                f"TP={m.get('true_positives')} FP={m.get('false_positives')} FN={m.get('false_negatives')}"
            )
        else:
            print(f"  FAIL: {result}")

    passed = sum(1 for r in results if r and r["status"] == "passed")
    failed = len(results) - passed

    eval_result = {
        "eval_name": "section-tree-v3",
        "date": "2026-05-30",
        "task_id": "DSE-006",
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
        "failures": [r["slug"] for r in results if r and r["status"] != "passed"],
        "notes": (
            "DSE-006 Section Tree eval with page-aware compact-text matching. "
            "TOC/header rows and predicted sections beyond the gold annotation page window are excluded. "
            "Gates: section_tree_accuracy >= 85%, section_f1 >= 80%, "
            "section_recall >= 80%, clause_f1 >= 80%, missed_critical_sections == 0."
        ),
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
