import argparse
import hashlib
import json
import os
import pathlib
import sys
import time
from typing import List, Optional

import pdfplumber
from pdfplumber.page import Page as PdfPlumberPage
from pdfplumber.table import Table as PdfPlumberTable

from pdf_parser.debug_html_generator import generate_all
from pdf_parser.header_footer_detector import process as process_header_footer
from pdf_parser.models import (
    Block,
    BlockType,
    Line,
    Page,
    ParserIssue,
    PhysicalDocument,
    Region,
    Span,
)


def _stable_id(prefix: str, counter: int) -> str:
    return f"{prefix}_{counter}"


def _hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def _is_table_region(page: PdfPlumberPage, x0: float, top: float, x1: float, bottom: float) -> bool:
    if not hasattr(page, "find_tables"):
        return False
    tables: List[PdfPlumberTable] = page.find_tables()
    for t in tables:
        tx0, ttop, tx1, tbottom = t.bbox
        overlap_x = max(0, min(x1, tx1) - max(x0, tx0))
        overlap_y = max(0, min(bottom, tbottom) - max(top, ttop))
        if overlap_x > 0 and overlap_y > 0:
            return True
    return False


def _chars_to_spans(page: PdfPlumberPage, page_num: int) -> List[Span]:
    spans: List[Span] = []
    counter = 0
    if not page.chars:
        return spans
    for c in page.chars:
        counter += 1
        span = Span(
            span_id=_stable_id(f"p{page_num}s", counter),
            text=c.get("text", ""),
            bbox=[c.get("x0", 0), c.get("top", 0), c.get("x1", 0), c.get("bottom", 0)],
            font_name=c.get("fontname"),
            font_size=c.get("size"),
            is_bold="Bold" in (c.get("fontname") or ""),
            is_italic="Italic" in (c.get("fontname") or ""),
            color=str(c.get("color")) if c.get("color") is not None else None,
            char_start=c.get("char_index", c.get("mcid")),
            char_end=None,
        )
        spans.append(span)
    return spans


def _extract_curves(page: PdfPlumberPage) -> List[dict]:
    if not hasattr(page, "curves"):
        return []
    return page.curves


def _extract_images(page: PdfPlumberPage) -> List[dict]:
    if not hasattr(page, "images"):
        return []
    return page.images


def extract_pdf(pdf_path: str, policy_id: str, pipeline_run_id: str) -> PhysicalDocument:
    file_hash = _hash_file(pdf_path)
    doc_issues: List[ParserIssue] = []
    pages: List[Page] = []

    try:
        pdf = pdfplumber.open(pdf_path)
    except Exception as e:
        doc_issues.append(ParserIssue(type="unreadable_pdf", page_number=0, message=str(e)))
        return PhysicalDocument(
            pipeline_run_id=pipeline_run_id,
            document_id=file_hash,
            policy_id=policy_id,
            source_pdf_path=pdf_path,
            file_hash=file_hash,
            page_count=0,
            issues=doc_issues,
        )

    with pdf:
        if not pdf.pages:
            doc_issues.append(
                ParserIssue(type="empty_pdf", page_number=0, message="No pages found")
            )
            return PhysicalDocument(
                pipeline_run_id=pipeline_run_id,
                document_id=file_hash,
                policy_id=policy_id,
                source_pdf_path=pdf_path,
                file_hash=file_hash,
                page_count=0,
                issues=doc_issues,
            )

        for page_num, plumber_page in enumerate(pdf.pages, start=1):
            page_issues: List[ParserIssue] = []
            page_width = float(plumber_page.width or 0)
            page_height = float(plumber_page.height or 0)
            rotation = getattr(plumber_page, "rotation", 0) or 0

            chars = plumber_page.chars or []
            text_direct = plumber_page.extract_text() or ""

            spans = _chars_to_spans(plumber_page, page_num)

            lines: List[Line] = []
            lines_by_bottom: dict = {}
            line_counter = 0
            for ch_idx, ch in enumerate(chars):
                cx0 = ch.get("x0", 0)
                ctop = ch.get("top", 0)
                cx1 = ch.get("x1", 0)
                cbottom = ch.get("bottom", 0)
                cy = round(cbottom, 1)
                if cy not in lines_by_bottom:
                    line_counter += 1
                    lines_by_bottom[cy] = {
                        "line_id": _stable_id(f"p{page_num}l", line_counter),
                        "text": "",
                        "x0": cx0,
                        "top": ctop,
                        "x1": cx1,
                        "bottom": cbottom,
                        "fonts": [],
                        "sizes": [],
                        "span_ids": [],
                    }
                entry = lines_by_bottom[cy]
                entry["text"] += ch.get("text", "")
                entry["x0"] = min(entry["x0"], cx0)
                entry["top"] = min(entry["top"], ctop)
                entry["x1"] = max(entry["x1"], cx1)
                entry["bottom"] = max(entry["bottom"], cbottom)
                if ch.get("fontname"):
                    entry["fonts"].append(ch["fontname"])
                if ch.get("size"):
                    entry["sizes"].append(ch["size"])
                entry["span_ids"].append(_stable_id(f"p{page_num}s", ch_idx + 1))

            for cy in sorted(lines_by_bottom.keys()):
                entry = lines_by_bottom[cy]
                region = Region.body
                lines.append(
                    Line(
                        line_id=entry["line_id"],
                        bbox=[entry["x0"], entry["top"], entry["x1"], entry["bottom"]],
                        text=entry["text"],
                        region=region,
                        font_sizes=entry["sizes"],
                        font_names=entry["fonts"],
                        span_ids=entry["span_ids"],
                    )
                )

            blocks: List[Block] = []
            block_counter = 0
            if lines:
                block_counter += 1
                min_x0 = min(l.bbox[0] for l in lines)
                min_top = min(l.bbox[1] for l in lines)
                max_x1 = max(l.bbox[2] for l in lines)
                max_bottom = max(l.bbox[3] for l in lines)
                blocks.append(
                    Block(
                        block_id=_stable_id(f"p{page_num}b", block_counter),
                        block_type=BlockType.text,
                        bbox=[min_x0, min_top, max_x1, max_bottom],
                        text=" ".join(l.text for l in lines),
                        line_ids=[l.line_id for l in lines],
                        reading_order=0,
                    )
                )

            page = Page(
                page_number=page_num,
                width=page_width,
                height=page_height,
                rotation=rotation,
                text_length=len(text_direct),
                blocks=blocks,
                lines=lines,
                spans=spans,
                issues=page_issues,
            )
            pages.append(page)

    if not pages:
        doc_issues.append(
            ParserIssue(type="empty_document", page_number=0, message="No pages extracted")
        )

    process_header_footer(pages)

    return PhysicalDocument(
        schema_version="1.0.0",
        parser_version="1.0.0",
        pipeline_run_id=pipeline_run_id,
        document_id=file_hash,
        policy_id=policy_id,
        source_pdf_path=pdf_path,
        file_hash=file_hash,
        page_count=len(pages),
        pages=pages,
        issues=doc_issues,
    )


def save_document(doc: PhysicalDocument, output_root: str, policy_slug: str) -> str:
    out_dir = os.path.join(output_root, policy_slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "document_physical.json")
    data = json.loads(doc.model_dump_json(exclude_none=True))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return out_path


def save_issues(doc: PhysicalDocument, output_root: str, policy_slug: str) -> str:
    out_dir = os.path.join(output_root, policy_slug)
    os.makedirs(out_dir, exist_ok=True)
    issues_data = []
    for issue in doc.issues:
        issues_data.append(issue.model_dump(exclude_none=True))
    for page in doc.pages:
        for issue in page.issues:
            issues_data.append(issue.model_dump(exclude_none=True))
    out_path = os.path.join(out_dir, "issues.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(issues_data, f, indent=2)
    return out_path


def process_single_pdf(
    pdf_path: str,
    policy_id: str,
    policy_slug: str,
    output_root: str,
    debug_root: Optional[str] = None,
    pipeline_run_id: Optional[str] = None,
) -> PhysicalDocument:
    if pipeline_run_id is None:
        pipeline_run_id = f"physical_v1_{int(time.time())}"

    doc = extract_pdf(pdf_path, policy_id, pipeline_run_id)
    save_document(doc, output_root, policy_slug)
    save_issues(doc, output_root, policy_slug)

    if debug_root:
        debug_dir = os.path.join(debug_root, policy_slug)
        generate_all(doc, debug_dir)

    return doc


def process_gold_corpus(
    gold_corpus_root: str,
    policy_data_root: str,
    output_root: str,
    debug_root: Optional[str] = None,
    pipeline_run_id: Optional[str] = None,
) -> List[dict]:
    if pipeline_run_id is None:
        pipeline_run_id = f"physical_v1_{int(time.time())}"

    results = []
    policies_dir = os.path.join(gold_corpus_root, "policies")
    if not os.path.isdir(policies_dir):
        print(f"ERROR: gold corpus policies dir not found: {policies_dir}", file=sys.stderr)
        return results

    slugs = sorted(os.listdir(policies_dir))
    for slug in slugs:
        metadata_path = os.path.join(policies_dir, slug, "metadata.json")
        if not os.path.isfile(metadata_path):
            print(f"  SKIP {slug}: no metadata.json", file=sys.stderr)
            continue

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        policy_id = metadata.get("policy_id", slug)
        rel_pdf_path = metadata.get("source_pdf_path", "")
        pdf_path = os.path.join(policy_data_root, rel_pdf_path)
        expected_hash = metadata.get("file_hash", "")
        expected_pages = metadata.get("page_count", 0)

        if not os.path.isfile(pdf_path):
            print(f"  ERROR {slug}: PDF not found at {pdf_path}", file=sys.stderr)
            results.append({"slug": slug, "status": "pdf_not_found", "path": pdf_path})
            continue

        print(f"  Processing {slug} ...")
        doc = process_single_pdf(
            pdf_path=pdf_path,
            policy_id=policy_id,
            policy_slug=slug,
            output_root=output_root,
            debug_root=debug_root,
            pipeline_run_id=pipeline_run_id,
        )

        actual_hash = doc.file_hash or ""
        page_count_ok = doc.page_count == expected_pages
        hash_ok = actual_hash == expected_hash

        issues = [i.model_dump() for i in doc.issues]
        if not page_count_ok:
            issues.append(
                {
                    "type": "page_count_mismatch",
                    "message": f"Expected {expected_pages}, got {doc.page_count}",
                }
            )

        result = {
            "slug": slug,
            "status": "ok",
            "page_count": doc.page_count,
            "expected_pages": expected_pages,
            "page_count_match": page_count_ok,
            "hash_match": hash_ok,
            "issue_count": len(issues),
        }
        results.append(result)
        print(f"    pages={doc.page_count}/{expected_pages} hash_ok={hash_ok}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Physical Layout Extractor v1")
    parser.add_argument("--pdf", help="Path to single PDF file")
    parser.add_argument("--policy-id", help="Policy ID for single PDF mode")
    parser.add_argument("--policy-slug", help="Policy slug for output directory naming")
    parser.add_argument("--gold-corpus", help="Path to gold_corpus/ dir for batch mode")
    _default_policy_data = str(
        pathlib.Path(__file__).resolve().parent.parent.parent / "policy_data"
    )
    parser.add_argument(
        "--policy-data-root",
        default=_default_policy_data,
        help="Root of the read-only policy_data directory",
    )
    parser.add_argument(
        "--output-root",
        default="data/interim/physical",
        help="Output root for document_physical.json",
    )
    parser.add_argument(
        "--debug-root", default="data/reports/physical_debug", help="Output root for debug HTML"
    )
    parser.add_argument("--pipeline-run-id", help="Optional override for pipeline_run_id")

    args = parser.parse_args()

    if args.gold_corpus:
        print(f"Processing gold corpus from {args.gold_corpus}")
        results = process_gold_corpus(
            gold_corpus_root=args.gold_corpus,
            policy_data_root=args.policy_data_root,
            output_root=args.output_root,
            debug_root=args.debug_root,
            pipeline_run_id=args.pipeline_run_id,
        )

        summary_path = os.path.join(args.output_root, "gold_run_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Summary written to {summary_path}")

        ok_count = sum(1 for r in results if r["status"] == "ok")
        fail_count = len(results) - ok_count
        print(f"\nDone: {ok_count} ok, {fail_count} failed")
        return

    if args.pdf:
        if not args.policy_id:
            print("ERROR: --policy-id is required with --pdf", file=sys.stderr)
            sys.exit(1)
        slug = args.policy_slug or args.policy_id
        print(f"Processing single PDF: {args.pdf}")
        doc = process_single_pdf(
            pdf_path=args.pdf,
            policy_id=args.policy_id,
            policy_slug=slug,
            output_root=args.output_root,
            debug_root=args.debug_root,
            pipeline_run_id=args.pipeline_run_id,
        )
        print(f"Done: {doc.page_count} pages, {len(doc.issues)} issues")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
