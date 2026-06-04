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
        assert matches_numbering("Section A. PREAMBLE")
        assert matches_numbering("Section I: Basic Covers:")

    def test_part_prefix(self):
        assert matches_numbering("PART II OF THE POLICY SCHEDULE")
        assert matches_numbering("PART III OF THE POLICY SCHEDULE")

    def test_roman_numeral(self):
        assert matches_numbering("I.  SCOPE OF COVER")
        assert matches_numbering("IV.  OPTIONAL BENEFITS")
        assert matches_numbering("V.  CUMULATIVE BONUS")

    def test_letter_numbered_heading(self):
        assert matches_numbering("A. Definitions")
        assert matches_numbering("B. Coverage")
        assert matches_numbering("(a) In-patient Hospitalization:")

    def test_serial_number_row_not_letter_heading(self):
        assert not matches_numbering("S. No.")
        assert not matches_numbering("S. No.\tBenefits\tPayment Basis")

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

    def test_letter_numbering_token_and_level(self):
        scorer = HeadingScorer()
        line = {
            "line_id": "l1",
            "text": "A. Definitions",
            "region": "body",
            "is_header_candidate": False,
            "is_footer_candidate": False,
            "span_ids": ["s1"],
        }
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": [line],
            "spans": [
                {
                    "span_id": "s1",
                    "text": "A. Definitions",
                    "font_size": 11.0,
                    "font_name": "Helvetica-Bold",
                    "is_bold": True,
                    "bbox": [0, 0, 120, 15],
                }
            ],
        }
        doc = {"document_id": "test", "policy_id": "test", "pages": [page]}

        cand = scorer.score_document(doc)["candidates"][0]

        assert cand["features"]["matches_numbering"] == 1.0
        assert cand["numbering_token"] == "A."
        assert cand["level_hint"] == 1

    def test_bold_numbered_sentence_case_penalty_reduced(self):
        scorer = HeadingScorer()
        line = {
            "line_id": "l1",
            "text": "6. Claim procedure",
            "region": "body",
            "is_header_candidate": False,
            "is_footer_candidate": False,
            "span_ids": ["s1"],
        }
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": [line],
            "spans": [
                {
                    "span_id": "s1",
                    "text": "6. Claim procedure",
                    "font_size": 11.0,
                    "font_name": "Helvetica-Bold",
                    "is_bold": True,
                    "bbox": [0, 0, 120, 15],
                }
            ],
        }
        doc = {"document_id": "test", "policy_id": "test", "pages": [page]}

        cand = scorer.score_document(doc)["candidates"][0]

        assert cand["features"]["is_sentence_case"] == 1.0
        assert cand["features"]["is_bold"] == 1.0
        assert cand["features"]["matches_numbering"] == 1.0
        assert cand["feature_contributions"]["is_sentence_case"] == -0.1

    def test_zero_heading_fallback_promotes_structural_headings(self):
        scorer = HeadingScorer(threshold=0.9)
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": [
                {
                    "line_id": "l0",
                    "text": "This is ordinary policy body text before the heading section starts.",
                    "bbox": [50, 100, 450, 112],
                    "region": "body",
                    "span_ids": ["s0"],
                },
                {
                    "line_id": "l1",
                    "text": "1. PREAMBLE",
                    "bbox": [50, 150, 170, 162],
                    "region": "body",
                    "span_ids": ["s1"],
                },
                {
                    "line_id": "l2",
                    "text": "This is a long body line used to keep the document median line length stable.",
                    "bbox": [50, 172, 500, 184],
                    "region": "body",
                    "span_ids": ["s2"],
                },
                {
                    "line_id": "l3",
                    "text": "A. DEFINITIONS",
                    "bbox": [50, 225, 180, 237],
                    "region": "body",
                    "span_ids": ["s3"],
                },
                {
                    "line_id": "l4",
                    "text": "This is another long body line after the definitions heading.",
                    "bbox": [50, 247, 500, 259],
                    "region": "body",
                    "span_ids": ["s4"],
                },
                {
                    "line_id": "l5",
                    "text": "PART I: DEFINITIONS",
                    "bbox": [50, 300, 220, 312],
                    "region": "body",
                    "span_ids": ["s5"],
                },
                {
                    "line_id": "l6",
                    "text": "This is a final long body line after the part heading.",
                    "bbox": [50, 322, 500, 334],
                    "region": "body",
                    "span_ids": ["s6"],
                },
            ],
            "spans": [
                {"span_id": f"s{i}", "font_size": 10.0, "is_bold": False}
                for i in range(7)
            ],
        }
        doc = {"document_id": "test", "policy_id": "test", "pages": [page]}

        result = scorer.score_document(doc)
        promoted = [c for c in result["candidates"] if c.get("promotion_source")]

        assert result["fallback_promotions"] >= 3
        assert {c["text"] for c in promoted} >= {
            "1. PREAMBLE",
            "A. DEFINITIONS",
            "PART I: DEFINITIONS",
        }
        for candidate in promoted:
            assert candidate["promotion_source"] == "fallback_zero_heading"
            assert candidate["original_decision"] == "non-heading"
            assert candidate["fallback_evaluation"]["promotion_reasons"]

    def test_zero_heading_fallback_does_not_activate_when_normal_heading_exists(self):
        scorer = HeadingScorer()
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": [
                {
                    "line_id": "l0",
                    "text": "This ordinary body line establishes the document body font.",
                    "bbox": [50, 70, 420, 84],
                    "region": "body",
                    "span_ids": ["s0"],
                },
                {
                    "line_id": "l1",
                    "text": "1. PREAMBLE",
                    "bbox": [50, 100, 180, 114],
                    "region": "body",
                    "span_ids": ["s1"],
                },
                {
                    "line_id": "l2",
                    "text": "A. DEFINITIONS",
                    "bbox": [50, 160, 200, 174],
                    "region": "body",
                    "span_ids": ["s2"],
                },
                {
                    "line_id": "l3",
                    "text": "Another ordinary body line keeps the body font as the mode.",
                    "bbox": [50, 190, 450, 204],
                    "region": "body",
                    "span_ids": ["s3"],
                },
            ],
            "spans": [
                {"span_id": "s0", "font_size": 10.0, "is_bold": False},
                {"span_id": "s1", "font_size": 12.0, "is_bold": True},
                {"span_id": "s2", "font_size": 10.0, "is_bold": False},
                {"span_id": "s3", "font_size": 10.0, "is_bold": False},
            ],
        }
        doc = {"document_id": "test", "policy_id": "test", "pages": [page]}

        result = scorer.score_document(doc)

        assert result["total_headings"] >= 1
        assert result["fallback_promotions"] == 0
        assert not any(c.get("promotion_source") for c in result["candidates"])

    def test_fallback_rejects_common_false_positive_rows(self):
        scorer = HeadingScorer()
        candidates = [
            {"text": "S. No.", "features": {}, "numbering_token": None, "score": 0.45},
            {
                "text": "1. Preamble ............................................",
                "features": {"has_toc_dots": 1.0, "matches_numbering": 1.0},
                "numbering_token": "1.",
                "score": 0.45,
            },
            {
                "text": "Room Rent\t1% of Sum Insured\tPer Day",
                "features": {"matches_numbering": 0.0},
                "numbering_token": None,
                "score": 0.45,
            },
            {
                "text": "43 SPLINT",
                "features": {"matches_numbering": 1.0, "is_all_caps": 1.0},
                "numbering_token": "43",
                "score": 0.45,
            },
        ]

        guard_reasons = [scorer._fallback_guard_reasons(c) for c in candidates]

        assert "serial_number_row" in guard_reasons[0]
        assert "toc_dot_leader" in guard_reasons[1]
        assert "tabular_text" in guard_reasons[2]
        assert "price_or_benefit_value_row" in guard_reasons[2]
        assert "procedure_or_item_list" in guard_reasons[3]

    def test_zero_heading_fallback_promotes_section_alpha_heading(self):
        scorer = HeadingScorer()
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": [
                {
                    "line_id": "l1",
                    "text": "Section A. PREAMBLE",
                    "bbox": [50, 100, 220, 112],
                    "region": "body",
                    "span_ids": ["s1"],
                }
            ],
            "spans": [{"span_id": "s1", "font_size": 10.0, "is_bold": False}],
        }
        doc = {"document_id": "test", "policy_id": "test", "pages": [page]}

        cand = scorer.score_document(doc)["candidates"][0]

        assert cand["features"]["section_token_heading"] == 1.0
        assert cand["promotion_source"] == "fallback_zero_heading"
        assert cand["decision"] == "heading"

    def test_zero_heading_fallback_promotes_parenthesized_letter_heading(self):
        scorer = HeadingScorer()
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": [
                {
                    "line_id": "l1",
                    "text": "(a) In-patient Hospitalization:",
                    "bbox": [50, 100, 260, 112],
                    "region": "body",
                    "span_ids": ["s1"],
                }
            ],
            "spans": [{"span_id": "s1", "font_size": 10.0, "is_bold": False}],
        }
        doc = {"document_id": "test", "policy_id": "test", "pages": [page]}

        cand = scorer.score_document(doc)["candidates"][0]

        assert cand["features"]["parenthesized_letter_heading"] == 1.0
        assert cand["numbering_token"] == "(a"
        assert cand["promotion_source"] == "fallback_zero_heading"
        assert cand["decision"] == "heading"

    def test_zero_heading_fallback_promotes_short_bold_dictionary_heading(self):
        scorer = HeadingScorer()
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": [
                {
                    "line_id": "l0",
                    "text": "Body text before the preamble.",
                    "bbox": [50, 100, 260, 112],
                    "region": "body",
                    "span_ids": ["s0"],
                },
                {
                    "line_id": "l1",
                    "text": "Preamble",
                    "bbox": [50, 150, 130, 162],
                    "region": "body",
                    "span_ids": ["s1"],
                },
            ],
            "spans": [
                {"span_id": "s0", "font_size": 12.0, "is_bold": False},
                {"span_id": "s1", "font_size": 10.0, "is_bold": True},
            ],
        }
        doc = {"document_id": "test", "policy_id": "test", "pages": [page]}

        cand = next(c for c in scorer.score_document(doc)["candidates"] if c["line_id"] == "l1")

        assert cand["features"]["short_dictionary_heading"] == 1.0
        assert cand["promotion_source"] == "fallback_zero_heading"
        assert cand["decision"] == "heading"

    def test_safe_patterns_do_not_promote_known_bad_rows(self):
        scorer = HeadingScorer()
        lines = [
            {"line_id": "l1", "text": "4    80%", "bbox": [50, 100, 120, 112], "region": "body", "span_ids": ["s1"]},
            {"line_id": "l2", "text": "S. Item S. Item", "bbox": [50, 120, 180, 132], "region": "body", "span_ids": ["s2"]},
            {"line_id": "l3", "text": "5 BUDS 39 STEAM INHALER", "bbox": [50, 140, 250, 152], "region": "body", "span_ids": ["s3"]},
            {"line_id": "l4", "text": "1 Month 75%", "bbox": [50, 160, 160, 172], "region": "body", "span_ids": ["s4"]},
            {"line_id": "l5", "text": "POLICY WORDINGS", "bbox": [50, 180, 200, 192], "region": "body", "span_ids": ["s5"]},
        ]
        page = {
            "page_number": 1,
            "width": 612,
            "height": 792,
            "lines": lines,
            "spans": [{"span_id": f"s{i}", "font_size": 10.0, "is_bold": False} for i in range(1, 6)],
        }
        doc = {"document_id": "test", "policy_id": "test", "pages": [page]}

        result = scorer.score_document(doc)

        by_text = {c["text"]: c for c in result["candidates"]}
        assert by_text["4    80%"]["decision"] == "non-heading"
        assert by_text["S. Item S. Item"]["decision"] == "non-heading"
        assert by_text["5 BUDS 39 STEAM INHALER"]["decision"] == "non-heading"
        assert by_text["1 Month 75%"]["decision"] == "non-heading"
        assert by_text["POLICY WORDINGS"]["decision"] == "non-heading"


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
