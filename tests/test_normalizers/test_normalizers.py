from normalizers.age import find_ages
from normalizers.coverage_status import normalize_coverage_status
from normalizers.duration import find_durations
from normalizers.indian_number_words import MULTIPLIERS, parse_number_word_phrase
from normalizers.money import find_money_values
from normalizers.percentage import find_percentages


def first_normalized(results):
    assert results
    return results[0]["normalized"]


def test_money_normalizer_examples_from_eval_doc():
    cases = {
        "₹5 lakh": {"amount": 500000, "currency": "INR"},
        "Rs. 5,00,000": {"amount": 500000, "currency": "INR"},
        "INR 5 lakhs": {"amount": 500000, "currency": "INR"},
        "1 crore": {"amount": 10000000, "currency": "INR"},
        "50 lacs": {"amount": 5000000, "currency": "INR"},
        "₹ 1,00,000": {"amount": 100000, "currency": "INR"},
        "Rs. 2.5 lakhs": {"amount": 250000, "currency": "INR"},
    }
    for text, expected in cases.items():
        assert first_normalized(find_money_values(text)) == expected


def test_money_special_values_are_explicit_not_zero_or_none():
    cases = {
        "actuals": "actuals",
        "as charged": "as_charged",
        "subject to limit": "subject_to_limit",
    }
    for text, expected in cases.items():
        normalized = first_normalized(find_money_values(text))
        assert normalized == {"special_value": expected, "currency": "INR"}
        assert normalized["special_value"] not in {0, None}


def test_duration_normalizer_examples_from_eval_doc():
    cases = {
        "36 months": {"months": 36},
        "2 years": {"months": 24},
        "90 days": {"days": 90},
        "thirty days": {"days": 30},
        "one year": {"months": 12},
        "1 yr": {"months": 12},
    }
    for text, expected in cases.items():
        assert first_normalized(find_durations(text)) == expected


def test_percentage_normalizer_examples_from_eval_doc():
    cases = {
        "20%": {"percentage": 20},
        "20 per cent": {"percentage": 20},
        "twenty percent": {"percentage": 20},
        "1% of SI": {"percentage": 1},
        "20% of claim": {"percentage": 20},
    }
    for text, expected in cases.items():
        assert first_normalized(find_percentages(text)) == expected


def test_age_normalizer_exact_and_comparator_examples():
    cases = {
        "60 years": {"age_years": 60, "comparator": "eq"},
        "18 yrs": {"age_years": 18, "comparator": "eq"},
        "aged 61 years": {"age_years": 61, "comparator": "eq"},
        "beyond 60 years": {"age_years": 60, "comparator": "gt"},
        "61 years or above": {"age_years": 61, "comparator": "gte"},
    }
    for text, expected in cases.items():
        assert first_normalized(find_ages(text)) == expected


def test_coverage_status_examples_from_eval_doc():
    cases = {
        "covered": {"coverage_status": "covered"},
        "not covered": {"coverage_status": "not_covered"},
        "covered after waiting period": {"coverage_status": "conditional"},
        "up to actuals": {"coverage_status": "covered_with_actuals"},
        "not admissible": {"coverage_status": "not_covered"},
    }
    for text, expected in cases.items():
        assert normalize_coverage_status(text)["normalized"] == expected


def test_indian_number_words_and_magnitudes():
    assert MULTIPLIERS["lakh"] == 100000
    assert MULTIPLIERS["lac"] == 100000
    assert MULTIPLIERS["crore"] == 10000000
    assert MULTIPLIERS["thousand"] == 1000
    assert parse_number_word_phrase("forty-eight") == 48
    assert parse_number_word_phrase("twenty four") == 24

