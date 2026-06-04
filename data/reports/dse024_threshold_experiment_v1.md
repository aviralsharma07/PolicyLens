# DSE-024 Phase C0: Threshold Experiment Results

**Date:** 2026-06-04
**Zero-clause policies:** 132
**Gold policies evaluated:** 20
**Thresholds tested:** 0.45, 0.475, 0.5

## Summary Comparison Across Thresholds

| Metric | t=0.45 | t=0.475 | t=0.50 (current) |
|--------|--------|---------|-------------------|
| Processed | 132 | 132 | 132 |
| ≥1 Heading | 59 | 44 | 0 |
| ≥5 Headings | 16 | 2 | 0 |
| Total Accepted | 214 | 87 | 0 |
| TOC Risk | 55 | 24 | 0 |
| List/Item Risk | 61 | 26 | 0 |

### Candidate Classification (Zero-Clause Policies)

| Classification | t=0.45 | t=0.475 | t=0.50 |
|---------------|--------|---------|--------|
| numbered_item | 59 | 26 | 0 |
| other | 17 | 11 | 0 |
| real_heading | 136 | 50 | 0 |
| short_label | 2 | 0 | 0 |

## False-Positive Risk Assessment

- **t=0.45:** 0 TOC candidates (0.0%), 0 list/item candidates (0.0%) out of 214 total
- **t=0.475:** 0 TOC candidates (0.0%), 0 list/item candidates (0.0%) out of 87 total
- **t=0.5:** 0 TOC candidates (0%), 0 list/item candidates (0%) out of 0 total

## Gold Heading Scorer Eval Results

| Threshold | Precision | Recall | F1 | FP | FN | Status |
|-----------|-----------|--------|----|----|-----|--------|
| 0.45 | 57.1% | 67.4% | 61.8 | 163 | 105 | 3/20 passed |
| 0.475 | 72.8% | 67.4% | 70.0 | 81 | 105 | 5/20 passed |
| 0.5 | 100.0% | 67.4% | 80.5 | 0 | 105 | 18/20 passed |

## Top 20 Newly Accepted Candidates (across all thresholds)

### Threshold 0.45

| # | Slug | Text | Score | Page | Classification |
|---|------|------|-------|------|----------------|
| 1 | 09_hdfc_ergo_hdfc_ergo_critical_illness_ | I. Contact Us | 0.499 | 15 | numbered_item |
| 2 | 02_star_health_star_health_star_care_mic | I. COVERAGE | 0.4988 | 3 | numbered_item |
| 3 | 19_liberty_liberty_79fc880c_2c03_e5e9_3a | 10.Renewal | 0.4987 | 14 | real_heading |
| 4 | 14_universal_sompo_universal_sompo_group | 10.Migration | 0.4978 | 11 | real_heading |
| 5 | 18_cholamandalam_cholamandalam_chola_cla | 27.Migration | 0.4978 | 19 | real_heading |
| 6 | 12_iffco_tokio_iffco_tokio_group_medishi | 20. Illness | 0.4976 | 3 | real_heading |
| 7 | 02_star_health_star_health_star_group_he | 7. Cancellation: | 0.4975 | 18 | real_heading |
| 8 | 04_icici_lombard_icici_lombard_health_ca | 0.25 years | 0.4974 | 11 | numbered_item |
| 9 | 09_hdfc_ergo_hdfc_ergo_protector_rider | Section 5. Claim Procedure | 0.4971 | 8 | real_heading |
| 10 | 12_iffco_tokio_iffco_tokio_family_health | 8. Migration | 0.4967 | 35 | real_heading |
| 11 | 12_iffco_tokio_iffco_tokio_family_health | 8. Migration | 0.4967 | 35 | real_heading |
| 12 | 10_tata_aig_tata_aig_wellsurance_family_ | POLICY WORDINGS | 0.4964 | 1 | real_heading |
| 13 | 20_sbi_general_sbi_retail_health_pw | 1 | 0.4957 | 5 | other |
| 14 | 05_niva_bupa_niva_bupa_health_pulse | 6. Exclusions | 0.4947 | 22 | real_heading |
| 15 | 02_star_health_star_group_accident_insur | 2. Permanent Total Disablement - Benefit 2 | 0.4944 | 3 | real_heading |
| 16 | 18_cholamandalam_cholamandalam_chola_cla | 28.Migration | 0.4942 | 23 | real_heading |
| 17 | 02_star_health_star_health_star_care_mic | MICRO-INSURANCE PRODUCT | 0.493 | 1 | other |
| 18 | 02_star_health_star_health_star_care_mic | MICRO-INSURANCE PRODUCT | 0.493 | 3 | other |
| 19 | 10_tata_aig_tata_aig_wellsurance_family_ | Part D: Coverage | 0.4929 | 8 | real_heading |
| 20 | 12_iffco_tokio_iffco_tokio_group_medishi | 4. Migration | 0.4929 | 14 | real_heading |

### Threshold 0.475

| # | Slug | Text | Score | Page | Classification |
|---|------|------|-------|------|----------------|
| 1 | 09_hdfc_ergo_hdfc_ergo_critical_illness_ | I. Contact Us | 0.499 | 15 | numbered_item |
| 2 | 02_star_health_star_health_star_care_mic | I. COVERAGE | 0.4988 | 3 | numbered_item |
| 3 | 19_liberty_liberty_79fc880c_2c03_e5e9_3a | 10.Renewal | 0.4987 | 14 | real_heading |
| 4 | 14_universal_sompo_universal_sompo_group | 10.Migration | 0.4978 | 11 | real_heading |
| 5 | 18_cholamandalam_cholamandalam_chola_cla | 27.Migration | 0.4978 | 19 | real_heading |
| 6 | 12_iffco_tokio_iffco_tokio_group_medishi | 20. Illness | 0.4976 | 3 | real_heading |
| 7 | 02_star_health_star_health_star_group_he | 7. Cancellation: | 0.4975 | 18 | real_heading |
| 8 | 04_icici_lombard_icici_lombard_health_ca | 0.25 years | 0.4974 | 11 | numbered_item |
| 9 | 09_hdfc_ergo_hdfc_ergo_protector_rider | Section 5. Claim Procedure | 0.4971 | 8 | real_heading |
| 10 | 12_iffco_tokio_iffco_tokio_family_health | 8. Migration | 0.4967 | 35 | real_heading |
| 11 | 12_iffco_tokio_iffco_tokio_family_health | 8. Migration | 0.4967 | 35 | real_heading |
| 12 | 10_tata_aig_tata_aig_wellsurance_family_ | POLICY WORDINGS | 0.4964 | 1 | real_heading |
| 13 | 20_sbi_general_sbi_retail_health_pw | 1 | 0.4957 | 5 | other |
| 14 | 05_niva_bupa_niva_bupa_health_pulse | 6. Exclusions | 0.4947 | 22 | real_heading |
| 15 | 02_star_health_star_group_accident_insur | 2. Permanent Total Disablement - Benefit 2 | 0.4944 | 3 | real_heading |
| 16 | 18_cholamandalam_cholamandalam_chola_cla | 28.Migration | 0.4942 | 23 | real_heading |
| 17 | 02_star_health_star_health_star_care_mic | MICRO-INSURANCE PRODUCT | 0.493 | 1 | other |
| 18 | 02_star_health_star_health_star_care_mic | MICRO-INSURANCE PRODUCT | 0.493 | 3 | other |
| 19 | 10_tata_aig_tata_aig_wellsurance_family_ | Part D: Coverage | 0.4929 | 8 | real_heading |
| 20 | 12_iffco_tokio_iffco_tokio_group_medishi | 4. Migration | 0.4929 | 14 | real_heading |

### Threshold 0.5

_No candidates accepted at this threshold._

## Sample Policy Details

For each of the 20 Phase B sample policies, this shows how many headings would be accepted at each threshold.

| Slug | t=0.45 | t=0.475 | t=0.50 | TOC risk | List risk |
|------|--------|---------|--------|----------|-----------|
| 02_star_health_star_health_star_group_health_ | 1 | 1 | 0 | 0 | 1 |
| 03_care_health_care_freedom_policy | 4 | 1 | 0 | 1 | 0 |
| 04_icici_lombard_icici_lombard_group_take_car | 0 | 0 | 0 | 0 | 0 |
| 05_niva_bupa_niva_bupa_health_plus | 5 | 0 | 0 | 0 | 5 |
| 05_niva_bupa_niva_bupa_health_pulse | 8 | 3 | 0 | 1 | 3 |
| 07_oriental_insurance_oriental_oriental_secur | 0 | 0 | 0 | 0 | 0 |
| 08_bajaj_allianz_bajaj_allianz_family_health_ | 0 | 0 | 0 | 0 | 0 |
| 09_hdfc_ergo_hdfc_ergo_my_optima_secure | 6 | 0 | 0 | 1 | 0 |
| 11_aditya_birla_aditya_birla_activ_health_202 | 0 | 0 | 0 | 0 | 0 |
| 12_iffco_tokio_iffco_tokio_family_health_prot | 4 | 3 | 0 | 0 | 0 |
| 12_iffco_tokio_iffco_tokio_family_health_prot | 4 | 3 | 0 | 0 | 0 |
| 13_future_generali_future_generali_future_poo | 0 | 0 | 0 | 0 | 0 |
| 14_universal_sompo_universal_sompo_csc_comple | 0 | 0 | 0 | 0 | 0 |
| 16_kotak_mahindra_kotak_kotak_group_hospital_ | 0 | 0 | 0 | 0 | 0 |
| 18_cholamandalam_cholamandalam_chola_classic_ | 6 | 2 | 0 | 0 | 0 |
| 19_liberty_liberty_79fc880c_2c03_e5e9_3a02_dc | 4 | 1 | 0 | 1 | 0 |
| 21_royal_sundaram_royal_sundaram_ace_health_a | 5 | 1 | 0 | 0 | 5 |
| 22_edelweiss_edelweiss_group_corona_pw | 18 | 0 | 0 | 6 | 0 |
| non_policy_wordings_nivabupa_health_recharge_ | 0 | 0 | 0 | 0 | 0 |
| tata_aig_arogya_sanjeevani | 2 | 0 | 0 | 0 | 2 |

## Recommendation

### Data-Driven Assessment

- **t=0.50 (current):** 0/132 zero-clause policies have ≥1 heading
- **t=0.475:** 44/132 policies gain ≥1 heading (+44 from t=0.50)
- **t=0.45:** 59/132 policies gain ≥1 heading (+59 from t=0.50)
- FP ratio at t=0.45: 54.2% of accepted candidates are TOC/list/table noise
- FP ratio at t=0.475: 57.5%

### Recommendation

**Feature-level fixes first, no threshold change.**

Threshold 0.45 would help 59 additional policies, but 54.2% of newly accepted candidates are TOC/list/table noise. Without TOC/list suppression, lowering the threshold would introduce many false-positive headings.

### Next Steps

1. Implement TOC suppression (has_toc_dots penalty).
2. Implement list-item suppression or all-caps-fp penalty for short numbered items.
3. Re-run experiment to verify reduced FP ratio.
4. If FP ratio drops below 25%, proceed with threshold change.

### Warning

**Do NOT commit gold eval temp files or interim scorer outputs.** The `data/interim/dse024/` directory contains temporary generated heading_candidates.json files that should be cleaned up after review. Only the final reports in `data/reports/` should be committed.