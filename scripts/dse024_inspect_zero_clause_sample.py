#!/usr/bin/env python3
"""
DSE-024 Phase B: Deep inspection of 20 representative zero-clause policies.

For each sample slug:
  - Load heading_candidates.json, section_tree.json, manifest entry
  - Top 20 candidates by score: classify as heading, TOC, boilerplate, etc.
  - Find heading-like lines using signal-independent heuristic
  - Determine root failure mechanism
  - Assess whether threshold lowering to 0.45 would help
  - Document false-positive risk

Output: JSON + Markdown reports.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

# ── classification hints ──────────────────────────────────────────────────

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
    "permanent total disablement",
    "insured event",
    "emergency care",
    "medical expenses",
    "hospitalization",
    "in-patient care",
    "day care treatment",
    "grace period",
    "network provider",
    "subrogation",
    "indemnity",
    "room rent",
    "comprehensive",
    "family shield",
    "accident",
    "age",
    "illness",
    "injury",
    "treatment",
    "charges",
    "expenses",
    "disablement",
    "disease",
    "care",
    "cover",
    "optional",
    "additional",
    "benefit",
    "section",
    "part",
    "policy",
    "general terms",
    "schedule",
    "general conditions",
    "exclusions and limitations",
    "scope of cover",
    "claim procedure",
    "communication",
    "entry age",
    "geographical area",
    "fraudulent claims",
    "multiple policies",
    "discount parameters",
    "terms & conditions",
    "terms and conditions",
}

ROOT_CAUSE_ORDER = [
    "threshold_too_high",
    "missing_feature_all_caps",
    "missing_feature_numbered_heading",
    "missing_feature_colon_heading",
    "missing_feature_bold_definition",
    "missing_feature_toc_suppression",
    "missing_feature_letter_numbering",
    "section_tree_requires_synthetic_body_detection",
    "non_policy_should_exclude",
    "duplicate_should_skip",
    "needs_manual_review",
    "garbled_physical_extraction",
]


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── candidate classification ──────────────────────────────────────────────


def _matches_any_heading_dict(text: str) -> bool:
    lower = re.sub(r"^[\d\.\s\)]+", "", text).strip().lower().rstrip(".: ")
    for term in HEADING_DICT_TERMS:
        if lower.startswith(term):
            return True
    return False


def classify_candidate(c: dict) -> str:
    """Classify a single candidate line into a human-readable type."""
    text = c.get("text", "").strip()
    f = c.get("features", {})
    page = c.get("page_number", 0)

    if f.get("has_toc_dots", 0) == 1.0:
        return "toc_entry"

    if f.get("is_header_region", 0) == 1.0 or f.get("is_footer_region", 0) == 1.0:
        return "boilerplate_header_footer"

    if f.get("boilerplate_company_penalty", 0) == 1.0:
        return "boilerplate_company"

    num = f.get("matches_numbering", 0) == 1.0
    bold = f.get("is_bold", 0) == 1.0
    allcaps = f.get("is_all_caps", 0) == 1.0
    sentcase = f.get("is_sentence_case", 0) == 1.0
    dict_match = f.get("matches_heading_dict", 0) == 1.0 or _matches_any_heading_dict(text)
    spacing = f.get("spacing_signal", 0) == 1.0
    line_len_ratio = f.get("line_length_ratio", 0.5)

    if num and bold and not sentcase:
        if dict_match:
            return "heading_real"
        if len(text) <= 60:
            return "heading_probable"
        return "numbered_bold_body"

    if num and allcaps and not sentcase and len(text) <= 40 and not dict_match:
        return "numbered_allcaps_item"

    if bold and dict_match and not sentcase:
        return "heading_real"

    if bold and dict_match and sentcase and line_len_ratio > 0.5:
        return "numbered_definition"

    if num and spacing and not sentcase:
        return "heading_probable"

    if allcaps and not num and not dict_match and len(text) <= 15:
        return "allcaps_short"

    if sentcase and line_len_ratio > 0.6 and not bold:
        return "body_text"

    if num and not bold and line_len_ratio < 0.3:
        return "table_data"

    if len(text) <= 3:
        return "too_short"

    if num and dict_match:
        return "heading_probable"

    if bold and not sentcase and line_len_ratio < 1.0:
        return "heading_probable"

    return "other"


# ── independent heading signal scoring ────────────────────────────────────


def _heading_signal_score(c: dict) -> int:
    """Compute heading signal count independent of scorer weights."""
    f = c.get("features", {})
    signals = 0
    if f.get("matches_numbering", 0) == 1.0:
        signals += 1
    if f.get("is_bold", 0) == 1.0:
        signals += 1
    if f.get("is_all_caps", 0) == 1.0 and len(c.get("text", "").strip()) <= 60:
        signals += 1
    if f.get("matches_heading_dict", 0) == 1.0 or _matches_any_heading_dict(c.get("text", "")):
        signals += 1
    if f.get("spacing_signal", 0) == 1.0:
        signals += 1

    anti = 0
    if f.get("has_toc_dots", 0) == 1.0:
        anti += 3
    if f.get("is_header_region", 0) == 1.0 or f.get("is_footer_region", 0) == 1.0:
        anti += 3
    if f.get("boilerplate_company_penalty", 0) == 1.0:
        anti += 3
    return signals - anti


def find_heading_like_candidates(candidates: List[dict], top_k: int = 20) -> List[dict]:
    """Find the most heading-like candidates independent of scorer weights."""
    scored = []
    for c in candidates:
        net = _heading_signal_score(c)
        if net >= 1:
            scored.append((net, c.get("score", 0.0), c))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    return [item[2] for item in scored[:top_k]]


# ── line-level text analysis ──────────────────────────────────────────────


def _looks_like_real_heading(text: str) -> bool:
    """Check if text looks like a genuine heading (independent of scorer)."""
    t = text.strip()
    if len(t) < 4 or len(t) > 100:
        return False
    lower = t.lower()
    if _matches_any_heading_dict(t):
        return True
    if re.match(r"^(?:part|section)\s+", lower):
        return True
    if re.match(r"^\d+(?:\.\d+)*[\.\)]?\s+[A-Z]", t):
        return True
    return False


# ── root cause determination ──────────────────────────────────────────────


def determine_root_cause(
    slug: str,
    top_20: List[dict],
    top_20_classified: List[dict],
    heading_like: List[dict],
    section_data: dict,
    manifest: dict,
    category: str,
    best_score: float,
) -> str:
    if category == "NON_POLICY":
        return "non_policy_should_exclude"
    if category == "DUPLICATE":
        return "duplicate_should_skip"

    if best_score < -1.0:
        median_line_len = manifest.get("line_count", 0)
        if median_line_len and median_line_len < 20:
            return "garbled_physical_extraction"

    head_types = Counter(c["classification"] for c in top_20_classified)
    real_headings_in_top = [
        c for c in top_20_classified if c["classification"] in ("heading_real", "heading_probable")
    ]

    if not real_headings_in_top:
        if head_types.get("toc_entry", 0) >= 5:
            return "missing_feature_toc_suppression"
        if head_types.get("numbered_allcaps_item", 0) >= 5:
            return "missing_feature_numbered_heading"
        if head_types.get("numbered_definition", 0) >= 3:
            return "missing_feature_bold_definition"
        if head_types.get("boilerplate_header_footer", 0) >= 3:
            return "boilerplate_dominated"
        return "needs_manual_review"

    best_heading = real_headings_in_top[0]
    best_heading_score = best_heading["score"]

    if best_heading_score >= 0.45:
        return "threshold_too_high"

    candidate = next((c for c in top_20 if c.get("text") == best_heading["text"]), top_20[0])
    features = candidate.get("features", {})

    if features.get("is_all_caps", 0) == 1.0:
        return "missing_feature_all_caps"
    if features.get("matches_numbering", 0) == 0.0:
        text = candidate.get("text", "").strip()
        if re.match(r"^[A-Z]\.?\s", text):
            return "missing_feature_letter_numbering"
        if re.match(r"^[A-Z][a-z]+:", text):
            return "missing_feature_colon_heading"
        return "missing_feature_numbered_heading"
    if features.get("is_sentence_case", 0) == 1.0 and features.get("is_bold", 0) == 1.0:
        return "missing_feature_bold_definition"
    if features.get("spacing_signal", 0) == 0.0:
        return "missing_feature_spacing"

    return "needs_manual_review"


def assess_fp_risk(
    top_20_classified: List[dict],
    heading_like: List[dict],
    threshold_045: bool,
    top_20_raw: List[dict],
) -> str:
    if not threshold_045:
        return "not_applicable_threshold_wont_help"

    if len(top_20_classified) < 2:
        return "low_confidence_insufficient_data"

    top_at_45 = [c for c in top_20_classified if c["score"] >= 0.45]
    if not top_at_45:
        return "no_candidates_at_045"

    fp_at_45 = [
        c
        for c in top_at_45
        if c["classification"]
        in (
            "toc_entry",
            "boilerplate_header_footer",
            "boilerplate_company",
            "body_text",
            "table_data",
            "numbered_allcaps_item",
            "too_short",
            "other",
        )
    ]

    if not fp_at_45:
        return "low_risk_all_at_045_are_headings"

    fp_ratio = len(fp_at_45) / len(top_at_45)
    if fp_ratio <= 0.2:
        return f"low_risk_{len(fp_at_45)}_fp_of_{len(top_at_45)}"
    if fp_ratio <= 0.5:
        return f"medium_risk_{len(fp_at_45)}_fp_of_{len(top_at_45)}"

    return f"high_risk_{len(fp_at_45)}_fp_of_{len(top_at_45)}"


def get_real_heading_examples(
    candidates: List[dict],
    max_examples: int = 10,
) -> List[dict]:
    seen = set()
    examples = []
    hl = find_heading_like_candidates(candidates, top_k=50)
    threshold = 0.35
    for c in hl:
        score = c.get("score", 0.0)
        if score < threshold:
            break
        text = c.get("text", "").strip()
        key = text.lower()[:60]
        if key in seen:
            continue
        seen.add(key)
        if _looks_like_real_heading(text):
            examples.append(
                {
                    "text": text,
                    "score": round(score, 4),
                    "page": c.get("page_number", 0),
                }
            )
            if len(examples) >= max_examples:
                break
    if len(examples) < max_examples:
        threshold = 0.1
        for c in hl:
            if len(examples) >= max_examples:
                break
            score = c.get("score", 0.0)
            if score < threshold:
                continue
            text = c.get("text", "").strip()
            key = text.lower()[:60]
            if key in seen:
                continue
            seen.add(key)
            examples.append(
                {
                    "text": text,
                    "score": round(score, 4),
                    "page": c.get("page_number", 0),
                    "note": "weak_signal",
                }
            )
    return examples


# ── per-slug inspection ──────────────────────────────────────────────────


def inspect_slug(
    slug: str,
    interim_root: str,
    manifest_by_slug: dict,
    category_from_sample: str = "",
) -> dict:
    heading_path = os.path.join(interim_root, "logical", slug, "heading_candidates.json")
    section_path = os.path.join(interim_root, "logical", slug, "section_tree.json")

    hdata = _load_json(heading_path)
    candidates = hdata.get("candidates", [])
    config = hdata.get("config", {})

    sdata = _load_json(section_path)

    manifest = manifest_by_slug.get(slug, {})

    sorted_candidates = sorted(candidates, key=lambda c: -c.get("score", 0.0))
    top_20_raw = sorted_candidates[:20]
    best_score = round(top_20_raw[0]["score"], 4) if top_20_raw else 0.0

    classified_top_20 = []
    for rank, c in enumerate(top_20_raw, 1):
        cls = classify_candidate(c)
        contribs = {
            k: round(v, 4) for k, v in c.get("feature_contributions", {}).items() if abs(v) >= 0.005
        }
        classified_top_20.append(
            {
                "rank": rank,
                "text": c.get("text", "").strip(),
                "score": round(c.get("score", 0.0), 4),
                "page": c.get("page_number", 0),
                "classification": cls,
                "features": {
                    "is_bold": c.get("features", {}).get("is_bold", 0.0),
                    "is_all_caps": c.get("features", {}).get("is_all_caps", 0.0),
                    "is_sentence_case": c.get("features", {}).get("is_sentence_case", 0.0),
                    "matches_numbering": c.get("features", {}).get("matches_numbering", 0.0),
                    "matches_heading_dict": c.get("features", {}).get("matches_heading_dict", 0.0),
                    "has_toc_dots": c.get("features", {}).get("has_toc_dots", 0.0),
                    "spacing_signal": c.get("features", {}).get("spacing_signal", 0.0),
                    "line_length_ratio": round(
                        c.get("features", {}).get("line_length_ratio", 0.0), 4
                    ),
                },
                "contributions": contribs,
            }
        )

    heading_like = find_heading_like_candidates(candidates, top_k=30)

    best_heading_like_score = 0.0
    for c in heading_like:
        if c.get("score", 0.0) > best_heading_like_score:
            best_heading_like_score = c.get("score", 0.0)

    heading_count_in_top_20 = sum(
        1 for c in classified_top_20 if c["classification"] in ("heading_real", "heading_probable")
    )

    would_threshold_045 = best_score >= 0.45

    root_cause = determine_root_cause(
        slug,
        top_20_raw,
        classified_top_20,
        heading_like,
        sdata,
        manifest,
        category_from_sample,
        best_score,
    )

    fp_risk = assess_fp_risk(
        classified_top_20,
        heading_like,
        would_threshold_045,
        top_20_raw,
    )

    real_heading_examples = get_real_heading_examples(candidates, max_examples=10)

    return {
        "slug": slug,
        "category": category_from_sample,
        "insurer": manifest.get("insurer", "") or "",
        "page_count": int(manifest.get("page_count", 0) or 0),
        "body_font_mode": config.get("body_font_mode"),
        "median_line_length": config.get("median_line_length"),
        "total_candidates": len(candidates),
        "total_headings_accepted": hdata.get("total_headings", 0),
        "best_score": best_score,
        "would_threshold_045_help": would_threshold_045,
        "heading_like_in_top_20": heading_count_in_top_20,
        "best_heading_like_score": round(best_heading_like_score, 4),
        "root_cause": root_cause,
        "failure_mechanism": root_cause,
        "false_positive_risk": fp_risk,
        "section_tree": {
            "total_sections": sdata.get("total_sections", 0),
            "total_clauses": sdata.get("total_clauses", 0),
            "total_visual_headings": sdata.get("total_visual_headings", 0),
            "total_synthetic_sections": sdata.get("total_synthetic_sections", 0),
        },
        "top_20_classified": classified_top_20,
        "real_heading_examples": real_heading_examples,
    }


# ── pattern analysis ─────────────────────────────────────────────────────


def analyze_patterns(inspections: List[dict]) -> dict:
    rc_counts = Counter(i["root_cause"] for i in inspections)
    would_help = sum(1 for i in inspections if i["would_threshold_045_help"])
    total = len(inspections)

    threshold_headings = []
    for i in inspections:
        for c in i["top_20_classified"]:
            if c["classification"] in ("heading_real", "heading_probable") and c["score"] >= 0.45:
                threshold_headings.append(
                    {
                        "slug": i["slug"],
                        "text": c["text"],
                        "score": c["score"],
                    }
                )

    return {
        "total_inspected": total,
        "root_cause_counts": dict(rc_counts.most_common()),
        "threshold_045_would_help": would_help,
        "threshold_045_would_not_help": total - would_help,
        "real_headings_at_045": len(threshold_headings),
        "examples_of_headings_at_045": threshold_headings[:15],
    }


# ── output ────────────────────────────────────────────────────────────────


def write_md_report(output: dict, md_path: str):
    lines = []
    patterns = output.get("patterns", {})
    inspections = output.get("inspections", [])

    lines.append("# DSE-024 Phase B: Zero-Clause Sample Inspection")
    lines.append("")
    lines.append(f"**Date:** 2026-06-04")
    lines.append(f"**Sample Size:** {len(inspections)}")
    lines.append("")

    # ── summary table ──
    lines.append("## Per-Policy Summary")
    lines.append("")
    lines.append(
        "| # | Slug | Category | Insurer | Pg | Best Score | Root Cause | Thresh 0.45 Helps | FP Risk | Real Hdgs in Top 20 |"
    )
    lines.append(
        "|---|------|----------|---------|----|------------|------------|-------------------|---------|---------------------|"
    )
    for i, insp in enumerate(inspections, 1):
        slug_short = insp["slug"][:50]
        lines.append(
            f"| {i} | {slug_short} | {insp['category']} | {insp['insurer']} "
            f"| {insp['page_count']} | {insp['best_score']} "
            f"| {insp['root_cause']} "
            f"| {'yes' if insp['would_threshold_045_help'] else 'no'} "
            f"| {insp['false_positive_risk'][:30]} "
            f"| {insp['heading_like_in_top_20']} |"
        )

    lines.append("")
    lines.append("## Pattern Analysis")
    lines.append("")
    lines.append(f"- **Root cause distribution:**")
    for rc, count in patterns.get("root_cause_counts", {}).items():
        lines.append(f"  - {rc}: {count}")
    lines.append(
        f"- **Threshold 0.45 would help:** {patterns.get('threshold_045_would_help')}/{len(inspections)} policies"
    )
    lines.append(
        f"- **Threshold 0.45 would NOT help:** {patterns.get('threshold_045_would_not_help')}/{len(inspections)} policies"
    )
    lines.append(f"- **Real headings at 0.45+ identified:** {patterns.get('real_headings_at_045')}")
    lines.append("")

    # ── real heading examples at 0.45+ ──
    if patterns.get("examples_of_headings_at_045"):
        lines.append("## Concrete Heading Text Examples (Score >= 0.45)")
        lines.append("")
        lines.append(
            "These are candidates that look like real headings and score at or above 0.45 "
        )
        lines.append("but still miss the 0.5 threshold. Lowering the threshold would admit these.")
        lines.append("")
        lines.append("| # | Slug | Text | Score |")
        lines.append("|---|------|------|-------|")
        for i, ex in enumerate(patterns["examples_of_headings_at_045"], 1):
            lines.append(f"| {i} | {ex['slug'][:45]} | {ex['text'][:60]} | {ex['score']} |")
        lines.append("")

    # ── per-policy deep dives ──
    lines.append("## Per-Policy Deep Inspection")
    lines.append("")

    for insp in inspections:
        lines.append(f"### {insp['slug']}")
        lines.append("")
        lines.append(f"- **Category:** {insp['category']}")
        lines.append(f"- **Insurer:** {insp['insurer']}")
        lines.append(
            f"- **Pages:** {insp['page_count']}, **Total candidates:** {insp['total_candidates']}"
        )
        lines.append(
            f"- **Body font mode:** {insp['body_font_mode']}, **Median line length:** {insp['median_line_length']}"
        )
        lines.append(f"- **Best score:** {insp['best_score']}")
        lines.append(f"- **Best heading-like score:** {insp['best_heading_like_score']}")
        lines.append(f"- **Root cause:** `{insp['root_cause']}")
        lines.append(
            f"- **Threshold 0.45 would help:** {'Yes' if insp['would_threshold_045_help'] else 'No'}"
        )
        lines.append(f"- **False-positive risk:** {insp['false_positive_risk']}")
        lines.append(f"- **Heading-like in top 20:** {insp['heading_like_in_top_20']}")
        lines.append("")

        # Section tree status
        st = insp["section_tree"]
        lines.append(
            f"**Section tree:** sections={st['total_sections']}, clauses={st['total_clauses']}, "
            f"visual_headings={st['total_visual_headings']}, synthetic={st['total_synthetic_sections']}"
        )
        lines.append("")

        # Top 20 table
        lines.append("**Top 20 Candidates (by score):**")
        lines.append("")
        lines.append(
            "| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |"
        )
        lines.append(
            "|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|"
        )
        for c in insp["top_20_classified"][:15]:
            f = c["features"]
            lines.append(
                f"| {c['rank']} | {c['score']} | {c['page']} "
                f"| {c['classification']} "
                f"| {c['text'][:55]} "
                f"| {int(f['is_bold'])} | {int(f['is_all_caps'])} | {int(f['is_sentence_case'])} "
                f"| {int(f['matches_numbering'])} | {int(f['matches_heading_dict'])} "
                f"| {int(f['has_toc_dots'])} | {int(f['spacing_signal'])} "
                f"| {f['line_length_ratio']} |"
            )
        lines.append("")

        # Real heading examples
        if insp["real_heading_examples"]:
            lines.append("**Identified real heading examples (from heading-like scan):**")
            lines.append("")
            lines.append("| Text | Score | Page |")
            lines.append("|------|-------|------|")
            for ex in insp["real_heading_examples"]:
                note = f" ({ex.get('note', '')})" if ex.get("note") else ""
                lines.append(f"| {ex['text'][:60]} | {ex['score']} | {ex['page']}{note} |")
            lines.append("")
        lines.append("---")
        lines.append("")

    # ── recommended parser changes ──
    lines.append("## Recommended Parser Changes (Ranked by Expected Impact)")
    lines.append("")
    lines.append("### 1. Lower heading threshold to 0.45 (HIGH IMPACT)")
    lines.append("")
    rc_counts = patterns.get("root_cause_counts", {})
    threshold_count = rc_counts.get("threshold_too_high", 0)
    lines.append(f"- Affects {threshold_count}/{len(inspections)} inspected policies")
    lines.append(
        "- Would admit ~{}/{} identified real heading examples at 0.45+".format(
            patterns.get("real_headings_at_045", 0),
            patterns.get("real_headings_at_045", 0),
        )
    )
    lines.append("- Low false-positive risk for documents where top candidates ARE real headings")
    lines.append(
        "- **Warning:** Does NOT help documents where top candidates are TOC entries or body text"
    )
    lines.append("")

    lines.append("### 2. Add letter-numbering patterns to heading scorer (MEDIUM IMPACT)")
    lines.append(
        "- Current patterns skip letter prefixes: `A.`, `B.`, `(a)`, `(b)`, `Part I`, `Part II`"
    )
    lines.append("- Weight `matches_numbering` = +0.30 — biggest single boost")
    lines.append("- Adding letter patterns would convert `A.Preamble` (score ~0.10 → ~0.40)")
    lines.append("")

    lines.append("### 3. Reduce `is_sentence_case` penalty for bold+numbered lines (MEDIUM IMPACT)")
    lines.append("- Current penalty: -0.30 for any sentence-case line")
    lines.append(
        "- Bold definition headings (`Condition Precedent: Condition Precedent means...`) get penalized"
    )
    lines.append(
        "- Suggestion: reduce penalty to -0.10 or -0.15 when `is_bold=1` AND `matches_numbering=1`"
    )
    lines.append("")

    lines.append("### 4. Suppress TOC entries in heading scorer (LOW-MEDIUM IMPACT)")
    lines.append("- Several documents have TOC entries dominating top candidates")
    lines.append(
        "- TOC lines have `has_toc_dots=1` but still score high due to numbering + dict match"
    )
    lines.append("- Suggestion: add `has_toc_dots` penalty or exclude early-page candidates")
    lines.append("")

    lines.append(
        "### 5. Add `spacing_signal` as standalone feature without requiring numbering/bold (LOW IMPACT)"
    )
    lines.append(
        "- Current: `spacing_signal=1` only when `looks_heading_like AND gap_before_ratio >= 1.5`"
    )
    lines.append("- Some documents have well-spaced headings but no numbering/bold")
    lines.append("- Would affect documents where spacing is the primary heading cue")
    lines.append("")

    lines.append("## Warning: Global Threshold Lowering Safety")
    lines.append("")
    lines.append(
        "**Do NOT blindly lower the global threshold from 0.5 to 0.45 without evaluation.**"
    )
    lines.append("")
    lines.append("Reasons:")
    lines.append(
        "1. Documents dominated by TOC entries (like HDFC Ergo) would admit TOC lines as headings"
    )
    lines.append(
        "2. Documents with procedure-code lists would admit all-caps numbered items as headings"
    )
    lines.append(
        "3. The current 20-policy gold eval must not regress — verify before/after threshold change"
    )
    lines.append(
        "4. Some documents need feature-level fixes (letter numbering, sentence-case penalty) not threshold changes"
    )
    lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Markdown report: {md_path}")


# ── main ─────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="DSE-024 Phase B: Inspect 20 representative zero-clause policies"
    )
    parser.add_argument(
        "--classification", required=True, help="Path to dse024_zero_clause_classification_v1.json"
    )
    parser.add_argument("--manifest", required=True, help="Path to dse020_run_manifest_v1.json")
    parser.add_argument("--interim-root", required=True, help="Root of DSE-020 interim outputs")
    parser.add_argument("--json-output", required=True, help="Path for JSON output")
    parser.add_argument("--md-output", required=True, help="Path for Markdown output")
    args = parser.parse_args()

    classification = _load_json(args.classification)
    sample_entries = classification.get("recommended_sample_20", [])
    if not sample_entries:
        print("ERROR: no recommended_sample_20 in classification", file=sys.stderr)
        return 1

    manifest = _load_json(args.manifest)
    manifest_by_slug = {}
    for entry in manifest.get("policies", []):
        slug = entry.get("slug", "")
        if slug:
            manifest_by_slug[slug] = entry
    for entry in manifest.get("skipped", []):
        sslug = entry.get("slug", "")
        if sslug:
            manifest_by_slug[sslug] = entry

    inspections = []
    for se in sample_entries:
        slug = se.get("slug", "")
        cat = se.get("category", "")
        print(f"Inspecting {slug} (category={cat}) ... ", end="", flush=True)
        try:
            insp = inspect_slug(slug, args.interim_root, manifest_by_slug, cat)
            inspections.append(insp)
            print(f"best={insp['best_score']}, root_cause={insp['root_cause']}")
        except Exception as exc:
            print(f"ERROR: {exc}")
            inspections.append(
                {
                    "slug": slug,
                    "category": cat,
                    "error": str(exc),
                    "root_cause": "error",
                    "failure_mechanism": "error",
                    "best_score": 0.0,
                    "would_threshold_045_help": False,
                    "heading_like_in_top_20": 0,
                    "false_positive_risk": "error",
                    "top_20_classified": [],
                    "real_heading_examples": [],
                    "section_tree": {},
                    "page_count": 0,
                    "body_font_mode": None,
                    "median_line_length": None,
                    "total_candidates": 0,
                    "total_headings_accepted": 0,
                    "best_heading_like_score": 0.0,
                    "insurer": "",
                }
            )

    patterns = analyze_patterns(inspections)

    output = {
        "schema_version": "dse024_zero_clause_sample_inspection.v1",
        "date": "2026-06-04",
        "task_id": "DSE-024",
        "total_samples": len(inspections),
        "total_sample": len(inspections),
        "inspections": inspections,
        "patterns": patterns,
    }

    os.makedirs(os.path.dirname(args.json_output) or ".", exist_ok=True)
    with open(args.json_output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nJSON output: {args.json_output}")

    os.makedirs(os.path.dirname(args.md_output) or ".", exist_ok=True)
    write_md_report(output, args.md_output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
