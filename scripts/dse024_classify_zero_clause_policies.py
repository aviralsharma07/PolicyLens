#!/usr/bin/env python3
"""
DSE-024 Phase A: Classify 132 zero-clause/zero-heading policies from DSE-020
scale triage by root cause.

Categories:
  NON_POLICY     — not a policy wording (brochure, CIS, prospectus, product list)
  HEADING_MISS   — heading scorer failed to produce any candidate above threshold
  SECTION_FAIL   — headings exist but section tree produced zero clauses
  PHYSICAL_BAD   — pdfplumber extracted garbled/missing text
  DUPLICATE      — same hash as another entry; non-canonical duplicate
  UNSUPPORTED    — tables-only / non-standard layout / add-on
  UNKNOWN        — insufficient evidence

Usage:
  PYTHONPATH=. .venv/bin/python scripts/dse024_classify_zero_clause_policies.py \
    --triage data/reports/dse020_scale_triage_report_v1.json \
    --manifest data/manifests/dse020_run_manifest_v1.json \
    --interim-root data/interim/dse020 \
    --json-output data/reports/dse024_zero_clause_classification_v1.json \
    --md-output data/reports/dse024_zero_clause_classification_v1.md
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict


NON_POLICY_SLUG_TOKENS = frozenset(
    {
        "brochure",
        "prospectus",
        "sales_literature",
        "product_list",
        "cis",
    }
)


def get_heading_max_score(path):
    """Parse heading_candidates.json and return max score without keeping full data."""
    max_score = 0.0
    count = 0
    try:
        with open(path) as f:
            data = json.load(f)
        for c in data.get("candidates", []):
            score = c.get("score", 0)
            count += 1
            if score > max_score:
                max_score = score
    except Exception:
        pass
    return max_score, count


def load_tables(path):
    """Load tables JSON and return table count."""
    try:
        with open(path) as f:
            data = json.load(f)
        tables = data.get("tables", data.get("extracted_tables", []))
        return len(tables)
    except Exception:
        return 0


def load_facts(path):
    """Load fact_candidates.json and return candidate count."""
    try:
        with open(path) as f:
            data = json.load(f)
        cands = data.get("candidates", data.get("fact_candidates", []))
        return len(cands)
    except Exception:
        return 0


def classify(
    slug,
    manifest_entry,
    max_heading_score,
    heading_count,
    section_data,
    tables_count,
    facts_count,
    duplicate_hash_groups,
):
    """Classify a single policy slug into exactly one category."""

    document_type = (manifest_entry or {}).get("document_type", "")
    triage_flags = (manifest_entry or {}).get("triage_flags", [])
    document_id = (manifest_entry or {}).get("document_id", "")
    page_count = (manifest_entry or {}).get("page_count", 0)

    # ── Rule 1: NON_POLICY (document_type or slug keywords) ──────
    if document_type == "brochure":
        return "NON_POLICY"

    slug_lower = slug.lower()
    for token in NON_POLICY_SLUG_TOKENS:
        if token in slug_lower:
            return "NON_POLICY"
    if slug_lower.startswith("non_policy_wordings"):
        return "NON_POLICY"

    # ── Rule 2: DUPLICATE (same hash as another entry) ───────────
    if document_id and duplicate_hash_groups.get(document_id):
        group = duplicate_hash_groups[document_id]
        if len(group) >= 2:
            sorted_group = sorted(group)
            if slug == sorted_group[-1]:
                return "DUPLICATE"

    # ── Rule 3: PHYSICAL_BAD ────────────────────────────────────
    if page_count == 0:
        return "PHYSICAL_BAD"
    if page_count < 2:
        return "PHYSICAL_BAD"

    # ── Read section tree data ──────────────────────────────────
    section_tree = section_data if section_data else {}
    total_clauses = section_tree.get("total_clauses", 0)
    total_sections = section_tree.get("total_sections", 0)

    # ── Rule 4: SECTION_FAIL ────────────────────────────────────
    if max_heading_score >= 0.5 and total_clauses == 0:
        return "SECTION_FAIL"

    # ── Rule 5: HEADING_MISS (heading scorer failed) ────────────
    if heading_count > 0 and max_heading_score < 0.5:
        # All zero-heading policies have many lines of text (known from DSE-020)
        return "HEADING_MISS"

    # ── Rule 6: UNSUPPORTED ─────────────────────────────────────
    if page_count < 5:
        return "UNSUPPORTED"

    # ── Fallback ────────────────────────────────────────────────
    return "UNKNOWN"


def build_duplicate_hash_groups(manifest_policies):
    """Build map of document_id -> list of slugs sharing that hash."""
    groups = defaultdict(list)
    for p in manifest_policies:
        h = p.get("document_id") or p.get("file_hash")
        if h:
            groups[h].append(p["slug"])
    return {h: slugs for h, slugs in groups.items() if len(slugs) > 1}


def recommend_sample(classifications):
    """Select 20 representative policies for Phase B deep inspection."""
    by_category = defaultdict(list)
    for c in classifications:
        by_category[c["category"]].append(c)

    sample = []
    seen_slugs = set()

    category_order = ["HEADING_MISS", "NON_POLICY", "DUPLICATE", "UNSUPPORTED", "UNKNOWN"]
    for cat in category_order:
        group = by_category.get(cat, [])
        if not group:
            continue
        group.sort(key=lambda x: -x["page_count"])
        candidates = [c for c in group if c["slug"] not in seen_slugs]
        if candidates:
            sample.append(candidates[0])
            seen_slugs.add(candidates[0]["slug"])

    remaining_slots = 20 - len(sample)
    if remaining_slots > 0:
        insurer_slugs = defaultdict(list)
        for c in by_category.get("HEADING_MISS", []):
            if c["slug"] not in seen_slugs:
                insurer_slugs[c["insurer"]].append(c)

        for insurer, candidates in sorted(insurer_slugs.items(), key=lambda x: -len(x[1])):
            if remaining_slots <= 0:
                break
            candidates.sort(key=lambda x: -x["page_count"])
            sample.append(candidates[0])
            seen_slugs.add(candidates[0]["slug"])
            remaining_slots -= 1

        if remaining_slots > 0:
            remaining = [c for c in classifications if c["slug"] not in seen_slugs]
            remaining.sort(key=lambda x: -x.get("_max_heading_score", 0))
            for c in remaining[:remaining_slots]:
                sample.append(c)
                seen_slugs.add(c["slug"])

    return sample[:20]


def main():
    parser = argparse.ArgumentParser(description="DSE-024 Phase A: Classify zero-clause policies")
    parser.add_argument("--triage", required=True, help="Path to DSE-020 triage report JSON")
    parser.add_argument("--manifest", required=True, help="Path to DSE-020 run manifest JSON")
    parser.add_argument("--interim-root", required=True, help="Root of DSE-020 interim outputs")
    parser.add_argument("--json-output", required=True, help="Path for JSON classification output")
    parser.add_argument("--md-output", required=True, help="Path for Markdown summary output")
    args = parser.parse_args()

    print(f"[dse024] Loading triage report: {args.triage}")
    with open(args.triage) as f:
        triage = json.load(f)
    zero_slugs = triage["metrics"]["zero_clauses"]
    print(f"[dse024] {len(zero_slugs)} zero-clause policies to classify")

    print(f"[dse024] Loading manifest: {args.manifest}")
    with open(args.manifest) as f:
        manifest = json.load(f)
    slug_map = {p["slug"]: p for p in manifest["policies"]}

    print(f"[dse024] Building duplicate hash groups...")
    duplicate_groups = build_duplicate_hash_groups(manifest["policies"])

    classifications = []
    errors = []

    for idx, slug in enumerate(zero_slugs):
        if (idx + 1) % 20 == 0:
            print(f"[dse024]  ... {idx + 1}/{len(zero_slugs)}")

        manifest_entry = slug_map.get(slug, {})
        page_count = manifest_entry.get("page_count", 0)

        # Headings
        heading_path = os.path.join(args.interim_root, "logical", slug, "heading_candidates.json")
        max_heading_score, heading_count = (
            get_heading_max_score(heading_path) if os.path.exists(heading_path) else (0.0, 0)
        )

        # Section tree (small JSON, load fully)
        section_data = {}
        section_path = os.path.join(args.interim_root, "logical", slug, "section_tree.json")
        if os.path.exists(section_path):
            try:
                with open(section_path) as f:
                    section_data = json.load(f)
            except Exception as e:
                errors.append(f"section/{slug}: {e}")

        # Tables
        tables_count = 0
        tables_path = os.path.join(args.interim_root, "tables", slug, "document_tables.json")
        if os.path.exists(tables_path):
            tables_count = load_tables(tables_path)

        # Facts
        facts_count = 0
        facts_path = os.path.join(args.interim_root, "facts", slug, "fact_candidates.json")
        if os.path.exists(facts_path):
            facts_count = load_facts(facts_path)

        section_count = section_data.get("total_sections", 0)
        clause_count = section_data.get("total_clauses", 0)

        category = classify(
            slug=slug,
            manifest_entry=manifest_entry,
            max_heading_score=max_heading_score,
            heading_count=heading_count,
            section_data=section_data,
            tables_count=tables_count,
            facts_count=facts_count,
            duplicate_hash_groups=duplicate_groups,
        )

        doc_id = manifest_entry.get("document_id", "")
        dup_group = duplicate_groups.get(doc_id, [])
        dup_size = len(dup_group)

        classifications.append(
            {
                "slug": slug,
                "category": category,
                "insurer": manifest_entry.get("insurer", ""),
                "filename": manifest_entry.get("filename", ""),
                "page_count": page_count,
                "heading_count": heading_count,
                "max_heading_score": round(max_heading_score, 4),
                "section_count": section_count,
                "clause_count": clause_count,
                "table_count": tables_count,
                "fact_candidate_count": facts_count,
                "duplicate_group_size": dup_size,
                "document_type": manifest_entry.get("document_type", ""),
                "triage_flags": manifest_entry.get("triage_flags", []),
                "_max_heading_score": max_heading_score,
            }
        )

    # ── Category summary ────────────────────────────────────────
    category_counts = Counter(c["category"] for c in classifications)
    category_summary = {
        cat: category_counts.get(cat, 0)
        for cat in [
            "NON_POLICY",
            "HEADING_MISS",
            "DUPLICATE",
            "SECTION_FAIL",
            "PHYSICAL_BAD",
            "UNSUPPORTED",
            "UNKNOWN",
        ]
    }

    # ── Top insurers ────────────────────────────────────────────
    insurer_counts = Counter(c["insurer"] for c in classifications)
    top_insurers = insurer_counts.most_common(15)

    # ── Insurer patterns ────────────────────────────────────────
    insurer_patterns = defaultdict(lambda: {"count": 0, "categories": Counter()})
    for c in classifications:
        ins = c["insurer"]
        insurer_patterns[ins]["count"] += 1
        insurer_patterns[ins]["categories"][c["category"]] += 1

    # ── Sample for Phase B ──────────────────────────────────────
    recommended_sample_20 = recommend_sample(classifications)

    # ── High-leverage fixes ─────────────────────────────────────
    heading_miss_count = category_summary.get("HEADING_MISS", 0)
    non_policy_count = category_summary.get("NON_POLICY", 0)

    hm_scores = [c["max_heading_score"] for c in classifications if c["category"] == "HEADING_MISS"]
    hm_near_threshold = sum(1 for s in hm_scores if s >= 0.45)

    high_level_fixes = []
    if heading_miss_count > 0:
        high_level_fixes.append(
            f"Lower heading threshold from 0.50 to ~0.45 "
            f"({hm_near_threshold}/{heading_miss_count} HEADING_MISS have max score >= 0.45)"
        )
        high_level_fixes.append(
            f"Improve ALL-CAPS / sentence-case detection for {heading_miss_count} "
            f"policies where heading scorer produces candidates below threshold"
        )
        high_level_fixes.append(
            "Increase bold-weight / font-size-ratio signal for policies where "
            "headings use bold or larger font but scorer under-weighs visual features"
        )
    if non_policy_count > 0:
        high_level_fixes.append(
            f"Review corpus lockdown — {non_policy_count} NON_POLICY documents "
            f"may need exclusion from active policy set"
        )

    # ── Write JSON output ──────────────────────────────────────
    output_json = {
        "schema_version": "dse024_zero_clause_classification.v1",
        "task_id": "DSE-024",
        "date": "2026-06-04",
        "total_policies": len(classifications),
        "category_summary": category_summary,
        "top_insurers": [{"insurer": ins, "count": cnt} for ins, cnt in top_insurers],
        "insurer_patterns": {
            ins: {"count": data["count"], "categories": dict(data["categories"])}
            for ins, data in sorted(insurer_patterns.items(), key=lambda x: -x[1]["count"])
        },
        "recommended_parser_fixes": high_level_fixes,
        "recommended_sample_20": [
            {
                "slug": c["slug"],
                "category": c["category"],
                "insurer": c["insurer"],
                "page_count": c["page_count"],
                "max_heading_score": c["max_heading_score"],
            }
            for c in recommended_sample_20
        ],
        "classifications": [
            {
                "slug": c["slug"],
                "category": c["category"],
                "insurer": c["insurer"],
                "filename": c["filename"],
                "page_count": c["page_count"],
                "heading_count": c["heading_count"],
                "max_heading_score": c["max_heading_score"],
                "section_count": c["section_count"],
                "clause_count": c["clause_count"],
                "table_count": c["table_count"],
                "fact_candidate_count": c["fact_candidate_count"],
                "duplicate_group_size": c["duplicate_group_size"],
                "document_type": c["document_type"],
                "triage_flags": c["triage_flags"],
            }
            for c in classifications
        ],
    }

    print(f"[dse024] Writing JSON: {args.json_output}")
    os.makedirs(os.path.dirname(args.json_output), exist_ok=True)
    with open(args.json_output, "w") as f:
        json.dump(output_json, f, indent=2)

    # ── Write Markdown output ──────────────────────────────────
    md_lines = [
        "# DSE-024: Zero-Clause Policy Classification (Phase A)",
        "",
        "**Date:** 2026-06-04",
        f"**Total Policies:** {len(classifications)}",
        f"**Errors:** {len(errors)}" if errors else "**Errors:** 0",
        "",
        "## Category Summary",
        "",
        "| Category | Count | % |",
        "|----------|-------|---|",
    ]
    for cat in [
        "NON_POLICY",
        "HEADING_MISS",
        "DUPLICATE",
        "SECTION_FAIL",
        "PHYSICAL_BAD",
        "UNSUPPORTED",
        "UNKNOWN",
    ]:
        cnt = category_summary.get(cat, 0)
        pct = (cnt / len(classifications) * 100) if classifications else 0
        md_lines.append(f"| {cat} | {cnt} | {pct:.1f}% |")

    md_lines += [
        "",
        "## Top Insurers Affected",
        "",
        "| Insurer | Count | Categories |",
        "|---------|-------|------------|",
    ]
    for ins, cnt in top_insurers:
        cats = dict(insurer_patterns[ins]["categories"])
        cat_str = ", ".join(f"{k}={v}" for k, v in sorted(cats.items()))
        md_lines.append(f"| {ins} | {cnt} | {cat_str} |")

    md_lines += [
        "",
        "## Recommended Parser Fixes",
        "",
    ]
    for fix in high_level_fixes:
        md_lines.append(f"- {fix}")

    md_lines += [
        "",
        "## Recommended 20-Policy Sample for Phase B",
        "",
        "| # | Slug | Category | Insurer | Pages | Max Heading Score |",
        "|---|------|----------|---------|-------|-------------------|",
    ]
    for i, c in enumerate(recommended_sample_20, 1):
        md_lines.append(
            f"| {i} | {c['slug']} | {c['category']} | "
            f"{c['insurer']} | {c['page_count']} | {c['max_heading_score']} |"
        )

    # Add all classifications as a data appendix
    md_lines += [
        "",
        "## All 132 Classifications",
        "",
        "| Slug | Category | Insurer | Pages | Headings | Max Score | "
        "Sections | Clauses | Tables | Facts | Notes |",
        "|------|----------|---------|-------|----------|-----------|"
        "---------|---------|--------|-------|-------|",
    ]
    for c in classifications:
        notes = []
        if c["duplicate_group_size"] > 1:
            notes.append(f"dup={c['duplicate_group_size']}")
        if c["document_type"] == "brochure":
            notes.append("brochure")
        if c["triage_flags"]:
            notes.append(",".join(c["triage_flags"]))
        notes_str = "; ".join(notes) if notes else ""
        md_lines.append(
            f"| {c['slug']} | {c['category']} | {c['insurer']} | "
            f"{c['page_count']} | {c['heading_count']} | "
            f"{c['max_heading_score']} | "
            f"{c['section_count']} | {c['clause_count']} | "
            f"{c['table_count']} | {c['fact_candidate_count']} | "
            f"{notes_str} |"
        )

    print(f"[dse024] Writing Markdown: {args.md_output}")
    os.makedirs(os.path.dirname(args.md_output), exist_ok=True)
    with open(args.md_output, "w") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"[dse024] Done. {len(classifications)} policies classified.")
    if errors:
        print(f"[dse024] WARNING: {len(errors)} errors:")
        for e in errors[:10]:
            print(f"  {e}")

    print("\nCategory breakdown:")
    for cat, cnt in sorted(category_summary.items()):
        if cnt > 0:
            print(f"  {cat}: {cnt}")
    print("\nHighest-leverage fixes:")
    for fix in high_level_fixes:
        print(f"  - {fix}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
