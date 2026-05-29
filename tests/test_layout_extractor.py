import json
import os
import pathlib

import pytest

from pdf_parser.header_footer_detector import (
    classify_line_region,
    process as hf_process,
)
from pdf_parser.models import (
    Block,
    BlockType,
    Line,
    Page,
    PhysicalDocument,
    Region,
    Span,
)

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _check_bbox(bbox, width, height):
    """Inline bbox validation mirroring validate_physical_outputs.validate_bbox."""
    errs = []
    if len(bbox) != 4:
        errs.append("len != 4")
        return errs
    x0, top, x1, bottom = bbox
    if x0 < -1 or x1 > width + 1 or top < -1 or bottom > height + 1:
        errs.append("out of bounds")
    if x0 >= x1:
        errs.append(f"x0 ({x0}) >= x1 ({x1})")
    if top >= bottom:
        errs.append(f"top ({top}) >= bottom ({bottom})")
    return errs


class TestBboxValidation:
    def test_valid_bbox(self):
        page = Page(
            page_number=1,
            width=612,
            height=792,
            blocks=[
                Block(
                    block_id="p1b_1",
                    block_type=BlockType.text,
                    bbox=[50, 100, 562, 120],
                    text="Test line",
                    line_ids=["p1l_1"],
                    reading_order=0,
                )
            ],
            lines=[
                Line(
                    line_id="p1l_1",
                    bbox=[50, 100, 562, 115],
                    text="Test line",
                    region=Region.body,
                )
            ],
            spans=[
                Span(
                    span_id="p1s_1",
                    text="Test",
                    bbox=[50, 100, 200, 115],
                    font_size=12,
                    font_name="Helvetica",
                )
            ],
        )
        assert page.width == 612
        assert page.height == 792
        assert page.blocks[0].bbox == [50, 100, 562, 120]

    def test_invalid_bbox_x0_gt_x1_detected(self):
        bbox = [500, 100, 50, 120]
        errs = _check_bbox(bbox, 612, 792)
        assert any("x0" in e for e in errs), f"Expected x0>=x1 error, got {errs}"

    def test_bbox_zero_dimensions(self):
        block = Block(
            block_id="zero",
            block_type=BlockType.text,
            text="",
            bbox=[0, 0, 0, 0],
            reading_order=0,
        )
        assert block.bbox == [0, 0, 0, 0]


class TestStableIdFormat:
    def test_block_id_format(self):
        block = Block(
            block_id="p1b_1",
            block_type=BlockType.text,
            text="test",
            bbox=[0, 0, 100, 10],
            reading_order=0,
        )
        assert block.block_id.startswith("p")

    def test_line_id_format(self):
        line = Line(
            line_id="p1l_5",
            bbox=[0, 0, 100, 10],
            text="hello",
            region=Region.body,
        )
        assert "l" in line.line_id

    def test_span_id_format(self):
        span = Span(
            span_id="p1s_3",
            text="world",
            bbox=[0, 0, 50, 10],
        )
        assert span.span_id.startswith("p")


class TestHeaderFooterDetection:
    def test_classify_top_region(self):
        line = Line(
            line_id="l1",
            bbox=[0, 0, 100, 30],
            text="Header",
            region=Region.body,
        )
        result = classify_line_region(line, page_height=300)
        assert result == Region.top

    def test_classify_body_region(self):
        line = Line(
            line_id="l2",
            bbox=[0, 100, 100, 115],
            text="Body text",
            region=Region.body,
        )
        result = classify_line_region(line, page_height=300)
        assert result == Region.body

    def test_classify_bottom_region(self):
        line = Line(
            line_id="l3",
            bbox=[0, 280, 100, 295],
            text="Footer",
            region=Region.body,
        )
        result = classify_line_region(line, page_height=300)
        assert result == Region.bottom

    def test_repeated_header_tagged(self):
        page1 = Page(
            page_number=1,
            width=612,
            height=792,
            lines=[
                Line(
                    line_id="p1l_1",
                    bbox=[0, 0, 200, 20],
                    text="Page Header Text",
                    region=Region.body,
                ),
                Line(
                    line_id="p1l_2",
                    bbox=[0, 100, 500, 115],
                    text="Some body text",
                    region=Region.body,
                ),
            ],
        )
        page2 = Page(
            page_number=2,
            width=612,
            height=792,
            lines=[
                Line(
                    line_id="p2l_1",
                    bbox=[0, 0, 200, 20],
                    text="Page Header Text",
                    region=Region.body,
                ),
                Line(
                    line_id="p2l_2",
                    bbox=[0, 100, 500, 115],
                    text="Different body text",
                    region=Region.body,
                ),
            ],
        )
        page3 = Page(
            page_number=3,
            width=612,
            height=792,
            lines=[
                Line(
                    line_id="p3l_1",
                    bbox=[0, 0, 200, 20],
                    text="Page Header Text",
                    region=Region.body,
                ),
                Line(
                    line_id="p3l_2",
                    bbox=[0, 100, 500, 115],
                    text="More body text",
                    region=Region.body,
                ),
            ],
        )
        hf_process([page1, page2, page3])

        for page in [page1, page2, page3]:
            header_line = page.lines[0]
            body_line = page.lines[1]
            assert header_line.is_header_candidate or header_line.is_footer_candidate
            assert not body_line.is_header_candidate
            assert not body_line.is_footer_candidate

    def test_single_line_not_tagged(self):
        page = Page(
            page_number=1,
            width=612,
            height=792,
            lines=[
                Line(
                    line_id="p1l_1",
                    bbox=[0, 0, 200, 20],
                    text="Unique Header",
                    region=Region.body,
                ),
            ],
        )
        hf_process([page])
        assert not page.lines[0].is_header_candidate
        assert not page.lines[0].is_footer_candidate


class TestLineSpanIntegrity:
    def test_all_span_refs_resolve(self):
        spans = [
            Span(span_id="p1s_1", text="A", bbox=[0, 0, 10, 10]),
            Span(span_id="p1s_2", text="B", bbox=[10, 0, 20, 10]),
        ]
        lines = [
            Line(
                line_id="p1l_1",
                text="AB",
                bbox=[0, 0, 20, 10],
                region=Region.body,
                span_ids=["p1s_1", "p1s_2"],
            )
        ]
        page = Page(page_number=1, width=100, height=100, spans=spans, lines=lines)
        span_set = {s.span_id for s in page.spans}
        for line in page.lines:
            for ref in line.span_ids:
                assert ref in span_set, f"Line {line.line_id} references {ref} not in spans"

    def test_dangling_ref_detected(self):
        spans = [Span(span_id="p1s_1", text="A", bbox=[0, 0, 10, 10])]
        lines = [
            Line(
                line_id="p1l_1",
                text="AB",
                bbox=[0, 0, 20, 10],
                region=Region.body,
                span_ids=["p1s_1", "p1s_999"],
            )
        ]
        page = Page(page_number=1, width=100, height=100, spans=spans, lines=lines)
        span_set = {s.span_id for s in page.spans}
        found_dangling = False
        for line in page.lines:
            for ref in line.span_ids:
                if ref not in span_set:
                    found_dangling = True
        assert found_dangling, "Expected a dangling span ref to be detected"


class TestPhysicalDocument:
    def test_empty_document(self):
        doc = PhysicalDocument(
            pipeline_run_id="test_run",
            document_id="test_doc",
            policy_id="test_policy",
            source_pdf_path="/fake/path.pdf",
            page_count=0,
        )
        assert doc.page_count == 0
        assert len(doc.pages) == 0
        assert doc.schema_version == "1.0.0"
        assert doc.parser_version == "1.0.0"

    def test_serialize_roundtrip(self):
        doc = PhysicalDocument(
            pipeline_run_id="test_run",
            document_id="test_doc",
            policy_id="test_policy",
            source_pdf_path="/fake/path.pdf",
            file_hash="sha256:abc123",
            page_count=1,
            pages=[
                Page(
                    page_number=1,
                    width=612,
                    height=792,
                    blocks=[
                        Block(
                            block_id="p1b_1",
                            block_type=BlockType.text,
                            bbox=[50, 100, 562, 120],
                            text="Test content",
                            line_ids=["p1l_1"],
                            reading_order=0,
                        )
                    ],
                    lines=[
                        Line(
                            line_id="p1l_1",
                            bbox=[50, 100, 562, 115],
                            text="Test content",
                            region=Region.body,
                        )
                    ],
                    spans=[
                        Span(
                            span_id="p1s_1",
                            text="Test",
                            bbox=[50, 100, 200, 115],
                            font_size=12,
                        )
                    ],
                )
            ],
        )
        data = json.loads(doc.model_dump_json(exclude_none=True))
        restored = PhysicalDocument(**data)
        assert restored.page_count == 1
        assert restored.pages[0].page_number == 1
        assert restored.pages[0].spans[0].font_size == 12

    def test_document_with_issues(self):
        doc = PhysicalDocument(
            pipeline_run_id="test_run",
            document_id="test_doc",
            policy_id="test_policy",
            source_pdf_path="/fake/path.pdf",
            page_count=0,
            issues=[{"type": "empty_pdf", "page_number": 0, "message": "No pages"}],
        )
        assert len(doc.issues) == 1
        assert doc.issues[0].type == "empty_pdf"


class TestBlockTypeEnum:
    def test_all_block_types(self):
        for bt in BlockType:
            assert bt.value in ("text", "header", "footer", "image_region", "unknown")


class TestRegionEnum:
    def test_all_regions(self):
        for r in Region:
            assert r.value in ("top", "body", "bottom")


class TestIntegrationAgainstGoldPdf:
    def extract_and_check(self, policy_slug):
        metadata_path = _PROJECT_ROOT / "gold_corpus" / "policies" / policy_slug / "metadata.json"
        assert metadata_path.is_file(), f"Missing metadata for {policy_slug}"

        import json

        with open(metadata_path) as f:
            meta = json.load(f)

        pdf_rel = meta["source_pdf_path"]
        policy_data_root = _PROJECT_ROOT.parent / "policy_data"
        pdf_path = policy_data_root / pdf_rel
        assert pdf_path.is_file(), f"PDF not found: {pdf_path}"

        from pdf_parser.layout_extractor import extract_pdf

        doc = extract_pdf(str(pdf_path), meta["policy_id"], "test_integration")

        assert doc.page_count == meta["page_count"], (
            f"Page count: got {doc.page_count}, expected {meta['page_count']}"
        )
        assert doc.file_hash == meta["file_hash"], f"Hash mismatch for {policy_slug}"
        total_spans = sum(len(p.spans) for p in doc.pages)
        assert total_spans > 0, "Zero spans extracted"

        span_ref_total = 0
        span_ref_valid = 0
        for page in doc.pages:
            span_set = {s.span_id for s in page.spans}
            for line in page.lines:
                for ref in line.span_ids:
                    span_ref_total += 1
                    if ref in span_set:
                        span_ref_valid += 1
        integrity_pct = (span_ref_valid / span_ref_total * 100) if span_ref_total else 100.0
        assert integrity_pct == 100.0, (
            f"Span ref integrity: {integrity_pct:.2f}% ({span_ref_valid}/{span_ref_total})"
        )

    def test_star_medi_classic_accident(self):
        self.extract_and_check("star_medi_classic_accident")

    def test_hdfc_arogya_sanjeevani(self):
        self.extract_and_check("hdfc_arogya_sanjeevani")
