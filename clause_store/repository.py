"""
Clause Store Repository — DSE-010

All SQLite read/write operations.
Uses stdlib sqlite3 — no ORM, no external DB dependencies.
FK enforcement via PRAGMA foreign_keys = ON (set in init_db).
Idempotent: INSERT OR REPLACE for stable-ID rows, INSERT OR IGNORE for pipeline_runs history.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
from typing import Iterator, List, Optional, Tuple

from clause_store.models import (
    DocumentBlock,
    DocumentIssue,
    DocumentLine,
    DocumentPage,
    DocumentSection,
    DocumentTable,
    DocumentTableCell,
    PolicyClause,
    PipelineRun,
    Product,
    ProductVersion,
    SourceDocument,
    SourceSpan,
)

_SCHEMA_PATH = pathlib.Path(__file__).parent / "schema.sql"


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


def init_db(db_path: str) -> sqlite3.Connection:
    """
    Create (or open) the SQLite database, apply the full schema, and return
    a connection with FK enforcement enabled.

    Idempotent: safe to call multiple times on the same file.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Pipeline runs
# ---------------------------------------------------------------------------


def insert_pipeline_run(conn: sqlite3.Connection, run: PipelineRun) -> None:
    conn.execute(
        """INSERT OR IGNORE INTO pipeline_runs
           (id, git_commit, parser_version, extractor_version,
            started_at, finished_at, status, input_count, success_count,
            failure_count, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            run.id,
            run.git_commit,
            run.parser_version,
            run.extractor_version,
            run.started_at,
            run.finished_at,
            run.status,
            run.input_count,
            run.success_count,
            run.failure_count,
            run.notes,
        ),
    )
    conn.commit()


def update_pipeline_run_finished(
    conn: sqlite3.Connection,
    run_id: str,
    status: str,
    finished_at: str,
    success_count: int,
    failure_count: int,
) -> None:
    conn.execute(
        """UPDATE pipeline_runs
           SET status=?, finished_at=?, success_count=?, failure_count=?
           WHERE id=?""",
        (status, finished_at, success_count, failure_count, run_id),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Products / versions / documents
# ---------------------------------------------------------------------------


def insert_product(conn: sqlite3.Connection, product: Product) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO products
           (product_id, uin_base, normalized_insurer, normalized_plan_name,
            product_type, insurance_type)
           VALUES (?,?,?,?,?,?)""",
        (
            product.product_id,
            product.uin_base,
            product.normalized_insurer,
            product.normalized_plan_name,
            product.product_type,
            product.insurance_type,
        ),
    )


def insert_product_version(conn: sqlite3.Connection, version: ProductVersion) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO product_versions
           (version_id, product_id, full_uin, version_label, active_status)
           VALUES (?,?,?,?,?)""",
        (
            version.version_id,
            version.product_id,
            version.full_uin,
            version.version_label,
            version.active_status,
        ),
    )


def insert_source_document(conn: sqlite3.Connection, doc: SourceDocument) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO source_documents
           (document_id, version_id, policy_id, document_type,
            source_pdf_path, file_hash, page_count, parser_status)
           VALUES (?,?,?,?,?,?,?,?)""",
        (
            doc.document_id,
            doc.version_id,
            doc.policy_id,
            doc.document_type,
            doc.source_pdf_path,
            doc.file_hash,
            doc.page_count,
            doc.parser_status,
        ),
    )


# ---------------------------------------------------------------------------
# Physical layer: pages, blocks, lines
# ---------------------------------------------------------------------------


def insert_pages(conn: sqlite3.Connection, pages: List[DocumentPage]) -> None:
    conn.executemany(
        """INSERT OR REPLACE INTO document_pages
           (page_id, document_id, page_number, width, height, rotation)
           VALUES (?,?,?,?,?,?)""",
        [(p.page_id, p.document_id, p.page_number, p.width, p.height, p.rotation) for p in pages],
    )


def insert_blocks(conn: sqlite3.Connection, blocks: List[DocumentBlock]) -> None:
    conn.executemany(
        """INSERT OR REPLACE INTO document_blocks
           (block_id, page_id, document_id, block_type, bbox_json, reading_order)
           VALUES (?,?,?,?,?,?)""",
        [
            (b.block_id, b.page_id, b.document_id, b.block_type, b.bbox_json, b.reading_order)
            for b in blocks
        ],
    )


def insert_lines(conn: sqlite3.Connection, lines: List[DocumentLine]) -> None:
    conn.executemany(
        """INSERT OR REPLACE INTO document_lines
           (line_id, block_id, document_id, page_number,
            bbox_json, text, region, is_header_candidate, is_footer_candidate)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        [
            (
                ln.line_id,
                ln.block_id,
                ln.document_id,
                ln.page_number,
                ln.bbox_json,
                ln.text,
                ln.region,
                int(ln.is_header_candidate),
                int(ln.is_footer_candidate),
            )
            for ln in lines
        ],
    )


# ---------------------------------------------------------------------------
# Logical layer: sections, clauses
# ---------------------------------------------------------------------------


def insert_sections(conn: sqlite3.Connection, sections: List[DocumentSection]) -> None:
    """
    Insert or replace document sections.
    Parent-before-child ordering is required by the caller to satisfy self-referential FK.
    """
    conn.executemany(
        """INSERT OR REPLACE INTO document_sections
           (section_id, document_id, parent_id, section_number,
            title, normalized_title, level, heading_type,
            heading_score, heading_line_id, page_start, page_end, pipeline_run_id)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [
            (
                s.section_id,
                s.document_id,
                s.parent_id,
                s.section_number,
                s.title,
                s.normalized_title,
                s.level,
                s.heading_type,
                s.heading_score,
                s.heading_line_id,
                s.page_start,
                s.page_end,
                s.pipeline_run_id,
            )
            for s in sections
        ],
    )


def insert_clauses(conn: sqlite3.Connection, clauses: List[PolicyClause]) -> None:
    conn.executemany(
        """INSERT OR REPLACE INTO policy_clauses
           (clause_id, document_id, section_id, clause_number,
            title, raw_text, page_start, page_end,
            line_ids_json, segmentation_method, confidence, pipeline_run_id)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        [
            (
                c.clause_id,
                c.document_id,
                c.section_id,
                c.clause_number,
                c.title,
                c.raw_text,
                c.page_start,
                c.page_end,
                c.line_ids_json,
                c.segmentation_method,
                c.confidence,
                c.pipeline_run_id,
            )
            for c in clauses
        ],
    )


# ---------------------------------------------------------------------------
# Source spans
# ---------------------------------------------------------------------------


def insert_source_spans(conn: sqlite3.Connection, spans: List[SourceSpan]) -> None:
    conn.executemany(
        """INSERT OR REPLACE INTO source_spans
           (span_id, document_id, clause_id, table_cell_id,
            span_type, text, char_start, char_end, page_regions_json, pipeline_run_id)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        [
            (
                s.span_id,
                s.document_id,
                s.clause_id,
                s.table_cell_id,
                s.span_type,
                s.text,
                s.char_start,
                s.char_end,
                s.page_regions_json,
                s.pipeline_run_id,
            )
            for s in spans
        ],
    )


# ---------------------------------------------------------------------------
# Tables / cells
# ---------------------------------------------------------------------------


def insert_tables(conn: sqlite3.Connection, tables: List[DocumentTable]) -> None:
    conn.executemany(
        """INSERT OR REPLACE INTO document_tables
           (table_id, document_id, page, bbox_json,
            parent_clause_id, parent_clause_confidence,
            extraction_method, table_type, table_type_confidence,
            row_count, col_count, has_header_row, issues_json)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [
            (
                t.table_id,
                t.document_id,
                t.page,
                t.bbox_json,
                t.parent_clause_id,
                t.parent_clause_confidence,
                t.extraction_method,
                t.table_type,
                t.table_type_confidence,
                t.row_count,
                t.col_count,
                int(t.has_header_row),
                t.issues_json,
            )
            for t in tables
        ],
    )


def insert_table_cells(conn: sqlite3.Connection, cells: List[DocumentTableCell]) -> None:
    conn.executemany(
        """INSERT OR REPLACE INTO document_table_cells
           (cell_id, table_id, row_index, col_index, text,
            bbox_json, is_header, column_header_text, row_header_text)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        [
            (
                c.cell_id,
                c.table_id,
                c.row_index,
                c.col_index,
                c.text,
                c.bbox_json,
                int(c.is_header),
                c.column_header_text,
                c.row_header_text,
            )
            for c in cells
        ],
    )


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------


def insert_issues(conn: sqlite3.Connection, issues: List[DocumentIssue]) -> None:
    conn.executemany(
        """INSERT INTO document_issues
           (document_id, pipeline_run_id, issue_type, severity,
            page_number, description, raw_context)
           VALUES (?,?,?,?,?,?,?)""",
        [
            (
                i.document_id,
                i.pipeline_run_id,
                i.issue_type,
                i.severity,
                i.page_number,
                i.description,
                i.raw_context,
            )
            for i in issues
        ],
    )


# ---------------------------------------------------------------------------
# Spatial query: table parent clause via bbox overlap
# ---------------------------------------------------------------------------


def _bbox_iou(a: Optional[list], b: Optional[list]) -> float:
    """Intersection-over-Union for two [x0, top, x1, bottom] bboxes."""
    if not a or not b or len(a) != 4 or len(b) != 4:
        return 0.0
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    inter = (x1 - x0) * (y1 - y0)
    area_a = max(0.0, (a[2] - a[0]) * (a[3] - a[1]))
    area_b = max(0.0, (b[2] - b[0]) * (b[3] - b[1]))
    union = area_a + area_b - inter
    return inter / union if union else 0.0


def backfill_table_parent_clauses(conn: sqlite3.Connection, document_id: str) -> int:
    """
    For each document_table in document_id:
    1. Get table page and bbox.
    2. Query policy_clauses where page_start <= page <= page_end.
    3. For each candidate, fetch its clause_body source_span's page_regions.
    4. Compute IoU(table_bbox, clause_region_bbox_on_that_page).
    5. Assign clause with max IoU > 0.10.

    Returns count of tables where parent_clause_id was set or improved.
    Runs AFTER clause source_spans are inserted.
    """
    _MIN_IOU = 0.10

    cursor = conn.execute(
        "SELECT table_id, page, bbox_json FROM document_tables WHERE document_id = ?",
        (document_id,),
    )
    tables = cursor.fetchall()

    updated = 0
    for row in tables:
        table_id = row["table_id"]
        page = row["page"]
        try:
            table_bbox = json.loads(row["bbox_json"]) if row["bbox_json"] else None
        except (json.JSONDecodeError, TypeError):
            table_bbox = None
        if not table_bbox:
            continue

        # Candidate clauses covering this page
        cand_cursor = conn.execute(
            """SELECT clause_id FROM policy_clauses
               WHERE document_id = ? AND page_start <= ? AND page_end >= ?""",
            (document_id, page, page),
        )
        clause_ids = [r[0] for r in cand_cursor.fetchall()]
        if not clause_ids:
            continue

        best_clause_id: Optional[str] = None
        best_iou = 0.0

        for clause_id in clause_ids:
            span_cur = conn.execute(
                """SELECT page_regions_json FROM source_spans
                   WHERE clause_id = ? AND span_type = 'clause_body' LIMIT 1""",
                (clause_id,),
            )
            span_row = span_cur.fetchone()
            if not span_row:
                continue
            try:
                page_regions = json.loads(span_row[0])
            except (json.JSONDecodeError, TypeError):
                continue
            for region in page_regions:
                if region.get("page") == page and region.get("bbox"):
                    iou = _bbox_iou(table_bbox, region["bbox"])
                    if iou > best_iou:
                        best_iou = iou
                        best_clause_id = clause_id

        if best_clause_id and best_iou >= _MIN_IOU:
            conn.execute(
                """UPDATE document_tables
                   SET parent_clause_id = ?, parent_clause_confidence = ?
                   WHERE table_id = ?""",
                (best_clause_id, round(best_iou, 4), table_id),
            )
            updated += 1

    conn.commit()
    return updated


# ---------------------------------------------------------------------------
# Query: clauses with their source_spans (for DSE-011 consumption)
# ---------------------------------------------------------------------------


def query_clauses_with_spans(conn: sqlite3.Connection, document_id: str) -> List[dict]:
    """
    Return all policy_clauses for a document enriched with their clause_body
    source_span data.
    """
    cursor = conn.execute(
        """SELECT c.clause_id, c.section_id, c.clause_number, c.title,
                  c.raw_text, c.page_start, c.page_end, c.line_ids_json,
                  c.segmentation_method, c.confidence,
                  s.span_id, s.page_regions_json, s.char_start, s.char_end
           FROM policy_clauses c
           LEFT JOIN source_spans s
             ON s.clause_id = c.clause_id AND s.span_type = 'clause_body'
           WHERE c.document_id = ?
           ORDER BY c.page_start, c.clause_id""",
        (document_id,),
    )
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    return results


# ---------------------------------------------------------------------------
# Integrity checks (used by validate_source_spans.py)
# ---------------------------------------------------------------------------


def count_dangling_fks(conn: sqlite3.Connection) -> int:
    """
    Count dangling FK references across key tables.
    sqlite3 provides PRAGMA foreign_key_check which returns rows for violations.
    """
    cursor = conn.execute("PRAGMA foreign_key_check")
    return len(cursor.fetchall())


def get_table_counts(conn: sqlite3.Connection) -> dict:
    """Return {table_name: row_count} for all tables."""
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    counts = {}
    for table in tables:
        c = conn.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = c.fetchone()[0]
    return counts


def get_db_size_bytes(db_path: str) -> int:
    """Return the SQLite file size in bytes."""
    return pathlib.Path(db_path).stat().st_size
