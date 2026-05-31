"""
Table type classifier — DSE-009

Keyword-based precision-first classifier. No ML.
Matches against cell text + heading context from physical doc lines.

Types: waiting_period, schedule_of_benefits, room_rent, premium,
       claims_documents, network_list, unknown
"""

from typing import List, Optional, Tuple

from table_engine.models import TableType

# ---------------------------------------------------------------------------
# Keyword sets per type — all lowercase, matched as substrings
# ---------------------------------------------------------------------------

_KEYWORDS: dict = {
    TableType.waiting_period: [
        "waiting period",
        "waiting period type",
        "pre-existing",
        "pre existing",
        "ped",
        "initial waiting",
        "initial wait",
        "specific disease",
        "specific waiting",
        "specific illness",
        "duration",
        "maternity waiting",
        "named ailment",
        "first year exclusion",
        "second year exclusion",
        "moratorium",
    ],
    TableType.schedule_of_benefits: [
        "schedule of benefits",
        "schedule of benefit",
        "table of benefits",
        "benefits",
        "losses covered",
        "insured events",
        "amount payable",
        "% of sum insured",
        "% of the sum insured",
        "percentage of sum insured",
        "sum insured payable",
        "continuous hospitalization",
        "fracture",
        "treatment or procedure",
        "limit (per policy period)",
        "room rent, boarding",
        "intensive care unit",
        "ambulance",
        "restoration benefit",
        "cumulative bonus",
        "no claim bonus",
        "ncb",
        "organ donor",
        "modern treatment",
        "ayush",
        "limit/condition",
        "benefit / sub-limit",
        "benefit/sub limit",
        "cataract",
        "cataract surgery",
        "limit for cataract",
        "sub-limit",
        "benefit sub limit",
        "benefit",
    ],
    TableType.room_rent: [
        "room rent",
        "room category",
        "single private",
        "icu charges",
        "intensive care unit",
        "suite",
        "twin sharing",
        "shared accommodation",
        "ac room",
        "non-ac",
        "1% of si",
        "2% of si",
        "1% of sum insured",
        "2% of sum insured",
        "per day",
        "per day of hospitalisation",
        "per day of hospitalization",
        "room type",
    ],
    TableType.premium: [
        "rate of premium",
        "period on risk",
        "premium rate",
        "annual premium",
        "monthly premium",
        "quarterly premium",
        "half yearly premium",
        "installment premium",
        "premium amount",
        "premium payable",
        "premium",
        "age band",
        "entry age",
        "day of cancellation",
        "cancellation date",
        "% of premium refund",
    ],
    TableType.claims_documents: [
        "claim documents",
        "documents required",
        "documents to be submitted",
        "discharge summary",
        "indoor case papers",
        "investigation report",
        "original bills",
        "claim form",
        "medical records",
        "type of claim",
        "prescribed time limit",
        "time of intimation",
        "claim settlement",
        "intimation of claim",
        "claim intimation",
        "sl no",
    ],
    TableType.network_list: [
        "network hospital",
        "hospital name",
        "empanelled",
        "list of hospital",
        "hospital list",
        "pin code",
        "contact number",
        "hospital address",
        "empanelment",
    ],
}

# Minimum confidence threshold — below this, emit unknown.
# Keywords lists are long (15-16 per type); real tables typically hit 1-4 keywords.
# A ratio of 0.05 means at least 1 keyword from the winning type must match.
_MIN_CONFIDENCE = 0.05

# Heading context lines to extract above table bbox
_HEADING_CONTEXT_LINES = 3


def _flatten_grid(grid: List[List[Optional[str]]]) -> str:
    """Flatten all cell text into a single lowercase string for matching."""
    parts = []
    for row in grid:
        for cell in row:
            if cell:
                parts.append(cell.strip().lower())
    return " ".join(parts)


def _score_text(text: str, keywords: List[str]) -> float:
    """Count how many unique keywords appear in text. Normalized 0-1."""
    if not keywords:
        return 0.0
    hits = sum(1 for kw in keywords if kw in text)
    return hits / len(keywords)


def classify(
    grid: List[List[Optional[str]]],
    heading_context: Optional[str] = None,
) -> Tuple[TableType, float]:
    """
    Classify a table by its cell text and optional heading context.

    Args:
        grid: Raw cell grid from pdfplumber or text alignment detector.
        heading_context: Text from lines immediately above the table (optional).

    Returns:
        (TableType, confidence) where confidence is in [0, 1].
        Returns (TableType.unknown, score) if best score < _MIN_CONFIDENCE.
    """
    cell_text = _flatten_grid(grid)

    # Combine cell text with heading context (heading gets 2x weight via repetition)
    combined = cell_text
    if heading_context:
        combined = heading_context.lower() + " " + heading_context.lower() + " " + cell_text

    scores: dict = {}
    for table_type, keywords in _KEYWORDS.items():
        scores[table_type] = _score_text(combined, keywords)

    best_type = max(scores, key=lambda t: scores[t])
    best_score = scores[best_type]

    # Disambiguation: room_rent vs schedule_of_benefits
    # If table has ambulance, restoration, ncb, cataract → prefer schedule_of_benefits.
    if best_type == TableType.room_rent:
        sob_disambiguators = [
            "ambulance",
            "restoration benefit",
            "restoration",
            "ncb",
            "cumulative bonus",
            "organ",
            "cataract",
            "limit for",
        ]
        if any(d in combined for d in sob_disambiguators):
            if scores[TableType.schedule_of_benefits] > 0:
                best_type = TableType.schedule_of_benefits
                best_score = scores[TableType.schedule_of_benefits]

    # Disambiguation: physical benefit grids often mention "sum insured" but
    # are not premium tables unless premium/cancellation language is present.
    benefit_grid_markers = [
        "losses covered",
        "insured events",
        "amount payable",
        "% of sum insured",
        "% of the sum insured",
        "percentage of sum insured",
        "benefits",
        "treatment or procedure",
        "limit (per policy period)",
        "fracture",
        "cataract",
    ]
    premium_markers = ["premium", "period on risk", "rate of premium", "cancellation"]
    if best_type == TableType.premium and any(marker in combined for marker in benefit_grid_markers):
        if not any(marker in combined for marker in premium_markers):
            best_type = TableType.schedule_of_benefits
            best_score = max(best_score, scores[TableType.schedule_of_benefits])

    if best_type == TableType.waiting_period and "fracture" in combined:
        best_type = TableType.schedule_of_benefits
        best_score = max(best_score, scores[TableType.schedule_of_benefits])

    if best_score < _MIN_CONFIDENCE:
        return TableType.unknown, best_score

    return best_type, best_score


def classify_from_cells(
    cells_text: List[str],
    heading_context: Optional[str] = None,
) -> Tuple[TableType, float]:
    """
    Convenience: classify from a flat list of cell text strings.
    """
    grid = [[t] for t in cells_text]
    return classify(grid, heading_context)
