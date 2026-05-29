import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class BlockType(str, Enum):
    text = "text"
    header = "header"
    footer = "footer"
    image_region = "image_region"
    unknown = "unknown"


class Region(str, Enum):
    top = "top"
    body = "body"
    bottom = "bottom"


class ParserIssue(BaseModel):
    type: str
    page_number: int
    message: str
    details: Optional[dict] = None


class Span(BaseModel):
    span_id: str
    text: str
    bbox: List[float]
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    is_bold: Optional[bool] = None
    is_italic: Optional[bool] = None
    color: Optional[str] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None


class Line(BaseModel):
    line_id: str
    bbox: List[float]
    text: str
    region: Region
    font_sizes: List[float] = Field(default_factory=list)
    font_names: List[str] = Field(default_factory=list)
    span_ids: List[str] = Field(default_factory=list)
    is_header_candidate: bool = False
    is_footer_candidate: bool = False


class Block(BaseModel):
    block_id: str
    block_type: BlockType = BlockType.text
    bbox: List[float]
    text: str
    line_ids: List[str] = Field(default_factory=list)
    reading_order: int = 0


class Page(BaseModel):
    page_number: int
    width: float
    height: float
    rotation: int = 0
    text_length: int = 0
    blocks: List[Block] = Field(default_factory=list)
    lines: List[Line] = Field(default_factory=list)
    spans: List[Span] = Field(default_factory=list)
    issues: List[ParserIssue] = Field(default_factory=list)


class PhysicalDocument(BaseModel):
    schema_version: str = "1.0.0"
    parser_version: str = "1.0.0"
    pipeline_run_id: str
    document_id: str
    policy_id: str
    source_pdf_path: str
    file_hash: Optional[str] = None
    page_count: int
    pages: List[Page] = Field(default_factory=list)
    issues: List[ParserIssue] = Field(default_factory=list)
