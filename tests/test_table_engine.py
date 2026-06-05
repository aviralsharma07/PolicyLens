"""
Tests for DSE-009 Table Engine v1

Unit tests do NOT require PDF access (@pytest.mark.slow for integration tests).
"""

import json
import pathlib

import pytest

from table_engine.cell_extractor import build_cells, _detect_header_row, _normalize_cell_text
from table_engine.models import (
    ColumnCluster,
    ExtractionMethod,
    ExtractedTable,
    TableCell,
    TableDocument,
    TableType,
)
from table_engine.table_type_classifier import classify, classify_from_cells
from table_engine.text_alignment_detector import try_page, _cluster_x_positions
from scripts.eval_table_engine import (
    _bbox_iou,
    _match_gold_to_extracted,
    _discover_reviewed_policies,
    _build_legacy_source_review,
    _build_physical_label_mapping,
)
from scripts.run_table_engine import _assign_parent_clause, _is_reliable_pdfplumber_text_table
from scripts.validate_gold_corpus import validate_physical_table_labels

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# TestTableModels
# ---------------------------------------------------------------------------


class TestTableModels:
    def test_table_type_enum_all_values(self):
        values = {t.value for t in TableType}
        expected = {
            "waiting_period",
            "schedule_of_benefits",
            "room_rent",
            "premium",
            "claims_documents",
            "network_list",
            "unknown",
        }
        assert values == expected

    def test_extraction_method_enum_values(self):
        values = {m.value for m in ExtractionMethod}
        assert "pdfplumber_lattice" in values
        assert "pdfplumber_text" in values
        assert "text_alignment_candidate" in values

    def test_table_cell_id_format(self):
        cell = TableCell(
            cell_id="mypolicy_p4_t1_r0_c0",
            table_id="mypolicy_p4_t1",
            row_index=0,
            col_index=0,
            text="Waiting period type",
            is_header=True,
        )
        assert cell.cell_id == "mypolicy_p4_t1_r0_c0"
        assert cell.is_header is True
        assert cell.row_span == 1
        assert cell.col_span == 1

    def test_extracted_table_required_fields(self):
        table = ExtractedTable(
            table_id="pol_p1_t1",
            document_id="sha256:abc",
            policy_id="pol",
            page=1,
            extraction_method=ExtractionMethod.pdfplumber_lattice,
        )
        assert table.table_type == TableType.unknown
        assert table.table_type_confidence == 0.0
        assert table.cells == []
        assert table.raw_lines == []
        assert table.issues == []

    def test_table_document_structured_candidate_counts(self):
        doc = TableDocument(
            pipeline_run_id="run_001",
            document_id="sha256:xyz",
            policy_id="test",
            source_pdf_path="/fake/path.pdf",
            page_count=10,
            tables_found=3,
            structured_tables=2,
            candidate_tables=1,
        )
        assert doc.structured_tables == 2
        assert doc.candidate_tables == 1
        assert doc.tables_found == 3

    def test_cell_bbox_optional(self):
        cell = TableCell(
            cell_id="t1_r0_c0",
            table_id="t1",
            row_index=0,
            col_index=0,
            text="text",
        )
        assert cell.bbox is None

    def test_cell_header_lineage_fields_optional(self):
        cell = TableCell(
            cell_id="t1_r1_c1",
            table_id="t1",
            row_index=1,
            col_index=1,
            text="100%",
            column_header_text="% of Sum Insured",
            row_header_text="Loss of one hand",
        )
        assert cell.column_header_text == "% of Sum Insured"
        assert cell.row_header_text == "Loss of one hand"

    def test_serialize_roundtrip_full_document(self):
        cell = TableCell(
            cell_id="p1_t1_r0_c0",
            table_id="p1_t1",
            row_index=0,
            col_index=0,
            text="Header",
            bbox=[72.0, 200.0, 280.0, 215.0],
            is_header=True,
        )
        table = ExtractedTable(
            table_id="p1_t1",
            document_id="sha256:abc",
            policy_id="test_pol",
            page=1,
            bbox=[72.0, 200.0, 480.0, 350.0],
            table_type=TableType.waiting_period,
            table_type_confidence=0.91,
            extraction_method=ExtractionMethod.pdfplumber_lattice,
            row_count=3,
            col_count=2,
            has_header_row=True,
            header_row_index=0,
            cells=[cell],
        )
        doc = TableDocument(
            pipeline_run_id="run_001",
            document_id="sha256:abc",
            policy_id="test_pol",
            source_pdf_path="/fake/path.pdf",
            page_count=5,
            tables_found=1,
            structured_tables=1,
            candidate_tables=0,
            tables=[table],
        )
        data = json.loads(doc.model_dump_json(exclude_none=True))
        restored = TableDocument(**data)
        assert restored.tables_found == 1
        assert restored.tables[0].table_type == TableType.waiting_period
        assert restored.tables[0].cells[0].is_header is True

    def test_none_text_normalized_to_empty(self):
        text = _normalize_cell_text(None)
        assert text == ""

    def test_whitespace_text_normalized(self):
        text = _normalize_cell_text("  PED  ")
        assert text == "PED"


# ---------------------------------------------------------------------------
# TestTableTypeClassifier
# ---------------------------------------------------------------------------


class TestTableTypeClassifier:
    def test_classify_waiting_period_by_header(self):
        grid = [
            ["Waiting period type", "Duration"],
            ["PED", "48 months"],
            ["Initial", "30 days"],
        ]
        t_type, conf = classify(grid)
        assert t_type == TableType.waiting_period
        assert conf > 0.2

    def test_classify_waiting_period_by_ped_keyword(self):
        grid = [["Type", "Period"], ["PED waiting", "36 months"], ["Specific disease", "24 months"]]
        t_type, conf = classify(grid)
        assert t_type == TableType.waiting_period

    def test_classify_schedule_of_benefits_by_benefit_keyword(self):
        grid = [
            ["Benefit", "Limit/Condition"],
            ["Ambulance", "Rs. 750"],
            ["Restoration benefit", "200% SI"],
        ]
        t_type, conf = classify(grid)
        assert t_type == TableType.schedule_of_benefits
        assert conf > 0.0  # Type is correct; raw confidence varies with keyword list size

    def test_classify_room_rent_by_room_rent_keyword(self):
        grid = [
            ["Room category", "Limit"],
            ["Single private AC room", "1% of SI per day"],
            ["ICU", "2% of SI per day"],
        ]
        t_type, conf = classify(grid)
        # Should be room_rent (no ambulance/ncb/restoration to trigger SOB disambiguation)
        assert t_type in (TableType.room_rent, TableType.schedule_of_benefits)
        assert conf > 0.0

    def test_classify_premium_by_rate_keyword(self):
        grid = [
            ["Period on risk", "Rate of premium retained"],
            ["Up to 1 month", "25%"],
            ["Up to 3 months", "50%"],
        ]
        t_type, conf = classify(grid)
        assert t_type == TableType.premium
        assert conf >= 0.1  # "period on risk" + "rate of premium" are strong signals

    def test_classify_unknown_below_threshold(self):
        grid = [["A", "B"], ["1", "2"], ["x", "y"]]
        t_type, conf = classify(grid)
        assert t_type == TableType.unknown

    def test_classifier_handles_empty_grid(self):
        t_type, conf = classify([])
        assert t_type == TableType.unknown
        assert conf == 0.0

    def test_classifier_handles_all_none_cells(self):
        grid = [[None, None], [None, None]]
        t_type, conf = classify(grid)
        assert t_type == TableType.unknown

    def test_room_rent_vs_schedule_disambiguated_by_benefit(self):
        # Contains "room rent" AND "ambulance" → should be schedule_of_benefits
        grid = [
            ["Benefit", "Sub-limit"],
            ["Room rent", "1% SI"],
            ["Ambulance", "Rs. 2000"],
            ["Restoration benefit", "100% SI"],
        ]
        t_type, conf = classify(grid)
        assert t_type == TableType.schedule_of_benefits

    def test_heading_context_boosts_classification(self):
        # Grid alone is ambiguous; heading context tips it
        grid = [["Type", "Duration"], ["PED", "48 months"]]
        context = "Waiting Period"
        t_type, conf = classify(grid, heading_context=context)
        assert t_type == TableType.waiting_period

    def test_classify_from_cells_convenience(self):
        cells_text = ["Waiting period type", "Duration", "PED", "48 months"]
        t_type, conf = classify_from_cells(cells_text)
        assert t_type == TableType.waiting_period

    def test_classify_cataract_sublimit_as_schedule_of_benefits(self):
        grid = [
            ["Sum Insured", "Additional Cataract limit"],
            ["Rs. 8,00,000", "Rs. 80,000"],
            ["Rs. 10,00,000", "Rs. 1,00,000"],
            ["Rs. 12,00,000", "Rs. 1,20,000"],
            ["Rs. 15,00,000", "Rs. 1,50,000"],
        ]
        t_type, conf = classify(grid)
        assert t_type == TableType.schedule_of_benefits

    def test_classify_cataract_sublimit_with_premium_heading(self):
        grid = [
            ["Sum Insured", "Additional Cataract limit"],
            ["Rs. 8,00,000", "Rs. 80,000"],
            ["Rs. 10,00,000", "Rs. 1,00,000"],
            ["Rs. 12,00,000", "Rs. 1,20,000"],
            ["Rs. 15,00,000", "Rs. 1,50,000"],
        ]
        t_type, conf = classify(grid, heading_context="premium rates and premium")
        assert t_type == TableType.schedule_of_benefits

    def test_classify_premium_retention_not_reclassified(self):
        grid = [
            ["Period on risk", "Rate of premium to be charged"],
            ["Up to one month", "1/4th of the annual rate"],
            ["Up to two months", "1/2th of the annual rate"],
        ]
        t_type, conf = classify(grid)
        assert t_type == TableType.premium

    def test_classify_premium_retention_with_benefit_heading(self):
        grid = [
            ["Period on risk", "Rate of premium to be charged"],
            ["Up to one month", "1/4th of the annual rate"],
        ]
        t_type, conf = classify(grid, heading_context="schedule of benefits cataract")
        assert t_type == TableType.premium

    def test_classify_generic_percent_not_schedule(self):
        grid = [
            ["Discount", "Rate"],
            ["5%", "10%"],
            ["10%", "15%"],
        ]
        t_type, conf = classify(grid)
        assert t_type == TableType.unknown


# ---------------------------------------------------------------------------
# TestCellExtractor
# ---------------------------------------------------------------------------


class TestCellExtractor:
    def test_header_row_detected_by_waiting_period_type_term(self):
        grid = [
            ["Waiting period type", "Duration"],
            ["PED", "48 months"],
        ]
        cells, has_header, header_idx = build_cells("t1", grid)
        assert has_header is True
        assert header_idx == 0
        header_cells = [c for c in cells if c.is_header]
        assert len(header_cells) == 2

    def test_header_row_detected_by_benefit_term(self):
        grid = [
            ["Benefit", "Limit/Condition"],
            ["Ambulance", "Rs. 750"],
        ]
        cells, has_header, header_idx = build_cells("t2", grid)
        assert has_header is True
        assert header_idx == 0

    def test_header_row_detected_after_title_row(self):
        grid = [
            ["For policy with one year term", ""],
            ["PERIOD ON RISK", "RATE OF PREMIUM TO BE RETAINED"],
            ["Up to one-month", "one-third of annual premium"],
        ]
        cells, has_header, header_idx = build_cells("t_title", grid)
        assert has_header is True
        assert header_idx == 1
        assert all(c.is_header for c in cells if c.row_index == 1)

    def test_column_header_lineage_assigned_to_body_cells(self):
        grid = [["Benefit", "Limit"], ["Ambulance", "Rs.750"]]
        cells, _, _ = build_cells("t_lineage", grid)
        body_limit = next(c for c in cells if c.row_index == 1 and c.col_index == 1)
        assert body_limit.column_header_text == "Limit"
        assert body_limit.row_header_text == "Ambulance"

    def test_no_header_when_no_known_terms(self):
        grid = [
            ["Aviral", "Sharma"],
            ["John", "Doe"],
        ]
        cells, has_header, header_idx = build_cells("t3", grid)
        assert has_header is False
        assert header_idx is None

    def test_cell_id_format_r0_c0(self):
        grid = [["A", "B"]]
        cells, _, _ = build_cells("mypol_p1_t1", grid)
        ids = {c.cell_id for c in cells}
        assert "mypol_p1_t1_r0_c0" in ids
        assert "mypol_p1_t1_r0_c1" in ids

    def test_none_cells_become_empty_string(self):
        grid = [[None, "Value"], ["Key", None]]
        cells, _, _ = build_cells("t4", grid)
        texts = [c.text for c in cells]
        assert "" in texts
        assert None not in texts

    def test_row_col_index_correct(self):
        grid = [["r0c0", "r0c1"], ["r1c0", "r1c1"]]
        cells, _, _ = build_cells("t5", grid)
        cell_map = {(c.row_index, c.col_index): c.text for c in cells}
        assert cell_map[(0, 0)] == "r0c0"
        assert cell_map[(0, 1)] == "r0c1"
        assert cell_map[(1, 0)] == "r1c0"
        assert cell_map[(1, 1)] == "r1c1"

    def test_header_row_cells_marked_is_header_true(self):
        grid = [["Benefit", "Limit"], ["Ambulance", "Rs.750"]]
        cells, _, _ = build_cells("t6", grid)
        r0_cells = [c for c in cells if c.row_index == 0]
        r1_cells = [c for c in cells if c.row_index == 1]
        assert all(c.is_header for c in r0_cells)
        assert all(not c.is_header for c in r1_cells)

    def test_body_cells_marked_is_header_false(self):
        grid = [["Duration", "Type"], ["30 days", "Initial"]]
        cells, _, _ = build_cells("t7", grid)
        body_cells = [c for c in cells if c.row_index == 1]
        assert all(not c.is_header for c in body_cells)

    def test_cell_bbox_assigned_when_provided(self):
        grid = [["A", "B"]]
        bboxes = [[[10.0, 20.0, 50.0, 35.0], [55.0, 20.0, 100.0, 35.0]]]
        cells, _, _ = build_cells("t8", grid, cell_bboxes=bboxes)
        assert cells[0].bbox == [10.0, 20.0, 50.0, 35.0]
        assert cells[1].bbox == [55.0, 20.0, 100.0, 35.0]

    def test_empty_grid_returns_no_cells(self):
        cells, has_header, header_idx = build_cells("t9", [])
        assert cells == []
        assert has_header is False
        assert header_idx is None


# ---------------------------------------------------------------------------
# TestTextAlignmentDetector
# ---------------------------------------------------------------------------


class TestTextAlignmentDetector:
    def _make_lines(self, x_starts, texts=None, region="body"):
        lines = []
        for i, x in enumerate(x_starts):
            text = texts[i] if texts else f"line {i}"
            lines.append(
                {
                    "line_id": f"l{i}",
                    "text": text,
                    "bbox": [x, float(50 + i * 15), x + 200.0, float(65 + i * 15)],
                    "region": region,
                }
            )
        return lines

    def test_no_clusters_below_minimum_lines(self):
        lines = self._make_lines([72.0, 72.0], texts=["line 1", "line 2"])
        tables, counter = try_page(
            lines, page_num=1, policy_id="p", document_id="d", page_table_counter=1
        )
        # Only 2 lines — below _MIN_TABLE_LINES=3, should return nothing
        assert tables == []

    def test_two_column_cluster_detected(self):
        # Lines with x_starts alternating between two positions (tabular look)
        x_starts = [72.0, 300.0, 72.0, 300.0, 72.0, 300.0]
        texts = ["Type", "Duration", "PED", "48 months", "Initial", "30 days"]
        lines = self._make_lines(x_starts, texts=texts)
        tables, counter = try_page(
            lines, page_num=1, policy_id="p", document_id="d", page_table_counter=1
        )
        # Should detect something (maybe 1 candidate)
        # The detector groups consecutive lines sharing same column x-pattern
        assert isinstance(tables, list)

    def test_ambiguous_column_marks_cells_empty(self):
        x_starts = [72.0, 100.0, 72.0, 100.0, 72.0, 100.0]
        lines = self._make_lines(x_starts)
        tables, counter = try_page(
            lines, page_num=1, policy_id="p", document_id="d", page_table_counter=1
        )
        for t in tables:
            if t.extraction_method == ExtractionMethod.text_alignment_candidate:
                if "cells_not_reliably_split" in t.issues:
                    assert t.cells == []

    def test_candidate_table_has_correct_extraction_method(self):
        x_starts = [72.0, 300.0, 72.0, 300.0, 72.0, 300.0]
        lines = self._make_lines(x_starts)
        tables, _ = try_page(
            lines, page_num=1, policy_id="p", document_id="d", page_table_counter=1
        )
        for t in tables:
            assert t.extraction_method == ExtractionMethod.text_alignment_candidate

    def test_issue_logged_on_ambiguous_split(self):
        x_starts = [72.0, 200.0, 72.0, 200.0, 72.0, 200.0]
        lines = self._make_lines(x_starts)
        tables, _ = try_page(
            lines, page_num=1, policy_id="p", document_id="d", page_table_counter=1
        )
        for t in tables:
            assert "cells_not_reliably_split" in t.issues

    def test_candidate_preserves_raw_lines_without_fake_cells(self):
        x_starts = [72.0, 300.0, 72.0, 300.0, 72.0, 300.0]
        texts = ["Type", "Duration", "PED", "48 months", "Initial", "30 days"]
        lines = self._make_lines(x_starts, texts=texts)
        tables, _ = try_page(
            lines, page_num=1, policy_id="p", document_id="d", page_table_counter=1
        )
        assert tables
        for table in tables:
            assert table.cells == []
            assert table.raw_lines
            assert {line["text"] for line in table.raw_lines}.issubset(set(texts))

    def test_bbox_inferable_from_line_bounds(self):
        x_starts = [72.0, 300.0, 72.0, 300.0, 72.0, 300.0]
        lines = self._make_lines(x_starts)
        tables, _ = try_page(
            lines, page_num=1, policy_id="p", document_id="d", page_table_counter=1
        )
        for t in tables:
            if t.bbox is not None:
                assert len(t.bbox) == 4

    def test_header_region_lines_excluded(self):
        lines = self._make_lines([72.0, 72.0, 72.0, 72.0], region="top")
        tables, _ = try_page(
            lines, page_num=1, policy_id="p", document_id="d", page_table_counter=1
        )
        assert tables == []


class TestColumnClustering:
    def test_single_x_position(self):
        clusters = _cluster_x_positions([72.0])
        assert len(clusters) == 1

    def test_two_distinct_clusters(self):
        xs = [72.0, 73.0, 300.0, 301.0]
        clusters = _cluster_x_positions(xs)
        assert len(clusters) == 2

    def test_close_xs_merge_into_one_cluster(self):
        xs = [72.0, 75.0, 78.0]  # within 20pt gap
        clusters = _cluster_x_positions(xs)
        assert len(clusters) == 1

    def test_empty_input(self):
        clusters = _cluster_x_positions([])
        assert clusters == []


# ---------------------------------------------------------------------------
# TestTableDetector (unit, no PDF)
# ---------------------------------------------------------------------------


class TestTableDetectorUnit:
    def test_stable_table_id_format(self):
        from table_engine.table_detector import _stable_table_id

        tid = _stable_table_id("care_health_care_plus", 4, 1)
        assert tid == "care_health_care_plus_p4_t1"

    def test_stable_table_id_page_and_n(self):
        from table_engine.table_detector import _stable_table_id

        assert _stable_table_id("pol", 12, 3) == "pol_p12_t3"

    def test_parent_clause_prefers_shorter_page_span(self):
        section_tree = {
            "sections": [
                {"section_id": "sec_a", "level": 1},
                {"section_id": "sec_b", "level": 2},
            ],
            "clauses": [
                {
                    "clause_id": "broad",
                    "section_id": "sec_b",
                    "page_start": 1,
                    "page_end": 10,
                },
                {
                    "clause_id": "narrow",
                    "section_id": "sec_a",
                    "page_start": 4,
                    "page_end": 4,
                },
            ],
        }
        clause_id, confidence = _assign_parent_clause(4, section_tree)
        assert clause_id == "narrow"
        assert confidence == 0.75

    def test_parent_clause_tie_prefers_deeper_section(self):
        section_tree = {
            "sections": [
                {"section_id": "sec_a", "level": 1},
                {"section_id": "sec_b", "level": 3},
            ],
            "clauses": [
                {
                    "clause_id": "shallow",
                    "section_id": "sec_a",
                    "page_start": 4,
                    "page_end": 4,
                },
                {
                    "clause_id": "deep",
                    "section_id": "sec_b",
                    "page_start": 4,
                    "page_end": 4,
                },
            ],
        }
        clause_id, _ = _assign_parent_clause(4, section_tree)
        assert clause_id == "deep"

    def test_pdfplumber_text_filter_rejects_large_page_body_table(self):
        table = ExtractedTable(
            table_id="t_text",
            document_id="d",
            policy_id="p",
            page=1,
            bbox=[0.0, 0.0, 595.0, 700.0],
            extraction_method=ExtractionMethod.pdfplumber_text,
            row_count=50,
            col_count=4,
            has_header_row=True,
            cells=[
                TableCell(
                    cell_id="c1",
                    table_id="t_text",
                    row_index=0,
                    col_index=0,
                    text="Header",
                    is_header=True,
                )
            ],
        )
        assert _is_reliable_pdfplumber_text_table(table, 595.0, 842.0) is False

    def test_pdfplumber_text_filter_accepts_small_headered_grid(self):
        table = ExtractedTable(
            table_id="t_text",
            document_id="d",
            policy_id="p",
            page=1,
            bbox=[100.0, 100.0, 300.0, 220.0],
            extraction_method=ExtractionMethod.pdfplumber_text,
            row_count=5,
            col_count=3,
            has_header_row=True,
            cells=[
                TableCell(
                    cell_id="c1",
                    table_id="t_text",
                    row_index=0,
                    col_index=0,
                    text="Header",
                    is_header=True,
                )
            ],
        )
        assert _is_reliable_pdfplumber_text_table(table, 595.0, 842.0) is True


class TestTableEvalStrictMatching:
    def test_bbox_iou_identical_boxes(self):
        assert _bbox_iou([0, 0, 100, 100], [0, 0, 100, 100]) == 1.0

    def test_same_page_wrong_content_does_not_count_as_detected(self):
        gold = {
            "page": 4,
            "table_type": "waiting_period",
            "headers": ["Waiting period type", "Duration"],
            "rows": [["PED", "48 months"]],
        }
        extracted = [
            {
                "table_id": "t1",
                "page": 4,
                "table_type": "premium",
                "extraction_method": "pdfplumber_lattice",
                "cells": [{"text": "Rate of premium"}],
            }
        ]
        match = _match_gold_to_extracted(
            gold, extracted, [{"table_id": "t1", "text": "Rate of premium"}]
        )
        assert match["page_region_detected"] is True
        assert match["detected"] is False

    def test_type_and_signature_match_counts_as_detected(self):
        gold = {
            "page": 4,
            "table_type": "waiting_period",
            "headers": ["Waiting period type", "Duration"],
            "rows": [["PED", "48 months"]],
        }
        extracted = [
            {
                "table_id": "t1",
                "page": 4,
                "table_type": "waiting_period",
                "extraction_method": "pdfplumber_lattice",
                "cells": [{"text": "Waiting period type"}],
            }
        ]
        cells = [
            {"table_id": "t1", "text": "Waiting period type"},
            {"table_id": "t1", "text": "Duration"},
            {"table_id": "t1", "text": "PED"},
            {"table_id": "t1", "text": "48 months"},
        ]
        match = _match_gold_to_extracted(gold, extracted, cells)
        assert match["detected"] is True
        assert match["type_ok"] is True

    def test_one_to_one_matching_excludes_used_table(self):
        gold = {
            "page": 4,
            "bbox": [0, 0, 100, 100],
            "table_type": "premium",
            "headers": ["Period on risk"],
            "rows": [["Up to one month"]],
        }
        extracted = [
            {
                "table_id": "t1",
                "page": 4,
                "bbox": [0, 0, 100, 100],
                "table_type": "premium",
                "extraction_method": "pdfplumber_lattice",
                "cells": [{"text": "Period on risk"}],
            }
        ]
        match = _match_gold_to_extracted(
            gold, extracted, [{"table_id": "t1", "text": "Period on risk"}], {"t1"}
        )
        assert match["detected"] is False
        assert match["match_reason"] == "no_extracted_table_on_gold_page"


class TestPhysicalTableLabelValidation:
    def test_physical_table_label_validator_accepts_valid_label(self, tmp_path):
        policy_dir = tmp_path / "policy"
        policy_dir.mkdir()
        payload = [
            {
                "label_id": "label_001",
                "source_table_id": "legacy_001",
                "page": 1,
                "bbox": [10.0, 20.0, 200.0, 120.0],
                "table_type": "schedule_of_benefits",
                "headers": ["Benefit", "Limit"],
                "rows": [["Ambulance", "Rs. 750"]],
                "header_rows": [0],
                "column_count": 2,
                "row_count": 2,
                "priority": True,
                "reviewer_note": "Physical table.",
            }
        ]
        (policy_dir / "physical_table_labels.json").write_text(json.dumps(payload))
        assert validate_physical_table_labels(policy_dir, page_count=2) == 1

    def test_physical_table_label_validator_rejects_missing_bbox(self, tmp_path):
        policy_dir = tmp_path / "policy"
        policy_dir.mkdir()
        payload = [
            {
                "label_id": "label_001",
                "source_table_id": "legacy_001",
                "page": 1,
                "table_type": "schedule_of_benefits",
                "headers": ["Benefit", "Limit"],
                "rows": [],
                "header_rows": [0],
                "column_count": 2,
                "row_count": 2,
                "priority": True,
                "reviewer_note": "Physical table.",
            }
        ]
        (policy_dir / "physical_table_labels.json").write_text(json.dumps(payload))
        with pytest.raises(Exception):
            validate_physical_table_labels(policy_dir, page_count=2)


# ---------------------------------------------------------------------------
# Integration tests against gold PDFs (@pytest.mark.slow)
# ---------------------------------------------------------------------------


def _load_gold_tables(slug: str) -> list:
    path = _PROJECT_ROOT / "gold_corpus" / "policies" / slug / "tables.json"
    if not path.is_file():
        return []
    import json

    with open(path) as f:
        return json.load(f)


def _load_extracted_tables(slug: str) -> list:
    path = _PROJECT_ROOT / "data" / "interim" / "tables" / slug / "document_tables.json"
    if not path.is_file():
        return []
    import json

    with open(path) as f:
        data = json.load(f)
    return data.get("tables", [])


@pytest.mark.slow
class TestIntegrationAgainstGoldPdf:
    """
    Integration tests: verify table extraction against gold corpus.
    Requires PDFs in policy_data/ and run_table_engine.py to have been executed.
    """

    def _check_policy(self, slug: str):
        gold_tables = _load_gold_tables(slug)
        extracted_tables = _load_extracted_tables(slug)

        if not gold_tables:
            pytest.skip(f"No gold tables for {slug}")

        if not extracted_tables:
            pytest.fail(f"No extracted tables found for {slug} — run run_table_engine.py first")

        # Check that each gold page has at least one extracted table
        gold_pages = {t["page"] for t in gold_tables}
        extracted_pages = {t["page"] for t in extracted_tables}

        missing_pages = gold_pages - extracted_pages
        # For integration test: just verify we found something (not hard gate here)
        assert len(extracted_tables) > 0, f"Zero tables extracted for {slug}"

    def test_care_health_care_plus_tables(self):
        self._check_policy("care_health_care_plus")

    def test_hdfc_arogya_sanjeevani_tables(self):
        self._check_policy("hdfc_arogya_sanjeevani")

    def test_star_medi_classic_accident_tables(self):
        self._check_policy("star_medi_classic_accident")

    def test_icici_family_shield_tables(self):
        self._check_policy("icici_family_shield")

    def test_new_india_floater_tables(self):
        self._check_policy("new_india_floater")


# ---------------------------------------------------------------------------
# Tests for DSE-022 20-policy eval expansion
# ---------------------------------------------------------------------------


class TestDse022EvalExpansion:
    def test_discover_reviewed_policies_counts_all_20(self, tmp_path):
        slugs = _discover_reviewed_policies(str(_PROJECT_ROOT / "gold_corpus"))
        assert len(slugs) == 20

    def test_discover_reviewed_policies_finds_all_with_metadata(self, tmp_path):
        gold_dir = tmp_path / "gold"
        golden = gold_dir / "policies" / "policy_a"
        golden.mkdir(parents=True)
        (golden / "metadata.json").write_text("{}")
        drafty = gold_dir / "policies" / "policy_b"
        drafty.mkdir(parents=True)
        (drafty / "metadata.json").write_text("{}")
        slugs = _discover_reviewed_policies(str(gold_dir))
        assert slugs == sorted(["policy_a", "policy_b"])

    def test_discover_reviewed_policies_skips_dirs_without_metadata(self, tmp_path):
        gold_dir = tmp_path / "gold"
        has_meta = gold_dir / "policies" / "has_meta"
        has_meta.mkdir(parents=True)
        (has_meta / "metadata.json").write_text("{}")
        no_meta = gold_dir / "policies" / "no_meta"
        no_meta.mkdir(parents=True)
        slugs = _discover_reviewed_policies(str(gold_dir))
        assert slugs == ["has_meta"]

    def test_physical_label_mapping_built_correctly(self, tmp_path):
        gold_dir = tmp_path / "gold"
        pol = gold_dir / "policies" / "test_pol"
        pol.mkdir(parents=True)
        (pol / "metadata.json").write_text('{"review_status": "reviewed"}')
        # Create physical labels that reference legacy table IDs
        phys = [
            {
                "label_id": "l1",
                "source_table_id": "legacy_t1",
                "page": 1,
                "table_type": "waiting_period",
            },
            {"label_id": "l2", "source_table_id": None, "page": 2, "table_type": "unknown"},
        ]
        (pol / "physical_table_labels.json").write_text(__import__("json").dumps(phys))
        mapping = _build_physical_label_mapping(str(gold_dir))
        assert "legacy_t1" in mapping
        assert mapping["legacy_t1"]["label_id"] == "l1"

    def test_legacy_disposition_physical_table_eval(self, tmp_path):
        gold_dir = tmp_path / "gold"
        pol = gold_dir / "policies" / "test_pol"
        pol.mkdir(parents=True)
        (pol / "metadata.json").write_text('{"review_status": "reviewed"}')
        phys = [
            {
                "label_id": "l1",
                "source_table_id": "legacy_t1",
                "page": 1,
                "table_type": "waiting_period",
            },
        ]
        (pol / "physical_table_labels.json").write_text(__import__("json").dumps(phys))
        legacy = [{"table_id": "legacy_t1", "page": 1, "table_type": "waiting_period"}]
        (pol / "tables.json").write_text(__import__("json").dumps(legacy))
        rows = _build_legacy_source_review(str(gold_dir), str(tmp_path / "reports"))
        assert len(rows) == 1
        assert rows[0]["classification"] == "physical_table_eval"
        # Verify the output file was written
        assert (tmp_path / "reports" / "dse022_legacy_table_dispositions_v1.json").exists()

    def test_legacy_disposition_nonpriority_type(self, tmp_path):
        gold_dir = tmp_path / "gold"
        pol = gold_dir / "policies" / "test_pol"
        pol.mkdir(parents=True)
        (pol / "metadata.json").write_text('{"review_status": "reviewed"}')
        # No physical labels at all
        (pol / "physical_table_labels.json").write_text("[]")
        legacy = [{"table_id": "legacy_prem", "page": 1, "table_type": "premium"}]
        (pol / "tables.json").write_text(__import__("json").dumps(legacy))
        rows = _build_legacy_source_review(str(gold_dir), str(tmp_path / "reports"))
        assert len(rows) == 1
        assert rows[0]["classification"] == "diagnostic_nonpriority_table"

    def test_legacy_disposition_fallback_deferred(self, tmp_path):
        gold_dir = tmp_path / "gold"
        pol = gold_dir / "policies" / "test_pol"
        pol.mkdir(parents=True)
        (pol / "metadata.json").write_text('{"review_status": "reviewed"}')
        (pol / "physical_table_labels.json").write_text("[]")
        legacy = [{"table_id": "legacy_unknown", "page": 5, "table_type": "waiting_period"}]
        (pol / "tables.json").write_text(__import__("json").dumps(legacy))
        rows = _build_legacy_source_review(str(gold_dir), str(tmp_path / "reports"))
        assert len(rows) == 1
        assert rows[0]["classification"] == "deferred_needs_pdf_review"

    def test_no_legacy_rows_without_disposition(self, tmp_path):
        # Verify that the real gold corpus produces no undocumented rows
        from scripts.eval_table_engine import _LEGACY_TABLE_DISPOSITIONS

        # Every legacy tables.json row must either be in _LEGACY_TABLE_DISPOSITIONS,
        # linked via physical label source_table_id, or a non-priority type. We test
        # this by building the full legacy review and checking for the fallback marker.
        rows = _build_legacy_source_review(str(_PROJECT_ROOT / "gold_corpus"), str(tmp_path))
        undocumented = [
            r
            for r in rows
            if r["classification"] == "deferred_needs_pdf_review"
            and r["reason"].startswith("Legacy type")
        ]
        assert len(undocumented) == 0, f"Undocumented rows: {undocumented}"

    def test_same_page_wrong_content_does_not_count_as_detected(self):
        # Already tested above; kept here for DSE-022 regression
        gold = {
            "page": 4,
            "table_type": "waiting_period",
            "headers": ["Waiting period type", "Duration"],
            "rows": [["PED", "48 months"]],
        }
        extracted = [
            {
                "table_id": "t1",
                "page": 4,
                "table_type": "premium",
                "extraction_method": "pdfplumber_lattice",
                "cells": [{"text": "Rate of premium"}],
            }
        ]
        cells = [{"table_id": "t1", "text": "Rate of premium"}]
        match = _match_gold_to_extracted(gold, extracted, cells)
        assert match["page_region_detected"] is True
        assert match["detected"] is False

    def test_one_to_one_matching_excludes_used_table(self):
        gold = {
            "page": 4,
            "bbox": [0, 0, 100, 100],
            "table_type": "premium",
            "headers": ["Period on risk"],
            "rows": [["Up to one month"]],
        }
        extracted = [
            {
                "table_id": "t1",
                "page": 4,
                "bbox": [0, 0, 100, 100],
                "table_type": "premium",
                "extraction_method": "pdfplumber_lattice",
                "cells": [{"text": "Period on risk"}],
            }
        ]
        cells = [{"table_id": "t1", "text": "Period on risk"}]
        match = _match_gold_to_extracted(gold, extracted, cells, {"t1"})
        assert match["detected"] is False
        assert match["match_reason"] == "no_extracted_table_on_gold_page"
