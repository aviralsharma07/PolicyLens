"""
Clause Store row dataclasses — DSE-010

Lightweight Python dataclasses for passing structured data to/from SQLite.
No Pydantic overhead — these are internal DB layer types only.
All JSON fields stored as strings; callers handle json.dumps/json.loads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PipelineRun:
    id: str
    started_at: str
    git_commit: str = ""
    parser_version: str = "1.0.0"
    extractor_version: str = "1.0.0"
    status: str = "running"
    input_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    notes: str = ""
    finished_at: Optional[str] = None


@dataclass
class Product:
    product_id: str
    uin_base: str
    normalized_insurer: str
    normalized_plan_name: str
    product_type: str = "health"
    insurance_type: str = "individual"


@dataclass
class ProductVersion:
    version_id: str
    product_id: str
    full_uin: str
    version_label: Optional[str] = None
    active_status: str = "active"


@dataclass
class SourceDocument:
    document_id: str  # = file_hash from physical JSON
    policy_id: str
    source_pdf_path: str
    file_hash: str
    page_count: int
    document_type: str = "policy_wording"
    parser_status: str = "parsed"
    version_id: Optional[str] = None


@dataclass
class DocumentPage:
    page_id: str  # "{document_id}_p{page_number}"
    document_id: str
    page_number: int
    width: float
    height: float
    rotation: int = 0


@dataclass
class DocumentBlock:
    block_id: str
    page_id: str
    document_id: str
    block_type: Optional[str] = None
    bbox_json: Optional[str] = None  # JSON "[x0, top, x1, bottom]"
    reading_order: Optional[int] = None


@dataclass
class DocumentLine:
    line_id: str  # global UID
    block_id: str
    document_id: str
    page_number: int
    bbox_json: str  # JSON "[x0, top, x1, bottom]"
    text: str
    source_line_id: str = ""
    region: Optional[str] = None
    is_header_candidate: bool = False
    is_footer_candidate: bool = False


@dataclass
class DocumentSection:
    section_id: str  # global UID
    document_id: str
    pipeline_run_id: str
    source_section_id: str = ""
    level: int = 0
    heading_type: str = "root"
    page_start: int = 0
    page_end: int = 0
    parent_id: Optional[str] = None
    section_number: Optional[str] = None
    title: Optional[str] = None
    normalized_title: Optional[str] = None
    heading_score: Optional[float] = None
    heading_line_id: Optional[str] = None


@dataclass
class PolicyClause:
    clause_id: str  # global UID
    document_id: str
    section_id: str
    pipeline_run_id: str
    raw_text: str
    page_start: int
    page_end: int
    line_ids_json: str  # JSON array of global line UIDs
    source_clause_id: str = ""
    source_line_ids_json: str = ""  # JSON array of source-local line IDs
    clause_number: Optional[str] = None
    title: Optional[str] = None
    segmentation_method: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class SourceSpan:
    span_id: str
    document_id: str
    span_type: str  # clause_body|fact_evidence|table_cell|heading
    text: str
    page_regions_json: str  # JSON [{page, bbox:[x0,top,x1,bottom], line_ids:[...]}]
    pipeline_run_id: str
    clause_id: Optional[str] = None
    table_cell_id: Optional[str] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None


@dataclass
class DocumentTable:
    table_id: str
    document_id: str
    page: int
    extraction_method: Optional[str] = None
    table_type: Optional[str] = None
    table_type_confidence: Optional[float] = None
    row_count: int = 0
    col_count: int = 0
    has_header_row: bool = False
    bbox_json: Optional[str] = None
    parent_clause_id: Optional[str] = None
    parent_clause_confidence: Optional[float] = None
    issues_json: Optional[str] = None


@dataclass
class DocumentTableCell:
    cell_id: str
    table_id: str
    row_index: int
    col_index: int
    text: str = ""
    bbox_json: Optional[str] = None
    is_header: bool = False
    column_header_text: Optional[str] = None
    row_header_text: Optional[str] = None


@dataclass
class DocumentIssue:
    pipeline_run_id: str
    issue_type: str
    description: str
    severity: str = "warning"
    document_id: Optional[str] = None
    page_number: Optional[int] = None
    raw_context: Optional[str] = None


# ---------------------------------------------------------------------------
# DSE-011: Fact candidates, extracted facts, conflicts
# ---------------------------------------------------------------------------


@dataclass
class ExtractedFactCandidate:
    id: str  # global UID: "{document_id}:{source_candidate_id}"
    source_candidate_id: str  # DSE-007 candidate_id
    clause_id: str  # global UID (FK)
    source_clause_id: str  # source-local clause ID
    document_id: str
    concept: str
    extractor_name: str
    pipeline_run_id: str
    confidence: float = 0.0  # extractor-assigned
    score: float = 0.0  # composite score
    accepted: bool = False
    candidate_value_json: Optional[str] = None
    normalized_value_json: Optional[str] = None
    fact_status: str = "present"
    scope_json: Optional[str] = None
    condition_json: Optional[str] = None
    evidence_span_id: Optional[str] = None
    evidence_text: Optional[str] = None
    evidence_page: Optional[int] = None
    extractor_version: Optional[str] = None
    pattern_id: Optional[str] = None
    rejection_reason: Optional[str] = None


@dataclass
class ExtractedFact:
    id: str  # global UID: "{document_id}:{source_candidate_id}"
    source_candidate_id: str
    clause_id: str  # global UID (FK)
    source_clause_id: str
    document_id: str
    concept: str
    extraction_method: str
    pipeline_run_id: str
    fact_status: str = "present"  # only present | explicitly_not_covered
    confidence: float = 0.0
    value_json: Optional[str] = None
    normalized_value_json: Optional[str] = None
    value_type: Optional[str] = None
    scope_json: Optional[str] = None
    condition_json: Optional[str] = None
    evidence_span_id: Optional[str] = None
    validated: bool = False
    validator: Optional[str] = None


@dataclass
class FactConflict:
    document_id: str
    concept: str
    fact_a_id: str  # FK to extracted_fact_candidates
    fact_b_id: str  # FK to extracted_fact_candidates
    conflict_type: str  # value_disagreement | status_disagreement | scope_disagreement
    pipeline_run_id: str
    resolution: str = (
        "unresolved"  # unresolved | higher_score_wins | manual_review_required | merged
    )
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
