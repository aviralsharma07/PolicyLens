import json
from pathlib import Path

from extractors.deterministic import (
    CoPayExtractor,
    FreeLookExtractor,
    GracePeriodExtractor,
    InitialWaitingPeriodExtractor,
    PedWaitingPeriodExtractor,
)
from extractors.registry import run_extractors
from normalizers.duration import find_durations
from normalizers.percentage import find_percentages
from scripts.eval_fact_extractors import _values_match


def clause(text, clause_id="clause_0001", page=1):
    return {
        "clause_id": clause_id,
        "page_start": page,
        "page_end": page,
        "line_ids": [f"p{page}l_1"],
        "text": text,
    }


def accepted_for(concept, clauses):
    _, accepted = run_extractors(clauses, "test_run")
    return {fact["concept"]: fact for fact in accepted}[concept]


def test_duration_normalizer_handles_words_and_units():
    values = find_durations("fifteen days, forty eight months, and two years")
    assert [item["normalized"] for item in values] == [
        {"days": 15},
        {"months": 48},
        {"months": 24},
    ]


def test_duration_normalizer_handles_policy_adjectives_and_hyphens():
    values = find_durations("30-day waiting period and 48 consecutive months of coverage")
    assert [item["normalized"] for item in values] == [
        {"days": 30},
        {"months": 48},
    ]


def test_percentage_normalizer_handles_percent_spellings():
    values = find_percentages("5%, 10 percent and 20 per cent")
    assert [item["normalized"] for item in values] == [
        {"percentage": 5},
        {"percentage": 10},
        {"percentage": 20},
    ]


def test_free_look_extracts_primary_and_distance_marketing():
    fact = accepted_for(
        "free_look_period",
        [
            clause(
                "Free Look Period: A free look period of 15 days from receipt of policy "
                "is available. For distance marketing, free look period is 30 days."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"days": 15}
    assert fact["value_json"]["distance_marketing_days"] == 30


def test_free_look_uses_adjacent_heading_context():
    fact = accepted_for(
        "free_look_period",
        [
            clause("F.1.14 Free look period", clause_id="clause_0001"),
            clause(
                "The insured shall be allowed a period of fifteen days from date of "
                "receipt of the Policy to review the terms and conditions.",
                clause_id="clause_0002",
            ),
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"days": 15}


def test_free_look_accepts_thirty_day_primary_when_policy_says_so():
    fact = accepted_for(
        "free_look_period",
        [
            clause(
                "Free look period: The insured person shall be provided a free look "
                "period of thirty days beginning from the date of receipt of the Policy."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"days": 30}


def test_grace_period_chooses_renewal_30_days_over_installment_grace():
    fact = accepted_for(
        "grace_period",
        [
            clause("A grace period of 15 days is available for monthly installment premium."),
            clause("A grace period of 30 days from the date of expiry is available for renewal."),
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"days": 30}
    assert "installment" not in fact["evidence_text"].lower()


def test_ped_waiting_rejects_definition_only_clause():
    fact = accepted_for(
        "ped_waiting_period",
        [
            clause("Pre-existing disease means any condition diagnosed within 48 months."),
            clause(
                "Pre-Existing Diseases: Expenses related to treatment of PED shall be "
                "excluded until the expiry of 48 months of continuous coverage."
            ),
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"months": 48}
    assert "excluded until" in fact["evidence_text"].lower()


def test_ped_waiting_parses_loose_column_interleaved_months():
    fact = accepted_for(
        "ped_waiting_period",
        [
            clause(
                "Expenses related to the treatment of a pre-existing Disease (PED) "
                "shall be excluded until the expiry of 36 is an accumulated bonus "
                "months of continuous coverage after the date of inception."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"months": 36}


def test_ped_waiting_rejects_incidental_specific_waiting_reference():
    fact = accepted_for(
        "ped_waiting_period",
        [
            clause(
                "Specific waiting period: treatment shall be excluded for 24 months. "
                "If these are pre-existing at proposal, they will be covered subject "
                "to the waiting period mentioned in exclusion 1 above."
            )
        ],
    )
    assert fact["fact_status"] == "not_found"


def test_initial_waiting_not_confused_with_grace_period():
    fact = accepted_for(
        "initial_waiting_period",
        [
            clause("A grace period of 30 days from expiry is available for renewal."),
            clause(
                "The Company shall not be liable for illness during the first 30 days "
                "from policy commencement. Such illness shall be excluded during this period."
            ),
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"days": 30}
    assert "first 30 days" in fact["evidence_text"].lower()


def test_initial_waiting_handles_pdf_ligature_and_exclusion_wording():
    fact = accepted_for(
        "initial_waiting_period",
        [
            clause(
                "Any disease contracted by the insured person during the ﬁrst 30 days "
                "from the commencement date of the policy. This exclusion shall not "
                "apply in case of accident."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"days": 30}


def test_initial_waiting_rejects_claim_timeline_30_days():
    fact = accepted_for(
        "initial_waiting_period",
        [
            clause(
                "The insured shall deliver to the Company, within 30 days of the date "
                "of occurrence of the insured event, a detailed claim form and documents."
            )
        ],
    )
    assert fact["fact_status"] == "not_found"


def test_copay_rejects_definition_without_percentage():
    fact = accepted_for(
        "co_pay",
        [clause("Co-payment is a cost-sharing requirement under a health insurance policy.")],
    )
    assert fact["fact_status"] == "not_found"


def test_copay_extracts_hdfc_admissible_claim_basis():
    fact = accepted_for(
        "co_pay",
        [clause("Co-Payment: The insured person shall bear 5% of admissible claim amount.")],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"percentage": 5, "basis": "admissible_claim_amount"}


def test_copay_extracts_star_age_based_percentage():
    fact = accepted_for(
        "co_pay",
        [clause("21. 10% of each and every claim amount for insured persons beyond 60 years at entry level.")],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"percentage": 10}
    assert fact["condition_json"] == {"entry_age": "beyond_60_years"}


def test_care_copay_components_are_merged():
    fact = accepted_for(
        "co_pay",
        [
            clause("Smart Select: Co-Payment of 20% shall apply if treatment is taken outside Annexure III hospital."),
            clause("Optional Co-payment for persons aged 61 years and above shall be as specified in the Policy Schedule."),
        ],
    )
    assert fact["fact_status"] == "present"
    assert _values_match(
        fact["normalized_value_json"],
        {
            "components": [
                {"scope": "smart_select_non_annexure_iii_hospital", "percentage": 20},
                {
                    "scope": "age_61_plus_optional_copayment",
                    "percentage": None,
                    "schedule_dependent": True,
                },
            ]
        },
    )


def test_value_match_allows_predicted_metadata_superset():
    assert _values_match(
        {"percentage": 5, "basis": "admissible_claim_amount"},
        {"percentage": 5},
    )
    assert not _values_match({"months": 48}, {"months": 36})


def test_registry_emits_not_found_for_missing_safe_candidate():
    _, accepted = run_extractors([clause("This policy has no relevant co-payment percentage.")], "test_run")
    facts = {fact["concept"]: fact for fact in accepted}
    assert set(facts) == {
        "free_look_period",
        "grace_period",
        "ped_waiting_period",
        "initial_waiting_period",
        "co_pay",
    }
    assert facts["co_pay"]["fact_status"] == "not_found"


def test_gold_integration_all_policies_have_section_tree_outputs():
    root = Path("data/interim/logical")
    expected = {
        "hdfc_arogya_sanjeevani",
        "new_india_floater",
        "care_health_care_plus",
        "star_medi_classic_accident",
        "icici_family_shield",
    }
    assert {path.parent.name for path in root.glob("*/section_tree.json")} >= expected
