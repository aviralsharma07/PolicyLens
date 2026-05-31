"""
Text alignment fallback detector — DSE-009

Detects borderless table-like regions using column x-cluster heuristics.
Extraction method: text_alignment_candidate.

Precision-first: if column split is ambiguous, cells=[] and an issue is logged.
No silent failure. No fake structure.
"""

import logging
from typing import List, Optional, Tuple

from table_engine.models import (
    ColumnCluster,
    ExtractionMethod,
    ExtractedTable,
)

logger = logging.getLogger(__name__)

# Minimum consecutive lines that share the same column structure to count as a table
_MIN_TABLE_LINES = 3

# Maximum gap between x-positions within the same column cluster (points)
_COLUMN_CLUSTER_GAP = 20.0

# Minimum number of distinct column clusters to consider a region tabular
_MIN_COLUMNS = 2

# Confidence assigned to reliably-split text_alignment_candidate tables
_STRUCTURED_CONFIDENCE = 0.55

# Confidence assigned to candidate tables where cells could not be reliably split
_AMBIGUOUS_CONFIDENCE = 0.30


def _cluster_x_positions(x_starts: List[float]) -> List[Tuple[float, float, float]]:
    """
    Cluster a list of x-start positions into column groups.

    Returns: list of (x_center, x_min, x_max) per cluster, sorted by x_center.
    """
    if not x_starts:
        return []

    sorted_xs = sorted(set(round(x, 1) for x in x_starts))
    clusters: List[List[float]] = []
    current: List[float] = [sorted_xs[0]]

    for x in sorted_xs[1:]:
        if x - current[-1] <= _COLUMN_CLUSTER_GAP:
            current.append(x)
        else:
            clusters.append(current)
            current = [x]
    clusters.append(current)

    result = []
    for group in clusters:
        x_min = min(group)
        x_max = max(group)
        x_center = sum(group) / len(group)
        result.append((x_center, x_min, x_max))

    return result


def _extract_word_starts(line_data: dict) -> List[float]:
    """
    Extract x-start positions of words from a physical doc line dict.
    line_data has 'text' and 'bbox': [x0, top, x1, bottom].
    """
    # We use the line's x0 as a crude column indicator.
    # A more precise approach would split on word boundaries using char-level spans,
    # but for v1, we use line-level x0 and approximate word splitting by spaces.
    text = line_data.get("text", "")
    line_x0 = line_data.get("bbox", [0])[0]
    if not text.strip():
        return []

    # Simple heuristic: if tab characters present, use them as column delimiters
    if "\t" in text:
        # Can't determine per-column x from line_x0 alone without char data
        return [line_x0]

    # For non-tab lines, return just the line's x0 as a single column indicator
    return [line_x0]


def try_page(
    physical_page_lines: List[dict],
    page_num: int,
    policy_id: str,
    document_id: str,
    page_table_counter: int,
    page_width: float = 595.0,
    page_height: float = 842.0,
) -> Tuple[List[ExtractedTable], int]:
    """
    Attempt to detect borderless table-like regions on a page using text alignment.

    Args:
        physical_page_lines: List of line dicts from PhysicalDocument.Page.
                             Each dict: {'line_id', 'bbox', 'text', 'region'}.
        page_num: 1-based page number.
        policy_id: Policy identifier.
        document_id: Document identifier.
        page_table_counter: Table counter (1-based) for this page.
        page_width: Page width in points (for column gap analysis).
        page_height: Page height in points.

    Returns:
        (list of ExtractedTable candidates, updated page_table_counter)
    """
    results: List[ExtractedTable] = []

    # Filter to body lines (exclude headers/footers)
    body_lines = [
        ln
        for ln in physical_page_lines
        if ln.get("region", "body") == "body" and ln.get("text", "").strip()
    ]

    if len(body_lines) < _MIN_TABLE_LINES:
        return results, page_table_counter

    # Collect x-start positions of all body lines
    x_starts = [ln.get("bbox", [0])[0] for ln in body_lines if ln.get("bbox")]
    clusters = _cluster_x_positions(x_starts)

    if len(clusters) < _MIN_COLUMNS:
        # Not enough distinct x positions to form column structure
        return results, page_table_counter

    # Find runs of lines that align with at least 2 of the detected columns
    # For v1: look for 3+ consecutive lines whose x0 falls within known cluster ranges
    cluster_ranges = [(x_min - 5, x_max + 5) for _, x_min, x_max in clusters]

    def _line_col_index(line_x0: float) -> Optional[int]:
        for idx, (lo, hi) in enumerate(cluster_ranges):
            if lo <= line_x0 <= hi:
                return idx
        return None

    # Group body lines into candidate regions
    current_region: List[dict] = []
    regions: List[List[dict]] = []

    for ln in body_lines:
        bbox = ln.get("bbox", [])
        if not bbox:
            continue
        col_idx = _line_col_index(bbox[0])
        if col_idx is not None:
            current_region.append(ln)
        else:
            if len(current_region) >= _MIN_TABLE_LINES:
                regions.append(current_region)
            current_region = []

    if len(current_region) >= _MIN_TABLE_LINES:
        regions.append(current_region)

    for region_lines in regions:
        table_id = f"{policy_id}_p{page_num}_t{page_table_counter}"
        page_table_counter += 1
        issues: List[str] = []

        # Infer bbox from line bboxes
        xs0 = [ln["bbox"][0] for ln in region_lines if ln.get("bbox")]
        tops = [ln["bbox"][1] for ln in region_lines if ln.get("bbox")]
        xs1 = [ln["bbox"][2] for ln in region_lines if ln.get("bbox")]
        bottoms = [ln["bbox"][3] for ln in region_lines if ln.get("bbox")]

        if xs0 and tops and xs1 and bottoms:
            bbox = [min(xs0), min(tops), max(xs1), max(bottoms)]
        else:
            bbox = None

        # Build column clusters for this region
        region_x_starts = [ln["bbox"][0] for ln in region_lines if ln.get("bbox")]
        region_clusters_raw = _cluster_x_positions(region_x_starts)
        col_clusters = [
            ColumnCluster(
                col_index=i,
                x_center=xc,
                x_min=xmin,
                x_max=xmax,
            )
            for i, (xc, xmin, xmax) in enumerate(region_clusters_raw)
        ]

        # Attempt to build a grid from the region lines
        # Strategy: assign each line to the column cluster matching its x0
        # Then group lines by y-proximity into "rows"
        # This is intentionally conservative — if ambiguous, emit cells=[]
        n_cols = len(region_clusters_raw)
        if n_cols >= _MIN_COLUMNS:
            # Build a simple 1-text-per-line grid (each line = one row, one column)
            # This is the safest v1 approach for text-alignment tables.
            # True multi-column grids require char-level x positions (deferred to v2).
            # Check if the grid has consistent structure
            # For v1: if each row has exactly 1 cell (we only track x0), mark as ambiguous
            # unless the text contains obvious column separators (spaces/tabs)
            # Real multi-col split requires char-level data → defer
            issues.append("cells_not_reliably_split")
            confidence = _AMBIGUOUS_CONFIDENCE
        else:
            issues.append("cells_not_reliably_split")
            confidence = _AMBIGUOUS_CONFIDENCE

        table = ExtractedTable(
            table_id=table_id,
            document_id=document_id,
            policy_id=policy_id,
            page=page_num,
            bbox=bbox,
            extraction_method=ExtractionMethod.text_alignment_candidate,
            row_count=len(region_lines),
            col_count=n_cols,
            has_header_row=False,
            cells=[],
            raw_lines=[
                {
                    "line_id": ln.get("line_id", ""),
                    "text": ln.get("text", ""),
                    "bbox": ln.get("bbox"),
                }
                for ln in region_lines
            ],
            column_clusters=col_clusters,
            issues=issues,
        )
        # Store raw grid for classifier
        table.__dict__["_raw_grid"] = [[ln.get("text", "")] for ln in region_lines]
        table.__dict__["_heading_context"] = ""
        # Override confidence (stored as a hint; type classifier sets table_type_confidence)
        table.__dict__["_base_confidence"] = confidence

        results.append(table)

    return results, page_table_counter
