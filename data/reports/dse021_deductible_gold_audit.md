# DSE-021 Deductible — Gold/Evidence Audit

Date: 2026-06-04
Task: DSE-021 Packet 1B
Branch: `feat/dse-021-extractor-wave2`

## Summary

This packet audited all 20 reviewed gold policies for `deductible` before implementing the extractor. The gold labels mix operative deductible clauses, definition-only clauses, not-applicable product types, and absent deductible language.

Important decision for Packet 1C: pure definitions such as `Deductible means...` must not be emitted as `present` unless the same policy also has operative language saying the deductible applies.

## Packet 1C Final Result

Final eval: `runs/evals/2026-06-04-fact-extraction-dse021-deductible.json`

| Metric | Result |
|---|---:|
| Policies evaluated | 20 |
| Policies passed | 20 |
| Precision | 100.00% |
| Recall | 99.55% |
| Normalized value accuracy | 100.00% |
| Status accuracy | 97.67% |
| Evidence accuracy | 100.00% |
| False present for gold `not_found` | 0 |

Packet 1C implemented the `DeductibleExtractor`, applied the three required source-backed gold fixes, and normalized custom deductible value shapes to canonical schedule-dependent values where needed.

## Classification Counts

| Classification | Count |
|---|---:|
| `schedule_dependent_present` | 5 |
| `operative_deductible_present` | 3 |
| `not_found_after_search` | 8 |
| `not_applicable_product_type` | 3 |
| `definition_only_not_present` | 1 |
| `gold_fix_required` | 3 |

`gold_fix_required` overlaps with the final target classification; it means the current gold value/status should be changed during Packet 1C before the extractor eval is used as a gate.

## Per-Policy Audit

| Policy | Current Gold | Final Classification | Packet 1C Gold Action | Source/Evidence Note |
|---|---|---|---|---|
| `aditya_birla_activ_care` | `not_found` | `not_found_after_search` | keep | Source hits are claim-settlement deficiency deductions, free-look premium deductions, and installment recovery, not deductible. |
| `bajaj_allianz_silver_health` | `present {"schedule_dependent": true}` | `schedule_dependent_present` | keep | Page 1 states cover applies `in excess of the amount of the Deductible`, subject to Policy Schedule. |
| `care_health_care_plus` | `present` with optional aggregate deductible details | `operative_deductible_present` | normalize to canonical rich shape | Page 27 `Deductible Option (if opted)` states claims are reduced by deductible in Policy Schedule and applies aggregate per policy year. |
| `cholamandalam_flexi_max_protect` | `not_found` | `not_found_after_search` | keep | Only premium/free-look deduction language found. |
| `future_generali_health_elite` | `present {"schedule_dependent": true}` | `definition_only_not_present` | change to `not_found` | Only generic moratorium language says policies are subject to limits/sub-limits/copayments/deductibles; no operative deductible clause found. |
| `hdfc_arogya_sanjeevani` | `not_found` | `not_found_after_search` | keep | Only co-payment deduction and free-look premium deduction found. |
| `icici_family_shield` | `present` schedule-dependent | `schedule_dependent_present` | normalize to canonical shape | Page 1 says deductible applies per year/per life/per event as stated in Policy Certificate; benefit clauses also say liability is in excess of deductible if applicable. |
| `iffco_tokio_health_protector` | `not_found` | `not_found_after_search` | keep | Only unrelated deduction/waiver/free-look language found. |
| `kotak_mahindra_health_premier` | `present {"schedule_dependent": true}` | `definition_only_not_present` | change to `not_found` | Source hits are the standard definition and unrelated premium recovery/room-rent cap language; no operative deductible clause found. |
| `liberty_critical_connect` | `not_applicable` | `not_applicable_product_type` | keep | Critical illness product; no deductible clause found. |
| `new_india_floater` | `not_found` | `not_found_after_search` | keep | Only free-look/proportionate premium deduction found. |
| `niva_bupa_health_recharge` | `present {"schedule_dependent": true}` | `operative_deductible_present` | normalize to canonical rich shape | Page 22 `Annual Aggregate Deductible` says the insured bears deductible specified in Policy Schedule for admissible claim amounts in a policy year. |
| `oriental_cancer_protect` | `not_applicable` | `not_applicable_product_type` | keep | Cancer product; deductible references are generic coordination/cashless clauses, not an operative deductible benefit. |
| `reliance_health_gain` | `not_found` | `operative_deductible_present` | change to `present` | Source text has `Voluntary Aggregate Deductible` and `Time Deductible` clauses; deductible limits are stated in Policy Schedule. |
| `royal_sundaram_advanced_topup` | `present {"schedule_dependent": true}` | `operative_deductible_present` | keep or enrich | Page 1/top-up wording says claims are payable over and above deductible amount; page 12 says claim payable after exhaustion of deductible specified in policy schedule. |
| `sbi_general_arogya_sanjeevani` | `not_found` | `not_found_after_search` | keep | Only co-payment deduction and free-look premium deduction found. |
| `star_medi_classic_accident` | `present` schedule-dependent | `schedule_dependent_present` | normalize to canonical shape | Policy schedule/table lists `Deductible`; later condition references deductibles for each policy period. |
| `tata_aig_arogya_sanjeevani` | `not_found` | `not_found_after_search` | keep | Only premium/free-look and co-payment deductions found. |
| `united_india_individual_health` | `present {"schedule_dependent": true}` | `operative_deductible_present` | enrich optional time-deductible metadata | Page 9 says deductible equivalent to Daily Cash Allowance for the first 48 hours hospitalization will be levied. |
| `universal_sompo_loan_secure` | `not_applicable` | `not_applicable_product_type` | keep | Loan/home-linked product; deductible not applicable to health deductible field. |

## Packet 1C Extractor Rules

- Emit `present` only for operative deductible language:
  - `in excess of the amount of the Deductible`
  - `Deductible Option`
  - `Annual Aggregate Deductible`
  - `Voluntary Aggregate Deductible`
  - `payable only after exhaustion of Deductible`
  - `deductible as specified in the Policy Schedule/Certificate`
  - `deductible equivalent to ... first 48 hours`
- Reject pure definitions:
  - `Deductible means a cost sharing requirement...`
  - `A deductible does not reduce the Sum Insured`
- Reject non-deductible `deduction` language:
  - free-look premium deductions
  - co-payment deduction
  - claim-deficiency deductions
  - installment premium recovery
- Canonical values:
  - `{"schedule_dependent": true}` for schedule/certificate-dependent deductible.
  - Add `basis` when directly stated: `policy_schedule`, `policy_certificate`, `aggregate_per_policy_year`, `top_up`, `daily_cash_allowance`.
  - Add `condition` only for optional clauses such as `if_opted`.
  - Add `hours` for time-deductible clauses only when directly stated.

## Required Packet 1C Gold Fixes

- `future_generali_health_elite`: `present {"schedule_dependent": true}` → `not_found`.
- `kotak_mahindra_health_premier`: `present {"schedule_dependent": true}` → `not_found`.
- `reliance_health_gain`: `not_found` → `present {"schedule_dependent": true}` with evidence from the Voluntary Aggregate Deductible or Time Deductible clause.

Optional normalization fixes for cleaner eval:

- Simplify existing deductible present values to canonical shapes where the current value contains custom keys such as `deductible_status`.
- Keep evidence text exact and source-backed.
