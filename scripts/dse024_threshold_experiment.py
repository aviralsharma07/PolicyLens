#!/usr/bin/env python3
"""
DSE-024 Phase C0: Controlled heading-threshold experiment.

For each threshold (0.45, 0.475, 0.50), compute:
  - Acceptance counts for 132 zero-clause policies
  - Candidate classification (heading vs FP risk) for 20 sample policies
  - Heading scorer eval for 20 gold policies
  - Estimated section tree impact

Output: JSON + Markdown reports.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

# ── classification helpers ───────────────────────────────────────────────

HEADING_DICT_TERMS = {
    "preamble",
    "definitions",
    "coverage",
    "exclusions",
    "conditions",
    "renewal",
    "claims",
    "premium",
    "deductible",
    "co-payment",
    "co payment",
    "limitations",
    "benefits",
    "moratorium",
    "miscellaneous",
    "free look",
    "portability",
    "migration",
    "nomination",
    "nominee",
    "arbitration",
    "cancellation",
    "fraud",
    "notice",
    "disclaimer",
    "operative clause",
    "waiting period",
    "waiting",
    "policy disputes",
    "policy period",
    "period of cover",
    "sum insured",
    "policy schedule",
    "pre-existing disease",
    "general terms",
    "schedule",
}


def _matches_heading_dict(text: str) -> bool:
    lower = re.sub(r"^[\d\.\s\)]+", "", text).strip().lower().rstrip(".: ")
    for term in HEADING_DICT_TERMS:
        if lower.startswith(term):
            return True
    return False


def _is_toc_text(text: str) -> bool:
    return bool(re.search(r"\.\s*\.\s*\.\s*\.\s*\.", text))


def classify_candidate_text(text: str, features: dict, page: int) -> str:
    if _is_toc_text(text):
        return "toc"
    if features.get("is_header_region", 0) == 1.0 or features.get("is_footer_region", 0) == 1.0:
        return "boilerplate"
    if features.get("boilerplate_company_penalty", 0) == 1.0:
        return "boilerplate"
    num = features.get("matches_numbering", 0) == 1.0
    bold = features.get("is_bold", 0) == 1.0
    ac = features.get("is_all_caps", 0) == 1.0
    sc = features.get("is_sentence_case", 0) == 1.0
    dm = features.get("matches_heading_dict", 0) == 1.0 or _matches_heading_dict(text)
    sp = features.get("spacing_signal", 0) == 1.0
    llr = features.get("line_length_ratio", 0.5)
    if num and bold and dm:
        return "real_heading"
    if num and dm:
        return "real_heading"
    if num and ac and not sc and len(text) <= 50:
        return "numbered_item"
    if num and sp and not sc and not dm:
        return "numbered_item"
    if num and llr < 0.3:
        return "table_data"
    if dm and (bold or ac):
        return "real_heading"
    if ac and len(text) <= 8:
        return "short_label"
    if sc and llr > 0.6 and not bold:
        return "body_text"
    return "other"


# ── file I/O ─────────────────────────────────────────────────────────────


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ── threshold metrics for a single slug ──────────────────────────────────


def analyze_slug(
    slug: str,
    logical_root: str,
    threshold: float,
) -> Optional[dict]:
    hpath = os.path.join(logical_root, slug, "heading_candidates.json")
    if not os.path.isfile(hpath):
        return None
    hdata = _load_json(hpath)
    candidates = hdata.get("candidates", [])
    config = hdata.get("config", {})

    accepted = [c for c in candidates if c.get("score", 0.0) >= threshold]
    num_accepted = len(accepted)
    pages_with_accepted = len(set(c.get("page_number", 0) for c in accepted))

    classifications = Counter()
    for c in accepted:
        cls = classify_candidate_text(
            c.get("text", ""), c.get("features", {}), c.get("page_number", 0)
        )
        classifications[cls] += 1

    # Estimate TOC/list risk: candidates from first 3 pages, or with TOC dots,
    # or classified as numbered_item
    toc_risk = sum(
        1 for c in accepted if c.get("page_number", 99) <= 3 or _is_toc_text(c.get("text", ""))
    )
    list_item_risk = sum(
        1
        for c in accepted
        if classify_candidate_text(
            c.get("text", ""), c.get("features", {}), c.get("page_number", 0)
        )
        in ("numbered_item", "table_data", "short_label")
    )

    return {
        "slug": slug,
        "threshold": threshold,
        "total_candidates": len(candidates),
        "accepted": num_accepted,
        "pages_with_accepted": pages_with_accepted,
        "classifications": dict(classifications),
        "toc_risk_count": toc_risk,
        "list_item_risk_count": list_item_risk,
        "top_accepted": [
            {
                "text": c.get("text", "")[:80],
                "score": round(c.get("score", 0.0), 4),
                "page": c.get("page_number", 0),
                "classification": classify_candidate_text(
                    c.get("text", ""), c.get("features", {}), c.get("page_number", 0)
                ),
            }
            for c in sorted(accepted, key=lambda x: -x.get("score", 0.0))[:20]
        ],
    }


# ── generate modified heading_candidates.json for a threshold ────────────


def generate_modified_candidates(
    slug: str,
    logical_root: str,
    threshold: float,
    output_dir: str,
) -> bool:
    """Generate a heading_candidates.json with decision recalculated at new threshold."""
    hpath = os.path.join(logical_root, slug, "heading_candidates.json")
    if not os.path.isfile(hpath):
        return False
    hdata = _load_json(hpath)
    for c in hdata.get("candidates", []):
        score = c.get("score", 0.0)
        c["decision"] = "heading" if score >= threshold else "non-heading"
    hdata["config"]["threshold"] = threshold
    out_dir = os.path.join(output_dir, slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "heading_candidates.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(hdata, f, indent=2)
    return True


# ── gold policy eval via subprocess ──────────────────────────────────────


def run_gold_heading_eval(
    candidates_root: str,
    gold_corpus_root: str,
    output_path: str,
) -> Optional[dict]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    cmd = [
        sys.executable,
        "scripts/eval_heading_scorer.py",
        "--candidates-root",
        candidates_root,
        "--gold-corpus",
        gold_corpus_root,
        "--output",
        output_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
        if result.returncode != 0:
            print(f"  eval_heading_scorer.py exited {result.returncode}")
            print(f"  stderr: {result.stderr[:500]}")
        if os.path.isfile(output_path):
            return _load_json(output_path)
        return None
    except subprocess.TimeoutExpired:
        print(f"  eval_heading_scorer.py TIMEOUT")
        return None
    except Exception as exc:
        print(f"  eval_heading_scorer.py error: {exc}")
        return None


# ── per-threshold computation ────────────────────────────────────────────


def compute_threshold_metrics(
    threshold: float,
    zero_clause_slugs: List[str],
    sample_slugs: set,
    gold_slugs: List[str],
    logical_root: str,
    gold_logical_root: str,
    physical_root: str,
    output_root: str,
    gold_corpus_root: str,
) -> dict:
    print(f"  Analyzing {len(zero_clause_slugs)} zero-clause policies ...")

    all_results = {}
    summary = {
        "threshold": threshold,
        "total_zero_clause": len(zero_clause_slugs),
        "processed": 0,
        "errors": 0,
        "with_at_least_1_accepted": 0,
        "with_at_least_5_accepted": 0,
        "total_accepted_all_policies": 0,
        "total_toc_risk": 0,
        "total_list_item_risk": 0,
        "classifications_agg": Counter(),
        "policies_by_category": {},
    }

    # Process all zero-clause slugs
    for slug in zero_clause_slugs:
        result = analyze_slug(slug, logical_root, threshold)
        if result is None:
            summary["errors"] += 1
            continue
        summary["processed"] += 1
        all_results[slug] = result
        accepted = result["accepted"]
        if accepted >= 1:
            summary["with_at_least_1_accepted"] += 1
        if accepted >= 5:
            summary["with_at_least_5_accepted"] += 1
        summary["total_accepted_all_policies"] += accepted
        summary["total_toc_risk"] += result["toc_risk_count"]
        summary["total_list_item_risk"] += result["list_item_risk_count"]
        for cls, count in result["classifications"].items():
            summary["classifications_agg"][cls] += count

    # Sample-specific detailed data
    sample_details = {}
    for entry in all_results:
        if entry in sample_slugs:
            sample_details[entry] = all_results[entry]

    # Gold policy heading eval
    gold_eval = None
    if gold_corpus_root and os.path.isdir(os.path.join(gold_corpus_root, "policies")):
        print(f"  Running gold heading eval for threshold {threshold} ...")
        temp_dir = os.path.join(output_root, f"threshold_{threshold:.2f}".replace(".", "_"))
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)

        gen_count = 0
        for slug in gold_slugs:
            ok = generate_modified_candidates(slug, gold_logical_root, threshold, temp_dir)
            if ok:
                gen_count += 1

        if gen_count > 0:
            eval_out = os.path.join(
                output_root, f"gold_eval_{threshold:.2f}.json".replace(".", "_")
            )
            gold_eval = run_gold_heading_eval(temp_dir, gold_corpus_root, eval_out)
            print(f"    Gold eval status: {'ok' if gold_eval else 'failed'}")

    # Build sorted top-newly-accepted across all processed
    all_accepted_candidates = []
    for slug, result in all_results.items():
        for entry in result.get("top_accepted", []):
            all_accepted_candidates.append(
                {
                    "slug": slug,
                    "text": entry["text"],
                    "score": entry["score"],
                    "page": entry["page"],
                    "classification": entry["classification"],
                }
            )
    all_accepted_candidates.sort(key=lambda x: -x["score"])
    top_20_new_across = all_accepted_candidates[:20]

    return {
        "summary": summary,
        "sample_details": sample_details,
        "gold_heading_eval": gold_eval,
        "top_20_new_across_policies": top_20_new_across,
    }


# ── main ─────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="DSE-024 Phase C0: Controlled heading-threshold experiment"
    )
    parser.add_argument("--classification", required=True)
    parser.add_argument("--sample-inspection", required=True)
    parser.add_argument("--physical-root", required=True)
    parser.add_argument("--logical-root", required=True)
    parser.add_argument(
        "--output-root", required=True, help="Temp/interim output root (data/interim/dse024)"
    )
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--md-output", required=True)
    parser.add_argument(
        "--gold-corpus", default="gold_corpus", help="Gold corpus root (default: gold_corpus)"
    )
    parser.add_argument(
        "--gold-logical-root",
        default=None,
        help="Logical root for gold policy heading candidates (default: same as --logical-root). "
        "Use data/interim/logical/ when --logical-root is data/interim/dse020/logical/.",
    )
    args = parser.parse_args()

    gold_logical_root = args.gold_logical_root or args.logical_root
    print(f"Logical root (zero-clause analysis): {args.logical_root}")
    print(f"Gold logical root (gold eval): {gold_logical_root}")

    # Load inputs
    classification = _load_json(args.classification)
    sample_inspection = _load_json(args.sample_inspection)

    zero_clause_slugs = [e["slug"] for e in classification.get("classifications", [])]
    sample_slugs_set = {e["slug"] for e in classification.get("recommended_sample_20", [])}

    # Gold slug list: intersect gold corpus with gold logical root
    gold_corpus_root = args.gold_corpus
    gold_policies_dir = os.path.join(gold_corpus_root, "policies")
    gold_slugs = []
    if os.path.isdir(gold_policies_dir):
        for slug in sorted(os.listdir(gold_policies_dir)):
            if os.path.isfile(os.path.join(gold_logical_root, slug, "heading_candidates.json")):
                gold_slugs.append(slug)
    print(f"Gold slugs available for eval: {len(gold_slugs)}")

    thresholds = [0.45, 0.475, 0.50]
    results_dict = {}

    for threshold in thresholds:
        print(f"\n{'=' * 60}")
        print(f"Threshold: {threshold}")
        print(f"{'=' * 60}")
        tr = compute_threshold_metrics(
            threshold=threshold,
            zero_clause_slugs=zero_clause_slugs,
            sample_slugs=sample_slugs_set,
            gold_slugs=gold_slugs,
            logical_root=args.logical_root,
            gold_logical_root=gold_logical_root,
            physical_root=args.physical_root,
            output_root=args.output_root,
            gold_corpus_root=gold_corpus_root,
        )
        results_dict[str(threshold)] = tr

    output = {
        "schema_version": "dse024_threshold_experiment.v2",
        "date": "2026-06-04",
        "task_id": "DSE-024",
        "thresholds_tested": thresholds,
        "gold_slugs_count": len(gold_slugs),
        "zero_clause_count": len(zero_clause_slugs),
        "logical_root": args.logical_root,
        "gold_logical_root": gold_logical_root,
        "results": results_dict,
    }

    _write_json(args.json_output, output)
    print(f"\nJSON output: {args.json_output}")

    write_md_report(output, args.md_output)
    print(f"Markdown output: {args.md_output}")
    return 0


# ── markdown report ──────────────────────────────────────────────────────


def write_md_report(output: dict, md_path: str):
    lines = []
    results = output.get("results", {})
    thresholds = output.get("thresholds_tested", [])

    lines.append("# DSE-024 Phase C0: Threshold Experiment Results")
    lines.append("")
    lines.append(f"**Date:** 2026-06-04")
    lines.append(f"**Zero-clause policies:** {output.get('zero_clause_count', 0)}")
    lines.append(f"**Gold policies evaluated:** {output.get('gold_slugs_count', 0)}")
    lines.append(f"**Thresholds tested:** {', '.join(str(t) for t in thresholds)}")
    lines.append(f"**Logical root (zero-clause analysis):** `{output.get('logical_root', 'N/A')}`")
    lines.append(
        f"**Gold logical root (gold heading eval):** `{output.get('gold_logical_root', 'N/A')}`"
    )
    lines.append("")

    # ── Summary comparison table ──
    lines.append("## Summary Comparison Across Thresholds")
    lines.append("")
    hdr = "| Metric | t=0.45 | t=0.475 | t=0.50 (current) |"
    sep = "|--------|--------|---------|-------------------|"
    lines.append(hdr)
    lines.append(sep)

    def _s(res, key):
        s = results.get(str(res), {})
        sm = s.get("summary", {})
        return sm.get(key, 0)

    for metric, label in [
        ("processed", "Processed"),
        ("with_at_least_1_accepted", "≥1 Heading"),
        ("with_at_least_5_accepted", "≥5 Headings"),
        ("total_accepted_all_policies", "Total Accepted"),
        ("total_toc_risk", "TOC Risk"),
        ("total_list_item_risk", "List/Item Risk"),
    ]:
        vals = [str(_s(t, metric)) for t in thresholds]
        lines.append(f"| {label} | {' | '.join(vals)} |")

    lines.append("")

    # ── Classification breakdown ──
    lines.append("### Candidate Classification (Zero-Clause Policies)")
    lines.append("")
    hdr2 = "| Classification | t=0.45 | t=0.475 | t=0.50 |"
    sep2 = "|---------------|--------|---------|--------|"
    lines.append(hdr2)
    lines.append(sep2)

    all_classes = set()
    for t in thresholds:
        agg = _s(t, "classifications_agg")
        if agg:
            all_classes.update(agg.keys())

    for cls in sorted(all_classes):
        vals = []
        for t in thresholds:
            agg = _s(t, "classifications_agg")
            vals.append(str(agg.get(cls, 0)))
        lines.append(f"| {cls} | {' | '.join(vals)} |")

    lines.append("")

    # ── False-Positive Risk ──
    lines.append("## False-Positive Risk Assessment")
    lines.append("")
    for t in thresholds:
        s = _s(t, "total_accepted_all_policies")
        toc = _s(t, "total_toc_risk")
        li = _s(t, "total_list_item_risk")
        toc_pct = round(100 * toc / s, 1) if s else 0
        li_pct = round(100 * li / s, 1) if s else 0
        lines.append(
            f"- **t={t}:** {toc} TOC candidates ({toc_pct}%), "
            f"{li} list/item candidates ({li_pct}%) out of {s} total"
        )

    lines.append("")

    # ── Gold heading eval ──
    lines.append("## Gold Heading Scorer Eval Results")
    lines.append("")
    lines.append("| Threshold | Precision | Recall | F1 | FP | FN | Status |")
    lines.append("|-----------|-----------|--------|----|----|-----|--------|")

    for t in thresholds:
        ge = results.get(str(t), {}).get("gold_heading_eval", {})
        if ge and ge.get("policy_results"):
            pr_list = ge["policy_results"]
            total_tp = sum(r.get("metrics", {}).get("true_positives", 0) for r in pr_list)
            total_fp = sum(r.get("metrics", {}).get("false_positives", 0) for r in pr_list)
            total_fn = sum(r.get("metrics", {}).get("false_negatives", 0) for r in pr_list)
            total_gold = sum(
                r.get("metrics", {}).get("total_gold_visual_headings", 0) for r in pr_list
            )
            total_cands = sum(
                r.get("metrics", {}).get("total_candidates_above_threshold", 0) for r in pr_list
            )
            p = round(total_tp / total_cands * 100, 1) if total_cands else 0
            r_val = round(total_tp / total_gold * 100, 1) if total_gold else 0
            f1 = round(2 * p * r_val / (p + r_val), 1) if (p + r_val) > 0 else 0
            passed = sum(1 for r in pr_list if r.get("status") == "passed")
            status_str = f"{passed}/{len(pr_list)} passed"
            lines.append(
                f"| {t} | {p}% | {r_val}% | {f1} | {total_fp} | {total_fn} | {status_str} |"
            )
        else:
            lines.append(f"| {t} | N/A | N/A | N/A | N/A | N/A | not run |")

    lines.append("")

    # ── Top newly accepted ──
    lines.append("## Top 20 Newly Accepted Candidates (across all thresholds)")
    lines.append("")
    for t in thresholds:
        top20 = results.get(str(t), {}).get("top_20_new_across_policies", [])
        lines.append(f"### Threshold {t}")
        lines.append("")
        if top20:
            lines.append("| # | Slug | Text | Score | Page | Classification |")
            lines.append("|---|------|------|-------|------|----------------|")
            for i, c in enumerate(top20[:20], 1):
                lines.append(
                    f"| {i} | {c['slug'][:40]} | {c['text'][:55]} "
                    f"| {c['score']} | {c['page']} | {c['classification']} |"
                )
        else:
            lines.append("_No candidates accepted at this threshold._")
        lines.append("")

    # ── Sample policy deep-dive ──
    lines.append("## Sample Policy Details")
    lines.append("")
    lines.append(
        "For each of the 20 Phase B sample policies, this shows how many "
        "headings would be accepted at each threshold."
    )
    lines.append("")
    lines.append("| Slug | t=0.45 | t=0.475 | t=0.50 | TOC risk | List risk |")
    lines.append("|------|--------|---------|--------|----------|-----------|")

    # Build per-slug cross-threshold table
    sample_slugs_seen = set()
    for t in thresholds:
        sd = results.get(str(t), {}).get("sample_details", {})
        for slug, data in sd.items():
            if slug not in sample_slugs_seen:
                sample_slugs_seen.add(slug)

    for slug in sorted(sample_slugs_seen):
        vals = []
        for t in thresholds:
            sd = results.get(str(t), {}).get("sample_details", {})
            data = sd.get(slug, {})
            vals.append(str(data.get("accepted", 0)))
        ref_data = results.get(str(thresholds[0]), {}).get("sample_details", {}).get(slug, {})
        toc_r = ref_data.get("toc_risk_count", "?")
        li_r = ref_data.get("list_item_risk_count", "?")
        lines.append(f"| {slug[:45]} | {' | '.join(vals)} | {toc_r} | {li_r} |")

    lines.append("")

    # ── Recommendation ──
    lines.append("## Recommendation")
    lines.append("")

    # Compute recommendation based on data
    s45 = results.get("0.45", {}).get("summary", {})
    s475 = results.get("0.475", {}).get("summary", {})

    fp_ratio_45 = (s45.get("total_toc_risk", 0) + s45.get("total_list_item_risk", 0)) / max(
        1, s45.get("total_accepted_all_policies", 1)
    )
    fp_ratio_475 = (s475.get("total_toc_risk", 0) + s475.get("total_list_item_risk", 0)) / max(
        1, s475.get("total_accepted_all_policies", 1)
    )

    gain_45 = s45.get("with_at_least_1_accepted", 0)
    gain_475 = s475.get("with_at_least_1_accepted", 0)
    current = results.get(str(thresholds[-1]), {}).get("summary", {})
    current_gain = current.get("with_at_least_1_accepted", 0)

    lines.append("### Data-Driven Assessment")
    lines.append("")
    lines.append(
        f"- **t=0.50 (current):** {current_gain}/{s45.get('processed', 0)} zero-clause policies have ≥1 heading"
    )
    lines.append(
        f"- **t=0.475:** {gain_475}/{s45.get('processed', 0)} policies gain ≥1 heading "
        f"(+{gain_475 - current_gain} from t=0.50)"
    )
    lines.append(
        f"- **t=0.45:** {gain_45}/{s45.get('processed', 0)} policies gain ≥1 heading "
        f"(+{gain_45 - current_gain} from t=0.50)"
    )
    lines.append(
        f"- FP ratio at t=0.45: {round(fp_ratio_45 * 100, 1)}% of accepted candidates "
        f"are TOC/list/table noise"
    )
    lines.append(f"- FP ratio at t=0.475: {round(fp_ratio_475 * 100, 1)}%")

    # Gold eval comparison (keys are str(float), so 0.50 -> '0.5')
    t50_key = str(thresholds[-1])
    t45_key = str(thresholds[0])
    ge50 = results.get(t50_key, {}).get("gold_heading_eval", {})
    ge45 = results.get(t45_key, {}).get("gold_heading_eval", {})
    if ge50 and ge45:

        def _agg_precision(ge):
            if not ge:
                return (0, 0, 0)
            prs = ge.get("policy_results", [])
            tp = sum(r.get("metrics", {}).get("true_positives", 0) for r in prs)
            fp = sum(r.get("metrics", {}).get("false_positives", 0) for r in prs)
            fn = sum(r.get("metrics", {}).get("false_negatives", 0) for r in prs)
            return (tp, fp, fn)

        tp50, fp50, fn50 = _agg_precision(ge50)
        tp45, fp45, fn45 = _agg_precision(ge45)
        lines.append(f"")
        lines.append(f"**Gold heading eval impact:**")
        lines.append(f"- t=0.50: TP={tp50} FP={fp50} FN={fn50}")
        lines.append(
            f"- t=0.45: TP={tp45} FP={fp45} FN={fn45} (+{tp45 - tp50} TP, +{fp45 - fp50} FP)"
        )

    lines.append("")
    lines.append("### Recommendation")
    lines.append("")

    # Logic for recommendation
    if gain_45 == current_gain:
        recommendation = (
            "No threshold change needed — current threshold already captures all possible headings."
        )
        fp_note = ""
    elif gain_45 > current_gain and fp_ratio_45 > 0.5:
        recommendation = "Feature-level fixes first, no threshold change."
        fp_note = (
            f"Threshold 0.45 would help {gain_45 - current_gain} additional policies, "
            f"but {round(fp_ratio_45 * 100, 1)}% of newly accepted candidates are TOC/list/table noise. "
            f"Without TOC/list suppression, lowering the threshold would introduce many false-positive headings."
        )
    elif gain_45 > current_gain and fp_ratio_45 > 0.25:
        recommendation = "Threshold change only with TOC/list suppression."
        fp_note = (
            f"Threshold 0.45 helps {gain_45 - current_gain} additional policies. "
            f"FP ratio is {round(fp_ratio_45 * 100, 1)}% — moderate noise. "
            f"Add TOC-dot detection and list-item suppression before or alongside threshold change."
        )
    elif gain_45 > current_gain:
        recommendation = "Threshold-only change is safe."
        fp_note = (
            f"Threshold 0.45 helps {gain_45 - current_gain} additional policies. "
            f"FP ratio is {round(fp_ratio_45 * 100, 1)}% — low noise. "
            f"Threshold reduction can proceed without additional suppression."
        )
    else:
        recommendation = "Mixed approach — threshold reduction + feature improvements."
        fp_note = (
            f"Threshold 0.45 helps some policies but additional feature-level improvements "
            f"(letter-numbering patterns, sentence-case penalty reduction) are needed "
            f"for the remaining hard cases."
        )

    lines.append(f"**{recommendation}**")
    lines.append("")
    if fp_note:
        lines.append(fp_note)
        lines.append("")

    lines.append("### Next Steps")
    lines.append("")
    if recommendation.startswith("No threshold change"):
        lines.append("1. Skip threshold change.")
        lines.append(
            "2. Focus on feature-level improvements: letter-numbering patterns,"
            " sentence-case penalty reduction, TOC suppression."
        )
    elif recommendation.startswith("Feature-level"):
        lines.append("1. Implement TOC suppression (has_toc_dots penalty).")
        lines.append(
            "2. Implement list-item suppression or all-caps-fp penalty for short numbered items."
        )
        lines.append("3. Re-run experiment to verify reduced FP ratio.")
        lines.append("4. If FP ratio drops below 25%, proceed with threshold change.")
    elif recommendation.startswith("Threshold change only"):
        lines.append("1. Lower heading threshold from 0.50 to 0.45.")
        lines.append(
            "2. Verify no regression on 20 gold policies (gold heading eval must not regress)."
        )
        lines.append("3. Run full DSE-020 re-execution to confirm zero-clause reduction.")
    else:
        lines.append("1. Lower heading threshold from 0.50 to 0.45 (immediate gain).")
        lines.append("2. Add TOC suppression / list-item suppression simultaneously.")
        lines.append(
            "3. Add letter-numbering patterns (`A.`, `B.`, `Part I`) as separate improvement."
        )
        lines.append("4. Re-run gold evals after each change to confirm no regression.")

    lines.append("")
    lines.append("### Warning")
    lines.append("")
    lines.append(
        "**Do NOT commit gold eval temp files or interim scorer outputs.** "
        "The `data/interim/dse024/` directory contains temporary generated "
        "heading_candidates.json files that should be cleaned up after review. "
        "Only the final reports in `data/reports/` should be committed."
    )

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Markdown report: {md_path}")


if __name__ == "__main__":
    raise SystemExit(main())
