"""
Run Table Engine — DSE-009

Batch CLI: extract tables from gold corpus PDFs using the two-tier detection strategy.
Outputs document_tables.json and document_table_cells.json per policy.

Usage:
  PYTHONPATH=. python scripts/run_table_engine.py \\
    --gold-corpus gold_corpus \\
    --policy-data-root ../policy_data \\
    --physical-root data/interim/physical \\
    --section-root data/interim/logical \\
    --output-root data/interim/tables
"""

import argparse
import json
import logging
import os
import pathlib
import sys
import time
from typing import Any, Dict, List, Optional

import pdfplumber

from table_engine.models import (
    ExtractionMethod,
    ExtractedTable,
    TableDocument,
    TableType,
)
from table_engine.table_detector import extract_tables_from_page, extract_text_tables_from_page
from table_engine.table_type_classifier import classify
from table_engine.text_alignment_detector import try_page

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("run_table_engine")

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_physical_doc(physical_root: str, slug: str) -> Optional[dict]:
    path = os.path.join(physical_root, slug, "document_physical.json")
    if not os.path.isfile(path):
        return None
    return _load_json(path)


def _load_section_tree(section_root: str, slug: str) -> Optional[dict]:
    path = os.path.join(section_root, slug, "section_tree.json")
    if not os.path.isfile(path):
        return None
    return _load_json(path)


def _assign_parent_clause(page: int, section_tree: Optional[dict]) -> tuple:
    """
    Provisional parent clause assignment: find the most specific clause whose
    page range contains the given page number.

    DSE-006 clauses do not carry their own level. Use the owning section's
    level plus the clause page-span as the specificity signal until DSE-010 can
    replace this with true bbox/source-span overlap.

    Returns (parent_clause_id, confidence) or (None, None).
    """
    if not section_tree:
        return None, None

    clauses = section_tree.get("clauses", [])
    sections_by_id = {
        section.get("section_id"): section
        for section in section_tree.get("sections", [])
        if section.get("section_id")
    }
    best_clause_id = None
    best_span = None
    best_level = -1
    confidence = 0.0

    for clause in clauses:
        p_start = clause.get("page_start", 0)
        p_end = clause.get("page_end", p_start)
        if p_start <= page <= p_end:
            section = sections_by_id.get(clause.get("section_id"), {})
            level = section.get("level", 0)
            span = max(0, p_end - p_start)
            if best_span is None or span < best_span or (
                span == best_span and level > best_level
            ):
                best_span = span
                best_level = level
                best_clause_id = clause.get("clause_id")
                confidence = 0.75

    return best_clause_id, confidence if best_clause_id else None


def _get_physical_page_lines(physical_doc: Optional[dict], page_num: int) -> List[dict]:
    """Extract line dicts from PhysicalDocument for a given page number."""
    if not physical_doc:
        return []
    for page in physical_doc.get("pages", []):
        if page.get("page_number") == page_num:
            lines = []
            for ln in page.get("lines", []):
                lines.append(
                    {
                        "line_id": ln.get("line_id", ""),
                        "text": ln.get("text", ""),
                        "bbox": ln.get("bbox", []),
                        "region": ln.get("region", "body"),
                    }
                )
            return lines
    return []


def _bbox_iou(a: Optional[List[float]], b: Optional[List[float]]) -> float:
    if not a or not b or len(a) != 4 or len(b) != 4:
        return 0.0
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    intersection = (x1 - x0) * (y1 - y0)
    area_a = max(0.0, (a[2] - a[0]) * (a[3] - a[1]))
    area_b = max(0.0, (b[2] - b[0]) * (b[3] - b[1]))
    union = area_a + area_b - intersection
    return intersection / union if union else 0.0


def _table_text(table: ExtractedTable) -> str:
    parts = [cell.text for cell in table.cells]
    parts.extend(line.get("text", "") for line in table.raw_lines)
    return " ".join(part for part in parts if part).lower()


def _deduplicate_tables(tables: List[ExtractedTable]) -> List[ExtractedTable]:
    deduped: List[ExtractedTable] = []
    for table in sorted(tables, key=lambda t: (t.page, t.bbox or [0, 0, 0, 0], t.table_id)):
        duplicate = False
        table_text = _table_text(table)
        for existing in deduped:
            if table.page != existing.page:
                continue
            iou = _bbox_iou(table.bbox, existing.bbox)
            existing_text = _table_text(existing)
            text_overlap = bool(table_text and existing_text and table_text[:80] in existing_text)
            if iou >= 0.85 or (iou >= 0.5 and text_overlap):
                duplicate = True
                existing.issues.append(f"deduplicated_overlap:{table.table_id}")
                break
        if not duplicate:
            deduped.append(table)
    return deduped


def _is_reliable_pdfplumber_text_table(table: ExtractedTable, page_width: float, page_height: float) -> bool:
    if table.extraction_method != ExtractionMethod.pdfplumber_text:
        return True
    if not table.has_header_row or not table.cells:
        return False
    if table.col_count < 2 or table.col_count > 8:
        return False
    if table.row_count < 2 or table.row_count > 30:
        return False
    if not table.bbox:
        return False
    table_area = max(0.0, table.bbox[2] - table.bbox[0]) * max(0.0, table.bbox[3] - table.bbox[1])
    page_area = page_width * page_height
    if page_area and table_area / page_area > 0.45:
        return False
    return True


def process_policy(
    pdf_path: str,
    policy_id: str,
    slug: str,
    physical_root: str,
    section_root: str,
    output_root: str,
    pipeline_run_id: str,
) -> dict:
    """
    Process a single policy PDF:
    1. Extract tables with primary (lattice) detector.
    2. For pages with no lattice tables, try text alignment fallback.
    3. Classify each table type.
    4. Assign parent clause.
    5. Save outputs.

    Returns a summary dict for the run report.
    """
    logger.info("Processing %s", slug)

    physical_doc = _load_physical_doc(physical_root, slug)
    section_tree = _load_section_tree(section_root, slug)

    if physical_doc is None:
        logger.warning(
            "  No document_physical.json found for %s — skipping fallback detector", slug
        )

    document_id = physical_doc.get("document_id", "") if physical_doc else ""
    page_count = physical_doc.get("page_count", 0) if physical_doc else 0

    all_tables: List[ExtractedTable] = []
    doc_issues: List[str] = []

    try:
        pdf = pdfplumber.open(pdf_path)
    except Exception as e:
        logger.error("  Cannot open PDF %s: %s", pdf_path, e)
        return {
            "slug": slug,
            "status": "pdf_open_failed",
            "error": str(e),
            "tables_found": 0,
        }

    with pdf:
        total_pages = len(pdf.pages)
        if page_count == 0:
            page_count = total_pages

        global_table_counter = 1  # across all pages

        for page_num, plumber_page in enumerate(pdf.pages, start=1):
            page_table_counter = 1  # per-page counter for stable IDs

            # --- Primary: pdfplumber lattice ---
            lattice_tables, page_table_counter = extract_tables_from_page(
                page=plumber_page,
                page_num=page_num,
                policy_id=policy_id,
                document_id=document_id,
                page_table_counter=page_table_counter,
            )

            # --- Secondary: conservative pdfplumber text table strategy ---
            text_tables: List[ExtractedTable] = []
            if not lattice_tables:
                text_tables, page_table_counter = extract_text_tables_from_page(
                    page=plumber_page,
                    page_num=page_num,
                    policy_id=policy_id,
                    document_id=document_id,
                    page_table_counter=page_table_counter,
                )
                text_tables = [
                    table
                    for table in text_tables
                    if _is_reliable_pdfplumber_text_table(table, plumber_page.width, plumber_page.height)
                ]

            # --- Fallback: text alignment ---
            fallback_tables: List[ExtractedTable] = []
            if not lattice_tables and not text_tables:
                phys_lines = _get_physical_page_lines(physical_doc, page_num)
                if phys_lines:
                    page_height = 842.0
                    page_width = 595.0
                    if physical_doc:
                        for pg in physical_doc.get("pages", []):
                            if pg.get("page_number") == page_num:
                                page_height = pg.get("height", 842.0)
                                page_width = pg.get("width", 595.0)
                                break
                    fallback_tables, page_table_counter = try_page(
                        physical_page_lines=phys_lines,
                        page_num=page_num,
                        policy_id=policy_id,
                        document_id=document_id,
                        page_table_counter=page_table_counter,
                        page_width=page_width,
                        page_height=page_height,
                    )

            page_tables = _deduplicate_tables(lattice_tables + text_tables + fallback_tables)

            # --- Classify + assign parent clause ---
            for table in page_tables:
                # Type classification
                raw_grid = table.__dict__.get("_raw_grid") or []
                heading_context = table.__dict__.get("_heading_context") or ""
                if raw_grid:
                    t_type, t_conf = classify(raw_grid, heading_context)
                else:
                    t_type, t_conf = TableType.unknown, 0.0
                table.table_type = t_type
                table.table_type_confidence = t_conf

                # For text_alignment_candidate, blend base confidence
                if table.extraction_method == ExtractionMethod.text_alignment_candidate:
                    base_conf = table.__dict__.get("_base_confidence", 0.30)
                    # type confidence modulates the base
                    table.table_type_confidence = round(t_conf * base_conf + 0.01, 4)

                # Parent clause assignment
                parent_id, parent_conf = _assign_parent_clause(table.page, section_tree)
                table.parent_clause_id = parent_id
                table.parent_clause_confidence = parent_conf

            all_tables.extend(page_tables)

    # --- Build TableDocument ---
    structured = sum(
        1
        for t in all_tables
        if t.extraction_method in {ExtractionMethod.pdfplumber_lattice, ExtractionMethod.pdfplumber_text}
    )
    candidates = sum(
        1 for t in all_tables if t.extraction_method == ExtractionMethod.text_alignment_candidate
    )

    table_doc = TableDocument(
        pipeline_run_id=pipeline_run_id,
        document_id=document_id,
        policy_id=policy_id,
        source_pdf_path=pdf_path,
        page_count=page_count,
        tables_found=len(all_tables),
        structured_tables=structured,
        candidate_tables=candidates,
        tables=all_tables,
        issues=doc_issues,
    )

    # --- Save outputs ---
    out_dir = os.path.join(output_root, slug)
    os.makedirs(out_dir, exist_ok=True)

    tables_path = os.path.join(out_dir, "document_tables.json")
    data = json.loads(table_doc.model_dump_json(exclude_none=True))
    with open(tables_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Flat cells file
    all_cells = []
    for t in all_tables:
        for cell in t.cells:
            all_cells.append(json.loads(cell.model_dump_json(exclude_none=True)))
    cells_path = os.path.join(out_dir, "document_table_cells.json")
    with open(cells_path, "w", encoding="utf-8") as f:
        json.dump(all_cells, f, indent=2)

    logger.info(
        "  %s: %d tables total (%d lattice, %d candidates), %d cells",
        slug,
        len(all_tables),
        structured,
        candidates,
        len(all_cells),
    )

    return {
        "slug": slug,
        "status": "ok",
        "tables_found": len(all_tables),
        "structured_tables": structured,
        "candidate_tables": candidates,
        "cells_extracted": len(all_cells),
        "issues": doc_issues,
    }


def main():
    parser = argparse.ArgumentParser(description="Table Engine v1 — DSE-009")
    parser.add_argument(
        "--gold-corpus",
        default="gold_corpus",
        help="Path to gold_corpus/ directory",
    )
    parser.add_argument(
        "--policy-data-root",
        default=str(_PROJECT_ROOT.parent / "policy_data"),
        help="Root of the read-only policy_data directory",
    )
    parser.add_argument(
        "--physical-root",
        default="data/interim/physical",
        help="Root of physical JSON outputs from DSE-004",
    )
    parser.add_argument(
        "--section-root",
        default="data/interim/logical",
        help="Root of section tree JSON outputs from DSE-006",
    )
    parser.add_argument(
        "--output-root",
        default="data/interim/tables",
        help="Output root for table JSON files",
    )
    parser.add_argument("--pipeline-run-id", help="Optional pipeline run ID override")
    args = parser.parse_args()

    pipeline_run_id = args.pipeline_run_id or f"table_v1_{int(time.time())}"
    policies_dir = os.path.join(args.gold_corpus, "policies")

    if not os.path.isdir(policies_dir):
        logger.error("Gold corpus policies dir not found: %s", policies_dir)
        sys.exit(1)

    slugs = sorted(os.listdir(policies_dir))
    results = []
    had_fatal = False

    for slug in slugs:
        metadata_path = os.path.join(policies_dir, slug, "metadata.json")
        if not os.path.isfile(metadata_path):
            logger.warning("SKIP %s: no metadata.json", slug)
            continue

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        policy_id = metadata.get("policy_id", slug)
        rel_pdf = metadata.get("source_pdf_path", "")
        pdf_path = os.path.join(args.policy_data_root, rel_pdf)

        if not os.path.isfile(pdf_path):
            logger.error("PDF not found: %s", pdf_path)
            results.append({"slug": slug, "status": "pdf_not_found", "path": pdf_path})
            had_fatal = True
            continue

        try:
            result = process_policy(
                pdf_path=pdf_path,
                policy_id=policy_id,
                slug=slug,
                physical_root=args.physical_root,
                section_root=args.section_root,
                output_root=args.output_root,
                pipeline_run_id=pipeline_run_id,
            )
            results.append(result)
        except Exception as e:
            logger.exception("FATAL error processing %s: %s", slug, e)
            results.append({"slug": slug, "status": "fatal_exception", "error": str(e)})
            had_fatal = True

    # Write run summary
    summary_path = os.path.join(args.output_root, "table_run_summary.json")
    os.makedirs(args.output_root, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "pipeline_run_id": pipeline_run_id,
                "policies": results,
                "total_ok": sum(1 for r in results if r.get("status") == "ok"),
                "total_failed": sum(1 for r in results if r.get("status") != "ok"),
            },
            f,
            indent=2,
        )
    logger.info("Run summary written to %s", summary_path)

    total_ok = sum(1 for r in results if r.get("status") == "ok")
    logger.info("Done: %d/%d policies processed successfully", total_ok, len(results))

    if had_fatal:
        sys.exit(1)


if __name__ == "__main__":
    main()
