import pytest

from extractors.wave2_utils import (
    clean_lower,
    coverage_value,
    evidence_window,
    find_duration_near_terms,
    has_any,
    near_terms,
    reject_if_context,
    schedule_dependent_value,
)


def test_clean_lower_normalizes_ligatures_and_spacing():
    result = clean_lower("ﬁrst  ﬂoor  policy")
    assert result == "first floor policy"


def test_clean_lower_handles_multiple_ligatures():
    result = clean_lower("ﬁ  ﬀ  ﬂ  ﬃ  ﬄ")
    assert result == "fi ff fl ffi ffl"


def test_has_any_returns_true_when_term_present():
    assert has_any("claim intimation period", ["intimation", "notification"])


def test_has_any_returns_false_when_no_term_present():
    assert not has_any("grace period", ["intimation", "notification"])


def test_evidence_window_returns_compact_text_around_span():
    text = "The insured shall intimate the company within 48 hours of hospitalization."
    span_start = text.find("48 hours")
    span_end = span_start + len("48 hours")
    result = evidence_window(text, span_start, span_end, radius=20)
    assert "48 hours" in result
    assert len(result) < len(text)


def test_evidence_window_center_of_text():
    text = "The company shall settle the claim within 30 days from receipt of documents."
    span_start = text.find("30 days")
    span_end = span_start + len("30 days")
    result = evidence_window(text, span_start, span_end, radius=15)
    assert "30 days" in result


def test_evidence_window_handles_start_near_beginning():
    text = "48 hours from the date of intimation, the insured shall notify."
    span_start = text.find("48 hours")
    span_end = span_start + len("48 hours")
    result = evidence_window(text, span_start, span_end, radius=200)
    assert "48 hours" in result


def test_near_terms_detects_signal_terms_near_span():
    text = "The insured shall intimate the company within 48 hours of hospitalization."
    span = (text.find("48 hours"), text.find("48 hours") + len("48 hours"))
    assert near_terms(text, span[0], span[1], ["intimate", "intimation", "hospitalization"])


def test_near_terms_ignores_far_terms():
    text = "The insured shall intimate. Far away. Far away. 48 hours of hospitalization."
    span = (text.find("48 hours"), text.find("48 hours") + len("48 hours"))
    assert not near_terms(text, span[0], span[1], ["grace period"], radius=30)


def test_near_terms_returns_false_when_term_missing():
    text = "A grace period of 30 days is available."
    span = (text.find("30 days"), text.find("30 days") + len("30 days"))
    assert not near_terms(text, span[0], span[1], ["intimation"])


def test_reject_if_context_returns_reason_when_reject_term_nearby():
    text = "The company shall pay the claim within 30 days. This is not a waiting period."
    span = (text.find("30 days"), text.find("30 days") + len("30 days"))
    reason = reject_if_context(text, span[0], span[1], ["waiting period"])
    assert reason == "context_contains_waiting_period"


def test_reject_if_context_returns_none_when_no_reject_term():
    text = "The company shall pay the claim within 30 days."
    span = (text.find("30 days"), text.find("30 days") + len("30 days"))
    assert reject_if_context(text, span[0], span[1], ["waiting period"]) is None


def test_find_duration_near_terms_finds_intimation_related_durations():
    text = (
        "The insured shall intimate the company within 30 days of "
        "hospitalization. The grace period for renewal is another period."
    )
    results = find_duration_near_terms(
        text,
        terms=["intimate", "intimation", "hospitalization"],
        allowed_units={"days", "months", "years"},
    )
    assert len(results) >= 1
    assert any(r["unit"] == "days" for r in results)


def test_find_duration_near_terms_excludes_unrelated_durations():
    text = (
        "The waiting period for pre-existing diseases is 24 months. This is a "
        "completely separate section with different terms and conditions. "
        "Claims under this policy shall be governed by the policy provisions. "
        "The insured shall intimate within 30 days."
    )
    results = find_duration_near_terms(
        text,
        terms=["intimate", "intimation"],
        allowed_units={"days", "months", "years"},
        radius=30,
    )
    assert all(r["unit"] == "days" for r in results)


def test_find_duration_near_terms_respects_allowed_units():
    text = "The insured shall intimate within 48 hours and within 30 days."
    results = find_duration_near_terms(
        text,
        terms=["intimate", "intimation"],
        allowed_units={"days"},
    )
    assert all(r["unit"] == "days" for r in results)


def test_schedule_dependent_value_has_correct_shape():
    result = schedule_dependent_value("per_policy_schedule")
    assert result == {"schedule_dependent": True, "basis": "per_policy_schedule"}


def test_coverage_value_covered():
    result = coverage_value("covered")
    assert result == {"coverage_status": "covered"}


def test_coverage_value_conditional():
    result = coverage_value("conditional")
    assert result == {"coverage_status": "conditional"}


def test_coverage_value_with_extra_fields():
    result = coverage_value("covered", limit={"percentage": 10})
    assert result["coverage_status"] == "covered"
    assert result["limit"] == {"percentage": 10}


def test_coverage_value_raises_for_unsupported_status():
    with pytest.raises(ValueError, match="Unsupported coverage status"):
        coverage_value("not_covered")


def test_coverage_value_raises_for_empty_status():
    with pytest.raises(ValueError, match="Unsupported coverage status"):
        coverage_value("")
