# DSE-021 Coverage Wave Gold/Evidence Audit

Date: 2026-06-05  
Task ID: DSE-021 Packet 3A  
Scope: `restoration_benefit`, `modern_treatment_coverage`, `newborn_coverage` across the 20 reviewed gold policies

## Summary

This audit source-reviewed the remaining three DSE-021 concepts before extractor implementation. The current gold set contains several real labels, but also several concept/evidence mismatches:

- `restoration_benefit`: 4 source-backed gold fixes are required. Oriental is body-part reconstruction, not sum-insured restoration. Universal Sompo is property-cover restoration in a loan/home section, not a health restoration benefit. Future Generali and Kotak need stronger operative evidence/value shapes.
- `modern_treatment_coverage`: 7 source-backed gold fixes are required. Care, SBI, and Tata AIG have operative modern-treatment coverage currently marked `not_found`; Bajaj/IFFCO/Niva/United India need canonical value shapes.
- `newborn_coverage`: 4 source-backed gold fixes are required. Future Generali and Kotak contain conditional newborn cover, while Aditya Birla and Reliance need status/value correction.

No extractor code or gold labels were changed in Packet 3A.

## Canonical Value Shapes Locked For Packet 3B

- Covered: `{"coverage_status": "covered"}`
- Conditional: `{"coverage_status": "conditional"}`
- Schedule-dependent: `{"schedule_dependent": true}`
- Explicitly not covered: `{"covered": false}`
- Restoration percentage: include `{"percentage": N}` only when directly stated.
- Modern treatment 50% limit: `{"coverage_status": "covered", "limit_percent_of_sum_insured": 50}`
- Newborn waiting/age/maternity dependency: include only when directly stated in evidence.

## Extractor Rules For Packet 3B

- `restoration_benefit`
  - Accept only operative health sum-insured restoration/recharge/reload clauses.
  - Strong positive terms: `restoration benefit`, `automatic recharge`, `reload of sum insured`, `restore sum insured`, `reinstatement of sum insured`.
  - Reject body-part reconstruction, rehab/restore-health wording, PED reinstatement, policy reinstatement, and property/home-cover restoration.
- `modern_treatment_coverage`
  - Accept operative coverage clauses for `modern treatment methods`, `advancement in technologies`, `advance technology methods`, or listed procedures such as uterine artery embolization, HIFU, balloon sinuplasty, oral chemotherapy, immunotherapy, intravitreal injections, robotic surgeries, bronchial thermoplasty, IONM, or hematopoietic stem cells.
  - Reject generic modern/equipment wording and exclusions unless the clause explicitly says the listed modern procedures are covered.
- `newborn_coverage`
  - Accept newborn/new born baby clauses only when tied to coverage, maternity, optional benefit, or covered family-member addition.
  - Reject definitions, non-medical item rows, baby-food/vaccine charge rows, and administrative claim-procedure text.
  - Emit `explicitly_not_covered` only for direct newborn-cover exclusion, not generic `baby charges not payable` annexure rows.

## Policy Audit

| Policy | Concept | Current gold | Classification | Source-backed audit note |
|---|---|---:|---|---|
| `aditya_birla_activ_care` | restoration | present schedule-dependent | `schedule_dependent_present` | Keep. Source page 2 has `Reload of Sum Insured` up to limits specified in Policy Schedule / Product Benefit Table. |
| `aditya_birla_activ_care` | modern treatment | not_found | `not_found_after_search` | Keep. Source search found procedure names in exclusions/day-care lists, but no safe operative modern-treatment coverage clause. |
| `aditya_birla_activ_care` | newborn | explicitly_not_covered | `gold_fix_required` | Fix to `not_found`. Current evidence is non-medical items / `VACCINE CHARGES FOR BABY Not Payable`, not an explicit newborn-cover exclusion. |
| `bajaj_allianz_silver_health` | restoration | not_found | `not_found_after_search` | Keep. Source hits are PED/policy reinstatement only. |
| `bajaj_allianz_silver_health` | modern treatment | present noncanonical `{"percentage": 50}` | `gold_fix_required` | Fix to canonical 50% limit shape. Source page 9 says Modern Treatment Methods are restricted to 50% of Sum Insured or max Rs. 5 lakh. |
| `bajaj_allianz_silver_health` | newborn | not_found | `not_found_after_search` | Keep. Source has only New Born Baby definition and non-medical baby-item rows. |
| `care_health_care_plus` | restoration | present covered | `covered_present` | Keep. Source page 16 says Unlimited Automatic Recharge reinstates up to base Sum Insured unlimited times. |
| `care_health_care_plus` | modern treatment | not_found | `gold_fix_required` | Fix to present. Source page 12 says Advance Technology Methods are indemnified under Hospitalization Expenses. |
| `care_health_care_plus` | newborn | present conditional | `conditional_present` | Keep. Source page 25 says optional Maternity and New Born Baby Cover is available if specified in the Policy Schedule and conditions are met. |
| `cholamandalam_flexi_max_protect` | restoration | not_found | `not_found_after_search` | Keep. No operative restoration/reload/recharge source hit found. |
| `cholamandalam_flexi_max_protect` | modern treatment | not_found | `not_found_after_search` | Keep. No operative modern-treatment source hit found. |
| `cholamandalam_flexi_max_protect` | newborn | not_found | `not_found_after_search` | Keep. No newborn-cover source hit found. |
| `future_generali_health_elite` | restoration | present schedule-dependent | `gold_fix_required` | Keep present but fix evidence/value. Source page 24 schedule says `Restoration Of The Sum Insured` up to 100% of Base SI for subsequent unrelated claims. |
| `future_generali_health_elite` | modern treatment | not_found | `not_found_after_search` | Keep. No operative modern-treatment source hit found. |
| `future_generali_health_elite` | newborn | explicitly_not_covered | `gold_fix_required` | Fix to conditional present. Source page 11 says Newborn Baby Expenses are payable if maternity claim is accepted; only Benefit 19 restoration is not applicable to this cover. |
| `hdfc_arogya_sanjeevani` | restoration | not_found | `not_found_after_search` | Keep. No restoration/recharge cover found. |
| `hdfc_arogya_sanjeevani` | modern treatment | present 50% | `covered_present` | Keep. Source page 10 says listed procedures are covered up to 50% of SI. |
| `hdfc_arogya_sanjeevani` | newborn | not_found | `not_found_after_search` | Keep. No newborn-cover source hit found. |
| `icici_family_shield` | restoration | not_found | `not_applicable_product_type` | Keep. Cash-benefit product; no health restoration/recharge benefit found. |
| `icici_family_shield` | modern treatment | not_found | `not_applicable_product_type` | Keep. Cash-benefit product; no modern-treatment indemnity benefit found. |
| `icici_family_shield` | newborn | not_found | `not_applicable_product_type` | Keep. Cash-benefit product; no newborn-cover benefit found. |
| `iffco_tokio_health_protector` | restoration | not_found | `not_found_after_search` | Keep. No operative restoration/recharge cover found. |
| `iffco_tokio_health_protector` | modern treatment | present noncanonical `{"percentage": 50}` | `gold_fix_required` | Fix to canonical 50% limit shape. Source page 21 says modern methods are covered up to 50% of SI during the policy period. |
| `iffco_tokio_health_protector` | newborn | not_found | `not_found_after_search` | Keep. No newborn-cover source hit found. |
| `kotak_mahindra_health_premier` | restoration | present schedule-dependent | `gold_fix_required` | Keep present but fix value/evidence. Source page 10 says `Restoration Benefit` provides 100% restoration of Base SI once per policy year. |
| `kotak_mahindra_health_premier` | modern treatment | not_found | `not_found_after_search` | Keep. No operative modern-treatment cover found. |
| `kotak_mahindra_health_premier` | newborn | explicitly_not_covered | `gold_fix_required` | Fix to conditional present. Source page 17 contains `New Born Baby Cover`; current evidence is not a direct exclusion of newborn cover. |
| `liberty_critical_connect` | restoration | not_found | `not_applicable_product_type` | Keep. Critical illness product; no health indemnity restoration benefit found. |
| `liberty_critical_connect` | modern treatment | not_found | `not_applicable_product_type` | Keep. Critical illness product; no modern-treatment indemnity benefit found. |
| `liberty_critical_connect` | newborn | not_found | `not_applicable_product_type` | Keep. Critical illness product; no newborn-cover benefit found. |
| `new_india_floater` | restoration | not_found | `not_found_after_search` | Keep. No operative restoration/recharge cover found. |
| `new_india_floater` | modern treatment | present covered | `covered_present` | Keep. Source page 16 has Modern Treatment/Procedures coverage with procedure-specific limits. |
| `new_india_floater` | newborn | present conditional | `conditional_present` | Keep. Source pages 11-12 cover newborn baby from birth subject to terms and renewal declaration conditions. |
| `niva_bupa_health_recharge` | restoration | not_found | `not_found_after_search` | Keep. Product name contains `Recharge`, but source search found no operative recharge/restoration benefit. |
| `niva_bupa_health_recharge` | modern treatment | present noncanonical `{"covered": true}` | `gold_fix_required` | Fix to canonical covered shape. Source page 12 has `Modern Treatments What is covered`; page 37 product table says covered up to Sum Insured with sub-limits on some conditions. |
| `niva_bupa_health_recharge` | newborn | not_found | `not_found_after_search` | Keep. No newborn-cover source hit found. |
| `oriental_cancer_protect` | restoration | present schedule-dependent | `gold_fix_required` | Fix to `not_found` or `not_applicable`. Source page 8 is reconstruction of affected body part to restore physical functioning after cancer surgery, not restoration/reload of sum insured. |
| `oriental_cancer_protect` | modern treatment | not_found | `not_applicable_product_type` | Keep. Cancer-specific product; no modern-treatment methods benefit found. |
| `oriental_cancer_protect` | newborn | not_found | `not_applicable_product_type` | Keep. Cancer-specific product; no newborn-cover benefit found. |
| `reliance_health_gain` | restoration | not_found | `not_found_after_search` | Keep. No operative restoration/recharge cover found. |
| `reliance_health_gain` | modern treatment | present schedule-dependent | `schedule_dependent_present` | Keep. Source page 6 says Modern Treatment expenses are indemnified up to limits specified in Policy Schedule. |
| `reliance_health_gain` | newborn | present `{"covered": true}` | `gold_fix_required` | Fix to conditional. Source page 23 says newborn baby is covered from 90 days under mid-term family addition terms. |
| `royal_sundaram_advanced_topup` | restoration | not_found | `not_found_after_search` | Keep. No operative restoration/recharge cover found. |
| `royal_sundaram_advanced_topup` | modern treatment | present schedule-dependent | `schedule_dependent_present` | Keep. Source page 13 says Modern Treatments are covered up to SI as specified in policy schedule. |
| `royal_sundaram_advanced_topup` | newborn | not_found | `not_found_after_search` | Keep. No newborn-cover source hit found. |
| `sbi_general_arogya_sanjeevani` | restoration | not_found | `not_found_after_search` | Keep. No restoration/recharge cover found. |
| `sbi_general_arogya_sanjeevani` | modern treatment | not_found | `gold_fix_required` | Fix to present 50% limit. Source pages 8-9 list covered modern procedures up to 50% SI. |
| `sbi_general_arogya_sanjeevani` | newborn | not_found | `not_found_after_search` | Keep. No newborn-cover source hit found; baby rows are non-medical items. |
| `star_medi_classic_accident` | restoration | present 200% | `covered_present` | Keep. Source page 9 says automatic restoration of Basic SI by 200% once during policy period. |
| `star_medi_classic_accident` | modern treatment | not_found | `not_found_after_search` | Keep. Source hits are exclusions/stem-cell item rows, not operative modern-treatment coverage. |
| `star_medi_classic_accident` | newborn | not_found | `not_found_after_search` | Keep. Source hits are vaccination and non-medical baby-item rows only. |
| `tata_aig_arogya_sanjeevani` | restoration | not_found | `not_found_after_search` | Keep. No restoration/recharge cover found. |
| `tata_aig_arogya_sanjeevani` | modern treatment | not_found | `gold_fix_required` | Fix to present 50% limit. Source page 8 lists covered modern procedures up to 50% SI. |
| `tata_aig_arogya_sanjeevani` | newborn | not_found | `not_found_after_search` | Keep. No newborn-cover source hit found; baby rows are non-medical items. |
| `united_india_individual_health` | restoration | not_found | `not_found_after_search` | Keep. Source hits are PED/policy reinstatement only. |
| `united_india_individual_health` | modern treatment | present noncanonical `{"covered": true}` | `gold_fix_required` | Fix to canonical covered shape. Source pages 7-8 cover modern treatment methods with procedure-specific sub-limits. |
| `united_india_individual_health` | newborn | not_found | `not_found_after_search` | Keep. Source hits are vaccination and non-medical baby-item rows only. |
| `universal_sompo_loan_secure` | restoration | present schedule-dependent | `gold_fix_required` | Fix to `not_applicable`. Source pages 23 and 25 describe property/home building/content restoration of sum insured after loss, not a health restoration/reload benefit. |
| `universal_sompo_loan_secure` | modern treatment | not_found | `not_applicable_product_type` | Keep. Loan/critical illness/property product; no modern-treatment indemnity benefit found. |
| `universal_sompo_loan_secure` | newborn | not_found | `not_applicable_product_type` | Keep. Loan/critical illness/property product; no newborn-cover benefit found. |

## Packet 3B Gold Corrections

Packet 3B should apply only the source-backed fixes listed above. High-confidence fixes:

- Aditya Birla newborn: change from `explicitly_not_covered` to `not_found`.
- Bajaj modern treatment: canonicalize to covered 50% SI limit, with max amount if Packet 3B supports it.
- Care modern treatment: change from `not_found` to present covered.
- Future Generali restoration: update evidence/value to restoration up to 100% Base SI; newborn: change from `explicitly_not_covered` to conditional present.
- IFFCO modern treatment: canonicalize to covered 50% SI limit.
- Kotak restoration: update evidence/value to 100% restoration; newborn: change from `explicitly_not_covered` to conditional present if Packet 3B source snippet is sufficient.
- Niva Bupa modern treatment: canonicalize to covered shape.
- Oriental restoration: change from present to `not_found` or `not_applicable`; body-part reconstruction is not sum-insured restoration.
- Reliance newborn: change from covered to conditional.
- SBI and Tata AIG modern treatment: change from `not_found` to present 50% SI limit.
- United India modern treatment: canonicalize to covered shape.
- Universal Sompo restoration: change from present to `not_applicable`; source is property/home-cover restoration.

## Packet 3B Test Requirements

- Restoration:
  - Accept automatic recharge/reload/restoration of sum insured.
  - Extract direct restoration percentages such as 100% and 200%.
  - Reject body-part reconstruction and home/property restoration.
- Modern treatment:
  - Accept named modern-treatment coverage clauses even when the heading is absent but the listed procedure set is present.
  - Extract 50% SI limits when stated.
  - Reject exclusions and generic stem-cell/procedure list references.
- Newborn:
  - Accept conditional newborn cover tied to maternity/newborn benefit wording.
  - Reject definitions and baby-item annexure rows.
  - Treat `baby charges/vaccine charges not payable` as insufficient for explicit newborn-cover exclusion.
