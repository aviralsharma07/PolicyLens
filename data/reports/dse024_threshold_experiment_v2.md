# DSE-024 Phase C0: Threshold Experiment Results

**Date:** 2026-06-04
**Zero-clause policies:** 132
**Gold policies evaluated:** 20
**Thresholds tested:** 0.45, 0.475, 0.5

## Summary Comparison Across Thresholds

| Metric | t=0.45 | t=0.475 | t=0.50 (current) |
|--------|--------|---------|-------------------|
| Processed | 132 | 132 | 132 |
| ≥1 Heading | 59 | 45 | 4 |
| ≥5 Headings | 13 | 1 | 0 |
| Total Accepted | 200 | 84 | 5 |
| TOC Risk | 53 | 22 | 0 |
| List/Item Risk | 43 | 22 | 5 |

### Candidate Classification (Zero-Clause Policies)

| Classification | t=0.45 | t=0.475 | t=0.50 |
|---------------|--------|---------|--------|
| numbered_item | 41 | 22 | 5 |
| other | 21 | 12 | 0 |
| real_heading | 136 | 50 | 0 |
| short_label | 2 | 0 | 0 |

## False-Positive Risk Assessment

- **t=0.45:** 0 TOC candidates (0.0%), 0 list/item candidates (0.0%) out of 200 total
- **t=0.475:** 0 TOC candidates (0.0%), 0 list/item candidates (0.0%) out of 84 total
- **t=0.5:** 0 TOC candidates (0.0%), 0 list/item candidates (0.0%) out of 5 total

## Gold Heading Scorer Eval Results

| Threshold | Precision | Recall | F1 | FP | FN | Status |
|-----------|-----------|--------|----|----|-----|--------|
| 0.45 | 60.8% | 62.1% | 61.4 | 129 | 122 | 1/20 passed |
| 0.475 | 73.3% | 61.5% | 66.9 | 72 | 124 | 4/20 passed |
| 0.5 | 94.2% | 60.6% | 73.8 | 12 | 127 | 14/20 passed |

## Top 20 Newly Accepted Candidates (across all thresholds)

### Threshold 0.45

| # | Slug | Text | Score | Page | Classification |
|---|------|------|-------|------|----------------|
| 1 | 03_care_health_assure_critical_illness_p | O.	Benefits	Payment	Basis | 0.6485 | 10 | numbered_item |
| 2 | 08_bajaj_allianz_bajaj_allianz_family_he | S. No.Item | 0.6074 | 20 | numbered_item |
| 3 | 08_bajaj_allianz_bajaj_allianz_extra_car | S. No. Item | 0.5833 | 22 | numbered_item |
| 4 | 05_niva_bupa_niva_bupa_health_plus | S. No. Disease | 0.5017 | 122 | numbered_item |
| 5 | 05_niva_bupa_niva_bupa_health_plus | S. No. Disease | 0.5017 | 122 | numbered_item |
| 6 | 09_hdfc_ergo_hdfc_ergo_critical_illness_ | I. Contact Us | 0.499 | 15 | numbered_item |
| 7 | 19_liberty_liberty_79fc880c_2c03_e5e9_3a | 10.Renewal | 0.4987 | 14 | real_heading |
| 8 | 14_universal_sompo_universal_sompo_group | 10.Migration | 0.4978 | 11 | real_heading |
| 9 | 18_cholamandalam_cholamandalam_chola_cla | 27.Migration | 0.4978 | 19 | real_heading |
| 10 | 12_iffco_tokio_iffco_tokio_group_medishi | 20. Illness | 0.4976 | 3 | real_heading |
| 11 | 02_star_health_star_health_star_group_he | 7. Cancellation: | 0.4975 | 18 | real_heading |
| 12 | 04_icici_lombard_icici_lombard_health_ca | 0.25 years | 0.4974 | 11 | numbered_item |
| 13 | 09_hdfc_ergo_hdfc_ergo_protector_rider | Section 5. Claim Procedure | 0.4971 | 8 | real_heading |
| 14 | 12_iffco_tokio_iffco_tokio_family_health | 8. Migration | 0.4967 | 35 | real_heading |
| 15 | 12_iffco_tokio_iffco_tokio_family_health | 8. Migration | 0.4967 | 35 | real_heading |
| 16 | 10_tata_aig_tata_aig_wellsurance_family_ | POLICY WORDINGS | 0.4964 | 1 | real_heading |
| 17 | 20_sbi_general_sbi_retail_health_pw | 1 | 0.4957 | 5 | other |
| 18 | 05_niva_bupa_niva_bupa_health_pulse | 6. Exclusions | 0.4947 | 22 | real_heading |
| 19 | 02_star_health_star_group_accident_insur | 2. Permanent Total Disablement - Benefit 2 | 0.4944 | 3 | real_heading |
| 20 | 18_cholamandalam_cholamandalam_chola_cla | 28.Migration | 0.4942 | 23 | real_heading |

### Threshold 0.475

| # | Slug | Text | Score | Page | Classification |
|---|------|------|-------|------|----------------|
| 1 | 03_care_health_assure_critical_illness_p | O.	Benefits	Payment	Basis | 0.6485 | 10 | numbered_item |
| 2 | 08_bajaj_allianz_bajaj_allianz_family_he | S. No.Item | 0.6074 | 20 | numbered_item |
| 3 | 08_bajaj_allianz_bajaj_allianz_extra_car | S. No. Item | 0.5833 | 22 | numbered_item |
| 4 | 05_niva_bupa_niva_bupa_health_plus | S. No. Disease | 0.5017 | 122 | numbered_item |
| 5 | 05_niva_bupa_niva_bupa_health_plus | S. No. Disease | 0.5017 | 122 | numbered_item |
| 6 | 09_hdfc_ergo_hdfc_ergo_critical_illness_ | I. Contact Us | 0.499 | 15 | numbered_item |
| 7 | 19_liberty_liberty_79fc880c_2c03_e5e9_3a | 10.Renewal | 0.4987 | 14 | real_heading |
| 8 | 14_universal_sompo_universal_sompo_group | 10.Migration | 0.4978 | 11 | real_heading |
| 9 | 18_cholamandalam_cholamandalam_chola_cla | 27.Migration | 0.4978 | 19 | real_heading |
| 10 | 12_iffco_tokio_iffco_tokio_group_medishi | 20. Illness | 0.4976 | 3 | real_heading |
| 11 | 02_star_health_star_health_star_group_he | 7. Cancellation: | 0.4975 | 18 | real_heading |
| 12 | 04_icici_lombard_icici_lombard_health_ca | 0.25 years | 0.4974 | 11 | numbered_item |
| 13 | 09_hdfc_ergo_hdfc_ergo_protector_rider | Section 5. Claim Procedure | 0.4971 | 8 | real_heading |
| 14 | 12_iffco_tokio_iffco_tokio_family_health | 8. Migration | 0.4967 | 35 | real_heading |
| 15 | 12_iffco_tokio_iffco_tokio_family_health | 8. Migration | 0.4967 | 35 | real_heading |
| 16 | 10_tata_aig_tata_aig_wellsurance_family_ | POLICY WORDINGS | 0.4964 | 1 | real_heading |
| 17 | 20_sbi_general_sbi_retail_health_pw | 1 | 0.4957 | 5 | other |
| 18 | 05_niva_bupa_niva_bupa_health_pulse | 6. Exclusions | 0.4947 | 22 | real_heading |
| 19 | 02_star_health_star_group_accident_insur | 2. Permanent Total Disablement - Benefit 2 | 0.4944 | 3 | real_heading |
| 20 | 18_cholamandalam_cholamandalam_chola_cla | 28.Migration | 0.4942 | 23 | real_heading |

### Threshold 0.5

| # | Slug | Text | Score | Page | Classification |
|---|------|------|-------|------|----------------|
| 1 | 03_care_health_assure_critical_illness_p | O.	Benefits	Payment	Basis | 0.6485 | 10 | numbered_item |
| 2 | 08_bajaj_allianz_bajaj_allianz_family_he | S. No.Item | 0.6074 | 20 | numbered_item |
| 3 | 08_bajaj_allianz_bajaj_allianz_extra_car | S. No. Item | 0.5833 | 22 | numbered_item |
| 4 | 05_niva_bupa_niva_bupa_health_plus | S. No. Disease | 0.5017 | 122 | numbered_item |
| 5 | 05_niva_bupa_niva_bupa_health_plus | S. No. Disease | 0.5017 | 122 | numbered_item |

## Sample Policy Details

For each of the 20 Phase B sample policies, this shows how many headings would be accepted at each threshold.

| Slug | t=0.45 | t=0.475 | t=0.50 | TOC risk | List risk |
|------|--------|---------|--------|----------|-----------|
| 02_star_health_star_health_star_group_health_ | 1 | 1 | 0 | 0 | 1 |
| 03_care_health_care_freedom_policy | 4 | 1 | 0 | 1 | 0 |
| 04_icici_lombard_icici_lombard_group_take_car | 0 | 0 | 0 | 0 | 0 |
| 05_niva_bupa_niva_bupa_health_plus | 3 | 2 | 2 | 0 | 2 |
| 05_niva_bupa_niva_bupa_health_pulse | 5 | 2 | 0 | 1 | 0 |
| 07_oriental_insurance_oriental_oriental_secur | 0 | 0 | 0 | 0 | 0 |
| 08_bajaj_allianz_bajaj_allianz_family_health_ | 1 | 1 | 1 | 0 | 1 |
| 09_hdfc_ergo_hdfc_ergo_my_optima_secure | 6 | 0 | 0 | 1 | 0 |
| 11_aditya_birla_aditya_birla_activ_health_202 | 0 | 0 | 0 | 0 | 0 |
| 12_iffco_tokio_iffco_tokio_family_health_prot | 4 | 3 | 0 | 0 | 0 |
| 12_iffco_tokio_iffco_tokio_family_health_prot | 4 | 3 | 0 | 0 | 0 |
| 13_future_generali_future_generali_future_poo | 0 | 0 | 0 | 0 | 0 |
| 14_universal_sompo_universal_sompo_csc_comple | 0 | 0 | 0 | 0 | 0 |
| 16_kotak_mahindra_kotak_kotak_group_hospital_ | 0 | 0 | 0 | 0 | 0 |
| 18_cholamandalam_cholamandalam_chola_classic_ | 6 | 2 | 0 | 0 | 0 |
| 19_liberty_liberty_79fc880c_2c03_e5e9_3a02_dc | 4 | 1 | 0 | 1 | 0 |
| 21_royal_sundaram_royal_sundaram_ace_health_a | 2 | 1 | 0 | 0 | 2 |
| 22_edelweiss_edelweiss_group_corona_pw | 18 | 0 | 0 | 6 | 0 |
| non_policy_wordings_nivabupa_health_recharge_ | 0 | 0 | 0 | 0 | 0 |
| tata_aig_arogya_sanjeevani | 2 | 0 | 0 | 0 | 2 |

## Recommendation

### Data-Driven Assessment

- **t=0.50 (current):** 0/132 zero-clause policies have ≥1 heading
- **t=0.475:** 45/132 policies gain ≥1 heading (+45 from t=0.50)
- **t=0.45:** 59/132 policies gain ≥1 heading (+59 from t=0.50)
- FP ratio at t=0.45: 48.0% of accepted candidates are TOC/list/table noise
- FP ratio at t=0.475: 52.4%

### Recommendation

**Threshold change only with TOC/list suppression.**

Threshold 0.45 helps 59 additional policies. FP ratio is 48.0% — moderate noise. Add TOC-dot detection and list-item suppression before or alongside threshold change.

### Next Steps

1. Lower heading threshold from 0.50 to 0.45.
2. Verify no regression on 20 gold policies (gold heading eval must not regress).
3. Run full DSE-020 re-execution to confirm zero-clause reduction.

### Warning

**Do NOT commit gold eval temp files or interim scorer outputs.** The `data/interim/dse024/` directory contains temporary generated heading_candidates.json files that should be cleaned up after review. Only the final reports in `data/reports/` should be committed.