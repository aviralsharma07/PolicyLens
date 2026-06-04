#!/usr/bin/env python3
"""DSE-024: Classify remaining 110 zero-clause policies into actionable buckets."""

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPORT_DIR = Path("data/reports")
MANIFEST_PATH = Path("data/manifests/dse020_run_manifest_v1.json")
TRIAGE_PATH = Path("data/reports/dse020_scale_triage_report_v1.json")
LOGICAL_ROOT = Path("data/interim/dse020/logical")

NON_POLICY_KEYWORDS = ["rider", "prospectus", "summary", "annexure"]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_heading_top_candidates(hd, n=10):
    candidates = hd.get("candidates", [])
    scored = [c for c in candidates if c.get("score") is not None]
    scored.sort(key=lambda x: x["score"], reverse=True)
    top = []
    for c in scored[:n]:
        feats = c.get("features", {})
        top.append(
            {
                "text": c["text"][:100],
                "score": round(c["score"], 4),
                "page": c.get("page_number"),
                "features": list(feats.keys())[:5],
                "feature_contributions": {
                    k: round(v, 4)
                    for k, v in c.get("feature_contributions", {}).items()
                    if abs(v) > 0.05
                },
            }
        )
    return top


def classify_policy(slug, hd, st, manifest_entry, collision_set):
    doc_type = manifest_entry.get("document_type", "unknown")
    insurer = manifest_entry.get("insurer", "unknown")
    uin = manifest_entry.get("uin", "")
    pages = manifest_entry.get("page_count", 0)

    total_headings = hd.get("total_headings", 0)
    fallback = hd.get("fallback_promotions", 0) or 0
    visual_headings = st.get("total_visual_headings", 0)
    total_clauses = st.get("total_clauses", 0)

    scores = [c["score"] for c in hd.get("candidates", []) if c.get("score") is not None]
    max_score = max(scores) if scores else -999
    above_03 = sum(1 for s in scores if s > 0.3)
    above_025 = sum(1 for s in scores if s > 0.25)
    above_02 = sum(1 for s in scores if s > 0.2)

    # Check collision (duplicate hash)
    if slug in collision_set:
        return "duplicate_or_superseded"

    # Non-policy / rider
    is_brochure = doc_type == "brochure"
    kw_match = any(kw in slug.lower() for kw in NON_POLICY_KEYWORDS)
    if is_brochure or kw_match:
        return "non_policy_or_rider"

    # Section tree fail: fallback promoted headings exist but tree wasn't rebuilt
    if fallback > 0 and visual_headings == 0:
        return "section_tree_fail"

    # Heading miss: zero-heading despite plausible near-miss candidates
    if total_headings == 0:
        if max_score > 0.3 or above_025 >= 3:
            return "heading_miss"
        if max_score > 0.2 and above_02 >= 5:
            return "heading_miss"
        if max_score <= 0.2:
            # Very low scores — might be physical text issue or unsupported format
            if pages <= 6 or len(scores) < 20:
                return "unsupported_format"
            return "needs_manual_review"

    # Fallback
    if total_clauses == 0 and total_headings > 0:
        return "section_tree_fail"

    return "needs_manual_review"


def main():
    triage = load_json(TRIAGE_PATH)
    manifest = load_json(MANIFEST_PATH)
    zero_clauses = triage["metrics"]["zero_clauses"]
    print(f"Classifying {len(zero_clauses)} zero-clause policies...", file=sys.stderr)

    # Build lookups
    ml = {p["slug"]: p for p in manifest["policies"]}

    # Build collision set: duplicate-hash policies
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
            st = load_json(LOGICAL_ROOT / slug / "section_tree.json")
        except FileNotFoundError as e:
            results.append(
                {
                    "slug": slug,
                    "error": f"Missing file: {e}",
                    "classification": "needs_manual_review",
                }
            )
            continue

        me = ml.get(slug, {})
        classification = classify_policy(slug, hd, st, me, collision_set)

        # Gather evidence fields
        total_headings = hd.get("total_headings", 0)
        fallback = hd.get("fallback_promotions", 0) or 0
        visual_headings = st.get("total_visual_headings", 0)
        total_clauses = st.get("total_clauses", 0)
        scores = [c["score"] for c in hd.get("candidates", []) if c.get("score") is not None]
        max_score = round(max(scores), 4) if scores else -999
        top_candidates = get_heading_top_candidates(hd, 10)

        # Build evidence note
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
            evidence_parts.append(
                f"max_score={max_score}, >0.3={sum(1 for s in scores if s > 0.3)}"
            )
            evidence_parts.append(
                f'Top candidate: "{top_candidates[0]["text"]}" (score={top_candidates[0]["score"]})'
                if top_candidates
                else "No candidates"
            )
        elif classification == "section_tree_fail":
            evidence_parts.append(
                f"fallback_headings={fallback}, visual_headings={visual_headings}"
            )
            if top_candidates:
                evidence_parts.append(
                    f'Top candidate: "{top_candidates[0]["text"]}" (score={top_candidates[0]["score"]})'
                )
        elif classification == "unsupported_format":
            evidence_parts.append(f"pages={me.get('page_count', 0)}, max_score={max_score}")
        else:
            evidence_parts.append(
                f"max_score={max_score}, headings={total_headings}/visual={visual_headings}"
            )

        evidence = "; ".join(evidence_parts)

        # Recommended action per bucket
        action_map = {
            "duplicate_or_superseded": "Deduplicate: keep canonical slug, drop duplicate",
            "non_policy_or_rider": "Exclude from extraction pipeline or handle separately",
            "heading_miss": "Add format-specific heading patterns or lower threshold with FP guard",
            "section_tree_fail": "Rebuild section tree after fallback promotion; reconnect pipeline",
            "unsupported_format": "Requires separate parser strategy or document-level filtering",
            "needs_manual_review": "Manually inspect PDF to determine appropriate parser strategy",
        }

        confidence_map = {
            "duplicate_or_superseded": "high",
            "non_policy_or_rider": "high",
            "section_tree_fail": "high",
            "heading_miss": "medium",
            "unsupported_format": "medium",
            "needs_manual_review": "low",
        }

        results.append(
            {
                "slug": slug,
                "insurer": me.get("insurer", "unknown"),
                "filename": me.get("filename", slug),
                "uin": me.get("uin", ""),
                "pages": me.get("page_count", 0),
                "zero_headings": total_headings == 0,
                "zero_clauses": total_clauses == 0,
                "total_headings": total_headings,
                "fallback_promotions": fallback,
                "visual_headings": visual_headings,
                "max_score": max_score,
                "top_candidates": top_candidates,
                "classification": classification,
                "recommended_action": action_map.get(classification, "Review"),
                "confidence": confidence_map.get(classification, "low"),
                "evidence": evidence,
            }
        )

    # Build summary
    cls_counts = Counter(r["classification"] for r in results)
    insurer_counts = Counter(r["insurer"] for r in results)
    cls_insurer = defaultdict(lambda: defaultdict(int))
    for r in results:
        cls_insurer[r["classification"]][r["insurer"]] += 1

    top_fix_candidates = sorted(
        [r for r in results if r["classification"] in ("heading_miss", "section_tree_fail")],
        key=lambda x: x["max_score"],
        reverse=True,
    )[:20]

    report = {
        "report_type": "dse024_residual_zero_clause_classification.v1",
        "task_id": "DSE-024",
        "date": "2026-06-04",
        "total_policies": len(results),
        "classification_summary": dict(cls_counts.most_common()),
        "insurer_summary": dict(insurer_counts.most_common()),
        "classification_by_insurer": {
            k: dict(sorted(v.items(), key=lambda x: -x[1])) for k, v in sorted(cls_insurer.items())
        },
        "top_20_parser_fix_candidates": [
            {
                "slug": r["slug"],
                "insurer": r["insurer"],
                "classification": r["classification"],
                "max_score": r["max_score"],
                "total_headings": r["total_headings"],
                "fallback_promotions": r["fallback_promotions"],
                "pages": r["pages"],
                "top_candidate_text": r["top_candidates"][0]["text"] if r["top_candidates"] else "",
                "top_candidate_score": r["top_candidates"][0]["score"]
                if r["top_candidates"]
                else None,
                "recommended_action": r["recommended_action"],
                "confidence": r["confidence"],
            }
            for r in top_fix_candidates
        ],
        "policies": results,
    }

    # Write JSON
    json_path = REPORT_DIR / "dse024_residual_zero_clause_classification_v1.json"
    json_path.write_text(json.dumps(report, indent=2, default=str))
    print(f"Wrote {json_path}", file=sys.stderr)

    # Write MD
    md_path = REPORT_DIR / "dse024_residual_zero_clause_classification_v1.md"
    with open(md_path, "w") as f:
        f.write("# DSE-024 Residual Zero-Clause Classification\n\n")
        f.write(f"Date: 2026-06-04\n\n")
        f.write("## Summary\n\n")
        f.write(f"Total zero-clause policies classified: **{len(results)}**\n\n")
        f.write("| Classification | Count |\n")
        f.write("|---|---:|\n")
        for cls, cnt in cls_counts.most_common():
            f.write(f"| {cls} | {cnt} |\n")
        f.write("\n")

        f.write("## Top Parser-Fix Candidates (Top 20)\n\n")
        f.write("Highest-confidence cases where parser changes could resolve zero-clause.\n\n")
        f.write(
            "| # | Insurer | Classification | Max Score | Headings | Fallback | Pages | Top Candidate |\n"
        )
        f.write("|---|---|---|---|---|---|---|---|\n")
        for i, r in enumerate(top_fix_candidates, 1):
            tc = r["top_candidates"][0] if r["top_candidates"] else {"text": "", "score": ""}
            f.write(
                f'| {i} | {r["insurer"]} | {r["classification"]} | {r["max_score"]} | {r["total_headings"]} | {r["fallback_promotions"]} | {r["pages"]} | "{tc["text"][:50]}" ({tc["score"]}) |\n'
            )
        f.write("\n")

        f.write("## Top Insurer Clusters\n\n")
        f.write("| Insurer | Zero-Clause |\n")
        f.write("|---|---:|\n")
        for ins, cnt in insurer_counts.most_common():
            f.write(f"| {ins} | {cnt} |\n")
        f.write("\n")

        f.write("## Classification by Insurer\n\n")
        for cls in cls_counts:
            f.write(f"### {cls}\n\n")
            f.write("| Insurer | Count |\n")
            f.write("|---|---:|\n")
            for ins, cnt in sorted(cls_insurer[cls].items(), key=lambda x: -x[1]):
                f.write(f"| {ins} | {cnt} |\n")
            f.write("\n")

        f.write("## Per-Policy Detail\n\n")
        f.write(
            "| Slug | Insurer | Pages | Zero Headings | Max Score | Classification | Confidence |\n"
        )
        f.write("|---|---|---|---|---|---|---|\n")
        for r in sorted(results, key=lambda x: (x["classification"], -x["max_score"])):
            zh = "Y" if r["zero_headings"] else "N"
            f.write(
                f"| {r['slug'][:50]} | {r['insurer'][:20]} | {r['pages']} | {zh} | {r['max_score']} | {r['classification']} | {r['confidence']} |\n"
            )
        f.write("\n")

    print(f"Wrote {md_path}", file=sys.stderr)

    # Validation
    unclassified = [r for r in results if r["classification"] == "unclassified"]
    if unclassified:
        print(f"WARNING: {len(unclassified)} unclassified policies!", file=sys.stderr)
    print(f"All {len(results)} classified, {len(unclassified)} unclassified.", file=sys.stderr)

    return report


if __name__ == "__main__":
    report = main()
    # Print classification summary to stdout for quick review
    print("\nClassification Summary:")
    for cls, cnt in Counter(r["classification"] for r in report["policies"]).most_common():
        print(f"  {cls}: {cnt}")
