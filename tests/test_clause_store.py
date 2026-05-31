"""
Tests for DSE-010 Clause Store + Source Spans

All tests use in-memory SQLite and synthetic data — no PDF access required.
"""

from __future__ import annotations

import json
import os
import pathlib
import tempfile

import pytest

from clause_store.fact_resolver import resolve_facts
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
from clause_store.repository import (
    _bbox_iou,
    backfill_table_parent_clauses,
    count_dangling_fks,
    get_table_counts,
    init_db,
    insert_blocks,
    insert_clauses,
    insert_issues,
    insert_lines,
    insert_pages,
    insert_pipeline_run,
    insert_product,
    insert_product_version,
    insert_sections,
    insert_source_document,
    insert_source_spans,
    insert_table_cells,
    insert_tables,
    query_clauses_with_spans,
)
from clause_store.span_builder import (
    build_clause_span,
    build_clause_spans,
    build_fact_evidence_span,
    build_fact_evidence_spans,
    build_line_index,
    build_table_cell_spans,
    compute_bbox_union,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def conn():
    """In-memory SQLite connection with full schema."""
    db = init_db(":memory:")
    yield db
    db.close()


@pytest.fixture
def base_run():
    return PipelineRun(id="run_test_001", started_at="2026-05-31T00:00:00")


@pytest.fixture
def base_product():
    return Product(
        product_id="test_policy",
        uin_base="TSTHLIP00000V000000",
        normalized_insurer="test_insurer",
        normalized_plan_name="test_plan",
    )


@pytest.fixture
def base_version():
    return ProductVersion(
        version_id="test_policy_v1",
        product_id="test_policy",
        full_uin="TSTHLIP00000V000000",
    )


@pytest.fixture
def base_doc():
    return SourceDocument(
        document_id="sha256:abc123",
        policy_id="test_policy",
        source_pdf_path="test/path.pdf",
        file_hash="sha256:abc123",
        page_count=10,
        version_id="test_policy_v1",
    )


def _seed_minimal(conn, run, product, version, doc):
    """Insert the minimum rows needed for FK-dependent tests."""
    insert_pipeline_run(conn, run)
    insert_product(conn, product)
    insert_product_version(conn, version)
    insert_source_document(conn, doc)
    conn.commit()


def _make_physical_doc(n_pages=3, n_lines_per_page=5):
    """Build a minimal synthetic physical document dict."""
    pages = []
    for p in range(1, n_pages + 1):
        lines = []
        for l in range(1, n_lines_per_page + 1):
            lines.append(
                {
                    "line_id": f"p{p}l_{l}",
                    "bbox": [72.0, float(50 + l * 20), 500.0, float(65 + l * 20)],
                    "text": f"Line {l} on page {p}",
                    "region": "body",
                    "is_header_candidate": False,
                    "is_footer_candidate": False,
                }
            )
        pages.append(
            {
                "page_number": p,
                "width": 595.0,
                "height": 842.0,
                "rotation": 0,
                "blocks": [{"block_id": f"p{p}b_1", "bbox": [0, 0, 595, 842]}],
                "lines": lines,
                "spans": [],
            }
        )
    return {
        "document_id": "sha256:abc123",
        "policy_id": "test_policy",
        "source_pdf_path": "test/path.pdf",
        "file_hash": "sha256:abc123",
        "page_count": n_pages,
        "pipeline_run_id": "run_test_001",
        "pages": pages,
    }


# ---------------------------------------------------------------------------
# TestSchema
# ---------------------------------------------------------------------------


class TestSchema:
    EXPECTED_TABLES = {
        "pipeline_runs",
        "products",
        "product_versions",
        "source_documents",
        "document_pages",
        "document_blocks",
        "document_lines",
        "document_text_spans",
        "document_sections",
        "policy_clauses",
        "document_tables",
        "document_table_cells",
        "source_spans",
        "document_issues",
        "extracted_fact_candidates",
        "extracted_facts",
        "fact_conflicts",
        "validation_labels",
        "derived_policy_features",
    }

    def test_init_db_creates_all_19_tables(self, conn):
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        found = {row[0] for row in cursor.fetchall()}
        # sqlite_sequence is auto-created by SQLite for AUTOINCREMENT columns — exclude it
        found -= {"sqlite_sequence"}
        assert self.EXPECTED_TABLES == found

    def test_init_db_is_idempotent(self):
        """Calling init_db twice on the same file must not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "test.sqlite")
            c1 = init_db(db_path)
            c1.close()
            c2 = init_db(db_path)
            c2.close()

    def test_deferred_tables_exist_but_empty(self, conn):
        for table in ["document_text_spans", "extracted_facts", "derived_policy_features"]:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            assert cursor.fetchone()[0] == 0

    def test_source_spans_span_type_check_constraint(
        self, conn, base_run, base_product, base_version, base_doc
    ):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        page = DocumentPage(
            page_id="sha256:abc123_p1",
            document_id="sha256:abc123",
            page_number=1,
            width=595.0,
            height=842.0,
        )
        insert_pages(conn, [page])
        block = DocumentBlock(
            block_id="sha256:abc123_p1_b1", page_id="sha256:abc123_p1", document_id="sha256:abc123"
        )
        insert_blocks(conn, [block])
        line = DocumentLine(
            line_id="p1l_1",
            block_id="sha256:abc123_p1_b1",
            document_id="sha256:abc123",
            page_number=1,
            bbox_json="[0,0,100,10]",
            text="test",
        )
        insert_lines(conn, [line])
        section = DocumentSection(
            section_id="sec_1", document_id="sha256:abc123", pipeline_run_id="run_test_001"
        )
        insert_sections(conn, [section])
        clause = PolicyClause(
            clause_id="c1",
            document_id="sha256:abc123",
            section_id="sec_1",
            pipeline_run_id="run_test_001",
            raw_text="hello",
            page_start=1,
            page_end=1,
            line_ids_json='["p1l_1"]',
        )
        insert_clauses(conn, [clause])
        with pytest.raises(Exception):
            # invalid span_type
            conn.execute(
                """INSERT INTO source_spans (span_id, document_id, clause_id, span_type, text, page_regions_json, pipeline_run_id)
                   VALUES (?,?,?,?,?,?,?)""",
                ("bad", "sha256:abc123", "c1", "INVALID_TYPE", "t", "[]", "run_test_001"),
            )
            conn.commit()

    def test_indexes_created(self, conn):
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
        )
        index_names = {row[0] for row in cursor.fetchall()}
        assert "idx_lines_doc_page" in index_names
        assert "idx_clauses_doc_page" in index_names
        assert "idx_spans_clause" in index_names
        assert "idx_spans_doc_type" in index_names

    def test_pipeline_runs_insert_or_ignore(self, conn):
        run = PipelineRun(id="run_001", started_at="2026-01-01T00:00:00", notes="first")
        insert_pipeline_run(conn, run)
        run2 = PipelineRun(id="run_001", started_at="2026-01-01T00:00:00", notes="second")
        insert_pipeline_run(conn, run2)  # should not raise, ignored
        cursor = conn.execute("SELECT notes FROM pipeline_runs WHERE id = 'run_001'")
        assert cursor.fetchone()[0] == "first"  # original preserved


# ---------------------------------------------------------------------------
# TestRepositoryInserts
# ---------------------------------------------------------------------------


class TestRepositoryInserts:
    def test_insert_source_document_replace(
        self, conn, base_run, base_product, base_version, base_doc
    ):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        cursor = conn.execute("SELECT COUNT(*) FROM source_documents")
        assert cursor.fetchone()[0] == 1

    def test_insert_pages_and_blocks(self, conn, base_run, base_product, base_version, base_doc):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        pages = [
            DocumentPage(
                page_id="sha256:abc123_p1",
                document_id="sha256:abc123",
                page_number=1,
                width=595.0,
                height=842.0,
            ),
            DocumentPage(
                page_id="sha256:abc123_p2",
                document_id="sha256:abc123",
                page_number=2,
                width=595.0,
                height=842.0,
            ),
        ]
        insert_pages(conn, pages)
        blocks = [
            DocumentBlock(
                block_id="b1",
                page_id="sha256:abc123_p1",
                document_id="sha256:abc123",
                block_type="text",
            ),
        ]
        insert_blocks(conn, blocks)
        conn.commit()
        assert conn.execute("SELECT COUNT(*) FROM document_pages").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM document_blocks").fetchone()[0] == 1

    def test_insert_lines(self, conn, base_run, base_product, base_version, base_doc):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        page = DocumentPage(
            page_id="sha256:abc123_p1",
            document_id="sha256:abc123",
            page_number=1,
            width=595.0,
            height=842.0,
        )
        insert_pages(conn, [page])
        block = DocumentBlock(
            block_id="b1", page_id="sha256:abc123_p1", document_id="sha256:abc123"
        )
        insert_blocks(conn, [block])
        lines = [
            DocumentLine(
                line_id="p1l_1",
                block_id="b1",
                document_id="sha256:abc123",
                page_number=1,
                bbox_json="[0,0,500,15]",
                text="hello",
            ),
            DocumentLine(
                line_id="p1l_2",
                block_id="b1",
                document_id="sha256:abc123",
                page_number=1,
                bbox_json="[0,15,500,30]",
                text="world",
                is_header_candidate=True,
            ),
        ]
        insert_lines(conn, lines)
        conn.commit()
        assert conn.execute("SELECT COUNT(*) FROM document_lines").fetchone()[0] == 2
        row = conn.execute(
            "SELECT is_header_candidate FROM document_lines WHERE line_id='p1l_2'"
        ).fetchone()
        assert row[0] == 1

    def test_insert_sections_self_ref_parent(
        self, conn, base_run, base_product, base_version, base_doc
    ):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        root = DocumentSection(
            section_id="sec_0",
            document_id="sha256:abc123",
            pipeline_run_id="run_test_001",
            level=0,
            heading_type="root",
        )
        child = DocumentSection(
            section_id="sec_1",
            document_id="sha256:abc123",
            pipeline_run_id="run_test_001",
            level=1,
            heading_type="visual",
            parent_id="sec_0",
        )
        insert_sections(conn, [root, child])
        conn.commit()
        row = conn.execute(
            "SELECT parent_id FROM document_sections WHERE section_id='sec_1'"
        ).fetchone()
        assert row[0] == "sec_0"

    def test_insert_clauses(self, conn, base_run, base_product, base_version, base_doc):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        section = DocumentSection(
            section_id="sec_1", document_id="sha256:abc123", pipeline_run_id="run_test_001"
        )
        insert_sections(conn, [section])
        clause = PolicyClause(
            clause_id="c1",
            document_id="sha256:abc123",
            section_id="sec_1",
            pipeline_run_id="run_test_001",
            raw_text="Free look period of 15 days",
            page_start=1,
            page_end=1,
            line_ids_json='["p1l_1"]',
        )
        insert_clauses(conn, [clause])
        conn.commit()
        assert conn.execute("SELECT COUNT(*) FROM policy_clauses").fetchone()[0] == 1

    def test_insert_source_span(self, conn, base_run, base_product, base_version, base_doc):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        section = DocumentSection(
            section_id="sec_1", document_id="sha256:abc123", pipeline_run_id="run_test_001"
        )
        insert_sections(conn, [section])
        clause = PolicyClause(
            clause_id="c1",
            document_id="sha256:abc123",
            section_id="sec_1",
            pipeline_run_id="run_test_001",
            raw_text="text",
            page_start=1,
            page_end=1,
            line_ids_json='["p1l_1"]',
        )
        insert_clauses(conn, [clause])
        span = SourceSpan(
            span_id="ss_test_policy_c1",
            document_id="sha256:abc123",
            clause_id="c1",
            span_type="clause_body",
            text="text",
            char_start=0,
            char_end=4,
            page_regions_json='[{"page":1,"bbox":[0,0,500,15],"line_ids":["p1l_1"]}]',
            pipeline_run_id="run_test_001",
        )
        insert_source_spans(conn, [span])
        conn.commit()
        assert conn.execute("SELECT COUNT(*) FROM source_spans").fetchone()[0] == 1

    def test_insert_table_null_parent_clause(
        self, conn, base_run, base_product, base_version, base_doc
    ):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        table = DocumentTable(
            table_id="t1",
            document_id="sha256:abc123",
            page=3,
            extraction_method="pdfplumber_lattice",
        )
        insert_tables(conn, [table])
        conn.commit()
        row = conn.execute(
            "SELECT parent_clause_id FROM document_tables WHERE table_id='t1'"
        ).fetchone()
        assert row[0] is None

    def test_insert_table_cells(self, conn, base_run, base_product, base_version, base_doc):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        table = DocumentTable(table_id="t1", document_id="sha256:abc123", page=1)
        insert_tables(conn, [table])
        cells = [
            DocumentTableCell(
                cell_id="c1_r0c0",
                table_id="t1",
                row_index=0,
                col_index=0,
                text="Header",
                is_header=True,
            ),
            DocumentTableCell(
                cell_id="c1_r1c0", table_id="t1", row_index=1, col_index=0, text="Value"
            ),
        ]
        insert_table_cells(conn, cells)
        conn.commit()
        assert conn.execute("SELECT COUNT(*) FROM document_table_cells").fetchone()[0] == 2


# ---------------------------------------------------------------------------
# TestBboxUnion
# ---------------------------------------------------------------------------


class TestBboxUnion:
    def test_single_bbox(self):
        result = compute_bbox_union([[10.0, 20.0, 100.0, 35.0]])
        assert result == [10.0, 20.0, 100.0, 35.0]

    def test_two_adjacent_bboxes(self):
        a = [10.0, 20.0, 100.0, 35.0]
        b = [10.0, 35.0, 100.0, 50.0]
        result = compute_bbox_union([a, b])
        assert result == [10.0, 20.0, 100.0, 50.0]

    def test_two_separated_bboxes(self):
        a = [10.0, 20.0, 200.0, 35.0]
        b = [50.0, 100.0, 300.0, 115.0]
        result = compute_bbox_union([a, b])
        assert result == [10.0, 20.0, 300.0, 115.0]

    def test_empty_returns_none(self):
        assert compute_bbox_union([]) is None
        assert compute_bbox_union([None]) is None

    def test_pdfplumber_coord_order(self):
        """pdfplumber uses [x0, top, x1, bottom] — min top = highest on page (smaller number)."""
        bboxes = [[72.0, 100.0, 500.0, 115.0], [72.0, 115.0, 500.0, 130.0]]
        result = compute_bbox_union(bboxes)
        assert result[1] == 100.0  # min top
        assert result[3] == 130.0  # max bottom


# ---------------------------------------------------------------------------
# TestBuildLineIndex
# ---------------------------------------------------------------------------


class TestBuildLineIndex:
    def test_line_index_keys_are_line_ids(self):
        doc = _make_physical_doc(n_pages=2, n_lines_per_page=3)
        idx = build_line_index(doc)
        assert "p1l_1" in idx
        assert "p1l_3" in idx
        assert "p2l_1" in idx

    def test_line_index_page_number_correct(self):
        doc = _make_physical_doc(n_pages=2, n_lines_per_page=3)
        idx = build_line_index(doc)
        assert idx["p1l_1"]["page"] == 1
        assert idx["p2l_1"]["page"] == 2

    def test_line_index_has_bbox(self):
        doc = _make_physical_doc(n_pages=1, n_lines_per_page=2)
        idx = build_line_index(doc)
        assert idx["p1l_1"]["bbox"] is not None
        assert len(idx["p1l_1"]["bbox"]) == 4


# ---------------------------------------------------------------------------
# TestSpanBuilderClause
# ---------------------------------------------------------------------------


class TestSpanBuilderClause:
    def _make_clause(self, clause_id, page_start, page_end, line_ids, text="clause text"):
        return {
            "clause_id": clause_id,
            "section_id": "sec_1",
            "page_start": page_start,
            "page_end": page_end,
            "line_ids": line_ids,
            "text": text,
        }

    def test_clause_span_id_format(self):
        doc = _make_physical_doc(n_pages=1, n_lines_per_page=3)
        idx = build_line_index(doc)
        clause = self._make_clause("clause_0001", 1, 1, ["p1l_1", "p1l_2"], "hello world")
        issues: list = []
        span = build_clause_span(clause, idx, "test_policy", "sha256:abc123", "run_001", issues)
        assert span is not None
        assert span.span_id == "ss_test_policy_clause_0001"

    def test_clause_span_single_page_one_region(self):
        doc = _make_physical_doc(n_pages=1, n_lines_per_page=3)
        idx = build_line_index(doc)
        clause = self._make_clause("c1", 1, 1, ["p1l_1", "p1l_2"])
        issues: list = []
        span = build_clause_span(clause, idx, "test_policy", "sha256:abc123", "run_001", issues)
        regions = json.loads(span.page_regions_json)
        assert len(regions) == 1
        assert regions[0]["page"] == 1
        assert regions[0]["bbox"] is not None
        assert len(issues) == 0

    def test_clause_span_cross_page_two_regions(self):
        doc = _make_physical_doc(n_pages=3, n_lines_per_page=4)
        idx = build_line_index(doc)
        # clause spans pages 1 and 2
        clause = self._make_clause("c_cross", 1, 2, ["p1l_1", "p1l_2", "p2l_1", "p2l_2"])
        issues: list = []
        span = build_clause_span(clause, idx, "pol", "sha256:abc123", "run_001", issues)
        regions = json.loads(span.page_regions_json)
        assert len(regions) == 2
        pages = [r["page"] for r in regions]
        assert 1 in pages and 2 in pages

    def test_clause_span_char_start_zero(self):
        doc = _make_physical_doc(n_pages=1, n_lines_per_page=3)
        idx = build_line_index(doc)
        clause = self._make_clause("c1", 1, 1, ["p1l_1"], "some text")
        issues: list = []
        span = build_clause_span(clause, idx, "pol", "sha256:abc123", "run_001", issues)
        assert span.char_start == 0

    def test_clause_span_char_end_equals_text_length(self):
        doc = _make_physical_doc(n_pages=1, n_lines_per_page=3)
        idx = build_line_index(doc)
        text = "Grace period of 30 days from the date of expiry"
        clause = self._make_clause("c1", 1, 1, ["p1l_1"], text)
        issues: list = []
        span = build_clause_span(clause, idx, "pol", "sha256:abc123", "run_001", issues)
        assert span.char_end == len(text)

    def test_clause_span_type_is_clause_body(self):
        doc = _make_physical_doc(n_pages=1, n_lines_per_page=3)
        idx = build_line_index(doc)
        clause = self._make_clause("c1", 1, 1, ["p1l_1"])
        issues: list = []
        span = build_clause_span(clause, idx, "pol", "sha256:abc123", "run_001", issues)
        assert span.span_type == "clause_body"

    def test_clause_span_missing_line_ids_returns_none_with_issue(self):
        idx = {}  # empty index
        clause = self._make_clause("c1", 1, 1, ["p1l_99"])
        issues: list = []
        span = build_clause_span(clause, idx, "pol", "sha256:abc123", "run_001", issues)
        assert span is None
        # Should have issues: line_id_not_in_physical_index + clause_span_no_lines
        issue_types = [i.issue_type for i in issues]
        assert "clause_span_no_lines" in issue_types

    def test_clause_span_filters_missing_line_ids(self):
        """Lines missing from index are logged but don't block the span."""
        doc = _make_physical_doc(n_pages=1, n_lines_per_page=3)
        idx = build_line_index(doc)
        clause = self._make_clause("c1", 1, 1, ["p1l_1", "p1l_99_MISSING"])
        issues: list = []
        span = build_clause_span(clause, idx, "pol", "sha256:abc123", "run_001", issues)
        assert span is not None  # span built from the valid line
        warning_types = [i.issue_type for i in issues]
        assert "line_id_not_in_physical_index" in warning_types


# ---------------------------------------------------------------------------
# TestSpanBuilderFactEvidence
# ---------------------------------------------------------------------------


class TestSpanBuilderFactEvidence:
    def _make_clause(self, clause_id, text):
        return {"clause_id": clause_id, "text": text, "line_ids": ["p1l_1", "p1l_2"]}

    def _make_fact(
        self,
        candidate_id,
        concept,
        evidence_text,
        clause_id,
        evidence_line_ids=None,
        evidence_page=1,
    ):
        return {
            "candidate_id": candidate_id,
            "concept": concept,
            "fact_status": "present",
            "evidence_text": evidence_text,
            "evidence_clause_id": clause_id,
            "evidence_line_ids": evidence_line_ids or ["p1l_1"],
            "evidence_page": evidence_page,
        }

    def test_fact_evidence_span_verified_text(self):
        doc = _make_physical_doc(n_pages=1, n_lines_per_page=3)
        idx = build_line_index(doc)
        clause = self._make_clause("c1", "A free look period of 15 days is available.")
        fact = self._make_fact("f001", "free_look", "free look period of 15 days", "c1")
        span = build_fact_evidence_span(
            fact, {"c1": clause}, idx, "pol", "sha256:abc123", "run_001"
        )
        assert span is not None
        assert span.span_type == "fact_evidence"
        assert span.span_id == "ss_pol_f001_evidence"

    def test_fact_evidence_char_start_correct(self):
        doc = _make_physical_doc(n_pages=1, n_lines_per_page=3)
        idx = build_line_index(doc)
        clause_text = "The grace period of 30 days applies."
        evidence = "grace period of 30 days"
        clause = self._make_clause("c1", clause_text)
        fact = self._make_fact("f002", "grace_period", evidence, "c1")
        span = build_fact_evidence_span(
            fact, {"c1": clause}, idx, "pol", "sha256:abc123", "run_001"
        )
        expected_start = clause_text.lower().find(evidence.lower())
        assert span.char_start == expected_start

    def test_fact_evidence_char_end_correct(self):
        doc = _make_physical_doc(n_pages=1, n_lines_per_page=3)
        idx = build_line_index(doc)
        clause_text = "A free look period of 15 days is available."
        evidence = "free look period of 15 days"
        clause = self._make_clause("c1", clause_text)
        fact = self._make_fact("f003", "free_look", evidence, "c1")
        span = build_fact_evidence_span(
            fact, {"c1": clause}, idx, "pol", "sha256:abc123", "run_001"
        )
        assert span.char_end == span.char_start + len(evidence)

    def test_fact_evidence_span_raises_on_missing_clause(self):
        idx = build_line_index(_make_physical_doc(1, 3))
        fact = self._make_fact("f004", "x", "some text", "nonexistent_clause")
        with pytest.raises(ValueError, match="not found in clause_lookup"):
            build_fact_evidence_span(fact, {}, idx, "pol", "sha256:abc123", "run_001")

    def test_fact_evidence_span_raises_on_empty_evidence_text(self):
        idx = build_line_index(_make_physical_doc(1, 3))
        clause = self._make_clause("c1", "Some text here.")
        fact = self._make_fact("f005", "x", "", "c1")
        with pytest.raises(ValueError, match="empty or whitespace-only"):
            build_fact_evidence_span(fact, {"c1": clause}, idx, "pol", "sha256:abc123", "run_001")

    def test_fact_evidence_span_degrades_gracefully_on_unverifiable_text(self):
        """
        Design: evidence_text not in clause → graceful degradation to clause-level precision.
        char_start=0, char_end=len(clause_text). Does NOT raise. Caller logs warning.
        """
        idx = build_line_index(_make_physical_doc(1, 3))
        clause_text = "Something completely different."
        clause = self._make_clause("c1", clause_text)
        fact = self._make_fact("f006", "x", "This text is not in the clause at all.", "c1")
        span = build_fact_evidence_span(
            fact, {"c1": clause}, idx, "pol", "sha256:abc123", "run_001"
        )
        assert span is not None
        assert span.char_start == 0
        assert span.char_end == len(clause_text)

    def test_build_fact_evidence_spans_skips_non_present(self):
        doc = _make_physical_doc(1, 3)
        idx = build_line_index(doc)
        clause = self._make_clause("c1", "A free look period of 15 days.")
        facts = [
            self._make_fact("f_present", "free_look", "free look period of 15 days", "c1"),
            {
                "candidate_id": "f_not_found",
                "concept": "grace_period",
                "fact_status": "not_found",
                "evidence_text": None,
                "evidence_clause_id": None,
                "evidence_line_ids": [],
                "evidence_page": None,
            },
        ]
        issues: list = []
        spans = build_fact_evidence_spans(
            facts, {"c1": clause}, idx, "pol", "sha256:abc123", "run_001", issues
        )
        assert len(spans) == 1
        assert spans[0].span_id == "ss_pol_f_present_evidence"


# ---------------------------------------------------------------------------
# TestSpanBuilderTableCells
# ---------------------------------------------------------------------------


class TestSpanBuilderTableCells:
    def _make_tables_doc(self, cells):
        return {
            "tables": [
                {
                    "table_id": "t1",
                    "page": 5,
                    "extraction_method": "pdfplumber_lattice",
                    "cells": cells,
                }
            ]
        }

    def test_table_cell_span_with_bbox(self):
        cells = [
            {
                "cell_id": "t1_r0c0",
                "text": "Benefit",
                "bbox": [10.0, 20.0, 200.0, 35.0],
                "is_header": True,
            }
        ]
        spans = build_table_cell_spans(
            self._make_tables_doc(cells), "sha256:abc123", "pol", "run_001"
        )
        assert len(spans) == 1
        assert spans[0].span_id == "ss_pol_t1_r0c0"
        assert spans[0].span_type == "table_cell"
        regions = json.loads(spans[0].page_regions_json)
        assert regions[0]["page"] == 5
        assert regions[0]["bbox"] == [10.0, 20.0, 200.0, 35.0]

    def test_table_cell_span_skips_cells_without_bbox(self):
        cells = [
            {"cell_id": "t1_r0c0", "text": "Header", "bbox": [10.0, 20.0, 200.0, 35.0]},
            {"cell_id": "t1_r0c1", "text": "Value", "bbox": None},  # no bbox
        ]
        spans = build_table_cell_spans(
            self._make_tables_doc(cells), "sha256:abc123", "pol", "run_001"
        )
        assert len(spans) == 1

    def test_table_cell_span_skips_empty_text_cells(self):
        cells = [
            {"cell_id": "t1_r0c0", "text": "Header", "bbox": [10.0, 20.0, 200.0, 35.0]},
            {"cell_id": "t1_r1c0", "text": "", "bbox": [10.0, 35.0, 200.0, 50.0]},
        ]
        spans = build_table_cell_spans(
            self._make_tables_doc(cells), "sha256:abc123", "pol", "run_001"
        )
        assert len(spans) == 1

    def test_table_with_empty_cells_list_generates_no_spans(self):
        """text_alignment_candidate tables have cells=[] — no spans."""
        doc = {
            "tables": [
                {
                    "table_id": "t_cand",
                    "page": 3,
                    "extraction_method": "text_alignment_candidate",
                    "cells": [],
                }
            ]
        }
        spans = build_table_cell_spans(doc, "sha256:abc123", "pol", "run_001")
        assert len(spans) == 0


# ---------------------------------------------------------------------------
# TestFactResolver
# ---------------------------------------------------------------------------


class TestFactResolver:
    def _make_present_fact(self, candidate_id, evidence_clause_id):
        return {
            "candidate_id": candidate_id,
            "concept": "free_look_period",
            "fact_status": "present",
            "evidence_span_id": f"clause:{evidence_clause_id}",
            "evidence_clause_id": evidence_clause_id,
            "evidence_text": "15 days free look",
        }

    def _make_not_found_fact(self, candidate_id):
        return {
            "candidate_id": candidate_id,
            "concept": "grace_period",
            "fact_status": "not_found",
            "evidence_span_id": None,
            "evidence_clause_id": None,
        }

    def _make_span(self, candidate_id):
        return SourceSpan(
            span_id=f"ss_pol_{candidate_id}_evidence",
            document_id="sha256:abc123",
            span_type="fact_evidence",
            text="15 days free look",
            page_regions_json='[{"page":1,"bbox":null,"line_ids":[]}]',
            pipeline_run_id="run_001",
            clause_id="c1",
            char_start=0,
            char_end=18,
        )

    def test_present_fact_gets_real_span_id(self):
        facts = [self._make_present_fact("f001", "c1")]
        spans = {"f001": self._make_span("f001")}
        resolved, warnings = resolve_facts(facts, spans, "pol")
        assert resolved[0]["evidence_span_id"] == "ss_pol_f001_evidence"

    def test_resolved_fact_preserves_provisional_id(self):
        facts = [self._make_present_fact("f001", "c1")]
        spans = {"f001": self._make_span("f001")}
        resolved, _ = resolve_facts(facts, spans, "pol")
        assert resolved[0]["provisional_evidence_span_id"] == "clause:c1"

    def test_resolved_fact_has_resolution_status_resolved(self):
        facts = [self._make_present_fact("f001", "c1")]
        spans = {"f001": self._make_span("f001")}
        resolved, _ = resolve_facts(facts, spans, "pol")
        assert resolved[0]["evidence_resolution_status"] == "resolved"

    def test_not_found_fact_gets_not_applicable_status(self):
        facts = [self._make_not_found_fact("f002")]
        resolved, _ = resolve_facts(facts, {}, "pol")
        assert resolved[0]["evidence_resolution_status"] == "not_applicable"

    def test_resolver_raises_on_present_fact_with_no_span(self):
        facts = [self._make_present_fact("f001", "c1")]
        with pytest.raises(ValueError, match="has no evidence span"):
            resolve_facts(facts, {}, "pol")  # empty spans dict

    def test_original_facts_not_mutated(self):
        facts = [self._make_present_fact("f001", "c1")]
        spans = {"f001": self._make_span("f001")}
        original_span_id = facts[0]["evidence_span_id"]
        resolve_facts(facts, spans, "pol")
        assert facts[0]["evidence_span_id"] == original_span_id  # original unchanged

    def test_multiple_present_facts_resolved(self):
        facts = [
            self._make_present_fact("f001", "c1"),
            self._make_present_fact("f002", "c2"),
            self._make_not_found_fact("f003"),
        ]
        spans = {
            "f001": self._make_span("f001"),
            "f002": SourceSpan(
                span_id="ss_pol_f002_evidence",
                document_id="sha256:abc123",
                span_type="fact_evidence",
                text="30 days grace",
                page_regions_json="[]",
                pipeline_run_id="run_001",
            ),
        }
        resolved, warnings = resolve_facts(facts, spans, "pol")
        assert resolved[0]["evidence_resolution_status"] == "resolved"
        assert resolved[1]["evidence_resolution_status"] == "resolved"
        assert resolved[2]["evidence_resolution_status"] == "not_applicable"
        assert len(warnings) == 0


# ---------------------------------------------------------------------------
# TestTableParentClause
# ---------------------------------------------------------------------------


class TestTableParentClause:
    def _seed_complete_policy(self, conn):
        """Seed a minimal complete policy with a clause and its source_span."""
        run = PipelineRun(id="run_test_001", started_at="2026-01-01T00:00:00")
        product = Product(
            product_id="pol", uin_base="X", normalized_insurer="x", normalized_plan_name="x"
        )
        version = ProductVersion(version_id="pol_v1", product_id="pol", full_uin="X")
        doc = SourceDocument(
            document_id="sha256:abc123",
            policy_id="pol",
            source_pdf_path="p.pdf",
            file_hash="sha256:abc123",
            page_count=5,
            version_id="pol_v1",
        )
        _seed_minimal(conn, run, product, version, doc)

        page = DocumentPage(
            page_id="sha256:abc123_p3",
            document_id="sha256:abc123",
            page_number=3,
            width=595.0,
            height=842.0,
        )
        insert_pages(conn, [page])
        block = DocumentBlock(
            block_id="b3", page_id="sha256:abc123_p3", document_id="sha256:abc123"
        )
        insert_blocks(conn, [block])
        line = DocumentLine(
            line_id="p3l_1",
            block_id="b3",
            document_id="sha256:abc123",
            page_number=3,
            bbox_json="[72,100,510,300]",
            text="Clause text",
        )
        insert_lines(conn, [line])

        section = DocumentSection(
            section_id="sec_1", document_id="sha256:abc123", pipeline_run_id="run_test_001"
        )
        insert_sections(conn, [section])
        clause = PolicyClause(
            clause_id="c1",
            document_id="sha256:abc123",
            section_id="sec_1",
            pipeline_run_id="run_test_001",
            raw_text="text",
            page_start=3,
            page_end=3,
            line_ids_json='["p3l_1"]',
        )
        insert_clauses(conn, [clause])

        # clause body span covering page 3 with same bbox as the line
        span = SourceSpan(
            span_id="ss_pol_c1",
            document_id="sha256:abc123",
            clause_id="c1",
            span_type="clause_body",
            text="text",
            char_start=0,
            char_end=4,
            page_regions_json='[{"page":3,"bbox":[72,100,510,300],"line_ids":["p3l_1"]}]',
            pipeline_run_id="run_test_001",
        )
        insert_source_spans(conn, [span])
        conn.commit()

    def test_backfill_finds_overlapping_clause(self, conn):
        self._seed_complete_policy(conn)
        # Table fully inside clause bbox → high IoU
        table = DocumentTable(
            table_id="t1", document_id="sha256:abc123", page=3, bbox_json="[100,150,400,250]"
        )
        insert_tables(conn, [table])
        conn.commit()
        updated = backfill_table_parent_clauses(conn, "sha256:abc123")
        assert updated == 1
        row = conn.execute(
            "SELECT parent_clause_id, parent_clause_confidence FROM document_tables WHERE table_id='t1'"
        ).fetchone()
        assert row[0] == "c1"
        assert float(row[1]) > 0.10

    def test_backfill_below_threshold_leaves_null(self, conn):
        self._seed_complete_policy(conn)
        # Table far away from clause bbox — no overlap
        table = DocumentTable(
            table_id="t2", document_id="sha256:abc123", page=3, bbox_json="[0,600,100,700]"
        )
        insert_tables(conn, [table])
        conn.commit()
        updated = backfill_table_parent_clauses(conn, "sha256:abc123")
        assert updated == 0
        row = conn.execute(
            "SELECT parent_clause_id FROM document_tables WHERE table_id='t2'"
        ).fetchone()
        assert row[0] is None

    def test_backfill_table_on_wrong_page_not_matched(self, conn):
        self._seed_complete_policy(conn)
        # Table on page 4 — clause is on page 3 → no match
        table = DocumentTable(
            table_id="t3", document_id="sha256:abc123", page=4, bbox_json="[72,100,510,300]"
        )
        insert_tables(conn, [table])
        conn.commit()
        updated = backfill_table_parent_clauses(conn, "sha256:abc123")
        assert updated == 0


# ---------------------------------------------------------------------------
# TestBboxIou
# ---------------------------------------------------------------------------


class TestBboxIou:
    def test_identical_boxes_is_1(self):
        assert _bbox_iou([0, 0, 100, 100], [0, 0, 100, 100]) == 1.0

    def test_no_overlap_is_0(self):
        assert _bbox_iou([0, 0, 50, 50], [60, 60, 100, 100]) == 0.0

    def test_partial_overlap_correct(self):
        iou = _bbox_iou([0, 0, 100, 100], [50, 50, 150, 150])
        assert 0.0 < iou < 1.0

    def test_none_inputs_return_0(self):
        assert _bbox_iou(None, [0, 0, 100, 100]) == 0.0
        assert _bbox_iou([0, 0, 100, 100], None) == 0.0

    def test_empty_lists_return_0(self):
        assert _bbox_iou([], [0, 0, 100, 100]) == 0.0


# ---------------------------------------------------------------------------
# TestRepositoryQueries
# ---------------------------------------------------------------------------


class TestRepositoryQueries:
    def test_query_clauses_with_spans_returns_clauses(
        self, conn, base_run, base_product, base_version, base_doc
    ):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        section = DocumentSection(
            section_id="sec_1", document_id="sha256:abc123", pipeline_run_id="run_test_001"
        )
        insert_sections(conn, [section])
        clause = PolicyClause(
            clause_id="c1",
            document_id="sha256:abc123",
            section_id="sec_1",
            pipeline_run_id="run_test_001",
            raw_text="text",
            page_start=1,
            page_end=1,
            line_ids_json='["p1l_1"]',
        )
        insert_clauses(conn, [clause])
        span = SourceSpan(
            span_id="ss_pol_c1",
            document_id="sha256:abc123",
            clause_id="c1",
            span_type="clause_body",
            text="text",
            char_start=0,
            char_end=4,
            page_regions_json='[{"page":1,"bbox":null,"line_ids":[]}]',
            pipeline_run_id="run_test_001",
        )
        insert_source_spans(conn, [span])
        conn.commit()
        results = query_clauses_with_spans(conn, "sha256:abc123")
        assert len(results) == 1
        assert results[0]["clause_id"] == "c1"
        assert results[0]["span_id"] == "ss_pol_c1"

    def test_count_dangling_fks_zero_after_valid_insert(
        self, conn, base_run, base_product, base_version, base_doc
    ):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        section = DocumentSection(
            section_id="sec_1", document_id="sha256:abc123", pipeline_run_id="run_test_001"
        )
        insert_sections(conn, [section])
        clause = PolicyClause(
            clause_id="c1",
            document_id="sha256:abc123",
            section_id="sec_1",
            pipeline_run_id="run_test_001",
            raw_text="t",
            page_start=1,
            page_end=1,
            line_ids_json="[]",
        )
        insert_clauses(conn, [clause])
        conn.commit()
        assert count_dangling_fks(conn) == 0

    def test_get_table_counts(self, conn, base_run, base_product, base_version, base_doc):
        _seed_minimal(conn, base_run, base_product, base_version, base_doc)
        counts = get_table_counts(conn)
        assert "source_documents" in counts
        assert counts["source_documents"] == 1
        assert "pipeline_runs" in counts
        assert counts["pipeline_runs"] == 1
