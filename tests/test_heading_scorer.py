import json
import os
import subprocess
import sys
import pytest

from scripts.eval_heading_scorer import compute_metrics
from structure_parser.heading_patterns import (
    matches_numbering,
    has_toc_dots,
    matches_heading_dict,
    is_all_caps,
    is_sentence_case,
    normalize_heading_text,
)
from structure_parser.heading_scorer import HeadingScorer

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
PHYSICAL_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "interim", "physical"
)
GOLD_CORPUS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "gold_corpus", "policies"
)


def _load_json(path):
    with open(path, "r") as f:
        return json.load(f)


class TestNumberingPatterns:
    def test_decimal_numbered(self):
        assert matches_numbering("1. PREAMBLE")
        assert matches_numbering("2. DEFINITIONS")
        assert matches_numbering("10. General Terms")

    def test_compact_numbered(self):
        assert matches_numbering("1.PREAMBLE:")
        assert matches_numbering("2.DEFINITIONS")
        assert matches_numbering("1.WHAT WE COVER")

    def test_multi_dot_numbered(self):
        assert matches_numbering("2.1 Standard Definitions:")
        assert matches_numbering("3.1. Accident means")

    def test_compact_multi_dot(self):
        assert matches_numbering("3.2OPTIONAL BENEFITS")

    def test_section_prefix(self):
        assert matches_numbering("SECTION A: SPECIFIC INFECTIOUS DISEASES BENEFIT")
        assert matches_numbering("SECTION A.2: RABIES AND TETANUS BENEFIT")

    def test_part_prefix(self):
        assert matches_numbering("PART II OF THE POLICY SCHEDULE")
        assert matches_numbering("PART III OF THE POLICY SCHEDULE")

    def test_roman_numeral(self):
        assert matches_numbering("I.  SCOPE OF COVER")
        assert matches_numbering("IV.  OPTIONAL BENEFITS")
        assert matches_numbering("V.  CUMULATIVE BONUS")

    def test_non_heading_does_not_match(self):
        assert not matches_numbering("This is body text")
        assert not matches_numbering("The policy covers")
        assert not matches_numbering("some random line")


class TestAllCaps:
    def test_all_caps_true(self):
        assert is_all_caps("FAMILY SHIELD")
        assert is_all_caps("EXCLUSIONS")
        assert is_all_caps("1. PREAMBLE")

    def test_all_caps_false(self):
        assert not is_all_caps("Family Shield")
        assert not is_all_caps("1. Preamble")
        assert not is_all_caps("Accident means sudden")

    def test_all_caps_compact(self):
        assert is_all_caps("1.PREAMBLE:")
        assert is_all_caps("2.DEFINITIONS")


class TestSentenceCase:
    def test_sentence_case_definition(self):
        assert is_sentence_case("Accident means sudden, unforeseen and involuntary event")
        assert is_sentence_case("Hospital means any institution established for in-patient care")

    def test_sentence_case_numbered(self):
        assert is_sentence_case("3.1. Accident means a sudden, unforeseen")
        assert is_sentence_case("2.1.1 Accidental / Accident is a sudden")

    def test_not_sentence_case_heading(self):
        assert not is_sentence_case("1. PREAMBLE")
        assert not is_sentence_case("EXCLUSIONS")
        assert not is_sentence_case("FAMILY SHIELD")


class TestHeadingDict:
    def test_dict_match_simple(self):
        assert matches_heading_dict("Preamble")
        assert matches_heading_dict("Definitions")
        assert matches_heading_dict("Exclusions")
        assert matches_heading_dict("Waiting Period")

    def test_dict_match_numbered(self):
        assert matches_heading_dict("1. Preamble")
        assert matches_heading_dict("2. Definitions")
        assert matches_heading_dict("10. Exclusions")

    def test_dict_match_compact(self):
        assert matches_heading_dict("1.PREAMBLE:")
        assert matches_heading_dict("2.DEFINITIONS")

    def test_dict_no_match_body(self):
        assert not matches_heading_dict("The quick brown fox")
        assert not matches_heading_dict("This policy covers")


class TestTOCDots:
    def test_toc_dots_present(self):
        assert has_toc_dots("1. Preamble ............................................")
        assert has_toc_dots("2. Definitions ............................................")

    def test_toc_dots_absent(self):
        assert not has_toc_dots("1. Preamble")
        assert not has_toc_dots("2. Definitions")


class TestNormalizeHeading:
    def test_toc_dots_removed(self):
        assert normalize_heading_text("1. Preamble ....") == "1. preamble"

    def test_whitespace_normalized(self):
        assert normalize_heading_text("2.   Definitions") == "2. definitions"


class TestHeadingScorerUnit:
    def test_empty_document(self):
        scorer = HeadingScorer()
        doc = {"document_id": "test", "policy_id": "test", "page_count": 0, "pages": []}
        result = scorer.score_document(doc)
        assert result["total_lines_scored"] == 0
        assert result["total_headings"] == 0
        assert result["config"]["threshold"] == 0.5

    def test_basic_heading_features(self):
        scorer = HeadingScorer()
        line = {
            "line_id": "l1",
            "text": "1. PREAMBLE",
            "region": "body",
            "is_header_candidate": False,
            "is_footer_candidate": False,
            "span_ids": ["s1", "s2"],
            "font_sizes": [14.0],
            "font_names": ["Helvetica-Bold"],
        }
        spans = [
            {
                "span_id": "s1",
                "text": "1. PREAMBLE",
                "font_size": 14.0,
                "font_name": "Helvetica-Bold",
                "is_bold": True,
                "is_italic": False,
                "bbox": [0, 0, 100, 20],
            },
            {
                "span_id": "s2",
                "text": "body text",
                "font_size": 11.0,
                "font_name": "Helvetica",
                "is_bold": False,
                "is_italic": False,
                "bbox": [0, 30, 200, 50],
            },
        ]
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": [line],
            "spans": spans,
            "blocks": [],
            "issues": [],
            "text_length": 11,
            "rotation": 0,
        }
        doc = {
            "document_id": "test",
            "policy_id": "test",
            "pipeline_run_id": "test",
            "page_count": 1,
            "pages": [page],
        }
        result = scorer.score_document(doc)
        assert result["total_lines_scored"] == 1
        cand = result["candidates"][0]
        assert cand["features"]["is_bold"] == 1.0
        assert cand["features"]["is_all_caps"] == 1.0
        assert cand["features"]["matches_numbering"] == 1.0
        assert cand["features"]["matches_heading_dict"] == 1.0

    def test_body_text_rejected(self):
        scorer = HeadingScorer()
        line = {
            "line_id": "l1",
            "text": "This policy covers hospitalization expenses for the insured person",
            "region": "body",
            "is_header_candidate": False,
            "is_footer_candidate": False,
            "span_ids": ["s1"],
            "font_sizes": [11.0],
            "font_names": ["Helvetica"],
        }
        spans = [
            {
                "span_id": "s1",
                "text": "This policy covers hospitalization expenses",
                "font_size": 11.0,
                "font_name": "Helvetica",
                "is_bold": False,
                "is_italic": False,
                "bbox": [0, 0, 300, 15],
            }
        ]
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": [line],
            "spans": spans,
            "blocks": [],
            "issues": [],
            "text_length": 55,
            "rotation": 0,
        }
        doc = {
            "document_id": "test",
            "policy_id": "test",
            "pipeline_run_id": "test",
            "page_count": 1,
            "pages": [page],
        }
        result = scorer.score_document(doc)
        assert result["total_lines_scored"] == 1
        cand = result["candidates"][0]
        assert cand["decision"] == "non-heading"

    def test_definition_entry_rejected(self):
        scorer = HeadingScorer()
        line = {
            "line_id": "l1",
            "text": "3.1. Accident means a sudden, unforeseen and involuntary event caused by external",
            "region": "body",
            "is_header_candidate": False,
            "is_footer_candidate": False,
            "span_ids": ["s1"],
            "font_sizes": [11.04],
            "font_names": ["Calibri"],
        }
        spans = [
            {
                "span_id": "s1",
                "text": "3.1. Accident means a sudden, unforeseen",
                "font_size": 11.04,
                "font_name": "Calibri",
                "is_bold": False,
                "is_italic": False,
                "bbox": [0, 0, 300, 15],
            }
        ]
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": [line],
            "spans": spans,
            "blocks": [],
            "issues": [],
            "text_length": 80,
            "rotation": 0,
        }
        doc = {
            "document_id": "test",
            "policy_id": "test",
            "pipeline_run_id": "test",
            "page_count": 1,
            "pages": [page],
        }
        result = scorer.score_document(doc)
        assert result["total_lines_scored"] == 1
        cand = result["candidates"][0]
        assert cand["decision"] == "non-heading"

    def test_spacing_feature_present_for_gap_before_heading(self):
        scorer = HeadingScorer()
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": [
                {
                    "line_id": "l1",
                    "text": "Body text before heading",
                    "bbox": [50, 100, 300, 112],
                    "region": "body",
                    "span_ids": ["s1"],
                },
                {
                    "line_id": "l2",
                    "text": "4. COVERAGE",
                    "bbox": [50, 150, 180, 164],
                    "region": "body",
                    "span_ids": ["s2"],
                },
                {
                    "line_id": "l3",
                    "text": "Body after heading",
                    "bbox": [50, 174, 260, 186],
                    "region": "body",
                    "span_ids": ["s3"],
                },
            ],
            "spans": [
                {"span_id": "s1", "font_size": 11.0, "is_bold": False},
                {"span_id": "s2", "font_size": 12.0, "is_bold": True},
                {"span_id": "s3", "font_size": 11.0, "is_bold": False},
            ],
        }
        doc = {"document_id": "test", "policy_id": "test", "pages": [page]}

        result = scorer.score_document(doc)
        heading = next(c for c in result["candidates"] if c["line_id"] == "l2")

        assert heading["features"]["spacing_signal"] == 1.0
        assert heading["feature_contributions"]["spacing_signal"] == 0.1
        assert heading["bbox"] == [50, 150, 180, 164]
        assert heading["span_ids"] == ["s2"]
        assert heading["normalized_text"] == "4. coverage"
        assert heading["numbering_token"] == "4."
        assert heading["level_hint"] == 1


class TestHeadingEvalMatching:
    def test_one_candidate_cannot_match_many_labels(self):
        candidates = [
            {
                "decision": "heading",
                "text": "2. Definitions",
                "page_number": 1,
                "line_id": "p1l_1",
                "score": 0.9,
            }
        ]
        labels = [
            {
                "expected_text": "2. Definitions",
                "page": 1,
                "line_id": "p1l_1",
                "is_visual_heading": True,
            },
            {
                "expected_text": "3. Exclusions",
                "page": 1,
                "line_id": "p1l_2",
                "is_visual_heading": True,
            },
        ]

        metrics = compute_metrics(candidates, labels)

        assert metrics["true_positives"] == 1
        assert metrics["false_negatives"] == 1
        assert metrics["count_invariant_ok"] is True

    def test_short_generic_heading_does_not_overmatch_long_clause(self):
        candidates = [
            {
                "decision": "heading",
                "text": "2. Definitions",
                "page_number": 1,
                "line_id": "p1l_1",
                "score": 0.9,
            }
        ]
        labels = [
            {
                "expected_text": "2. Definitions of words and expressions that apply to this Policy",
                "page": 1,
                "line_id": "p1l_99",
                "is_visual_heading": True,
            }
        ]

        metrics = compute_metrics(candidates, labels)

        assert metrics["true_positives"] == 0
        assert metrics["false_positives"] == 1
        assert metrics["false_negatives"] == 1


class TestHeadingScorerCli:
    def test_missing_policy_exits_nonzero(self, tmp_path):
        env = {
            **os.environ,
            "PYTHONPATH": os.path.dirname(os.path.dirname(__file__)),
        }
        result = subprocess.run(
            [
                sys.executable,
                "scripts/run_heading_scorer.py",
                "--physical-root",
                PHYSICAL_ROOT,
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
        assert "missing_physical_output" in (tmp_path / "heading_run_summary.json").read_text()


@pytest.mark.slow
class TestGoldIntegration:
    GOLD_SLUGS = ["star_medi_classic_accident", "hdfc_arogya_sanjeevani"]

    def _physical_path(self, slug):
        return os.path.join(PHYSICAL_ROOT, slug, "document_physical.json")

    def test_star_heading_detection(self):
        slug = "star_medi_classic_accident"
        path = self._physical_path(slug)
        if not os.path.isfile(path):
            pytest.skip(f"Physical output not found: {path}")

        doc = _load_json(path)
        scorer = HeadingScorer(threshold=0.5)
        result = scorer.score_document(doc)

        assert result["total_headings"] >= 8
        texts = {c["text"].strip() for c in result["candidates"] if c["decision"] == "heading"}
        assert "3. EXCLUSIONS" in texts
        assert "2. DEFINITIONS" in texts

    def test_hdfc_heading_detection(self):
        slug = "hdfc_arogya_sanjeevani"
        path = self._physical_path(slug)
        if not os.path.isfile(path):
            pytest.skip(f"Physical output not found: {path}")

        doc = _load_json(path)
        scorer = HeadingScorer(threshold=0.5)
        result = scorer.score_document(doc)

        assert result["total_headings"] >= 10
        texts = {c["text"].strip() for c in result["candidates"] if c["decision"] == "heading"}
        assert "1. Preamble" in texts
        assert "4. Coverage" in texts

    def test_icici_heading_detection(self):
        slug = "icici_family_shield"
        path = self._physical_path(slug)
        if not os.path.isfile(path):
            pytest.skip(f"Physical output not found: {path}")

        doc = _load_json(path)
        scorer = HeadingScorer(threshold=0.5)
        result = scorer.score_document(doc)

        assert result["total_headings"] >= 8
        texts = {c["text"].strip() for c in result["candidates"] if c["decision"] == "heading"}
        assert "FAMILY SHIELD" in texts
        assert "2.  DEFINITIONS" in texts or "2. DEFINITIONS" in texts
