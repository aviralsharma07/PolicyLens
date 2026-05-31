"""
Primary table detector — DSE-009

Uses pdfplumber.find_tables() with either visible-line settings or conservative
text settings.

For borderless tables (empty find_tables result), the caller should invoke
text_alignment_detector.try_page() as the fallback.
"""

import logging
from typing import List, Optional, Tuple

import pdfplumber
from pdfplumber.page import Page as PdfPage

from table_engine.cell_extractor import build_cells
from table_engine.models import ExtractionMethod, ExtractedTable

logger = logging.getLogger(__name__)


def _stable_table_id(policy_id: str, page: int, n: int) -> str:
    """Stable table ID: {policy_id}_p{page}_t{n} where n is 1-based per page."""
    return f"{policy_id}_p{page}_t{n}"


def _extract_heading_context(
    page: PdfPage, table_bbox: Tuple[float, float, float, float], n_lines: int = 3
) -> str:
    """
    Extract up to n_lines of text immediately above the table bbox.
    Used to provide heading context to the type classifier.
    """
    tx0, ttop, tx1, tbottom = table_bbox
    context_parts = []

    # Crop a region above the table
    above_top = max(0, ttop - 80)  # look 80pt above table
    if above_top >= ttop:
        return ""

    try:
        page_x0, page_top, page_x1, _page_bottom = page.bbox
        crop_x0 = max(page_x0, tx0 - 50)
        crop_x1 = min(page_x1, tx1 + 50)
        crop_top = max(page_top, above_top)
        crop_bottom = min(ttop, page.bbox[3])
        if crop_x0 >= crop_x1 or crop_top >= crop_bottom:
            return ""
        region = page.crop((crop_x0, crop_top, crop_x1, crop_bottom))
        text = region.extract_text() or ""
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        context_parts = lines[-n_lines:] if len(lines) > n_lines else lines
    except Exception as e:
        logger.warning(
            "Failed to extract heading context above table bbox %s on page %s: %s",
            table_bbox,
            getattr(page, "page_number", "unknown"),
            e,
        )

    return " ".join(context_parts)


def _get_cell_bboxes_from_table(plumber_table) -> Optional[List[List[Optional[List[float]]]]]:
    """
    Extract per-cell bboxes from a pdfplumber Table.

    Prefer row.cells because pdfplumber has already resolved row structure.
    This preserves merged/empty cells more reliably than reshaping the flat
    plumber_table.cells list.
    """
    try:
        if not plumber_table.rows:
            return None

        grid_bboxes: List[List[Optional[List[float]]]] = []
        for row in plumber_table.rows:
            row_bboxes = []
            for cell in row.cells:
                if cell is not None and len(cell) == 4:
                    row_bboxes.append([float(cell[0]), float(cell[1]), float(cell[2]), float(cell[3])])
                else:
                    row_bboxes.append(None)
            grid_bboxes.append(row_bboxes)
        return grid_bboxes
    except Exception as e:
        logger.debug("Could not extract per-cell bboxes: %s", e)
        return None


def _extract_with_settings(
    page: PdfPage,
    page_num: int,
    policy_id: str,
    document_id: str,
    page_table_counter: int,
    extraction_method: ExtractionMethod,
    table_settings: Optional[dict] = None,
) -> Tuple[List[ExtractedTable], int]:
    results: List[ExtractedTable] = []

    try:
        plumber_tables = page.find_tables(table_settings=table_settings)
    except Exception as e:
        logger.warning("find_tables(%s) failed on page %d: %s", extraction_method.value, page_num, e)
        return results, page_table_counter

    for plumber_table in plumber_tables:
        try:
            table_id = _stable_table_id(policy_id, page_num, page_table_counter)
            page_table_counter += 1

            # Raw cell grid
            grid = plumber_table.extract()
            if not grid:
                issues = ["empty_cell_grid"]
                results.append(
                    ExtractedTable(
                        table_id=table_id,
                        document_id=document_id,
                        policy_id=policy_id,
                        page=page_num,
                        bbox=list(plumber_table.bbox) if plumber_table.bbox else None,
                        extraction_method=extraction_method,
                        row_count=0,
                        col_count=0,
                        issues=issues,
                    )
                )
                continue

            # Per-cell bboxes
            cell_bboxes = _get_cell_bboxes_from_table(plumber_table)

            # Build structured cells
            cells, has_header_row, header_row_index = build_cells(table_id, grid, cell_bboxes)
            missing_cell_bbox_count = sum(1 for cell in cells if cell.bbox is None)

            # Heading context for classifier
            heading_context = ""
            if plumber_table.bbox:
                heading_context = _extract_heading_context(page, plumber_table.bbox)

            row_count = len(grid)
            col_count = max((len(row) for row in grid), default=0)

            bbox_list = list(plumber_table.bbox) if plumber_table.bbox else None

            table = ExtractedTable(
                table_id=table_id,
                document_id=document_id,
                policy_id=policy_id,
                page=page_num,
                bbox=bbox_list,
                extraction_method=extraction_method,
                row_count=row_count,
                col_count=col_count,
                has_header_row=has_header_row,
                header_row_index=header_row_index,
                header_rows=[header_row_index] if header_row_index is not None else [],
                column_headers=[
                    cell.text for cell in cells if header_row_index is not None and cell.row_index == header_row_index
                ],
                cells=cells,
                issues=[f"cell_bbox_missing:{missing_cell_bbox_count}"]
                if missing_cell_bbox_count
                else [],
            )
            # Store heading context on the table for later classification step
            table.__dict__["_heading_context"] = heading_context
            table.__dict__["_raw_grid"] = grid

            results.append(table)

        except Exception as e:
            logger.exception("Error extracting table on page %d: %s", page_num, e)
            issue_table = ExtractedTable(
                table_id=_stable_table_id(policy_id, page_num, page_table_counter - 1),
                document_id=document_id,
                policy_id=policy_id,
                page=page_num,
                extraction_method=extraction_method,
                issues=[f"extraction_exception: {e}"],
            )
            results.append(issue_table)

    return results, page_table_counter


def extract_tables_from_page(
    page: PdfPage,
    page_num: int,
    policy_id: str,
    document_id: str,
    page_table_counter: int,
) -> Tuple[List[ExtractedTable], int]:
    """
    Extract all visible-line / lattice-style tables from a single pdfplumber page.
    """
    return _extract_with_settings(
        page=page,
        page_num=page_num,
        policy_id=policy_id,
        document_id=document_id,
        page_table_counter=page_table_counter,
        extraction_method=ExtractionMethod.pdfplumber_lattice,
        table_settings=None,
    )


def extract_text_tables_from_page(
    page: PdfPage,
    page_num: int,
    policy_id: str,
    document_id: str,
    page_table_counter: int,
) -> Tuple[List[ExtractedTable], int]:
    """
    Conservative pdfplumber text-strategy extraction for borderless but genuinely
    columnar tables. This is not used to structure prose/list regions.
    """
    settings = {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "min_words_vertical": 3,
        "min_words_horizontal": 2,
        "intersection_tolerance": 5,
        "snap_tolerance": 3,
        "join_tolerance": 3,
    }
    return _extract_with_settings(
        page=page,
        page_num=page_num,
        policy_id=policy_id,
        document_id=document_id,
        page_table_counter=page_table_counter,
        extraction_method=ExtractionMethod.pdfplumber_text,
        table_settings=settings,
    )
