# DSE-021 Room Rent + ICU Gold/Evidence Audit

Date: 2026-06-04  
Task ID: DSE-021  
Scope: `room_rent_limit`, `icu_limit` across the 20 reviewed gold policies

## Summary

This audit source-reviewed the room rent and ICU concepts before implementing extractors. Source PDF text is authoritative; existing section trees and table outputs were used as cross-checks.

The current gold labels mix four real cases:

- explicit percentage / amount limits,
- actuals or no separate sub-limit,
- schedule / certificate dependent limits,
- non-indemnity or fixed-benefit products where room/ICU limits are not operative Product A facts.

Several current gold values need correction in Packet 2B. The most important issue is table-row bleed: for example, Bajaj room rent is currently labelled as `{"percentage": 3}`, but the source row says room rent is actual up to a single private air-conditioned room; `3%` belongs to pre-hospitalization hospital expenses.

## Canonical Value Shapes Locked For Packet 2B

| Case | Canonical normalized value |
|---|---|
| Room rent percentage | `{"percentage": 1, "unit": "percent_of_sum_insured_per_day"}` |
| ICU percentage | `{"percentage": 2, "unit": "percent_of_sum_insured_per_day"}` |
| Actuals / no separate fixed limit | `{"coverage_status": "actuals"}` |
| Schedule-only / certificate-only | `{"schedule_dependent": true}` |
| Policy schedule basis | add `{"basis": "policy_schedule"}` only when directly stated |
| Multi-condition limits | `{"components": [...]}` with condition text preserved |

## Extractor Rules For Packet 2B

- Accept operative clauses and benefit-table text with `room rent`, `room/ICU`, `ICU`, `ICCU`, `intensive care unit charges`, `single private room`, `actuals`, `no limit`, `% of sum insured`, or `specified in policy schedule`.
- Reject definition-only clauses such as `Room Rent means...` and `ICU Charges means...`.
- Reject proportionate deduction clauses unless they also state the underlying eligible room/ICU limit.
- Treat `specified in Policy Schedule`, `Product Benefits Table`, or `Policy Certificate` as `schedule_dependent`.
- Prefer explicit operative limits over definitions and over optional add-on discounts.
- For paired Arogya Sanjeevani clauses, emit room rent `2%` and ICU `5%` when those limits are present.
- For `actual`, `actuals`, `no limit`, and `without capping limits`, emit `{"coverage_status": "actuals"}`.

## Policy-Level Audit

| Policy | Concept | Gold status/value | Source-backed classification | Source-backed action |
|---|---|---|---|---|
| `aditya_birla_activ_care` | room | present `schedule_dependent` | `schedule_dependent_present` | Keep. Source page 1 covers room rent up to limits in Policy Schedule / Product Benefit Table. |
| `aditya_birla_activ_care` | ICU | present `schedule_dependent` | `schedule_dependent_present` | Keep. Same operative clause lists ICU Charges under the schedule/product table basis. |
| `bajaj_allianz_silver_health` | room | present `{"percentage": 3}` | `gold_fix_required` | Fix to actuals / room-category value. Source page 7 says `Room Rent Actual Up to Single Private Air Conditioned room`; the `3%` value belongs to pre-hospitalization expenses. |
| `bajaj_allianz_silver_health` | ICU | present `schedule_dependent` | `gold_fix_required` | Fix to `{"coverage_status": "actuals"}`. Source page 7 says `ICU Charges Actual`. |
| `care_health_care_plus` | room | present `{"basis": "policy_schedule"}` | `gold_fix_required` | Fix to explicit base limit `1% of Sum Insured per day` with schedule basis. Source pages 11-12 state the available room rent option. |
| `care_health_care_plus` | ICU | present `{"basis": "policy_schedule"}` | `gold_fix_required` | Fix to explicit base limit `2% of Sum Insured per day` with schedule basis; optional benefit can upgrade ICU to no limit. |
| `cholamandalam_flexi_max_protect` | room | not_found | `not_applicable_product_type` | Keep not_found for now. Source is critical-illness style wording with no operative room rent limit. |
| `cholamandalam_flexi_max_protect` | ICU | not_found | `not_applicable_product_type` | Keep not_found for now. ICU appears only inside disease definitions/clinical criteria, not as a benefit limit. |
| `future_generali_health_elite` | room | not_found | `gold_fix_required` | Fix to `schedule_dependent`. Source page 4 covers room rent and says specific sub-limits are in Schedule of Benefits / Annexure I. |
| `future_generali_health_elite` | ICU | not_found | `gold_fix_required` | Fix to `schedule_dependent`. Source page 4 explicitly lists ICU Charges under hospitalization covers subject to schedule sub-limits. |
| `hdfc_arogya_sanjeevani` | room | present `2%` | `operative_limit_present` | Keep. Source page 9 says room rent up to 2% SI, max Rs. 5,000 per day. |
| `hdfc_arogya_sanjeevani` | ICU | present `5%` | `operative_limit_present` | Keep. Source page 9 says ICU/ICCU up to 5% SI, max Rs. 10,000 per day. |
| `icici_family_shield` | room | not_applicable | `not_applicable_product_type` | Keep. Product is cash / benefit style; no operative room rent indemnity limit found. |
| `icici_family_shield` | ICU | present noncanonical `present_schedule_dependent` | `gold_fix_required` | Normalize to schedule-dependent ICU cash benefit. Source pages 12-13 say daily ICU cash amount and max days are specified in Policy Certificate. |
| `iffco_tokio_health_protector` | room | present `{"amount": 5, "currency": "INR"}` | `gold_fix_required` | Fix to conditional components. Source page 13: SI >= Rs. 5 lakhs has actual expenses without room-rent capping; SI below Rs. 5 lakhs has 1.75% SI/day in Class A cities and 1.50% in other cities. |
| `iffco_tokio_health_protector` | ICU | not_found | `gold_fix_required` | Fix to conditional components. Source page 13: ICU/therapeutic expenses 3% SI/day in Class A cities and 2.5% SI/day in other cities for SI below Rs. 5 lakhs; no ICU cap for SI >= Rs. 5 lakhs implied by the same room-rent capping structure. |
| `kotak_mahindra_health_premier` | room | present `schedule_dependent` | `schedule_dependent_present` | Keep. Source page 20 caps room rent to eligible Room Rent specified in Policy Schedule. |
| `kotak_mahindra_health_premier` | ICU | not_found | `not_found_after_search` | Keep. ICU appears in definitions/records but no operative ICU limit found. |
| `liberty_critical_connect` | room | not_found | `not_applicable_product_type` | Keep. Critical illness product, no operative room rent limit. |
| `liberty_critical_connect` | ICU | present `schedule_dependent` | `gold_fix_required` | Fix to not_found. Current evidence is neurological-symptom wording, not an ICU benefit limit. |
| `new_india_floater` | room | present `1%` | `operative_limit_present` | Keep. Source page 10 says room rent/boarding/nursing not exceeding 1% SI per day. |
| `new_india_floater` | ICU | present `2%` | `operative_limit_present` | Keep. Source page 10 says ICU/ICCU not exceeding 2% SI per day. |
| `niva_bupa_health_recharge` | room | not_found | `gold_fix_required` | Fix to schedule-dependent / eligible room category. Source page 6 lists Room Rent under inpatient care and says eligibility is as specified in Policy Schedule; page 22 has optional modification to Single Private Room. |
| `niva_bupa_health_recharge` | ICU | not_found | `gold_fix_required` | Fix to schedule-dependent. Source page 6 lists Intensive Care Unit Charges under inpatient care and schedule-based limits. |
| `oriental_cancer_protect` | room | present `schedule_dependent` | `gold_fix_required` | Fix to explicit conditional components. Source page 2: 1% SI with max INR 10,000/day for SI 5/10/15 lakh, and max INR 25,000/day for SI 20/25/50 lakh, actuals if lower. |
| `oriental_cancer_protect` | ICU | present `schedule_dependent` | `gold_fix_required` | Fix to `{"coverage_status": "actuals"}`. Source page 2 says ICU or specialised expenses are `Actuals`. |
| `reliance_health_gain` | room | not_found | `gold_fix_required` | Fix to schedule-dependent. Source pages 5-6 list Room Rent under hospitalization expenses and say limits are specified in Policy Schedule. |
| `reliance_health_gain` | ICU | not_found | `gold_fix_required` | Fix to schedule-dependent. Source pages 5-6 list Intensive Care Unit charges under hospitalization expenses and schedule limits. |
| `royal_sundaram_advanced_topup` | room | present `schedule_dependent` | `schedule_dependent_present` | Keep. Source page 12 covers room rent subject to Product Benefits Table / schedule sub-limits. |
| `royal_sundaram_advanced_topup` | ICU | not_found | `gold_fix_required` | Fix to schedule-dependent. Source page 12 explicitly lists ICU/ICCU expenses under inpatient care subject to Product Benefits Table / schedule sub-limits. |
| `sbi_general_arogya_sanjeevani` | room | present `schedule_dependent` | `gold_fix_required` | Fix to 2% SI/day. Source page 7 says room rent up to 2% SI, max Rs. 5,000 per day. |
| `sbi_general_arogya_sanjeevani` | ICU | not_found | `gold_fix_required` | Fix to 5% SI/day. Source page 7 says ICU/ICCU up to 5% SI, max Rs. 10,000 per day. |
| `star_medi_classic_accident` | room | present `policy_schedule` | `gold_fix_required` | Fix to actuals/no specific sub-limit. Source page 3 CIS says room/ICU charges beyond sublimit: Nil; no operative room-rent cap was found. |
| `star_medi_classic_accident` | ICU | present `policy_schedule` | `gold_fix_required` | Fix to actuals/no specific sub-limit for the same source reason. |
| `tata_aig_arogya_sanjeevani` | room | present `schedule_dependent` | `gold_fix_required` | Fix to 2% SI/day. Source page 7 says room rent up to 2% SI, max Rs. 5,000 per day. |
| `tata_aig_arogya_sanjeevani` | ICU | not_found | `gold_fix_required` | Fix to 5% SI/day. Source page 7 says ICU/ICCU up to 5% SI, max Rs. 10,000 per day. |
| `united_india_individual_health` | room | present `1%` | `operative_limit_present` | Keep; add canonical unit if patched. Source pages 6 and 20 say 1% SI per day. |
| `united_india_individual_health` | ICU | not_found | `gold_fix_required` | Fix to 2% SI/day. Source pages 6 and 20 say ICU/ICCU 2% SI. |
| `universal_sompo_loan_secure` | room | not_found | `not_applicable_product_type` | Keep. Loan/critical illness product has no operative room rent limit. |
| `universal_sompo_loan_secure` | ICU | not_found | `not_applicable_product_type` | Keep. ICU appears only incidentally in medical-condition text, not as a benefit limit. |

## Packet 2B Gold Corrections

Packet 2B should apply only the source-backed fixes listed above. High-confidence fixes:

- Bajaj: room actuals, ICU actuals.
- Care: room 1% SI/day, ICU 2% SI/day.
- Future Generali: room and ICU schedule-dependent.
- ICICI: normalize ICU cash schedule-dependent shape.
- IFFCO Tokio: room and ICU conditional components.
- Liberty: ICU to not_found.
- Niva Bupa: room and ICU schedule-dependent.
- Oriental: room conditional components, ICU actuals.
- Reliance: room and ICU schedule-dependent.
- Royal Sundaram: ICU schedule-dependent.
- SBI: room 2% SI/day, ICU 5% SI/day.
- Star: room and ICU actuals/no fixed sub-limit.
- Tata AIG: room 2% SI/day, ICU 5% SI/day.
- United India: ICU 2% SI/day; room unit normalization optional.

## Packet 2B Test Requirements

- Definition-only `Room Rent means...` and `ICU Charges means...` must remain rejected.
- Arogya-style room/ICU clauses must emit `2%` and `5%`.
- New India / United India style 1% / 2% clauses must emit the correct concept-specific value.
- Bajaj / Oriental / Star style `Actual` / `Actuals` / no sublimit clauses must emit actuals.
- Schedule/certificate-only limits must emit `schedule_dependent`.
- IFFCO conditional city/SI limits should emit `components` rather than a single misleading scalar.
