"""
Cell extractor — DSE-009

Transforms a raw pdfplumber cell grid + cell bboxes into structured TableCell objects.
Detects header row. Normalizes None cells to "".
Never claims structure that isn't there.
"""

from typing import List, Optional, Tuple

from table_engine.models import TableCell

# Known header-row terms (lowercase, substring match)
_HEADER_TERMS = [
    "sl no",
    "sl. no",
    "sr no",
    "sr. no",
    "waiting period type",
    "waiting period",
    "benefit",
    "benefits",
    "limit",
    "limit/condition",
    "duration",
    "variant",
    "cover",
    "sum insured",
    "rate",
    "period",
    "type",
    "description",
    "particulars",
    "item",
    "benefit / sub-limit",
    "room category",
    "amount",
    "amount payable",
    "documents",
    "losses covered",
    "percentage of sum insured",
    "% of sum",
    "fracture",
    "hospital name",
    "city",
    "state",
]


def _normalize_cell_text(text: Optional[str]) -> str:
    """Normalize None and whitespace-only cells to empty string."""
    if text is None:
        return ""
    return text.strip()


def _detect_header_row(grid: List[List[Optional[str]]]) -> Optional[int]:
    """
    Detect which row (if any) is the header row.

    Strategy:
    1. Check up to the first 3 rows for known header terms.
    2. Prefer rows with 2+ non-empty cells so a title row such as
       "For policy with one year term" does not block the true header row.
    3. If 1+ header term found → that row is the header.
    4. Otherwise, no header detected (has_header_row=False).

    Returns the header row index (int) or None.
    """
    if not grid:
        return None

    for row_idx, row in enumerate(grid[:3]):
        normalized_cells = [_normalize_cell_text(c) for c in row]
        non_empty_cells = [c for c in normalized_cells if c]
        if len(non_empty_cells) < 2:
            continue
        row_text = " ".join(normalized_cells).lower()
        for term in _HEADER_TERMS:
            if term in row_text:
                return row_idx

    return None


def build_cells(
    table_id: str,
    grid: List[List[Optional[str]]],
    cell_bboxes: Optional[List[List[Optional[List[float]]]]] = None,
) -> Tuple[List[TableCell], bool, Optional[int]]:
    """
    Build TableCell list from a raw cell grid.

    Args:
        table_id: Stable table ID for cell ID generation.
        grid: list[list[str|None]] from pdfplumber table.extract() or text alignment.
        cell_bboxes: Optional parallel structure with per-cell [x0,top,x1,bottom] bboxes.
                     May be None (no per-cell coords) or contain None entries.

    Returns:
        (cells, has_header_row, header_row_index)
    """
    header_row_index = _detect_header_row(grid)
    has_header_row = header_row_index is not None
    column_headers: List[str] = []
    if header_row_index is not None and header_row_index < len(grid):
        column_headers = [_normalize_cell_text(c) for c in grid[header_row_index]]

    cells: List[TableCell] = []

    for row_idx, row in enumerate(grid):
        for col_idx, raw_text in enumerate(row):
            text = _normalize_cell_text(raw_text)

            # Extract bbox for this cell if available
            bbox: Optional[List[float]] = None
            if cell_bboxes is not None:
                try:
                    raw_bbox = cell_bboxes[row_idx][col_idx]
                    if raw_bbox is not None and len(raw_bbox) == 4:
                        bbox = [float(v) for v in raw_bbox]
                except (IndexError, TypeError):
                    bbox = None

            cell = TableCell(
                cell_id=f"{table_id}_r{row_idx}_c{col_idx}",
                table_id=table_id,
                row_index=row_idx,
                col_index=col_idx,
                text=text,
                bbox=bbox,
                is_header=(row_idx == header_row_index),
                column_header_text=column_headers[col_idx]
                if column_headers and col_idx < len(column_headers) and row_idx != header_row_index
                else None,
                row_header_text=_normalize_cell_text(row[0])
                if row_idx != header_row_index and col_idx > 0 and row
                else None,
                row_span=1,
                col_span=1,
            )
            cells.append(cell)

    return cells, has_header_row, header_row_index
