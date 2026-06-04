import json
from pathlib import Path

from extractors.deterministic import (
    ClaimIntimationTimelineExtractor,
    ClaimSettlementTimelineExtractor,
    CoPayExtractor,
    FreeLookExtractor,
    GracePeriodExtractor,
    InitialWaitingPeriodExtractor,
    IcuLimitExtractor,
    MaternityWaitingExtractor,
    PedWaitingPeriodExtractor,
    RoomRentLimitExtractor,
    SpecificDiseaseWaitingPeriodsExtractor,
)
from extractors.models import TARGET_CONCEPTS
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
        [
            clause(
                "21. 10% of each and every claim amount for insured persons beyond 60 years at entry level."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"percentage": 10}
    assert fact["condition_json"] == {"entry_age": "beyond_60_years"}


def test_care_copay_components_are_merged():
    fact = accepted_for(
        "co_pay",
        [
            clause(
                "Smart Select: Co-Payment of 20% shall apply if treatment is taken outside Annexure III hospital."
            ),
            clause(
                "Optional Co-payment for persons aged 61 years and above shall be as specified in the Policy Schedule."
            ),
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


def test_claim_settlement_rejects_preauthorization_validity():
    fact = accepted_for(
        "claim_settlement_timeline",
        [
            clause(
                "Once the request for pre-authorisation has been granted, the treatment "
                "must take place within 15 days of the pre-authorization date."
            )
        ],
    )
    assert fact["fact_status"] == "not_found"


def test_claim_settlement_keeps_normal_and_investigation_days():
    fact = accepted_for(
        "claim_settlement_timeline",
        [
            clause(
                "Claim Settlement (provision for Penal Interest). The Company shall settle "
                "or reject a claim, as the case may be, within 30 days from the date of "
                "receipt of last necessary document. However, where the circumstances of a "
                "claim warrant an investigation, the Company shall settle the claim within "
                "45 days from the date of receipt of last necessary document."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"days": 30, "investigation_days": 45}


def test_claim_settlement_handles_noisy_settle_text():
    fact = accepted_for(
        "claim_settlement_timeline",
        [
            clause(
                "Claim Settlement (provision for Penal Interest) i. The Company shall "
                "settle or reject a clam, as the case may be, w i thin 15 days fom the "
                "date of recept of last necessary document."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"days": 15}


def test_specific_disease_parses_slash_separated_month_options():
    fact = accepted_for(
        "specific_disease_waiting_periods",
        [
            clause(
                "Specified disease/procedure waiting period - Code Excl02. Expenses related "
                "to listed conditions, surgeries/treatments shall be excluded until the "
                "expiry of 24/48 months of continuous coverage."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"months_options": [24, 48]}


def test_specific_disease_rejects_ped_definition_duration():
    fact = accepted_for(
        "specific_disease_waiting_periods",
        [
            clause(
                "Specified disease/procedure waiting period applies for cataract after "
                "24 months. Pre-existing Disease means any condition diagnosed within "
                "48 months prior to the policy."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"months_options": [24]}


def test_maternity_not_covered_until_duration_is_waiting_period():
    fact = accepted_for(
        "maternity_waiting",
        [
            clause(
                "Maternity Benefit Waiting Period. Any treatment arising from pregnancy, "
                "childbirth including caesarean section will not be covered until 36 months "
                "of continuous coverage has elapsed."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"months": 36}


def test_claim_intimation_detects_48_hours():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "In the event of Hospitalisation, We shall be given written notice of "
                "the claim within 48 hours of admission to the Hospital."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"hours": 48}


def test_claim_intimation_detects_within_30_days():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "Notice of claim with full particulars shall be sent to the Company "
                "within 30 days from the date of occurrence of the event."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"days": 30}


def test_claim_intimation_rejects_settlement_timeline():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "The Company shall settle the claim within 30 days from the date of "
                "receipt of last necessary document."
            )
        ],
    )
    assert fact["fact_status"] == "not_found"


def test_claim_intimation_rejects_free_look():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "A free look period of 15 days from receipt of policy is available "
                "for the insured to review the terms."
            )
        ],
    )
    assert fact["fact_status"] == "not_found"


def test_claim_intimation_rejects_grace_period():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "A grace period of 30 days from the date of expiry is available "
                "for renewal of the policy."
            )
        ],
    )
    assert fact["fact_status"] == "not_found"


def test_claim_intimation_handles_written_notice_of_claim():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "We shall be given written notice of the claim along with the "
                "following details within 48 hours of admission."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"hours": 48}


def test_claim_intimation_not_found_when_no_safe_candidate():
    fact = accepted_for(
        "claim_intimation_timeline",
        [clause("This policy has no requirement for claim notification or intimation.")],
    )
    assert fact["fact_status"] == "not_found"


def test_claim_intimation_rejects_cancellation_timeline():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "The Company reserves the right to cancel the policy by giving "
                "30 days written notice."
            )
        ],
    )
    assert fact["fact_status"] == "not_found"


def test_claim_intimation_detects_notified_pattern():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "the Company shall be notified with full particulars within 48 "
                "hours of Hospitalization commencing."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"hours": 48}


def test_claim_intimation_detects_notice_shall_be_sent():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "Notice with full particulars shall be sent to the Company as under: "
                "Within 24 hours from the date of emergency hospitalization required."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"hours": 24}


def test_claim_intimation_detects_must_be_given_notification():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "We must be given Notification of Claim in writing immediately "
                "and in any event within 48 hours of the diagnosis."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"hours": 48}


def test_claim_intimation_detects_at_least_hours_prior():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "Notice with full particulars shall be sent to the Company as under: "
                "Within 24 hours from the date of emergency hospitalization required "
                "or before discharge, whichever is earlier. "
                "At least 48 hours prior to admission in Hospital in case of "
                "a planned Hospitalization."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"hours": 24}


def test_claim_intimation_detects_split_notification_bullets():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause("9.2 Notification of Claim Notice with full particulars shall be sent as under:"),
            clause(
                "i. Within 24 hours from the date of emergency hospitalization required "
                "or before the Insured Person's discharge from Hospital, whichever is earlier."
            ),
            clause(
                "ii. At least 48 hours prior to admission in Hospital in case of "
                "a planned Hospitalization."
            ),
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"hours": 24}


def test_claim_intimation_rejects_adjacent_reimbursement_document_rows():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause("9.2 Notification of Claim Notice with full particulars shall be sent as under:"),
            clause(
                "Reimbursement of post hospitalization expenses within fifteen days "
                "from completion of post hospitalization treatment."
            ),
        ],
    )
    assert fact["fact_status"] == "not_found"


def test_claim_intimation_rejects_death_document_submission_deadline():
    fact = accepted_for(
        "claim_intimation_timeline",
        [
            clause(
                "The immediate family member claiming on behalf of the Insured Person "
                "must inform Us in writing immediately and send a copy of all the required "
                "documents to prove the cause of death within 30 days of the death."
            )
        ],
    )
    assert fact["fact_status"] == "not_found"


def test_deductible_detects_policy_schedule_dependent_clause():
    fact = accepted_for(
        "deductible",
        [
            clause(
                "Claim under this Policy will be payable only after exhaustion of "
                "Deductible amount as opted by the insured and as specified in the "
                "policy schedule."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"]["schedule_dependent"] is True
    assert fact["normalized_value_json"]["basis"] == "policy_schedule"


def test_deductible_rejects_definition_only_clause():
    fact = accepted_for(
        "deductible",
        [
            clause(
                "Deductible means a cost sharing requirement under a health insurance "
                "policy. A deductible does not reduce the Sum Insured."
            )
        ],
    )
    assert fact["fact_status"] == "not_found"


def test_deductible_rejects_free_look_premium_deduction():
    fact = accepted_for(
        "deductible",
        [
            clause(
                "If the policy is cancelled during free look, premium shall be refunded "
                "after deduction towards proportionate risk premium and stamp duty."
            )
        ],
    )
    assert fact["fact_status"] == "not_found"


def test_deductible_detects_explicit_amount():
    fact = accepted_for(
        "deductible",
        [clause("A deductible of Rs. 5,00,000 shall apply to each admissible claim.")],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {"amount": 500000, "currency": "INR"}


def test_deductible_detects_top_up_exhaustion_clause():
    fact = accepted_for(
        "deductible",
        [
            clause(
                "The top-up claim is payable only after exhaustion of Deductible "
                "specified in the Policy Schedule."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"]["schedule_dependent"] is True


def test_deductible_detects_time_deductible_hours():
    fact = accepted_for(
        "deductible",
        [
            clause(
                "Deductible equivalent to Daily Cash Allowance for the first 48 hours "
                "Hospitalization will be levied on each Hospitalisation during the Policy Period."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {
        "schedule_dependent": True,
        "hours": 48,
        "basis": "daily_cash_allowance",
    }


def test_room_rent_extracts_one_percent_si_limit():
    fact = accepted_for(
        "room_rent_limit",
        [
            clause(
                "Room Rent, boarding and nursing expenses as provided by the Hospital "
                "not exceeding 1% of the Sum Insured per day."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {
        "percentage": 1,
        "unit": "percent_of_sum_insured_per_day",
    }


def test_icu_extracts_two_percent_si_limit():
    fact = accepted_for(
        "icu_limit",
        [
            clause(
                "Charges for accommodation in Intensive Care Unit (ICU)/ICCU up to "
                "2% of Sum Insured per day or actual expenses whichever is less."
            )
        ],
    )
    assert fact["fact_status"] == "present"
    assert fact["normalized_value_json"] == {
        "percentage": 2,
        "unit": "percent_of_sum_insured_per_day",
    }


def test_room_and_icu_extract_actuals_from_table_like_clause():
    clauses = [
        clause(
            "Room Rent Actual Up to Single Private Air Conditioned room ICU Charges Actual "
            "Pre Hospitalization 30 Days 3% of hospital expenses."
        )
    ]
    room_fact = accepted_for("room_rent_limit", clauses)
    icu_fact = accepted_for("icu_limit", clauses)
    assert room_fact["normalized_value_json"] == {
        "coverage_status": "actuals",
        "room_category": "single_private_air_conditioned_room",
    }
    assert icu_fact["normalized_value_json"] == {"coverage_status": "actuals"}


def test_room_and_icu_extract_schedule_dependent_limits():
    clauses = [
        clause(
            "The Policy covers room rent and ICU charges subject to the limits "
            "specified in the Policy Schedule."
        )
    ]
    assert accepted_for("room_rent_limit", clauses)["normalized_value_json"] == {
        "schedule_dependent": True,
        "basis": "policy_schedule",
    }
    assert accepted_for("icu_limit", clauses)["normalized_value_json"] == {
        "schedule_dependent": True,
        "basis": "policy_schedule",
    }


def test_room_and_icu_reject_definition_only_clauses():
    clauses = [
        clause("Room Rent means the amount charged by a Hospital towards Room and Boarding expenses."),
        clause("ICU Charges means the amount charged by a Hospital towards ICU expenses."),
    ]
    assert accepted_for("room_rent_limit", clauses)["fact_status"] == "not_found"
    assert accepted_for("icu_limit", clauses)["fact_status"] == "not_found"


def test_iffco_room_and_icu_components_are_preserved():
    clauses = [
        clause(
            "Room Rent Expenses: In respect of sum insured of Rs. 5(five) lakhs and "
            "above, room-rent expenses will be payable according to actual expenses "
            "without any room rent expenses capping limits. In respect of sum insured "
            "less than Rs.5 lakhs, class A cities have a limit of 1.75% of the sum "
            "insured per day and other cities have a limit of 1.50%. For Intensive "
            "Care Unit/Therapeutic Expenses: class A cities have 3% of the sum insured "
            "per day and other cities 2.5% of the sum insured per day."
        )
    ]
    room_fact = accepted_for("room_rent_limit", clauses)
    icu_fact = accepted_for("icu_limit", clauses)
    assert room_fact["normalized_value_json"]["components"][1]["percentage"] == 1.75
    assert icu_fact["normalized_value_json"]["components"][1]["percentage"] == 3


def test_registry_emits_not_found_for_missing_safe_candidate():
    _, accepted = run_extractors(
        [clause("This policy has no relevant co-payment percentage.")], "test_run"
    )
    facts = {fact["concept"]: fact for fact in accepted}
    assert set(facts) == set(TARGET_CONCEPTS)
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
