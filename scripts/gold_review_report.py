"""
Gold Review Report — DSE-012

Generates per-policy human review reports for draft gold annotations.
Highlights risky areas that need targeted human attention.

Usage:
  PYTHONPATH=. python scripts/gold_review_report.py \\
    --manifest data/manifests/dse012_gold_expansion_candidates_v1.json \\
    --output-dir data/reports/dse012_review
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import time
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("gold_review_report")

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
_IMPLEMENTED_CONCEPTS = {
    "free_look_period",
    "grace_period",
    "ped_waiting_period",
    "initial_waiting_period",
    "co_pay",
}


def _load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def analyze_policy(policy: dict) -> dict:
    """Analyze one policy's draft gold and produce review findings."""
    slug = policy["slug"]
    gold_dir = f"gold_corpus/policies/{slug}"

    if not os.path.isdir(gold_dir):
        return {"slug": slug, "status": "no_draft_gold", "findings": [], "priority": "skip"}

    metadata = _load_json(f"{gold_dir}/metadata.json")
    sections = _load_json(f"{gold_dir}/sections.json")
    clauses = _load_json(f"{gold_dir}/clauses.json")
    tables = _load_json(f"{gold_dir}/tables.json")
    facts = _load_json(f"{gold_dir}/facts.json")
    heading_labels = _load_json(f"{gold_dir}/heading_labels.json")
    physical_table_labels = _load_json(f"{gold_dir}/physical_table_labels.json")

    findings: List[dict] = []
    priority = "normal"

    # --- Section tree analysis ---
    total_sections = len(sections)
    total_clauses = len(clauses)
    known_issues = metadata.get("known_issues", [])

    if "section_tree_failed_or_degenerate" in known_issues:
        findings.append(
            {
                "category": "CRITICAL",
                "area": "section_tree",
                "detail": f"Section tree is degenerate ({total_sections} sections, {total_clauses} clauses). "
                "Heading scorer found no visual headings. All sections/clauses need manual annotation.",
            }
        )
        priority = "critical"
    elif total_sections < 10:
        findings.append(
            {
                "category": "WARNING",
                "area": "section_tree",
                "detail": f"Unusually few sections ({total_sections}). May indicate heading detection issues.",
            }
        )
        if priority != "critical":
            priority = "high"
    elif total_sections > 300:
        findings.append(
            {
                "category": "WARNING",
                "area": "section_tree",
                "detail": f"Unusually many sections ({total_sections}). May indicate over-segmentation.",
            }
        )

    if total_clauses == 0:
        findings.append(
            {
                "category": "CRITICAL",
                "area": "clauses",
                "detail": "Zero clauses segmented. All clauses need manual annotation.",
            }
        )
        if priority != "critical":
            priority = "critical"

    # --- Fact analysis ---
    present_facts = [f for f in facts if f.get("fact_status") == "present"]
    not_found_facts = [f for f in facts if f.get("fact_status") == "not_found"]
    implemented_present = [f for f in present_facts if f["concept"] in _IMPLEMENTED_CONCEPTS]
    implemented_not_found = [f for f in not_found_facts if f["concept"] in _IMPLEMENTED_CONCEPTS]
    unimplemented = [f for f in facts if f["concept"] not in _IMPLEMENTED_CONCEPTS]

    low_confidence = [f for f in present_facts if (f.get("confidence") or 0) < 0.90]
    no_evidence = [f for f in present_facts if not f.get("evidence_text")]

    findings.append(
        {
            "category": "INFO",
            "area": "facts_summary",
            "detail": f"{len(present_facts)} present, {len(not_found_facts)} not_found. "
            f"{len(implemented_present)} from extractors, {len(unimplemented)} need manual annotation.",
        }
    )

    if low_confidence:
        findings.append(
            {
                "category": "WARNING",
                "area": "facts_low_confidence",
                "detail": f"{len(low_confidence)} present facts with confidence < 0.90: "
                + ", ".join(f["concept"] for f in low_confidence),
            }
        )

    if no_evidence:
        findings.append(
            {
                "category": "WARNING",
                "area": "facts_no_evidence",
                "detail": f"{len(no_evidence)} present facts without evidence text: "
                + ", ".join(f["concept"] for f in no_evidence),
            }
        )

    # 15 concepts with no extractor — all need manual annotation
    findings.append(
        {
            "category": "ACTION",
            "area": "facts_manual_required",
            "detail": f"15 concepts have no extractor. All are marked not_found and need manual search: "
            + ", ".join(f["concept"] for f in unimplemented[:5])
            + "...",
        }
    )

    # --- Table analysis ---
    findings.append(
        {
            "category": "INFO",
            "area": "tables",
            "detail": f"{len(tables)} semantic tables, {len(physical_table_labels)} physical table labels detected.",
        }
    )

    # --- Heading analysis ---
    findings.append(
        {
            "category": "INFO",
            "area": "headings",
            "detail": f"{len(heading_labels)} visual heading labels detected.",
        }
    )

    if len(heading_labels) == 0:
        findings.append(
            {
                "category": "WARNING",
                "area": "headings",
                "detail": "Zero heading labels. Heading scorer may have failed for this document format.",
            }
        )
    elif len(heading_labels) < 3 and total_sections > 1:
        findings.append(
            {
                "category": "WARNING",
                "area": "headings_low",
                "detail": f"Only {len(heading_labels)} heading labels detected despite {total_sections} sections. "
                "Heading scorer may have missed visual headings in this document format.",
            }
        )
        if priority == "normal":
            priority = "high"

    # --- Evidence sanity ---
    for f in present_facts:
        ev = f.get("evidence_text", "")
        if ev and len(ev) < 15:
            findings.append(
                {
                    "category": "WARNING",
                    "area": "evidence_short",
                    "detail": f"Fact '{f['concept']}' has very short evidence ({len(ev)} chars): {ev!r}",
                }
            )

    return {
        "slug": slug,
        "insurer": policy["insurer_display"],
        "plan": policy["plan_name_clean"],
        "pages": metadata.get("page_count", 0),
        "status": "analyzed",
        "priority": priority,
        "sections": total_sections,
        "clauses": total_clauses,
        "tables": len(tables),
        "facts_present": len(present_facts),
        "facts_not_found": len(not_found_facts),
        "heading_labels": len(heading_labels),
        "physical_table_labels": len(physical_table_labels),
        "known_issues": known_issues,
        "findings": findings,
    }


def render_markdown_report(analyses: List[dict]) -> str:
    """Render a consolidated markdown review report."""
    lines = [
        "# DSE-012: Gold Corpus Expansion — Human Review Report",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M')}",
        f"Policies: {len(analyses)}",
        "",
    ]

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append(
        "| # | Priority | Slug | Insurer | Pages | Sections | Clauses | Facts Present | Issues |"
    )
    lines.append(
        "|---|----------|------|---------|-------|----------|---------|---------------|--------|"
    )

    # Sort by priority: critical first, then high, then normal
    priority_order = {"critical": 0, "high": 1, "normal": 2, "skip": 3}
    sorted_analyses = sorted(analyses, key=lambda a: priority_order.get(a["priority"], 9))

    for i, a in enumerate(sorted_analyses, 1):
        issues_str = ", ".join(a.get("known_issues", [])) or "none"
        lines.append(
            f"| {i} | **{a['priority'].upper()}** | {a['slug'][:35]} | {a['insurer']} | "
            f"{a.get('pages', 0)} | {a.get('sections', 0)} | {a.get('clauses', 0)} | "
            f"{a.get('facts_present', 0)}/20 | {issues_str} |"
        )

    lines.append("")

    # Recommended review order
    lines.append("## Recommended Review Order")
    lines.append("")
    lines.append("1. **CRITICAL** policies first (degenerate section tree — need manual structure)")
    lines.append("2. **HIGH** priority (unusual section/heading counts)")
    lines.append("3. **NORMAL** priority (pipeline output looks reasonable)")
    lines.append("")

    # Per-policy detail
    lines.append("## Per-Policy Findings")
    lines.append("")

    for a in sorted_analyses:
        lines.append(f"### {a['slug']}")
        lines.append(
            f"**Insurer:** {a.get('insurer', '')} | **Plan:** {a.get('plan', '')} | "
            f"**Pages:** {a.get('pages', 0)} | **Priority:** {a['priority'].upper()}"
        )
        lines.append("")

        if a.get("known_issues"):
            lines.append(f"**Known issues:** {', '.join(a['known_issues'])}")
            lines.append("")

        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Sections | {a.get('sections', 0)} |")
        lines.append(f"| Clauses | {a.get('clauses', 0)} |")
        lines.append(f"| Tables (semantic) | {a.get('tables', 0)} |")
        lines.append(f"| Physical table labels | {a.get('physical_table_labels', 0)} |")
        lines.append(f"| Heading labels | {a.get('heading_labels', 0)} |")
        lines.append(f"| Facts present | {a.get('facts_present', 0)}/20 |")
        lines.append(f"| Facts not_found | {a.get('facts_not_found', 0)}/20 |")
        lines.append("")

        findings = a.get("findings", [])
        if findings:
            lines.append("**Findings:**")
            lines.append("")
            for f in findings:
                icon = {"CRITICAL": "!!!", "WARNING": "!!", "ACTION": ">>", "INFO": "--"}.get(
                    f["category"], "--"
                )
                lines.append(f"- [{f['category']}] {f['detail']}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gold Review Report — DSE-012")
    parser.add_argument(
        "--manifest", default="data/manifests/dse012_gold_expansion_candidates_v1.json"
    )
    parser.add_argument("--output-dir", default="data/reports/dse012_review")
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    policies = manifest.get("policies", [])

    analyses = []
    for policy in policies:
        analysis = analyze_policy(policy)
        analyses.append(analysis)
        logger.info(
            "  %s: priority=%s, %d findings",
            policy["slug"],
            analysis["priority"],
            len(analysis["findings"]),
        )

    # Write consolidated markdown report
    report_md = render_markdown_report(analyses)
    report_path = os.path.join(args.output_dir, "review_report.md")
    _write_text(report_path, report_md)

    # Write per-policy JSON analyses
    for analysis in analyses:
        json_path = os.path.join(args.output_dir, f"{analysis['slug']}_review.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

    logger.info("Review report written to %s", report_path)

    critical = sum(1 for a in analyses if a["priority"] == "critical")
    high = sum(1 for a in analyses if a["priority"] == "high")
    normal = sum(1 for a in analyses if a["priority"] == "normal")
    logger.info("Priority: %d critical, %d high, %d normal", critical, high, normal)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
