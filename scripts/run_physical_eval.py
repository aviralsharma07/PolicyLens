import argparse
import json
import os
import sys
from typing import Any, Dict, List

from pdf_parser.models import PhysicalDocument


def load_document(path: str) -> PhysicalDocument:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return PhysicalDocument(**data)


def normalize_text(t: str) -> str:
    import re

    t = t.lower()
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    return t


def fuzzy_substring_fraction(needle: str, haystack: str) -> float:
    n = normalize_text(needle)
    h = normalize_text(haystack)
    if not n:
        return 0.0
    if n in h:
        return 1.0
    best = 0.0
    nl = len(n)
    for i in range(len(h) - nl + 1):
        match = sum(1 for a, b in zip(n, h[i : i + nl]) if a == b)
        score = match / nl
        best = max(best, score)
    return best


def compute_metrics(doc: PhysicalDocument, metadata: dict, gold_facts_path: str) -> Dict[str, Any]:
    total_pages = doc.page_count
    pages_with_blocks = sum(1 for p in doc.pages if len(p.blocks) > 0)
    pages_with_text = sum(1 for p in doc.pages if p.text_length > 0)
    non_cover_pages = max(0, total_pages - 1)
    non_cover_with_text = sum(1 for p in doc.pages if p.page_number > 1 and p.text_length > 0)

    blocks_pct = (pages_with_blocks / total_pages * 100) if total_pages else 0
    text_pct = (non_cover_with_text / non_cover_pages * 100) if non_cover_pages else 100

    total_spans = sum(len(p.spans) for p in doc.pages)
    spans_with_font = sum(1 for p in doc.pages for s in p.spans if s.font_size is not None)
    font_pct = (spans_with_font / total_spans * 100) if total_spans else 100

    header_lines = sum(1 for p in doc.pages for l in p.lines if l.is_header_candidate)
    footer_lines = sum(1 for p in doc.pages for l in p.lines if l.is_footer_candidate)

    catastrophic_failures = []
    for p in doc.pages:
        if p.text_length == 0 and p.page_number > 1:
            catastrophic_failures.append(f"p{p.page_number}: empty non-cover page")

    span_ref_total = 0
    span_ref_valid = 0
    for page in doc.pages:
        span_set = {s.span_id for s in page.spans}
        for line in page.lines:
            for ref in line.span_ids:
                span_ref_total += 1
                if ref in span_set:
                    span_ref_valid += 1
    span_ref_integrity_pct = (span_ref_valid / span_ref_total * 100) if span_ref_total else 100.0

    evidence_coverage = 0.0
    evidence_checked = 0
    if os.path.isfile(gold_facts_path):
        with open(gold_facts_path, "r", encoding="utf-8") as f:
            facts = json.load(f)
        facts_list = facts if isinstance(facts, list) else facts.get("facts", [])

        doc_text = " ".join(l.text for p in doc.pages for l in p.lines)

        covered = 0
        checked = 0
        for fact in facts_list:
            status = fact.get("fact_status", "")
            evidence = fact.get("evidence_text")
            if evidence and status in ("present", "explicitly_not_covered"):
                checked += 1
                if fuzzy_substring_fraction(evidence, doc_text) >= 0.8:
                    covered += 1

        if checked > 0:
            evidence_coverage = covered / checked * 100
            evidence_checked = checked

    all_text = " ".join(l.text for p in doc.pages for l in p.lines)
    total_chars = len(all_text)

    return {
        "page_count": total_pages,
        "pages_with_blocks": pages_with_blocks,
        "pages_with_text": pages_with_text,
        "non_cover_with_text": non_cover_with_text,
        "blocks_pct": round(blocks_pct, 1),
        "text_coverage_pct": round(text_pct, 1),
        "total_spans": total_spans,
        "spans_with_font_size": spans_with_font,
        "font_size_metadata_pct": round(font_pct, 1),
        "header_candidate_lines": header_lines,
        "footer_candidate_lines": footer_lines,
        "catastrophic_failures": catastrophic_failures,
        "catastrophic_count": len(catastrophic_failures),
        "total_characters": total_chars,
        "span_ref_total": span_ref_total,
        "span_ref_valid": span_ref_valid,
        "span_ref_integrity_pct": round(span_ref_integrity_pct, 2),
        "evidence_coverage": round(evidence_coverage, 1),
        "evidence_checked": evidence_checked,
        "evidence_gate": "reported_only",
        "evidence_gate_deferred_to": "DSE-010",
    }


def evaluate_gold_policy(
    slug: str,
    physical_root: str,
    gold_corpus_root: str,
    debug_root: str,
) -> Dict[str, Any]:
    doc_path = os.path.join(physical_root, slug, "document_physical.json")
    metadata_path = os.path.join(gold_corpus_root, "policies", slug, "metadata.json")
    facts_path = os.path.join(gold_corpus_root, "policies", slug, "facts.json")
    debug_dir = os.path.join(debug_root, slug)

    if not os.path.isfile(doc_path):
        return {"slug": slug, "status": "missing_doc"}

    if not os.path.isfile(metadata_path):
        return {"slug": slug, "status": "missing_metadata"}

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    doc = load_document(doc_path)
    metrics = compute_metrics(doc, metadata, facts_path)

    html_files = set()
    if os.path.isdir(debug_dir):
        html_files = {f for f in os.listdir(debug_dir) if f.endswith(".html")}

    page_count_ok = doc.page_count == metadata.get("page_count", 0)
    text_gate = metrics["text_coverage_pct"] >= 95
    font_gate = metrics["font_size_metadata_pct"] >= 90
    cat_gate = metrics["catastrophic_count"] == 0
    debug_gate = (
        all(f"page_{p:03d}.html" in html_files for p in range(1, doc.page_count + 1))
        if doc.page_count > 0
        else False
    )
    span_ref_gate = metrics["span_ref_integrity_pct"] == 100.0

    gates_passed = (
        page_count_ok and text_gate and font_gate and cat_gate and debug_gate and span_ref_gate
    )

    return {
        "slug": slug,
        "status": "passed" if gates_passed else "failed",
        "page_count": doc.page_count,
        "expected_pages": metadata.get("page_count", 0),
        "page_count_ok": page_count_ok,
        "metrics": metrics,
        "gates": {
            "page_count_match": page_count_ok,
            "text_coverage_95pct": text_gate,
            "font_metadata_90pct": font_gate,
            "zero_catastrophic": cat_gate,
            "debug_html_all_pages": debug_gate,
            "span_ref_integrity_100pct": span_ref_gate,
        },
        "debug_html_count": len(html_files),
    }


def main():
    parser = argparse.ArgumentParser(description="DSE-004 Physical Parser Eval")
    parser.add_argument("--gold-corpus", required=True)
    parser.add_argument("--physical-root", required=True)
    parser.add_argument("--debug-root", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    policies_dir = os.path.join(args.gold_corpus, "policies")
    slugs = sorted(os.listdir(policies_dir))
    results = []

    for slug in slugs:
        print(f"Evaluating {slug} ...")
        result = evaluate_gold_policy(
            slug=slug,
            physical_root=args.physical_root,
            gold_corpus_root=args.gold_corpus,
            debug_root=args.debug_root,
        )
        results.append(result)
        if result["status"] == "passed":
            print(
                f"  PASS: {result['metrics']['page_count']} pages, "
                f"text={result['metrics']['text_coverage_pct']}%, "
                f"font={result['metrics']['font_size_metadata_pct']}%"
            )
        else:
            print(f"  FAIL: gates={result.get('gates', {})}")

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = len(results) - passed

    eval_result = {
        "eval_name": "physical-parser-v1",
        "date": "2026-05-29",
        "task_id": "DSE-004",
        "git_commit": None,
        "input_manifest": "gold_corpus (5 policies, 218 pages)",
        "metrics": {
            "policies_processed": len(results),
            "passed": passed,
            "failed": failed,
        },
        "policy_results": results,
        "passed": failed == 0,
        "failures": [r["slug"] for r in results if r["status"] != "passed"],
        "notes": "Physical parser v1 eval on 5 gold PDFs. Gates: page count match, text coverage >= 95%, font metadata >= 90%, zero catastrophic failures, debug HTML for all pages, span referential integrity = 100%. Evidence coverage is reported_only; hard gate deferred to DSE-010.",
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
