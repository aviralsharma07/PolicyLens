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


def validate_bbox(
    bbox: List[float], width: float, height: float, page_num: int, label: str
) -> List[str]:
    errs = []
    if len(bbox) != 4:
        errs.append(f"p{page_num} {label}: bbox length != 4 ({len(bbox)})")
        return errs
    x0, top, x1, bottom = bbox
    if x0 < -1 or x1 > width + 1 or top < -1 or bottom > height + 1:
        errs.append(
            f"p{page_num} {label}: bbox [{x0:.1f},{top:.1f},{x1:.1f},{bottom:.1f}] "
            f"out of bounds [0,0,{width},{height}]"
        )
    if x0 >= x1:
        errs.append(f"p{page_num} {label}: x0 ({x0}) >= x1 ({x1})")
    if top >= bottom:
        errs.append(f"p{page_num} {label}: top ({top}) >= bottom ({bottom})")
    return errs


def validate_page(page_data: Dict[str, Any], expected_page_count: int) -> List[str]:
    errs = []
    pn = page_data.get("page_number", 0)
    w = page_data.get("width", 0)
    h = page_data.get("height", 0)

    if w <= 0:
        errs.append(f"p{pn}: invalid width {w}")
    if h <= 0:
        errs.append(f"p{pn}: invalid height {h}")

    rotation = page_data.get("rotation", 0)
    if rotation not in (0, 90, 180, 270):
        errs.append(f"p{pn}: unusual rotation {rotation}")

    blocks = page_data.get("blocks", [])
    lines = page_data.get("lines", [])
    spans = page_data.get("spans", [])

    if not blocks and pn > 1:
        errs.append(f"p{pn}: no blocks (non-cover page)")
    if not lines:
        errs.append(f"p{pn}: no lines")
    if not spans:
        errs.append(f"p{pn}: no spans")

    for block in blocks:
        errs.extend(
            validate_bbox(block.get("bbox", []), w, h, pn, f"block_{block.get('block_id', '?')}")
        )

    for line in lines:
        errs.extend(
            validate_bbox(line.get("bbox", []), w, h, pn, f"line_{line.get('line_id', '?')}")
        )

    for span in spans:
        errs.extend(
            validate_bbox(span.get("bbox", []), w, h, pn, f"span_{span.get('span_id', '?')}")
        )

    return errs


def validate_document(doc_path: str, metadata_path: str, debug_dir: str) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    if not os.path.isfile(doc_path):
        return {
            "path": doc_path,
            "status": "missing",
            "errors": ["document_physical.json not found"],
        }

    if not os.path.isfile(metadata_path):
        return {
            "path": doc_path,
            "status": "missing_metadata",
            "errors": ["metadata.json not found"],
        }

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    try:
        doc = load_document(doc_path)
    except Exception as e:
        return {"path": doc_path, "status": "invalid", "errors": [f"Failed to load: {e}"]}

    expected_pages = metadata.get("page_count", 0)
    expected_hash = metadata.get("file_hash", "")

    if doc.page_count != expected_pages:
        errors.append(f"page_count mismatch: got {doc.page_count}, expected {expected_pages}")

    if doc.schema_version != "1.0.0":
        errors.append(f"schema_version: got {doc.schema_version}, expected 1.0.0")

    if doc.parser_version != "1.0.0":
        errors.append(f"parser_version: got {doc.parser_version}, expected 1.0.0")

    if not doc.pipeline_run_id:
        errors.append("pipeline_run_id is empty")

    if doc.file_hash and expected_hash and doc.file_hash != expected_hash:
        errors.append(f"file_hash mismatch: got {doc.file_hash}, expected {expected_hash}")

    for page_data in [p.model_dump() for p in doc.pages]:
        errs = validate_page(page_data, expected_pages)
        errors.extend(errs)

    non_empty = sum(1 for p in doc.pages if p.text_length > 0)
    total_pages = doc.page_count
    if total_pages > 2 and non_empty < max(1, total_pages - 2):
        errors.append(f"Only {non_empty}/{total_pages} pages have non-empty text")

    spans_with_font = sum(1 for p in doc.pages for s in p.spans if s.font_size is not None)
    total_spans = sum(len(p.spans) for p in doc.pages)
    if total_spans > 0:
        font_pct = spans_with_font / total_spans * 100
        if font_pct < 90:
            warnings.append(
                f"Font size metadata: {font_pct:.1f}% ({spans_with_font}/{total_spans})"
            )

    if debug_dir and os.path.isdir(debug_dir):
        html_files = sorted(f for f in os.listdir(debug_dir) if f.endswith(".html"))
        if len(html_files) != total_pages:
            warnings.append(f"Debug HTML: {len(html_files)} files for {total_pages} pages")
        for pn in range(1, total_pages + 1):
            expected = f"page_{pn:03d}.html"
            if expected not in html_files:
                warnings.append(f"Missing debug HTML: {expected}")
    else:
        warnings.append(f"Debug directory not found: {debug_dir}")

    return {
        "path": doc_path,
        "slug": os.path.basename(os.path.dirname(doc_path)),
        "status": "failed" if errors else "passed",
        "errors": errors,
        "warnings": warnings,
        "page_count": doc.page_count,
        "expected_pages": expected_pages,
        "total_pages_actual": len(doc.pages),
        "non_empty_pages": non_empty,
        "total_spans": total_spans,
        "spans_with_font": spans_with_font,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate Physical Parser Outputs")
    parser.add_argument("--gold-corpus", required=True, help="Path to gold_corpus/")
    parser.add_argument("--physical-root", required=True, help="Root of physical parser outputs")
    parser.add_argument("--debug-root", required=True, help="Root of debug HTML outputs")
    parser.add_argument("--output", help="Path to write validation report JSON")

    args = parser.parse_args()

    policies_dir = os.path.join(args.gold_corpus, "policies")
    slugs = sorted(os.listdir(policies_dir))
    results = []

    all_ok = True
    for slug in slugs:
        metadata_path = os.path.join(policies_dir, slug, "metadata.json")
        doc_path = os.path.join(args.physical_root, slug, "document_physical.json")
        debug_dir = os.path.join(args.debug_root, slug)

        result = validate_document(doc_path, metadata_path, debug_dir)
        results.append(result)

        if result["status"] == "passed":
            print(f"  PASS {slug}: {result['page_count']} pages, {result['total_spans']} spans")
        else:
            all_ok = False
            print(
                f"  FAIL {slug}: {len(result['errors'])} errors, {len(result['warnings'])} warnings"
            )
            for e in result["errors"][:5]:
                print(f"    ERR: {e}")
            for w in result["warnings"][:3]:
                print(f"    WARN: {w}")

    print(f"\nTotal: {len(results)} policies")
    passed = sum(1 for r in results if r["status"] == "passed")
    print(f"Passed: {passed}")
    print(f"Failed: {len(results) - passed}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Report written to {args.output}")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
