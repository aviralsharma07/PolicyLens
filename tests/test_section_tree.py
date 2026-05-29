import json
import os
import sys
import pytest

from structure_parser.section_tree import (
    SectionTreeBuilder,
    _infer_level,
    _is_body_numbered_line,
    _is_toc_or_cis_line,
    _normalize_title,
    _compact_text,
    _extract_number_from_heading,
    parse_numbered_prefix,
)
from structure_parser.clause_segmenter import (
    ClauseSegmenter,
    _is_toc_dot_leader,
)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
PHYSICAL_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "interim", "physical"
)
LOGICAL_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "interim", "logical"
)
GOLD_CORPUS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "gold_corpus", "policies"
)
OUTPUT_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "interim", "logical")


def _make_page(page_num, lines, spans=None):
    return {
        "page_number": page_num,
        "width": 612,
        "height": 792,
        "lines": lines,
        "spans": spans or [],
        "blocks": [],
        "issues": [],
    }


def _make_line(
    line_id, text, bbox=None, region="body", is_header=False, is_footer=False, span_ids=None
):
    return {
        "line_id": line_id,
        "text": text,
        "bbox": bbox or [50, 100, 300, 115],
        "region": region,
        "is_header_candidate": is_header,
        "is_footer_candidate": is_footer,
        "span_ids": span_ids or [],
        "font_sizes": [11.0],
        "font_names": ["Helvetica"],
    }


def _make_heading(
    line_id, text, page_num, bbox, decision="heading", numbering_token=None, level_hint=1, score=0.8
):
    return {
        "candidate_id": f"cand_{line_id}",
        "line_id": line_id,
        "text": text,
        "page_number": page_num,
        "bbox": bbox,
        "span_ids": [],
        "normalized_text": _normalize_title(text).lower(),
        "numbering_token": numbering_token,
        "level_hint": level_hint,
        "score": score,
        "features": {},
        "feature_contributions": {},
        "decision": decision,
        "threshold_applied": 0.5,
    }


class TestLevelInference:
    def test_level_1_numbered(self):
        assert _infer_level("1.", 1) == 1
        assert _infer_level("1", 1) == 1
        assert _infer_level("10.", 1) == 1
        assert _infer_level("I.", 1) == 1
        assert _infer_level("IV", 1) == 1

    def test_level_1_section_part(self):
        assert _infer_level("SECTION A", 1) == 1
        assert _infer_level("PART 1", 1) == 1

    def test_level_1_zero_suffix(self):
        assert _infer_level("1.0", 2) == 1

    def test_level_2_multi_dot(self):
        assert _infer_level("1.1", 2) == 2
        assert _infer_level("3.14", 2) == 2

    def test_level_3_triple_dot(self):
        assert _infer_level("1.1.1", 3) == 3

    def test_section_a1_level_2(self):
        assert _infer_level("SECTION A.1", 1) == 2

    def test_null_numbering(self):
        assert _infer_level(None, 1) == 1
        assert _infer_level(None, 2) == 2

    def test_level_clamped(self):
        assert _infer_level("1.2.3.4.5", 5) == 4


class TestNormalizeHelpers:
    def test_removes_toc_dots(self):
        result = _normalize_title("1. Preamble .................. 2")
        assert "Preamble" in result
        assert "..." not in result

    def test_whitespace_normalized(self):
        assert _normalize_title("2.   Definitions") == "2. Definitions"

    def test_trailing_dot_removed(self):
        result = _normalize_title("1. Preamble.")
        assert result == "1. Preamble" or result == "1. Preamble"

    def test_compact_text(self):
        assert _compact_text("1. Preamble") == "1preamble"

    def test_toc_line(self):
        assert _is_toc_or_cis_line("1. Preamble ........................... 2") is True
        assert _is_toc_or_cis_line("This is normal text") is False
        assert _is_toc_or_cis_line("1. Preamble") is False

    def test_body_numbered_line(self):
        assert _is_body_numbered_line("3.1. Accident means a sudden") is True
        assert _is_body_numbered_line("3.1 Accident means") is True
        assert _is_body_numbered_line("2.1.1Accident means") is True
        assert _is_body_numbered_line("5.10RENEWAL CLAUSE") is True
        assert _is_body_numbered_line("I.A malignant tumour") is True
        assert _is_body_numbered_line("This is body text") is False

    def test_parse_compact_numbered_prefix(self):
        parsed = parse_numbered_prefix("2.1.1Accidental / Accident is sudden")
        assert parsed == {
            "number": "2.1.1",
            "title": "Accidental / Accident is sudden",
            "kind": "arabic",
        }

    def test_parse_roman_compact_numbered_prefix(self):
        parsed = parse_numbered_prefix("II.The following are excluded")
        assert parsed == {
            "number": "II",
            "title": "The following are excluded",
            "kind": "roman",
        }

    def test_extract_number(self):
        assert _extract_number_from_heading({"numbering_token": "1."}) == "1"
        assert _extract_number_from_heading({"numbering_token": "1.1"}) == "1.1"
        assert _extract_number_from_heading({"text": "SECTION A: Coverage"}) is None


class TestTOCDotLeader:
    def test_toc_dots_detected(self):
        assert _is_toc_dot_leader("1. Preamble ........................")
        assert _is_toc_dot_leader("2. Definitions ....................... 2")

    def test_normal_text_not_toc(self):
        assert not _is_toc_dot_leader("1. Preamble")
        assert not _is_toc_dot_leader("This is body text")


class TestSectionTreeEmpty:
    def test_empty_document(self):
        pages = [_make_page(1, [])]
        builder = SectionTreeBuilder(
            heading_candidates=[],
            physical_pages=pages,
            policy_id="empty",
        )
        result = builder.build()
        sections = result["sections"]
        assert len(sections) == 1  # root only
        assert sections[0]["level"] == 0
        assert sections[0]["section_id"] is not None


class TestSectionTreeSingle:
    def test_single_heading(self):
        lines = [
            _make_line("p1l_1", "1. PREAMBLE", bbox=[50, 100, 300, 115]),
            _make_line("p1l_2", "This is the preamble text", bbox=[50, 120, 300, 135]),
        ]
        pages = [_make_page(1, lines)]
        headings = [
            _make_heading("p1l_1", "1. PREAMBLE", 1, [50, 100, 300, 115], numbering_token="1."),
        ]
        builder = SectionTreeBuilder(
            heading_candidates=headings,
            physical_pages=pages,
            policy_id="single",
        )
        result = builder.build()
        sections = result["sections"]
        non_root = [s for s in sections if s["level"] > 0]
        assert len(non_root) == 1
        assert non_root[0]["number"] == "1"
        assert non_root[0]["heading_type"] == "visual"


class TestSectionTreeHierarchy:
    def test_one_two_level(self):
        lines = [
            _make_line("p1l_1", "1. Definitions", bbox=[50, 100, 300, 115]),
            _make_line("p1l_2", "3.1. Accident means", bbox=[50, 130, 300, 145]),
            _make_line("p1l_3", "3.2. Age means", bbox=[50, 160, 300, 175]),
            _make_line("p1l_4", "2. Coverage", bbox=[50, 200, 300, 215]),
        ]
        pages = [_make_page(1, lines)]
        headings = [
            _make_heading("p1l_1", "1. Definitions", 1, [50, 100, 300, 115], numbering_token="1."),
            _make_heading("p1l_4", "2. Coverage", 1, [50, 200, 300, 215], numbering_token="2."),
        ]
        builder = SectionTreeBuilder(
            heading_candidates=headings,
            physical_pages=pages,
            policy_id="hier",
        )
        result = builder.build()
        sections = result["sections"]
        visual = [s for s in sections if s["heading_type"] == "visual"]
        assert len(visual) == 2

        defs_sec = visual[0]
        cov_sec = visual[1]
        assert defs_sec["number"] == "1"
        assert cov_sec["number"] == "2"
        assert defs_sec["parent_id"] == cov_sec["parent_id"]


class TestSectionTreeSynthetic:
    def test_synthetic_detected(self):
        lines = [
            _make_line("p1l_1", "3. Definitions", bbox=[50, 100, 300, 115]),
            _make_line(
                "p1l_2", "3.1. Accident means a sudden unforeseen event", bbox=[50, 130, 600, 145]
            ),
            _make_line(
                "p1l_3", "3.2. Age means age of the insured person", bbox=[50, 160, 600, 175]
            ),
            _make_line(
                "p1l_4", "3.3. Any One Illness means continuous period", bbox=[50, 190, 600, 205]
            ),
            _make_line("p1l_5", "2. Coverage", bbox=[50, 240, 300, 255]),
        ]
        pages = [_make_page(1, lines)]
        headings = [
            _make_heading("p1l_1", "3. Definitions", 1, [50, 100, 300, 115], numbering_token="3."),
            _make_heading("p1l_5", "2. Coverage", 1, [50, 240, 300, 255], numbering_token="2."),
        ]
        builder = SectionTreeBuilder(
            heading_candidates=headings,
            physical_pages=pages,
            policy_id="synth",
        )
        result = builder.build()
        sections = result["sections"]
        synthetic = [s for s in sections if s["heading_type"] == "synthetic_body_numbered"]
        assert len(synthetic) >= 2
        assert synthetic[0]["number"] == "3.1"
        assert synthetic[1]["number"] == "3.2"

    def test_compact_synthetic_detected_iteratively(self):
        lines = [
            _make_line("p1l_1", "2.DEFINITIONS", bbox=[50, 100, 300, 115]),
            _make_line("p1l_2", "2.1CRITICAL ILLNESSES means the following", bbox=[50, 130, 600, 145]),
            _make_line("p1l_3", "2.1.1CANCER means", bbox=[50, 160, 600, 175]),
            _make_line("p1l_4", "I.A malignant tumour", bbox=[50, 190, 600, 205]),
            _make_line("p1l_5", "II.The following are excluded", bbox=[50, 220, 600, 235]),
            _make_line("p1l_6", "2.2AGE means completed age", bbox=[50, 250, 600, 265]),
        ]
        pages = [_make_page(1, lines)]
        headings = [
            _make_heading("p1l_1", "2.DEFINITIONS", 1, [50, 100, 300, 115], numbering_token="2."),
        ]
        builder = SectionTreeBuilder(headings, pages, policy_id="compact")
        result = builder.build()
        synthetic = [s for s in result["sections"] if s["heading_type"] == "synthetic_body_numbered"]
        numbers = {s["number"] for s in synthetic}
        assert {"2.1", "2.1.1", "I", "II", "2.2"}.issubset(numbers)

    def test_numbered_list_items_do_not_become_sections_under_numbered_parent(self):
        lines = [
            _make_line("p1l_1", "3.1.15Benefit : Health Services", bbox=[50, 100, 300, 115]),
            _make_line("p1l_2", "1. Complete Haemogram Test", bbox=[50, 130, 600, 145]),
            _make_line("p1l_3", "2. Blood Sugar", bbox=[50, 160, 600, 175]),
            _make_line("p1l_4", "3. Lipid profile", bbox=[50, 190, 600, 205]),
        ]
        pages = [_make_page(1, lines)]
        headings = [
            _make_heading(
                "p1l_1",
                "3.1.15Benefit : Health Services",
                1,
                [50, 100, 300, 115],
                numbering_token="3.1.15",
            ),
        ]
        builder = SectionTreeBuilder(headings, pages, policy_id="no_list")
        result = builder.build()
        synthetic = [s for s in result["sections"] if s["heading_type"] == "synthetic_body_numbered"]
        assert synthetic == []

    def test_section_ids_are_deterministic(self):
        lines = [
            _make_line("p1l_1", "1. Preamble", bbox=[50, 100, 300, 115]),
            _make_line("p1l_2", "Body text", bbox=[50, 130, 300, 145]),
        ]
        pages = [_make_page(1, lines)]
        headings = [_make_heading("p1l_1", "1. Preamble", 1, [50, 100, 300, 115], numbering_token="1.")]
        first = SectionTreeBuilder(headings, pages, policy_id="stable").build()["sections"]
        second = SectionTreeBuilder(headings, pages, policy_id="stable").build()["sections"]
        assert [s["section_id"] for s in first] == [s["section_id"] for s in second]


class TestSectionTreeLevelHint:
    def test_unnumbered_heading_uses_level_hint(self):
        lines = [
            _make_line("p1l_1", "FAMILY SHIELD", bbox=[50, 100, 300, 115]),
            _make_line("p1l_2", "Some body text", bbox=[50, 130, 300, 145]),
        ]
        pages = [_make_page(1, lines)]
        headings = [
            _make_heading(
                "p1l_1", "FAMILY SHIELD", 1, [50, 100, 300, 115], numbering_token=None, level_hint=1
            ),
        ]
        builder = SectionTreeBuilder(
            heading_candidates=headings,
            physical_pages=pages,
            policy_id="hint",
        )
        result = builder.build()
        sections = result["sections"]
        non_root = [s for s in sections if s["level"] > 0]
        assert len(non_root) == 1
        assert non_root[0]["level"] == 1


class TestSectionTreeMultiPage:
    def test_multi_page_content(self):
        p1_lines = [
            _make_line("p1l_1", "1. Preamble", bbox=[50, 100, 300, 115]),
            _make_line("p1l_2", "Preamble text on page 1", bbox=[50, 130, 300, 145]),
        ]
        p2_lines = [
            _make_line("p2l_1", "More preamble on page 2", bbox=[50, 50, 300, 65]),
            _make_line("p2l_2", "2. Operative Clause", bbox=[50, 150, 300, 165]),
        ]
        pages = [
            _make_page(1, p1_lines),
            _make_page(2, p2_lines),
        ]
        headings = [
            _make_heading("p1l_1", "1. Preamble", 1, [50, 100, 300, 115], numbering_token="1."),
            _make_heading(
                "p2l_2", "2. Operative Clause", 2, [50, 150, 300, 165], numbering_token="2."
            ),
        ]
        builder = SectionTreeBuilder(
            heading_candidates=headings,
            physical_pages=pages,
            policy_id="multi",
        )
        result = builder.build()
        sections = result["sections"]
        preamble = next(s for s in sections if s.get("number") == "1")
        assert preamble["page_start"] == 1
        assert preamble["page_end"] == 2


class TestSectionTreeNumberingOneDotZero:
    def test_1dot0_is_level_1(self):
        lines = [
            _make_line("p1l_1", "1.0 Preamble", bbox=[50, 100, 300, 115]),
            _make_line("p1l_2", "Body text", bbox=[50, 130, 300, 145]),
        ]
        pages = [_make_page(1, lines)]
        headings = [
            _make_heading("p1l_1", "1.0 Preamble", 1, [50, 100, 300, 115], numbering_token="1.0"),
        ]
        builder = SectionTreeBuilder(
            heading_candidates=headings,
            physical_pages=pages,
            policy_id="onezero",
        )
        result = builder.build()
        sections = result["sections"]
        non_root = [s for s in sections if s["level"] > 0]
        assert non_root[0]["level"] == 1
        assert non_root[0]["heading_type"] == "visual"


class TestClauseSegmenter:
    def _build_clause_segmenter(self, pages):
        line_index = {}
        line_to_idx = {}
        idx = 0
        for page in pages:
            for line in page.get("lines", []):
                lid = line.get("line_id", "")
                if lid:
                    line_index[lid] = line
                    line_to_idx[lid] = idx
                    idx += 1
        return ClauseSegmenter(
            physical_pages=pages,
            line_index=line_index,
            line_to_idx=line_to_idx,
        )

    def test_section_with_two_numbered_clauses(self):
        lines = [
            _make_line("p1l_1", "4. Coverage", bbox=[50, 100, 300, 115]),
            _make_line("p1l_2", "4.1 Hospitalization expenses", bbox=[50, 130, 400, 145]),
            _make_line("p1l_3", "4.2 Day care procedures", bbox=[50, 160, 400, 175]),
        ]
        pages = [_make_page(1, lines)]
        segmenter = self._build_clause_segmenter(pages)
        section = {
            "section_id": "sec_1",
            "number": "4",
            "heading_type": "visual",
            "page_start": 1,
            "page_end": 1,
            "title": "4. Coverage",
            "text": "4.1 Hospitalization expenses 4.2 Day care procedures",
        }
        clauses = segmenter.segment_section(section, ["p1l_2", "p1l_3"], "sec_1", 0)
        assert len(clauses) == 2
        assert clauses[0]["clause_number"] == "4.1"
        assert clauses[1]["clause_number"] == "4.2"

    def test_default_clause_when_empty_body(self):
        pages = [_make_page(1, [])]
        segmenter = self._build_clause_segmenter(pages)
        section = {
            "section_id": "sec_1",
            "number": "1",
            "heading_type": "visual",
            "page_start": 1,
            "page_end": 1,
            "title": "1. Preamble",
            "text": "",
        }
        clauses = segmenter.segment_section(section, [], "sec_1", 0)
        assert len(clauses) == 1  # default clause

    def test_compact_numbered_clause_and_no_truncation(self):
        long_tail = " ".join(["fulltext"] * 120)
        lines = [
            _make_line("p1l_1", f"2.1.1Accident means {long_tail}", bbox=[50, 100, 600, 115]),
        ]
        pages = [_make_page(1, lines)]
        segmenter = self._build_clause_segmenter(pages)
        section = {
            "section_id": "sec_1",
            "number": "2.1",
            "heading_type": "synthetic_body_numbered",
            "page_start": 1,
            "page_end": 1,
            "title": "2.1 Definitions",
            "text": "",
        }
        clauses = segmenter.segment_section(section, ["p1l_1"], "sec_1", 0)
        assert clauses[0]["clause_number"] == "2.1.1"
        assert "..." not in clauses[0]["text"]
        assert len(clauses[0]["text"]) > 500


class TestSectionTreeEval:
    def test_low_recall_cannot_pass_tree_accuracy(self):
        from scripts.eval_section_tree import compute_metrics

        predicted = [
            {"section_id": "p1", "level": 1, "number": "1", "title": "1. Preamble", "page_start": 1},
        ]
        gold = [
            {"section_id": "g1", "level": 1, "section_number": "1", "title": "Preamble", "page_start": 1},
            {"section_id": "g2", "level": 1, "section_number": "2", "title": "Definitions", "page_start": 1},
        ]
        metrics = compute_metrics(predicted, [], gold, [])
        assert metrics["section_recall"] == 50.0
        assert metrics["section_tree_accuracy"] == 50.0


class TestCLI:
    def test_missing_policy_exits_nonzero(self, tmp_path):
        import subprocess

        env = {
            **os.environ,
            "PYTHONPATH": os.path.dirname(os.path.dirname(__file__)),
        }
        result = subprocess.run(
            [
                sys.executable,
                "scripts/run_section_tree.py",
                "--physical-root",
                PHYSICAL_ROOT,
                "--logical-root",
                LOGICAL_ROOT,
                "--output-root",
                str(tmp_path),
                "--policy",
                "missing_policy_slug",
            ],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode != 0
        summary = json.loads((tmp_path / "section_tree_run_summary.json").read_text())
        errors = sum(1 for r in summary["results"] if r["status"] != "ok")
        assert errors > 0


@pytest.mark.slow
class TestGoldIntegration:
    GOLD_SLUGS = ["star_medi_classic_accident", "hdfc_arogya_sanjeevani", "icici_family_shield"]

    def _physical_path(self, slug):
        return os.path.join(PHYSICAL_ROOT, slug, "document_physical.json")

    def _candidates_path(self, slug):
        return os.path.join(LOGICAL_ROOT, slug, "heading_candidates.json")

    def _load_json(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def _build_line_index(self, pages):
        index = {}
        for page in pages:
            for line in page.get("lines", []):
                lid = line.get("line_id", "")
                if lid:
                    index[lid] = line
        return index

    def _build_line_to_idx(self, pages):
        mapping = {}
        idx = 0
        for page in pages:
            for line in page.get("lines", []):
                lid = line.get("line_id", "")
                if lid:
                    mapping[lid] = idx
                    idx += 1
        return mapping

    def test_hdfc_section_tree(self):
        slug = "hdfc_arogya_sanjeevani"
        phys_path = self._physical_path(slug)
        cand_path = self._candidates_path(slug)
        if not os.path.isfile(phys_path):
            pytest.skip(f"Physical output not found: {phys_path}")
        if not os.path.isfile(cand_path):
            pytest.skip(f"Candidates not found: {cand_path}")

        doc = self._load_json(phys_path)
        cand_data = self._load_json(cand_path)

        builder = SectionTreeBuilder(
            heading_candidates=cand_data.get("candidates", []),
            physical_pages=doc.get("pages", []),
            policy_id=slug,
        )
        result = builder.build()
        sections = result["sections"]

        visual = [s for s in sections if s["heading_type"] == "visual"]
        assert len(visual) >= 10
        synthetic = [s for s in sections if s["heading_type"] == "synthetic_body_numbered"]
        assert len(synthetic) >= 40

        titles = {s.get("title") for s in visual}
        assert any("Preamble" in t for t in titles)
        assert any("Definitions" in t for t in titles)
        assert any("Coverage" in t for t in titles)

    def test_star_section_tree(self):
        slug = "star_medi_classic_accident"
        phys_path = self._physical_path(slug)
        cand_path = self._candidates_path(slug)
        if not os.path.isfile(phys_path):
            pytest.skip(f"Physical output not found: {phys_path}")
        if not os.path.isfile(cand_path):
            pytest.skip(f"Candidates not found: {cand_path}")

        doc = self._load_json(phys_path)
        cand_data = self._load_json(cand_path)

        builder = SectionTreeBuilder(
            heading_candidates=cand_data.get("candidates", []),
            physical_pages=doc.get("pages", []),
            policy_id=slug,
        )
        result = builder.build()
        sections = result["sections"]

        visual = [s for s in sections if s["heading_type"] == "visual"]
        assert len(visual) >= 5
        titles_upper = {s.get("title", "").upper() for s in visual}
        assert any("EXCLUSIONS" in t for t in titles_upper)
        assert any("DEFINITIONS" in t for t in titles_upper)

    def test_icici_section_tree(self):
        slug = "icici_family_shield"
        phys_path = self._physical_path(slug)
        cand_path = self._candidates_path(slug)
        if not os.path.isfile(phys_path):
            pytest.skip(f"Physical output not found: {phys_path}")
        if not os.path.isfile(cand_path):
            pytest.skip(f"Candidates not found: {cand_path}")

        doc = self._load_json(phys_path)
        cand_data = self._load_json(cand_path)

        builder = SectionTreeBuilder(
            heading_candidates=cand_data.get("candidates", []),
            physical_pages=doc.get("pages", []),
            policy_id=slug,
        )
        result = builder.build()
        sections = result["sections"]

        visual = [s for s in sections if s["heading_type"] == "visual"]
        assert len(visual) >= 5
        titles = {s.get("title") for s in visual}
        assert any("DEFINITIONS" in t.upper() for t in titles)
