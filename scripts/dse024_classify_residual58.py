#!/usr/bin/env python3
"""DSE-024 Phase E3A: Classify remaining 58 zero-clause policies after E2 section tree rebuild."""

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPORT_DIR = Path("data/reports")
MANIFEST_PATH = Path("data/manifests/dse020_run_manifest_v1.json")
TRIAGE_PATH = Path("data/reports/dse020_scale_triage_report_v1.json")
LOGICAL_ROOT = Path("data/interim/dse020/logical")
PHYSICAL_ROOT = Path("data/interim/dse020/physical")

NON_POLICY_KEYWORDS = ["rider", "prospectus", "brochure"]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_heading_top_candidates(hd, n=10):
    candidates = hd.get("candidates", [])
    scored = [c for c in candidates if c.get("score") is not None]
    scored.sort(key=lambda x: x["score"], reverse=True)
    top = []
    for c in scored[:n]:
        top.append(
            {
                "text": c["text"][:120],
                "score": round(c["score"], 4),
                "page": c.get("page_number"),
                "features": list(c.get("features", {}).keys())[:5],
                "feature_contributions": {
                    k: round(v, 4)
                    for k, v in c.get("feature_contributions", {}).items()
                    if abs(v) > 0.05
                },
            }
        )
    return top


def classify_policy(slug, hd, me, collision_set):
    doc_type = me.get("document_type", "unknown")
    pages = me.get("page_count", 0) or 0

    total_headings = hd.get("total_headings", 0) or 0
    fallback = hd.get("fallback_promotions", 0) or 0

    scores = [c["score"] for c in hd.get("candidates", []) if c.get("score") is not None]
    max_score = max(scores) if scores else -999
    above_03 = sum(1 for s in scores if s > 0.3)
    above_025 = sum(1 for s in scores if s > 0.25)
    above_02 = sum(1 for s in scores if s > 0.2)
    total_candidates = len(hd.get("candidates", []))

    # Collision (duplicate hash)
    if slug in collision_set:
        return "duplicate_or_superseded"

    # Non-policy / rider / brochure (by doc_type or keyword)
    is_brochure = doc_type == "brochure"
    kw_match = any(kw in slug.lower() for kw in NON_POLICY_KEYWORDS)
    if is_brochure or kw_match:
        return "non_policy_or_rider"

    # Section tree fail (should not happen post-E2, but guard)
    if fallback > 0 and total_headings == 0:
        return "section_tree_fail"

    # Physical text issue: max_score <= 0 — pdfplumber produced garbled/noisy extraction
    if max_score <= 0:
        return "physical_text_issue"

    # Unsupported format: very short or product-list documents
    if pages <= 6 or total_candidates < 20:
        return "unsupported_format"

    # Heading miss: plausible near-miss headings below t=0.5
    if max_score > 0.3 or above_03 >= 3:
        return "heading_miss"
    if max_score > 0.25 and above_025 >= 5:
        return "heading_miss"
    if max_score > 0.2 and above_02 >= 8:
        return "heading_miss"

    # Very low candidate quality despite reasonable page count — physical issue
    if max_score <= 0.2 and pages > 6:
        return "physical_text_issue"

    return "manual_review_required"


def main():
    triage = load_json(TRIAGE_PATH)
    manifest = load_json(MANIFEST_PATH)
    zero_clauses = triage["metrics"]["zero_clauses"]
    print(f"Classifying {len(zero_clauses)} zero-clause policies...", file=sys.stderr)

    ml = {p["slug"]: p for p in manifest["policies"]}

    # Collision set
    hash_map = defaultdict(list)
    for p in manifest["policies"]:
        h = p.get("file_hash", "")
        hash_map[h].append(p["slug"])
    collision_set = set()
    for h, slugs in hash_map.items():
        if len(slugs) > 1:
            collision_set.update(slugs)

    results = []
    for slug in zero_clauses:
        try:
            hd = load_json(LOGICAL_ROOT / slug / "heading_candidates.json")
        except FileNotFoundError as e:
            results.append(
                {
                    "slug": slug,
                    "error": f"Missing heading_candidates.json: {e}",
                    "classification": "manual_review_required",
                }
            )
            continue

        me = ml.get(slug, {})
        pages = me.get("page_count", 0) or 0
        total_candidates = len(hd.get("candidates", []))
        classification = classify_policy(slug, hd, me, collision_set)

        scores = [c["score"] for c in hd.get("candidates", []) if c.get("score") is not None]
        max_score = round(max(scores), 4) if scores else -999
        total_headings = hd.get("total_headings", 0) or 0
        fallback = hd.get("fallback_promotions", 0) or 0
        top_candidates = get_heading_top_candidates(hd, 10)
        above_03 = sum(1 for s in scores if s > 0.3)
        above_025 = sum(1 for s in scores if s > 0.25)
        above_02 = sum(1 for s in scores if s > 0.2)

        # Evidence
        evidence_parts = []
        if classification == "duplicate_or_superseded":
            dup_slugs = [s for s in hash_map.get(me.get("file_hash", ""), []) if s != slug]
            evidence_parts.append(f"Duplicate hash with: {', '.join(dup_slugs[:3])}")
        elif classification == "non_policy_or_rider":
            dt = me.get("document_type", "unknown")
            evidence_parts.append(f"Document type: {dt}")
            kw = [kw for kw in NON_POLICY_KEYWORDS if kw in slug.lower()]
            if kw:
                evidence_parts.append(f"Keyword match: {', '.join(kw)}")
        elif classification == "heading_miss":
            evidence_parts.append(f"max_score={max_score}, >0.3={above_03}")
            if top_candidates:
                evidence_parts.append(
                    f'Top: "{top_candidates[0]["text"]}" ({top_candidates[0]["score"]})'
                )
        elif classification == "physical_text_issue":
            evidence_parts.append(
                f"max_score={max_score}, >0.3={above_03}, >0.25={above_025}, >0.2={above_02}"
            )
            if top_candidates:
                evidence_parts.append(
                    f'Top: "{top_candidates[0]["text"]}" ({top_candidates[0]["score"]})'
                )
        elif classification == "unsupported_format":
            evidence_parts.append(
                f"pages={pages}, candidates={total_candidates}, max_score={max_score}"
            )
        elif classification == "section_tree_fail":
            evidence_parts.append(f"fallback={fallback}, headings={total_headings}")
        else:
            evidence_parts.append(f"max_score={max_score}, >0.3={above_03}, pages={pages}")

        evidence = "; ".join(evidence_parts)

        action_map = {
            "duplicate_or_superseded": "Deduplicate: keep canonical slug, drop duplicate",
            "non_policy_or_rider": "Filter from extraction pipeline or handle separately",
            "heading_miss": "Add format-specific heading pattern additions or fallback refinement",
            "physical_text_issue": "Inspect pdfplumber extraction quality; may need OCR or alternate parser",
            "unsupported_format": "Requires separate parser strategy or document-level filtering",
            "section_tree_fail": "Investigate section tree builder for this specific format (unexpected post-E2)",
            "manual_review_required": "Manually inspect PDF to determine appropriate strategy",
        }

        confidence_map = {
            "duplicate_or_superseded": "high",
            "non_policy_or_rider": "high",
            "heading_miss": "medium",
            "physical_text_issue": "medium",
            "unsupported_format": "medium",
            "section_tree_fail": "low",
            "manual_review_required": "low",
        }

        results.append(
            {
                "slug": slug,
                "insurer": me.get("insurer", "unknown"),
                "filename": me.get("filename", slug),
                "uin": me.get("uin", ""),
                "pages": me.get("page_count", 0),
                "zero_headings": total_headings == 0,
                "zero_clauses": True,
                "total_headings": total_headings,
                "fallback_promotions": fallback,
                "visual_headings": 0,
                "max_score": max_score,
                "candidates_above_0_3": above_03,
                "candidates_above_0_25": above_025,
                "candidates_above_0_2": above_02,
                "top_candidates": top_candidates,
                "classification": classification,
                "recommended_action": action_map.get(classification, "Review"),
                "confidence": confidence_map.get(classification, "low"),
                "evidence": evidence,
            }
        )

    # Summary
    cls_counts = Counter(r["classification"] for r in results)
    insurer_counts = Counter(r["insurer"] for r in results)
    cls_insurer = defaultdict(lambda: defaultdict(int))
    for r in results:
        cls_insurer[r["classification"]][r["insurer"]] += 1

    # Top heading_miss candidates by max_score
    parser_fix_candidates = sorted(
        [r for r in results if r["classification"] in ("heading_miss",)],
        key=lambda x: x["max_score"],
        reverse=True,
    )

    report = {
        "report_type": "dse024_residual58_classification.v1",
        "task_id": "DSE-024",
        "date": "2026-06-04",
        "phase": "E3A",
        "total_policies": len(results),
        "pipeline_context": "Post-E2 section tree rebuild. All section_tree_fail policies resolved.",
        "classification_summary": dict(cls_counts.most_common()),
        "insurer_summary": dict(insurer_counts.most_common()),
        "classification_by_insurer": {
            k: dict(sorted(v.items(), key=lambda x: -x[1])) for k, v in sorted(cls_insurer.items())
        },
        "parser_fix_candidates": [
            {
                "slug": r["slug"],
                "insurer": r["insurer"],
                "classification": r["classification"],
                "max_score": r["max_score"],
                "pages": r["pages"],
                "candidates_above_0_3": r["candidates_above_0_3"],
                "candidates_above_0_25": r["candidates_above_0_25"],
                "top_candidate_text": r["top_candidates"][0]["text"] if r["top_candidates"] else "",
                "top_candidate_score": r["top_candidates"][0]["score"]
                if r["top_candidates"]
                else None,
                "recommended_action": r["recommended_action"],
                "confidence": r["confidence"],
            }
            for r in parser_fix_candidates
        ],
        "policies": results,
    }

    # Write JSON
    json_path = REPORT_DIR / "dse024_residual58_classification_v1.json"
    json_path.write_text(json.dumps(report, indent=2, default=str))
    print(f"Wrote {json_path}", file=sys.stderr)

    # Write MD
    md_path = REPORT_DIR / "dse024_residual58_classification_v1.md"
    with open(md_path, "w") as f:
        f.write("# DSE-024 Phase E3A — Residual 58 Zero-Clause Classification\n\n")
        f.write("Date: 2026-06-04\n\n")
        f.write("## Context\n\n")
        f.write(
            "After DSE-024 Phase E2 section tree rebuild, 44 section_tree_fail policies were resolved. "
            "This report classifies the remaining **58 zero-clause policies** into actionable buckets.\n\n"
        )
        f.write("## Summary\n\n")
        f.write(f"Total policies classified: **{len(results)}**\n\n")
        f.write("| Classification | Count | Action |\n")
        f.write("|---|---|---|\n")
        action_guide = {
            "heading_miss": "Parser fix needed — add format-specific heading patterns",
            "duplicate_or_superseded": "Corpus filter — deduplicate by file hash",
            "non_policy_or_rider": "Corpus filter — exclude from extraction",
            "physical_text_issue": "Parser fix needed — investigate pdfplumber extraction",
            "unsupported_format": "Corpus filter — document-level filtering",
            "manual_review_required": "Manual review needed",
            "section_tree_fail": "Investigate (unexpected post-E2)",
        }
        for cls, cnt in cls_counts.most_common():
            guide = action_guide.get(cls, "")
            f.write(f"| {cls} | {cnt} | {guide} |\n")
        f.write("\n")

        f.write("**Fix parser vs filter corpus breakdown:**\n\n")
        fix_buckets = {"heading_miss", "physical_text_issue", "section_tree_fail"}
        filter_buckets = {"duplicate_or_superseded", "non_policy_or_rider", "unsupported_format"}
        fix_count = sum(cnt for cls, cnt in cls_counts.items() if cls in fix_buckets)
        filter_count = sum(cnt for cls, cnt in cls_counts.items() if cls in filter_buckets)
        review_count = sum(
            cnt for cls, cnt in cls_counts.items() if cls == "manual_review_required"
        )
        f.write(f"- **Fix parser:** {fix_count} (heading_miss + physical_text_issue)\n")
        f.write(
            f"- **Filter/defer corpus:** {filter_count} (duplicate + non_policy + unsupported)\n"
        )
        f.write(f"- **Manual review needed:** {review_count}\n\n")

        f.write("## Parser-Fix Candidates (heading_miss, sorted by max_score)\n\n")
        f.write(
            "Highest-confidence cases where heading scorer pattern additions could resolve zero-clause.\n\n"
        )
        f.write("| # | Insurer | Max Score | >0.3 | Pages | Top Candidate | Confidence |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for i, r in enumerate(parser_fix_candidates, 1):
            tc = r["top_candidates"][0] if r["top_candidates"] else {"text": "", "score": ""}
            f.write(
                f"| {i} | {r['insurer']} | {r['max_score']} | {r['candidates_above_0_3']} "
                f'| {r["pages"]} | "{tc["text"][:50]}" ({tc["score"]}) | {r["confidence"]} |\n'
            )
        f.write("\n")

        f.write("## Insurer Distribution\n\n")
        f.write("| Insurer | Zero-Clause Policies |\n")
        f.write("|---|---:|\n")
        for ins, cnt in insurer_counts.most_common():
            f.write(f"| {ins} | {cnt} |\n")
        f.write("\n")

        f.write("## Classification by Insurer\n\n")
        for cls, _ in cls_counts.most_common():
            f.write(f"### {cls}\n\n")
            f.write("| Insurer | Count |\n")
            f.write("|---|---:|\n")
            for ins, cnt in sorted(cls_insurer[cls].items(), key=lambda x: -x[1]):
                f.write(f"| {ins} | {cnt} |\n")
            f.write("\n")

        f.write("## Per-Policy Detail\n\n")
        f.write(
            "| Slug | Insurer | Pages | Max Score | >0.3 | Classification | Confidence | Evidence |\n"
        )
        f.write("|---|---|---|---|---|---|---|---|\n")
        for r in sorted(results, key=lambda x: (x["classification"], -x["max_score"])):
            slug_short = r["slug"][:45]
            ins_short = r["insurer"][:15]
            f.write(
                f"| {slug_short} | {ins_short} | {r['pages']} | {r['max_score']} "
                f"| {r['candidates_above_0_3']} | {r['classification']} | {r['confidence']} "
                f"| {r['evidence'][:80]} |\n"
            )
        f.write("\n")

    print(f"Wrote {md_path}", file=sys.stderr)

    # Validation
    unclassified = [r for r in results if r["classification"] == "unclassified"]
    if unclassified:
        print(f"WARNING: {len(unclassified)} unclassified policies!", file=sys.stderr)
    print(f"All {len(results)} classified, {len(unclassified)} unclassified.", file=sys.stderr)
    print(f"  Fix parser: {fix_count}", file=sys.stderr)
    print(f"  Filter corpus: {filter_count}", file=sys.stderr)
    print(f"  Manual review: {review_count}", file=sys.stderr)

    return report


if __name__ == "__main__":
    report = main()
    print("\nClassification Summary:")
    for cls, cnt in Counter(r["classification"] for r in report["policies"]).most_common():
        print(f"  {cls}: {cnt}")
