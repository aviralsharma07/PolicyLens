"""
Table Engine Pydantic models — DSE-009

Data contract: docs/data_contracts.md § Contract 3C
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExtractionMethod(str, Enum):
    pdfplumber_lattice = "pdfplumber_lattice"
    pdfplumber_text = "pdfplumber_text"
    text_alignment_candidate = "text_alignment_candidate"


class TableType(str, Enum):
    waiting_period = "waiting_period"
    schedule_of_benefits = "schedule_of_benefits"
    room_rent = "room_rent"
    premium = "premium"
    claims_documents = "claims_documents"
    network_list = "network_list"
    unknown = "unknown"


class TableCell(BaseModel):
    """A single cell in an extracted table."""

    cell_id: str = Field(..., description="Stable ID: {table_id}_r{row}_c{col}")
    table_id: str
    row_index: int = Field(..., ge=0)
    col_index: int = Field(..., ge=0)
    text: str = Field(default="", description="Cell text; None values normalized to ''")
    bbox: Optional[List[float]] = Field(
        default=None, description="[x0, top, x1, bottom] in pdfplumber coords"
    )
    is_header: bool = False
    column_header_text: Optional[str] = None
    row_header_text: Optional[str] = None
    row_span: int = Field(default=1, ge=1)
    col_span: int = Field(default=1, ge=1)


class ColumnCluster(BaseModel):
    """Column position cluster detected by text alignment heuristics (fallback only)."""

    col_index: int = Field(..., ge=0)
    x_center: float
    x_min: float
    x_max: float


class ExtractedTable(BaseModel):
    """A single table extracted from a PDF page."""

    table_id: str = Field(..., description="Stable ID: {policy_id}_p{page}_t{n}")
    document_id: str
    policy_id: str
    page: int = Field(..., ge=1)
    bbox: Optional[List[float]] = Field(
        default=None, description="[x0, top, x1, bottom] in pdfplumber coords"
    )
    table_type: TableType = TableType.unknown
    table_type_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    extraction_method: ExtractionMethod
    row_count: int = Field(default=0, ge=0)
    col_count: int = Field(default=0, ge=0)
    has_header_row: bool = False
    header_row_index: Optional[int] = None
    header_rows: List[int] = Field(default_factory=list)
    column_headers: List[str] = Field(default_factory=list)
    cells: List[TableCell] = Field(default_factory=list)
    raw_lines: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Source physical lines for text_alignment_candidate tables.",
    )
    column_clusters: Optional[List[ColumnCluster]] = Field(
        default=None, description="Populated only for text_alignment_candidate tables"
    )
    parent_clause_id: Optional[str] = Field(
        default=None,
        description="Provisional: page-range lookup from section_tree. Replaced by bbox overlap in DSE-010.",
    )
    parent_clause_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)


class TableDocument(BaseModel):
    """All tables extracted from a single policy document."""

    schema_version: str = "1.0.0"
    pipeline_run_id: str
    document_id: str
    policy_id: str
    source_pdf_path: str
    page_count: int = Field(default=0, ge=0)
    tables_found: int = Field(default=0, ge=0)
    structured_tables: int = Field(
        default=0, ge=0, description="Tables with extraction_method=pdfplumber_lattice"
    )
    candidate_tables: int = Field(
        default=0, ge=0, description="Tables with extraction_method=text_alignment_candidate"
    )
    tables: List[ExtractedTable] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
