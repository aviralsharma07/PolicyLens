# DSE-024 Phase B: Zero-Clause Sample Inspection

**Date:** 2026-06-04
**Sample Size:** 20

## Per-Policy Summary

| # | Slug | Category | Insurer | Pg | Best Score | Root Cause | Thresh 0.45 Helps | FP Risk | Real Hdgs in Top 20 |
|---|------|----------|---------|----|------------|------------|-------------------|---------|---------------------|
| 1 | 05_niva_bupa_niva_bupa_health_plus | HEADING_MISS | Niva_Bupa | 126 | 0.469 | missing_feature_spacing | yes | high_risk_5_fp_of_5 | 11 |
| 2 | non_policy_wordings_nivabupa_health_recharge_prosp | NON_POLICY | non_policy_wordings | 42 | 0.4198 | non_policy_should_exclude | no | not_applicable_threshold_wont_ | 15 |
| 3 | 12_iffco_tokio_iffco_tokio_family_health_protector | DUPLICATE | IFFCO_Tokio | 47 | 0.4967 | duplicate_should_skip | yes | low_risk_all_at_045_are_headin | 11 |
| 4 | 09_hdfc_ergo_hdfc_ergo_my_optima_secure | HEADING_MISS | HDFC_ERGO | 42 | 0.4699 | threshold_too_high | yes | low_risk_all_at_045_are_headin | 20 |
| 5 | 02_star_health_star_health_star_group_health_insur | HEADING_MISS | Star_Health | 50 | 0.4867 | threshold_too_high | yes | low_risk_all_at_045_are_headin | 17 |
| 6 | 11_aditya_birla_aditya_birla_activ_health_2021 | HEADING_MISS | Aditya_Birla | 67 | 0.3667 | needs_manual_review | no | not_applicable_threshold_wont_ | 4 |
| 7 | 13_future_generali_future_generali_future_poorna_s | HEADING_MISS | Future_Generali | 45 | 0.368 | missing_feature_numbered_heading | no | not_applicable_threshold_wont_ | 0 |
| 8 | 16_kotak_mahindra_kotak_kotak_group_hospital_cash | HEADING_MISS | Kotak_Mahindra | 30 | 0.35 | missing_feature_all_caps | no | not_applicable_threshold_wont_ | 2 |
| 9 | tata_aig_arogya_sanjeevani | HEADING_MISS | Tata_AIG | 28 | 0.4738 | threshold_too_high | yes | low_risk_all_at_045_are_headin | 12 |
| 10 | 04_icici_lombard_icici_lombard_group_take_care_ins | HEADING_MISS | ICICI_Lombard | 41 | 0.4481 | needs_manual_review | no | not_applicable_threshold_wont_ | 7 |
| 11 | 08_bajaj_allianz_bajaj_allianz_family_health_care | HEADING_MISS | Bajaj_Allianz | 37 | 0.3862 | needs_manual_review | no | not_applicable_threshold_wont_ | 12 |
| 12 | 12_iffco_tokio_iffco_tokio_family_health_protector | HEADING_MISS | IFFCO_Tokio | 47 | 0.4967 | threshold_too_high | yes | low_risk_all_at_045_are_headin | 11 |
| 13 | 07_oriental_insurance_oriental_oriental_secure_cre | HEADING_MISS | Oriental_Insurance | 44 | 0.4194 | missing_feature_spacing | no | not_applicable_threshold_wont_ | 16 |
| 14 | 14_universal_sompo_universal_sompo_csc_complete_he | HEADING_MISS | Universal_Sompo | 40 | 0.2 | needs_manual_review | no | not_applicable_threshold_wont_ | 0 |
| 15 | 21_royal_sundaram_royal_sundaram_ace_health_advant | HEADING_MISS | Royal_Sundaram | 56 | 0.4817 | threshold_too_high | yes | low_risk_all_at_045_are_headin | 11 |
| 16 | 03_care_health_care_freedom_policy | HEADING_MISS | Care_Health | 45 | 0.4905 | threshold_too_high | yes | low_risk_all_at_045_are_headin | 16 |
| 17 | 19_liberty_liberty_79fc880c_2c03_e5e9_3a02_dc75130 | HEADING_MISS | Liberty | 46 | 0.4987 | threshold_too_high | yes | low_risk_all_at_045_are_headin | 18 |
| 18 | 18_cholamandalam_cholamandalam_chola_classic_healt | HEADING_MISS | Cholamandalam | 35 | 0.4942 | threshold_too_high | yes | low_risk_all_at_045_are_headin | 20 |
| 19 | 22_edelweiss_edelweiss_group_corona_pw | HEADING_MISS | Edelweiss | 17 | 0.4639 | needs_manual_review | yes | high_risk_18_fp_of_18 | 0 |
| 20 | 05_niva_bupa_niva_bupa_health_pulse | HEADING_MISS | Niva_Bupa | 63 | 0.4947 | threshold_too_high | yes | medium_risk_2_fp_of_8 | 11 |

## Pattern Analysis

- **Root cause distribution:**
  - threshold_too_high: 9
  - needs_manual_review: 5
  - missing_feature_spacing: 2
  - non_policy_should_exclude: 1
  - duplicate_should_skip: 1
  - missing_feature_numbered_heading: 1
  - missing_feature_all_caps: 1
- **Threshold 0.45 would help:** 12/20 policies
- **Threshold 0.45 would NOT help:** 8/20 policies
- **Real headings at 0.45+ identified:** 41

## Concrete Heading Text Examples (Score >= 0.45)

These are candidates that look like real headings and score at or above 0.45 
but still miss the 0.5 threshold. Lowering the threshold would admit these.

| # | Slug | Text | Score |
|---|------|------|-------|
| 1 | 12_iffco_tokio_iffco_tokio_family_health_prot | 8. Migration | 0.4967 |
| 2 | 12_iffco_tokio_iffco_tokio_family_health_prot | 9. Portability | 0.4878 |
| 3 | 12_iffco_tokio_iffco_tokio_family_health_prot | 3.Co-Payment: - | 0.4833 |
| 4 | 12_iffco_tokio_iffco_tokio_family_health_prot | 12.Moratorium Period | 0.4611 |
| 5 | 09_hdfc_ergo_hdfc_ergo_my_optima_secure | 1. Preamble | 0.4699 |
| 6 | 09_hdfc_ergo_hdfc_ergo_my_optima_secure | 7. Exclusions | 0.4644 |
| 7 | 09_hdfc_ergo_hdfc_ergo_my_optima_secure | 8.11. Migration | 0.4589 |
| 8 | 09_hdfc_ergo_hdfc_ergo_my_optima_secure | 8.10. Portability | 0.4534 |
| 9 | 09_hdfc_ergo_hdfc_ergo_my_optima_secure | 9.7. Premium Tier | 0.4534 |
| 10 | 09_hdfc_ergo_hdfc_ergo_my_optima_secure | 4. Optional Covers | 0.4507 |
| 11 | 02_star_health_star_health_star_group_health_ | 12. Important Note: | 0.4867 |
| 12 | tata_aig_arogya_sanjeevani | 2.Family | 0.4738 |
| 13 | 12_iffco_tokio_iffco_tokio_family_health_prot | 8. Migration | 0.4967 |
| 14 | 12_iffco_tokio_iffco_tokio_family_health_prot | 9. Portability | 0.4878 |
| 15 | 12_iffco_tokio_iffco_tokio_family_health_prot | 3.Co-Payment: - | 0.4833 |

## Per-Policy Deep Inspection

### 05_niva_bupa_niva_bupa_health_plus

- **Category:** HEADING_MISS
- **Insurer:** Niva_Bupa
- **Pages:** 126, **Total candidates:** 5296
- **Body font mode:** 10.08, **Median line length:** 58
- **Best score:** 0.469
- **Best heading-like score:** 0.469
- **Root cause:** `missing_feature_spacing
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** high_risk_5_fp_of_5
- **Heading-like in top 20:** 11

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.469 | 117 | numbered_allcaps_item | 43 SPLINT | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.1552 |
| 2 | 0.4655 | 117 | numbered_allcaps_item | 64 PAN CAN | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.1724 |
| 3 | 0.4621 | 116 | numbered_allcaps_item | 1 BABY FOOD | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.1897 |
| 4 | 0.4586 | 118 | numbered_allcaps_item | 22 TORNIQUET | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.2069 |
| 5 | 0.4552 | 118 | numbered_allcaps_item | 16 X-RAY FILM | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.2241 |
| 6 | 0.4466 | 1 | heading_real | 2.Definitions & Interpretation | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5172 |
| 7 | 0.4379 | 116 | numbered_allcaps_item | 11 LAUNDRY CHARGES | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.3103 |
| 8 | 0.4345 | 117 | numbered_allcaps_item | 49 AMBULANCE COLLAR | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.3276 |
| 9 | 0.4345 | 117 | numbered_allcaps_item | 57 NEBULISATION KIT | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.3276 |
| 10 | 0.4207 | 118 | numbered_allcaps_item | 19 DISINFECTANT LOTIONS | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.3966 |
| 11 | 0.4121 | 80 | heading_probable | 14.Deafness | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.1897 |
| 12 | 0.4086 | 79 | heading_probable | 13.Blindness | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.2069 |
| 13 | 0.3948 | 83 | heading_probable | 27.Pneumonectomy | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.2759 |
| 14 | 0.3914 | 24 | heading_probable | 3.Open Chest CABG | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.2931 |
| 15 | 0.3914 | 77 | heading_probable | 3.Open Chest CABG | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.2931 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 43 SPLINT | 0.469 | 117 |
| 64 PAN CAN | 0.4655 | 117 |
| 1 BABY FOOD | 0.4621 | 116 |
| 22 TORNIQUET | 0.4586 | 118 |
| 16 X-RAY FILM | 0.4552 | 118 |
| 2.Definitions & Interpretation | 0.4466 | 1 |
| 11 LAUNDRY CHARGES | 0.4379 | 116 |
| 49 AMBULANCE COLLAR | 0.4345 | 117 |
| 57 NEBULISATION KIT | 0.4345 | 117 |
| 19 DISINFECTANT LOTIONS | 0.4207 | 118 |

---

### non_policy_wordings_nivabupa_health_recharge_prospectus

- **Category:** NON_POLICY
- **Insurer:** non_policy_wordings
- **Pages:** 42, **Total candidates:** 1794
- **Body font mode:** 11.0, **Median line length:** 53
- **Best score:** 0.4198
- **Best heading-like score:** 0.4198
- **Root cause:** `non_policy_should_exclude
- **Threshold 0.45 would help:** No
- **False-positive risk:** not_applicable_threshold_wont_help
- **Heading-like in top 20:** 15

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4198 | 29 | heading_probable | 10 lac ) | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.1509 |
| 2 | 0.4104 | 35 | heading_probable | 5 L / 7.5 L / 10L / 15L / 25L / 40L / | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0.6981 |
| 3 | 0.4085 | 2 | heading_probable | 2 year term | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.2075 |
| 4 | 0.4085 | 2 | heading_probable | 3 year term | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.2075 |
| 5 | 0.2283 | 29 | other | 1 to 44 yearsNilNil | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3585 |
| 6 | 0.2236 | 36 | heading_probable | E-saver | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0.1321 |
| 7 | 0.2236 | 42 | heading_real | Premium | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.1321 |
| 8 | 0.2208 | 21 | other | 3. Severe Sleep Apnea | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3962 |
| 9 | 0.217 | 24 | other | II. The Policy Number; | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0.4151 |
| 10 | 0.216 | 27 | heading_real | Migration | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.1698 |
| 11 | 0.2123 | 8 | allcaps_short | HIV / AIDS | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0.1887 |
| 12 | 0.2085 | 39 | heading_probable | Sl. No.Item | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0.2075 |
| 13 | 0.2085 | 40 | heading_probable | Sl. No.Item | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0.2075 |
| 14 | 0.2085 | 41 | heading_probable | Sl. No.Item | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0.2075 |
| 15 | 0.2047 | 27 | heading_real | Portability: | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.2264 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 5 L / 7.5 L / 10L / 15L / 25L / 40L / | 0.4104 | 35 |
| 10 lac ) | 0.4198 | 29 (weak_signal) |
| 2 year term | 0.4085 | 2 (weak_signal) |
| 3 year term | 0.4085 | 2 (weak_signal) |
| E-saver | 0.2236 | 36 (weak_signal) |
| Premium | 0.2236 | 42 (weak_signal) |
| Migration | 0.216 | 27 (weak_signal) |
| HIV / AIDS | 0.2123 | 8 (weak_signal) |
| Sl. No.Item | 0.2085 | 39 (weak_signal) |
| Portability: | 0.2047 | 27 (weak_signal) |

---

### 12_iffco_tokio_iffco_tokio_family_health_protector_irdai

- **Category:** DUPLICATE
- **Insurer:** IFFCO_Tokio
- **Pages:** 47, **Total candidates:** 2133
- **Body font mode:** 11.04, **Median line length:** 45
- **Best score:** 0.4967
- **Best heading-like score:** 0.4967
- **Root cause:** `duplicate_should_skip
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** low_risk_all_at_045_are_headings
- **Heading-like in top 20:** 11

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4967 | 35 | heading_real | 8. Migration | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2667 |
| 2 | 0.4878 | 35 | heading_real | 9. Portability | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.3111 |
| 3 | 0.4833 | 31 | heading_real | 3.Co-Payment: - | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.3333 |
| 4 | 0.4611 | 36 | heading_real | 12.Moratorium Period | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4444 |
| 5 | 0.4156 | 44 | numbered_allcaps_item | 49 AMBULANCE COLLAR | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.4222 |
| 6 | 0.4144 | 34 | heading_real | 6. Fraud | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.1778 |
| 7 | 0.3989 | 28 | heading_real | 2.     Disease Management Program: | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.7556 |
| 8 | 0.3878 | 34 | heading_real | 7.Cancellation | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3111 |
| 9 | 0.3878 | 36 | heading_real | 15. Nomination | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3111 |
| 10 | 0.3833 | 39 | heading_real | 31. Arbitration | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3333 |
| 11 | 0.3733 | 43 | numbered_allcaps_item | 5 BUDS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1333 |
| 12 | 0.3733 | 45 | numbered_allcaps_item | 4 CAPS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1333 |
| 13 | 0.3733 | 45 | numbered_allcaps_item | 6 COMB | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1333 |
| 14 | 0.3733 | 45 | numbered_allcaps_item | 9 GOWN | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1333 |
| 15 | 0.3689 | 45 | numbered_allcaps_item | 60 MASK | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1556 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 8. Migration | 0.4967 | 35 |
| 9. Portability | 0.4878 | 35 |
| 3.Co-Payment: - | 0.4833 | 31 |
| 12.Moratorium Period | 0.4611 | 36 |
| 49 AMBULANCE COLLAR | 0.4156 | 44 |
| 6. Fraud | 0.4144 | 34 |
| 2.     Disease Management Program: | 0.3989 | 28 |
| 7.Cancellation | 0.3878 | 34 |
| 15. Nomination | 0.3878 | 36 |
| 31. Arbitration | 0.3833 | 39 |

---

### 09_hdfc_ergo_hdfc_ergo_my_optima_secure

- **Category:** HEADING_MISS
- **Insurer:** HDFC_ERGO
- **Pages:** 42, **Total candidates:** 1917
- **Body font mode:** 9.94, **Median line length:** 73
- **Best score:** 0.4699
- **Best heading-like score:** 0.4699
- **Root cause:** `threshold_too_high
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** low_risk_all_at_045_are_headings
- **Heading-like in top 20:** 20

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4699 | 3 | heading_probable | 1. Preamble | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.1507 |
| 2 | 0.4644 | 14 | heading_probable | 7. Exclusions | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.1781 |
| 3 | 0.4589 | 22 | heading_probable | 8.11. Migration | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.2055 |
| 4 | 0.4534 | 22 | heading_probable | 8.10. Portability | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.2329 |
| 5 | 0.4534 | 28 | heading_probable | 9.7. Premium Tier | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.2329 |
| 6 | 0.4507 | 6 | heading_probable | 4. Optional Covers | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.2466 |
| 7 | 0.4479 | 12 | heading_probable | 6. Claims Procedure | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.2603 |
| 8 | 0.4397 | 20 | heading_probable | 8.6. Moratorium Period | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.3014 |
| 9 | 0.4288 | 6 | heading_probable | 3.8. Cumulative Bonus (CB) | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.3562 |
| 10 | 0.4205 | 3 | heading_probable | 3.1. Hospitalization Expenses | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.3973 |
| 11 | 0.3726 | 21 | heading_probable | 8.7. Fraud | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0.137 |
| 12 | 0.3644 | 27 | heading_probable | 9.4. Loadings | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0.1781 |
| 13 | 0.3616 | 27 | heading_probable | 9.3. Geography | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0.1918 |
| 14 | 0.3616 | 36 | heading_probable | 12. Contact Us | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0.1918 |
| 15 | 0.3562 | 3 | heading_probable | 3. Base Coverage | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0.2192 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 1. Preamble | 0.4699 | 3 |
| 7. Exclusions | 0.4644 | 14 |
| 8.11. Migration | 0.4589 | 22 |
| 8.10. Portability | 0.4534 | 22 |
| 9.7. Premium Tier | 0.4534 | 28 |
| 4. Optional Covers | 0.4507 | 6 |
| 6. Claims Procedure | 0.4479 | 12 |
| 8.6. Moratorium Period | 0.4397 | 20 |
| 3.8. Cumulative Bonus (CB) | 0.4288 | 6 |
| 3.1. Hospitalization Expenses | 0.4205 | 3 |

---

### 02_star_health_star_health_star_group_health_insurance_benefit_plus

- **Category:** HEADING_MISS
- **Insurer:** Star_Health
- **Pages:** 50, **Total candidates:** 2560
- **Body font mode:** 12.0, **Median line length:** 60
- **Best score:** 0.4867
- **Best heading-like score:** 0.4867
- **Root cause:** `threshold_too_high
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** low_risk_all_at_045_are_headings
- **Heading-like in top 20:** 17

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4867 | 44 | heading_probable | 12. Important Note: | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0.3167 |
| 2 | 0.4467 | 17 | heading_real | 1. Accidental Death – Benefit 1 | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5167 |
| 3 | 0.4367 | 13 | numbered_bold_body | 21. HIV DUE TO BLOOD TRANSFUSION AND OCCUPATIONALLY ACQ | 1 | 1 | 0 | 1 | 0 | 0 | 1 | 1.0667 |
| 4 | 0.4367 | 20 | heading_real | Section 1: Sickness Hospital Cash: | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5667 |
| 5 | 0.4367 | 20 | heading_real | Section 2: Accident Hospital Cash: | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5667 |
| 6 | 0.4167 | 44 | heading_real | 14.Notices | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.1667 |
| 7 | 0.41 | 17 | heading_real | 2. Permanent Total Disablement - Benefit 2 | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.7 |
| 8 | 0.4067 | 27 | heading_real | 8. MEDICAL EXPENSES IRRESPECTIVE OF AN ADMISSIBLE PERSO | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 1.2167 |
| 9 | 0.4 | 17 | heading_probable | 3 Critical Illnesses     6 Critical Illnesses | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0.75 |
| 10 | 0.4 | 44 | heading_probable | 16. Grievances: | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.25 |
| 11 | 0.3867 | 20 | heading_probable | I. Mandatory Cover: | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3167 |
| 12 | 0.3867 | 33 | heading_probable | 2. Claim Settlement | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3167 |
| 13 | 0.3867 | 44 | heading_probable | 15.Customer Service | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3167 |
| 14 | 0.3833 | 17 | heading_probable | 9 Critical Illnesses | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3333 |
| 15 | 0.3367 | 24 | heading_probable | 15 days and above 5 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0.3167 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 12. Important Note: | 0.4867 | 44 (weak_signal) |
| 1. Accidental Death – Benefit 1 | 0.4467 | 17 (weak_signal) |
| 21. HIV DUE TO BLOOD TRANSFUSION AND OCCUPATIONALLY ACQUIRED | 0.4367 | 13 (weak_signal) |
| Section 1: Sickness Hospital Cash: | 0.4367 | 20 (weak_signal) |
| Section 2: Accident Hospital Cash: | 0.4367 | 20 (weak_signal) |
| 14.Notices | 0.4167 | 44 (weak_signal) |
| 2. Permanent Total Disablement - Benefit 2 | 0.41 | 17 (weak_signal) |
| 8. MEDICAL EXPENSES IRRESPECTIVE OF AN ADMISSIBLE PERSONAL A | 0.4067 | 27 (weak_signal) |
| 3 Critical Illnesses     6 Critical Illnesses | 0.4 | 17 (weak_signal) |
| Waiting Period : | 0.2967 | 19 (weak_signal) |

---

### 11_aditya_birla_aditya_birla_activ_health_2021

- **Category:** HEADING_MISS
- **Insurer:** Aditya_Birla
- **Pages:** 67, **Total candidates:** 6916
- **Body font mode:** 8.5, **Median line length:** 24
- **Best score:** 0.3667
- **Best heading-like score:** 0.3667
- **Root cause:** `needs_manual_review
- **Threshold 0.45 would help:** No
- **False-positive risk:** not_applicable_threshold_wont_help
- **Heading-like in top 20:** 4

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.3667 | 43 | heading_probable | 25. Grace Period | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.6667 |
| 2 | 0.35 | 43 | heading_probable | 28. Policy Dispute | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.75 |
| 3 | 0.35 | 50 | numbered_allcaps_item | 5 BUDS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.25 |
| 4 | 0.35 | 51 | numbered_allcaps_item | 4 CAPS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.25 |
| 5 | 0.35 | 51 | numbered_allcaps_item | 6 COMB | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.25 |
| 6 | 0.35 | 51 | numbered_allcaps_item | 9 GOWN | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.25 |
| 7 | 0.3417 | 1 | heading_probable | Section A. PREAMBLE | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.7917 |
| 8 | 0.3417 | 51 | numbered_allcaps_item | 60 MASK | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.2917 |
| 9 | 0.3417 | 52 | numbered_allcaps_item | 8 GAUZE | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.2917 |
| 10 | 0.3333 | 39 | heading_probable | 5. Fraud | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0.3333 |
| 11 | 0.3333 | 52 | numbered_allcaps_item | 21 APRON | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.3333 |
| 12 | 0.325 | 50 | numbered_allcaps_item | 19 SLINGS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.375 |
| 13 | 0.325 | 51 | numbered_allcaps_item | 56 GLOVES | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.375 |
| 14 | 0.325 | 52 | numbered_allcaps_item | 3 EYE PAD | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.375 |
| 15 | 0.325 | 52 | numbered_allcaps_item | 18 COTTON | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.375 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 25. Grace Period | 0.3667 | 43 |
| 28. Policy Dispute | 0.35 | 43 |
| Section A. PREAMBLE | 0.3417 | 1 (weak_signal) |
| 5. Fraud | 0.3333 | 39 (weak_signal) |
| 16.  Nomination: | 0.2667 | 41 (weak_signal) |
| 14. Free Look Period | 0.1833 | 41 (weak_signal) |
| Section D. EXCLUSIONS | 0.175 | 34 (weak_signal) |
| Section B. DEFINITIONS | 0.1667 | 1 (weak_signal) |
| 11.  Moratorium Period | 0.1667 | 40 (weak_signal) |
| Section I: Basic Covers: | 0.15 | 7 (weak_signal) |

---

### 13_future_generali_future_generali_future_poorna_suraksha_group_0bc8ea4f

- **Category:** HEADING_MISS
- **Insurer:** Future_Generali
- **Pages:** 45, **Total candidates:** 2668
- **Body font mode:** 9.96, **Median line length:** 50
- **Best score:** 0.368
- **Best heading-like score:** 0.368
- **Root cause:** `missing_feature_numbered_heading
- **Threshold 0.45 would help:** No
- **False-positive risk:** not_applicable_threshold_wont_help
- **Heading-like in top 20:** 0

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.368 | 34 | numbered_allcaps_item | 51. ERCP | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.16 |
| 2 | 0.368 | 39 | numbered_allcaps_item | 5.  BUDS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.16 |
| 3 | 0.368 | 40 | numbered_allcaps_item | 4.  CAPS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.16 |
| 4 | 0.368 | 40 | numbered_allcaps_item | 6.  COMB | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.16 |
| 5 | 0.368 | 40 | numbered_allcaps_item | 9.  GOWN | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.16 |
| 6 | 0.364 | 4 | table_data | 10 Policy | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.18 |
| 7 | 0.364 | 39 | numbered_allcaps_item | 60.  MASK | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.18 |
| 8 | 0.364 | 40 | numbered_allcaps_item | 21.  HVAC | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.18 |
| 9 | 0.364 | 41 | numbered_allcaps_item | 8.  GAUZE | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.18 |
| 10 | 0.36 | 35 | numbered_allcaps_item | 119. TURBT | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.2 |
| 11 | 0.36 | 41 | numbered_allcaps_item | 21.  APRON | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.2 |
| 12 | 0.356 | 39 | numbered_allcaps_item | 19.  SLINGS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.22 |
| 13 | 0.356 | 39 | numbered_allcaps_item | 36.  SPACER | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.22 |
| 14 | 0.356 | 39 | numbered_allcaps_item | 43.  SPLINT | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.22 |
| 15 | 0.356 | 39 | numbered_allcaps_item | 56.  GLOVES | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.22 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 33.  EXPENSES RELATED TO PRESCRIPTION ON DISCHARGE | 0.3 | 40 (weak_signal) |
| 2.  HOSPITALISATION FOR EVALUATION/ DIAGNOSTIC PURPOSE | 0.284 | 41 (weak_signal) |
| 51. ERCP | 0.368 | 34 (weak_signal) |
| 5.  BUDS | 0.368 | 39 (weak_signal) |
| 4.  CAPS | 0.368 | 40 (weak_signal) |
| 6.  COMB | 0.368 | 40 (weak_signal) |
| 9.  GOWN | 0.368 | 40 (weak_signal) |
| 10 Policy | 0.364 | 4 (weak_signal) |
| 60.  MASK | 0.364 | 39 (weak_signal) |
| 21.  HVAC | 0.364 | 40 (weak_signal) |

---

### 16_kotak_mahindra_kotak_kotak_group_hospital_cash

- **Category:** HEADING_MISS
- **Insurer:** Kotak_Mahindra
- **Pages:** 30, **Total candidates:** 6301
- **Body font mode:** 8.5, **Median line length:** 3
- **Best score:** 0.35
- **Best heading-like score:** 0.35
- **Root cause:** `missing_feature_all_caps
- **Threshold 0.45 would help:** No
- **False-positive risk:** not_applicable_threshold_wont_help
- **Heading-like in top 20:** 2

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.35 | 1 | heading_real | PART I | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 2.0 |
| 2 | 0.1833 | 6 | too_short | • | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.3333 |
| 3 | 0.1833 | 6 | too_short | • | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.3333 |
| 4 | 0.1833 | 6 | too_short | • | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.3333 |
| 5 | 0.1167 | 12 | heading_real | PART III | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 2.6667 |
| 6 | 0.05 | 8 | too_short | I I | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 7 | 0.05 | 8 | too_short | I I | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 8 | 0.0333 | 1 | boilerplate_header_footer | e | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.3333 |
| 9 | -0.05 | 5 | too_short | Sr. | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 10 | -0.05 | 5 | too_short | No. | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 11 | -0.05 | 10 | too_short | Sr. | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 12 | -0.05 | 10 | too_short | No. | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 13 | -0.0667 | 1 | too_short | g | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.3333 |
| 14 | -0.0667 | 1 | too_short | n | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.3333 |
| 15 | -0.0667 | 1 | too_short | i | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.3333 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| PART I | 0.35 | 1 |
| PART III | 0.1167 | 12 (weak_signal) |

---

### tata_aig_arogya_sanjeevani

- **Category:** HEADING_MISS
- **Insurer:** Tata_AIG
- **Pages:** 28, **Total candidates:** 3847
- **Body font mode:** 9.5, **Median line length:** 21
- **Best score:** 0.4738
- **Best heading-like score:** 0.4738
- **Root cause:** `threshold_too_high
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** low_risk_all_at_045_are_headings
- **Heading-like in top 20:** 12

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4738 | 6 | heading_probable | 2.Family | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0.381 |
| 2 | 0.4619 | 28 | allcaps_short | TATA | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0.1905 |
| 3 | 0.4452 | 3 | heading_real | 18.Hospital | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5238 |
| 4 | 0.4357 | 5 | heading_real | 38. Renewal: | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5714 |
| 5 | 0.4262 | 6 | heading_real | 39. Room Rent | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.619 |
| 6 | 0.4262 | 21 | heading_real | 5. Co-payment | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.619 |
| 7 | 0.4167 | 2 | heading_real | 10. Co-payment | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.6667 |
| 8 | 0.4167 | 15 | heading_real | 10. Migration: | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.6667 |
| 9 | 0.4071 | 16 | heading_real | 11. Portability | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.7143 |
| 10 | 0.3952 | 22 | numbered_allcaps_item | 1 BABY FOOD | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.5238 |
| 11 | 0.3905 | 28 | too_short | m | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0476 |
| 12 | 0.3833 | 5 | heading_probable | 32. Out | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3333 |
| 13 | 0.381 | 14 | too_short | s. | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0952 |
| 14 | 0.3643 | 16 | heading_real | 13. Fraud | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.4286 |
| 15 | 0.3619 | 25 | heading_probable | Item | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.1905 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 2.Family | 0.4738 | 6 (weak_signal) |
| 18.Hospital | 0.4452 | 3 (weak_signal) |
| 38. Renewal: | 0.4357 | 5 (weak_signal) |
| 39. Room Rent | 0.4262 | 6 (weak_signal) |
| 5. Co-payment | 0.4262 | 21 (weak_signal) |
| 10. Co-payment | 0.4167 | 2 (weak_signal) |
| 10. Migration: | 0.4167 | 15 (weak_signal) |
| 11. Portability | 0.4071 | 16 (weak_signal) |
| 1 BABY FOOD | 0.3952 | 22 (weak_signal) |
| 13. Fraud | 0.3643 | 16 (weak_signal) |

---

### 04_icici_lombard_icici_lombard_group_take_care_insurance

- **Category:** HEADING_MISS
- **Insurer:** ICICI_Lombard
- **Pages:** 41, **Total candidates:** 1956
- **Body font mode:** 9.96, **Median line length:** 81
- **Best score:** 0.4481
- **Best heading-like score:** 0.4481
- **Root cause:** `needs_manual_review
- **Threshold 0.45 would help:** No
- **False-positive risk:** not_applicable_threshold_wont_help
- **Heading-like in top 20:** 7

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4481 | 1 | table_data | PART II OF THE POLICY | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.2593 |
| 2 | 0.4383 | 27 | heading_probable | Section C: WELLNESS COVER | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.3086 |
| 3 | 0.4309 | 6 | heading_probable | Section A: HOSPIFUND BENEFIT | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.3457 |
| 4 | 0.4259 | 21 | heading_probable | Section B : OUTPATIENT BENEFIT | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.3704 |
| 5 | 0.363 | 12 | numbered_allcaps_item | IV. ANGIOPLASTY | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1852 |
| 6 | 0.358 | 36 | table_data | 9.Policy Disputes | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2099 |
| 7 | 0.3556 | 25 | table_data | 1.Claims Procedure | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2222 |
| 8 | 0.3556 | 35 | table_data | 7.Free Look Period | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2222 |
| 9 | 0.3531 | 12 | numbered_allcaps_item | II. OPEN CHEST CABG | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.2346 |
| 10 | 0.3506 | 22 | heading_probable | 1. Outpatient Cover: | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0.2469 |
| 11 | 0.3481 | 9 | numbered_allcaps_item | VI. MAJOR HEAD TRAUMA | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.2593 |
| 12 | 0.3432 | 22 | table_data | Section B. Base Benefit | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.284 |
| 13 | 0.3358 | 6 | heading_probable | Section A.1: Base Benefits | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.321 |
| 14 | 0.321 | 19 | heading_probable | 25. Domiciliary Hospitalization. | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0.3951 |
| 15 | 0.3185 | 9 | numbered_allcaps_item | III. PERMANENT PARALYSIS OF LIMBS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.4074 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| PART II OF THE POLICY | 0.4481 | 1 |
| Section C: WELLNESS COVER | 0.4383 | 27 |
| Section A: HOSPIFUND BENEFIT | 0.4309 | 6 |
| Section B : OUTPATIENT BENEFIT | 0.4259 | 21 |
| PORTABILITY BENEFITS | 0.2506 | 33 (weak_signal) |
| POLICY RELATED TERMS AND CONDITIONS | 0.2136 | 34 (weak_signal) |
| SCOPE OF COVER | 0.1654 | 6 (weak_signal) |
| IV. ANGIOPLASTY | 0.363 | 12 (weak_signal) |
| 9.Policy Disputes | 0.358 | 36 (weak_signal) |
| 1.Claims Procedure | 0.3556 | 25 (weak_signal) |

---

### 08_bajaj_allianz_bajaj_allianz_family_health_care

- **Category:** HEADING_MISS
- **Insurer:** Bajaj_Allianz
- **Pages:** 37, **Total candidates:** 2225
- **Body font mode:** 8.0, **Median line length:** 47
- **Best score:** 0.3862
- **Best heading-like score:** 0.3862
- **Root cause:** `needs_manual_review
- **Threshold 0.45 would help:** No
- **False-positive risk:** not_applicable_threshold_wont_help
- **Heading-like in top 20:** 12

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.3862 | 1 | other | Policy Wordings | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0.3191 |
| 2 | 0.3862 | 21 | other | Policy Wordings | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0.3191 |
| 3 | 0.3532 | 12 | table_data | 16. Renewal | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.234 |
| 4 | 0.3532 | 30 | table_data | 16. Renewal | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.234 |
| 5 | 0.3362 | 31 | heading_probable | 25. Nomination: | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0.3191 |
| 6 | 0.3277 | 1 | heading_probable | 4. Road Ambulance | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0.3617 |
| 7 | 0.3202 | 20 | allcaps_short | HIV KIT | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0.1489 |
| 8 | 0.3191 | 9 | heading_probable | 7. Claims Procedure | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4043 |
| 9 | 0.3191 | 27 | heading_probable | 7. Claims Procedure | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4043 |
| 10 | 0.316 | 20 | allcaps_short | LOZENGES | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0.1702 |
| 11 | 0.3149 | 11 | heading_probable | 13. Free Look Period | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4255 |
| 12 | 0.3149 | 29 | heading_probable | 14. Free Look Period | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4255 |
| 13 | 0.3117 | 20 | allcaps_short | URINE BAG | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0.1915 |
| 14 | 0.3106 | 9 | heading_probable | 4. Moratorium Period: | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4468 |
| 15 | 0.3106 | 11 | heading_probable | 12. Cumulative Bonus: | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4468 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 25. Nomination: | 0.3362 | 31 (weak_signal) |
| Policy Wordings | 0.3862 | 1 (weak_signal) |
| 16. Renewal | 0.3532 | 12 (weak_signal) |
| 4. Road Ambulance | 0.3277 | 1 (weak_signal) |
| 7. Claims Procedure | 0.3191 | 9 (weak_signal) |
| 13. Free Look Period | 0.3149 | 11 (weak_signal) |
| 14. Free Look Period | 0.3149 | 29 (weak_signal) |
| 4. Moratorium Period: | 0.3106 | 9 (weak_signal) |
| 12. Cumulative Bonus: | 0.3106 | 11 (weak_signal) |
| 3. Post-Hospitalisation | 0.3021 | 1 (weak_signal) |

---

### 12_iffco_tokio_iffco_tokio_family_health_protector

- **Category:** HEADING_MISS
- **Insurer:** IFFCO_Tokio
- **Pages:** 47, **Total candidates:** 2133
- **Body font mode:** 11.04, **Median line length:** 45
- **Best score:** 0.4967
- **Best heading-like score:** 0.4967
- **Root cause:** `threshold_too_high
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** low_risk_all_at_045_are_headings
- **Heading-like in top 20:** 11

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4967 | 35 | heading_real | 8. Migration | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2667 |
| 2 | 0.4878 | 35 | heading_real | 9. Portability | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.3111 |
| 3 | 0.4833 | 31 | heading_real | 3.Co-Payment: - | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.3333 |
| 4 | 0.4611 | 36 | heading_real | 12.Moratorium Period | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4444 |
| 5 | 0.4156 | 44 | numbered_allcaps_item | 49 AMBULANCE COLLAR | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.4222 |
| 6 | 0.4144 | 34 | heading_real | 6. Fraud | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.1778 |
| 7 | 0.3989 | 28 | heading_real | 2.     Disease Management Program: | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.7556 |
| 8 | 0.3878 | 34 | heading_real | 7.Cancellation | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3111 |
| 9 | 0.3878 | 36 | heading_real | 15. Nomination | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3111 |
| 10 | 0.3833 | 39 | heading_real | 31. Arbitration | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3333 |
| 11 | 0.3733 | 43 | numbered_allcaps_item | 5 BUDS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1333 |
| 12 | 0.3733 | 45 | numbered_allcaps_item | 4 CAPS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1333 |
| 13 | 0.3733 | 45 | numbered_allcaps_item | 6 COMB | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1333 |
| 14 | 0.3733 | 45 | numbered_allcaps_item | 9 GOWN | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1333 |
| 15 | 0.3689 | 45 | numbered_allcaps_item | 60 MASK | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1556 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 8. Migration | 0.4967 | 35 |
| 9. Portability | 0.4878 | 35 |
| 3.Co-Payment: - | 0.4833 | 31 |
| 12.Moratorium Period | 0.4611 | 36 |
| 49 AMBULANCE COLLAR | 0.4156 | 44 |
| 6. Fraud | 0.4144 | 34 |
| 2.     Disease Management Program: | 0.3989 | 28 |
| 7.Cancellation | 0.3878 | 34 |
| 15. Nomination | 0.3878 | 36 |
| 31. Arbitration | 0.3833 | 39 |

---

### 07_oriental_insurance_oriental_oriental_secure_credit

- **Category:** HEADING_MISS
- **Insurer:** Oriental_Insurance
- **Pages:** 44, **Total candidates:** 2178
- **Body font mode:** 11.04, **Median line length:** 49
- **Best score:** 0.4194
- **Best heading-like score:** 0.4194
- **Root cause:** `missing_feature_spacing
- **Threshold 0.45 would help:** No
- **False-positive risk:** not_applicable_threshold_wont_help
- **Heading-like in top 20:** 16

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4194 | 34 | heading_real | Part 4:GENERAL TERMS AND CLAUSES | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.6531 |
| 2 | 0.4143 | 32 | heading_probable | 1.5.1 CLAIM PROCEDURE | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.4286 |
| 3 | 0.3888 | 1 | other | POLICY WORDINGS | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0.3061 |
| 4 | 0.3857 | 31 | heading_probable | 1.4.2CLAIMSSETTLEMENTPROCESS | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.5714 |
| 5 | 0.3776 | 7 | heading_probable | 1.1SECTION I: CRITICAL ILLNESS | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.6122 |
| 6 | 0.3694 | 22 | heading_probable | 1.2SECTION II: PERSONAL ACCIDENT | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.6531 |
| 7 | 0.3592 | 39 | table_data | 20.Renewal | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2041 |
| 8 | 0.351 | 36 | table_data | 18.Age Limit | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2449 |
| 9 | 0.349 | 32 | heading_probable | 1.5SECTION V: CHILD EDUCATION BENEFIT | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.7551 |
| 10 | 0.3429 | 36 | table_data | 17.Sum Insured | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2857 |
| 11 | 0.3408 | 20 | heading_probable | 1.1.3EXCLUSIONS APPLICABLE TO SECTION I | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.7959 |
| 12 | 0.3388 | 40 | heading_probable | 2.Policy Number | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0.3061 |
| 13 | 0.3367 | 25 | heading_probable | 1.2.3EXCLUSIONS APPLICABLE TO SECTION II | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.8163 |
| 14 | 0.3367 | 27 | heading_probable | 1.3SECTION III:  INVOLUNTARY LOSS OF JOB | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.8163 |
| 15 | 0.3327 | 28 | heading_probable | 1.3.2EXCLUSIONS APPLICABLE TO SECTION III | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.8367 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| Part 4:GENERAL TERMS AND CLAUSES | 0.4194 | 34 |
| 1.5.1 CLAIM PROCEDURE | 0.4143 | 32 |
| 1.4.2CLAIMSSETTLEMENTPROCESS | 0.3857 | 31 |
| 1.1SECTION I: CRITICAL ILLNESS | 0.3776 | 7 |
| 1.2SECTION II: PERSONAL ACCIDENT | 0.3694 | 22 |
| 1.5SECTION V: CHILD EDUCATION BENEFIT | 0.349 | 32 (weak_signal) |
| 1.1.3EXCLUSIONS APPLICABLE TO SECTION I | 0.3408 | 20 (weak_signal) |
| 1.2.3EXCLUSIONS APPLICABLE TO SECTION II | 0.3367 | 25 (weak_signal) |
| 1.3SECTION III:  INVOLUNTARY LOSS OF JOB | 0.3367 | 27 (weak_signal) |
| 1.3.2EXCLUSIONS APPLICABLE TO SECTION III | 0.3327 | 28 (weak_signal) |

---

### 14_universal_sompo_universal_sompo_csc_complete_healthcare_insurance

- **Category:** HEADING_MISS
- **Insurer:** Universal_Sompo
- **Pages:** 40, **Total candidates:** 15756
- **Body font mode:** 12.0, **Median line length:** 1
- **Best score:** 0.2
- **Best heading-like score:** 0.0
- **Root cause:** `needs_manual_review
- **Threshold 0.45 would help:** No
- **False-positive risk:** not_applicable_threshold_wont_help
- **Heading-like in top 20:** 0

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.2 | 37 | too_short | t | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 2 | 0.2 | 37 | too_short | r | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 3 | 0.05 | 3 | too_short | T | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 4 | 0.05 | 4 | too_short | w | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 5 | 0.05 | 11 | too_short | C | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 6 | 0.05 | 19 | too_short | E | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 7 | 0.05 | 37 | too_short | l | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 8 | 0.05 | 37 | too_short | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 9 | 0.05 | 37 | too_short | i | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 10 | 0.05 | 37 | too_short | I | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 11 | 0.05 | 37 | too_short | I | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 12 | 0.05 | 37 | too_short | l | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 13 | 0.05 | 37 | too_short | I | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 14 | 0.05 | 37 | too_short | I | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 15 | 0.05 | 37 | too_short | l | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |

---

### 21_royal_sundaram_royal_sundaram_ace_health_advantage_pw

- **Category:** HEADING_MISS
- **Insurer:** Royal_Sundaram
- **Pages:** 56, **Total candidates:** 2888
- **Body font mode:** 9.96, **Median line length:** 41
- **Best score:** 0.4817
- **Best heading-like score:** 0.4817
- **Root cause:** `threshold_too_high
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** low_risk_all_at_045_are_headings
- **Heading-like in top 20:** 11

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4817 | 52 | heading_probable | 10. Indexation | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0.3415 |
| 2 | 0.4622 | 8 | heading_probable | 3. OPEN CHEST CABG | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0.439 |
| 3 | 0.4524 | 8 | heading_probable | 7. MAJOR BURNS – 20% | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0.4878 |
| 4 | 0.4524 | 39 | heading_probable | 1. Ambulance Charges | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0.4878 |
| 5 | 0.4524 | 41 | heading_probable | 7. MAJOR BURNS – 20% | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0.4878 |
| 6 | 0.4122 | 5 | heading_probable | 8 Renewal Benefits | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.439 |
| 7 | 0.4024 | 53 | numbered_allcaps_item | 26 BIRTH CERTIFICATE | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.4878 |
| 8 | 0.3988 | 7 | heading_probable | 1. CANCER OF SPECIFIED SEVERITY | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0.7561 |
| 9 | 0.3988 | 40 | heading_probable | 1. CANCER OF SPECIFIED SEVERITY | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0.7561 |
| 10 | 0.378 | 3 | heading_probable | 4 Waiting Period D-Excl03 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0.6098 |
| 11 | 0.3707 | 52 | numbered_allcaps_item | 5 BUDS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1463 |
| 12 | 0.3707 | 54 | numbered_allcaps_item | 4 CAPS | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1463 |
| 13 | 0.3707 | 54 | numbered_allcaps_item | 6 COMB | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1463 |
| 14 | 0.3707 | 54 | numbered_allcaps_item | 9 GOWN | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1463 |
| 15 | 0.3659 | 53 | numbered_allcaps_item | 60 MASK | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0.1707 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 10. Indexation | 0.4817 | 52 (weak_signal) |
| 3. OPEN CHEST CABG | 0.4622 | 8 (weak_signal) |
| 7. MAJOR BURNS – 20% | 0.4524 | 8 (weak_signal) |
| 1. Ambulance Charges | 0.4524 | 39 (weak_signal) |
| 8 Renewal Benefits | 0.4122 | 5 (weak_signal) |
| 26 BIRTH CERTIFICATE | 0.4024 | 53 (weak_signal) |
| 1. CANCER OF SPECIFIED SEVERITY | 0.3988 | 7 (weak_signal) |
| 4 Waiting Period D-Excl03 | 0.378 | 3 (weak_signal) |
| 8. MAJOR ORGAN /BONE MARROW TRANSPLANT | 0.3646 | 8 (weak_signal) |
| 6. STROKE RESULTING IN PERMANENT SYMPTOMS | 0.35 | 8 (weak_signal) |

---

### 03_care_health_care_freedom_policy

- **Category:** HEADING_MISS
- **Insurer:** Care_Health
- **Pages:** 45, **Total candidates:** 3473
- **Body font mode:** 7.0, **Median line length:** 37
- **Best score:** 0.4905
- **Best heading-like score:** 0.4905
- **Root cause:** `threshold_too_high
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** low_risk_all_at_045_are_headings
- **Heading-like in top 20:** 16

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4905 | 17 | heading_real | 5.1.6 Fraud | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0.2973 |
| 2 | 0.4743 | 2 | heading_real | 2. Definitions | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.3784 |
| 3 | 0.4635 | 18 | heading_real | 5.1.8 Migration: | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4324 |
| 4 | 0.4527 | 18 | heading_real | 5.1.9 Portability: | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4865 |
| 5 | 0.4419 | 27 | heading_probable | 9. Oncology Related: | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0.5405 |
| 6 | 0.4365 | 20 | heading_real | 5.2.3 Policy Disputes | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5676 |
| 7 | 0.4311 | 21 | heading_real | 6.1.2 Claims Procedure | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5946 |
| 8 | 0.4311 | 23 | heading_probable | 6.2 Special Conditions | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0.5946 |
| 9 | 0.4257 | 19 | heading_real | 5.1.14 Free Look Period | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.6216 |
| 10 | 0.4203 | 19 | heading_real | 5.1.12 Moratorium Period | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.6486 |
| 11 | 0.4149 | 6 | heading_probable | 2.2 Specific Definitions: | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0.6757 |
| 12 | 0.4135 | 26 | numbered_allcaps_item | 166. MEATOPLASTY | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.4324 |
| 13 | 0.3986 | 17 | heading_real | 5. General Terms And Clauses | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.7568 |
| 14 | 0.3959 | 45 | allcaps_short | REACH US @ | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0.2703 |
| 15 | 0.3919 | 27 | heading_probable | 232. SURGERY FOR SUI | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.5405 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 5.1.6 Fraud | 0.4905 | 17 |
| 3.1.8 Benefit 8 : Dialysis Cover | 0.327 | 11 (weak_signal) |
| 3.2.2 Optional Cover 2 – Home Care | 0.3162 | 12 (weak_signal) |
| 417. SURGERY OF BUNION449. RECTAL PROLAPSE (DELORME'S | 0.3135 | 30 (weak_signal) |
| 416. TREATMENT OF FOOT DISLOCATION448. RECTAL-MYOMECTOMY | 0.2973 | 30 (weak_signal) |
| 3.2.3 Optional Cover 3 – Health Check+ | 0.2946 | 12 (weak_signal) |
| 1. Preamble:subsequent changes to the same and vice versa. | 0.1365 | 2 (weak_signal) |
| 2. Definitions | 0.4743 | 2 (weak_signal) |
| 5.1.8 Migration: | 0.4635 | 18 (weak_signal) |
| 5.1.9 Portability: | 0.4527 | 18 (weak_signal) |

---

### 19_liberty_liberty_79fc880c_2c03_e5e9_3a02_dc751307afff

- **Category:** HEADING_MISS
- **Insurer:** Liberty
- **Pages:** 46, **Total candidates:** 1849
- **Body font mode:** 12.0, **Median line length:** 39
- **Best score:** 0.4987
- **Best heading-like score:** 0.4987
- **Root cause:** `threshold_too_high
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** low_risk_all_at_045_are_headings
- **Heading-like in top 20:** 18

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4987 | 14 | heading_real | 10.Renewal | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2564 |
| 2 | 0.4577 | 7 | heading_real | Part II : Coverage | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4615 |
| 3 | 0.4577 | 15 | heading_real | 17.Policy Disputes | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4615 |
| 4 | 0.4526 | 1 | heading_real | Part I: Definitions | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4872 |
| 5 | 0.4474 | 9 | heading_real | Part III: Exclusions | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5128 |
| 6 | 0.4474 | 18 | heading_real | 22. Claim Procedure: | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5128 |
| 7 | 0.4423 | 16 | heading_real | 21.Portability Clause | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5385 |
| 8 | 0.4244 | 45 | heading_real | PART OF HOSPITAL'S OWN COSTS AND NOT PAYABLE | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 1.1282 |
| 9 | 0.4231 | 1 | heading_real | Policy Wordings | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.3846 |
| 10 | 0.4167 | 14 | heading_real | 12.Sum Insured Enhancement | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.6667 |
| 11 | 0.4064 | 13 | heading_real | Part IV : Terms & Conditions | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.7179 |
| 12 | 0.4064 | 21 | heading_real | Part V : Discount Parameters | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.7179 |
| 13 | 0.4038 | 16 | heading_real | 19.Notice | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.2308 |
| 14 | 0.3949 | 3 | too_short | “ | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0256 |
| 15 | 0.3885 | 14 | heading_real | 11.Entry Age | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.3077 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| PART OF HOSPITAL'S OWN COSTS AND NOT PAYABLE | 0.4244 | 45 |
| 10.Renewal | 0.4987 | 14 |
| Part II : Coverage | 0.4577 | 7 |
| 17.Policy Disputes | 0.4577 | 15 |
| Part I: Definitions | 0.4526 | 1 |
| Part III: Exclusions | 0.4474 | 9 |
| 22. Claim Procedure: | 0.4474 | 18 |
| 21.Portability Clause | 0.4423 | 16 |
| 12.Sum Insured Enhancement | 0.4167 | 14 |
| Part IV : Terms & Conditions | 0.4064 | 13 |

---

### 18_cholamandalam_cholamandalam_chola_classic_health_individual

- **Category:** HEADING_MISS
- **Insurer:** Cholamandalam
- **Pages:** 35, **Total candidates:** 1902
- **Body font mode:** 9.96, **Median line length:** 43
- **Best score:** 0.4942
- **Best heading-like score:** 0.4942
- **Root cause:** `threshold_too_high
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** low_risk_all_at_045_are_headings
- **Heading-like in top 20:** 20

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4942 | 23 | heading_real | 28.Migration | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2791 |
| 2 | 0.4802 | 23 | heading_real | 27.Portability: | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.3488 |
| 3 | 0.4663 | 9 | heading_real | 3.Cumulative Bonus | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4186 |
| 4 | 0.4663 | 17 | heading_real | 5.Free Look Period | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4186 |
| 5 | 0.4663 | 20 | heading_real | 19.Claim Procedure | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4186 |
| 6 | 0.457 | 18 | heading_real | 7. Moratorium Period | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4651 |
| 7 | 0.443 | 13 | heading_probable | V.  E X C L U S I O N S | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0.5349 |
| 8 | 0.4337 | 9 | heading_probable | IV. D E F I N I T I O N S | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0.5814 |
| 9 | 0.4302 | 1 | heading_real | Policy Wordings | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.3488 |
| 10 | 0.4302 | 2 | heading_real | Policy Wordings | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.3488 |
| 11 | 0.4302 | 3 | heading_real | Policy Wordings | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.3488 |
| 12 | 0.4302 | 4 | heading_real | Policy Wordings | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.3488 |
| 13 | 0.4302 | 5 | heading_real | Policy Wordings | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.3488 |
| 14 | 0.4302 | 6 | heading_real | Policy Wordings | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.3488 |
| 15 | 0.4302 | 7 | heading_real | Policy Wordings | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.3488 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 28.Migration | 0.4942 | 23 |
| 27.Portability: | 0.4802 | 23 |
| 5.Free Look Period | 0.4663 | 17 |
| 19.Claim Procedure | 0.4663 | 20 |
| 7. Moratorium Period | 0.457 | 18 |
| 26.Sum Insured Enhancement | 0.4291 | 23 |
| 13.Fraud | 0.4128 | 19 |
| 12.Nomination | 0.3895 | 18 |
| 31.Disclaimer | 0.3895 | 25 |
| 30.Arbitration | 0.3849 | 25 |

---

### 22_edelweiss_edelweiss_group_corona_pw

- **Category:** HEADING_MISS
- **Insurer:** Edelweiss
- **Pages:** 17, **Total candidates:** 2495
- **Body font mode:** 10.0, **Median line length:** 61
- **Best score:** 0.4639
- **Best heading-like score:** 0.4639
- **Root cause:** `needs_manual_review
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** high_risk_18_fp_of_18
- **Heading-like in top 20:** 0

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4639 | 2 | table_data | 1. PREAMBLE | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.1803 |
| 2 | 0.4639 | 3 | table_data | 1. PREAMBLE | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.1803 |
| 3 | 0.4639 | 4 | table_data | 1. PREAMBLE | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.1803 |
| 4 | 0.4639 | 5 | table_data | 1. PREAMBLE | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.1803 |
| 5 | 0.4639 | 6 | table_data | 1. PREAMBLE | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.1803 |
| 6 | 0.4639 | 7 | table_data | 1. PREAMBLE | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.1803 |
| 7 | 0.4574 | 2 | table_data | 8. EXCLUSIONS | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.2131 |
| 8 | 0.4574 | 3 | table_data | 8. EXCLUSIONS | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.2131 |
| 9 | 0.4574 | 4 | table_data | 8. EXCLUSIONS | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.2131 |
| 10 | 0.4574 | 5 | table_data | 8. EXCLUSIONS | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.2131 |
| 11 | 0.4574 | 6 | table_data | 8. EXCLUSIONS | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.2131 |
| 12 | 0.4574 | 7 | table_data | 8. EXCLUSIONS | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.2131 |
| 13 | 0.4541 | 2 | table_data | 3. DEFINITIONS | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.2295 |
| 14 | 0.4541 | 3 | table_data | 3. DEFINITIONS | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.2295 |
| 15 | 0.4541 | 4 | table_data | 3. DEFINITIONS | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.2295 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 1. PREAMBLE | 0.4639 | 2 |
| 8. EXCLUSIONS | 0.4574 | 2 |
| 3. DEFINITIONS | 0.4541 | 2 |
| 9. CLAIM PROCEDURE | 0.441 | 2 |
| 10. GENERAL TERMS &CONDITIONS | 0.4049 | 9 |
| PUNE | 0.3369 | 17 (weak_signal) |
| DELHI | 0.3336 | 16 (weak_signal) |
| PATNA | 0.3336 | 17 (weak_signal) |
| BHOPAL | 0.3303 | 16 (weak_signal) |
| JAIPUR | 0.3303 | 17 (weak_signal) |

---

### 05_niva_bupa_niva_bupa_health_pulse

- **Category:** HEADING_MISS
- **Insurer:** Niva_Bupa
- **Pages:** 63, **Total candidates:** 3117
- **Body font mode:** 9.96, **Median line length:** 47
- **Best score:** 0.4947
- **Best heading-like score:** 0.4947
- **Root cause:** `threshold_too_high
- **Threshold 0.45 would help:** Yes
- **False-positive risk:** medium_risk_2_fp_of_8
- **Heading-like in top 20:** 11

**Section tree:** sections=1, clauses=0, visual_headings=0, synthetic=0

**Top 20 Candidates (by score):**

| Rank | Score | Page | Classification | Text | Bold | Caps | Sent | Num | Dict | TOC | Spacing | LineLen |
|------|-------|------|----------------|------|------|------|------|-----|------|-----|---------|---------|
| 1 | 0.4947 | 22 | heading_real | 6. Exclusions | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2766 |
| 2 | 0.4904 | 1 | heading_real | 2. Definitions | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.2979 |
| 3 | 0.4819 | 12 | heading_probable | 3.14. HIV / AIDS | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0.3404 |
| 4 | 0.4734 | 22 | heading_real | 4.4. Hospital Cash | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.383 |
| 5 | 0.4649 | 13 | heading_real | 4. Optional Benefits | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4255 |
| 6 | 0.4574 | 45 | numbered_allcaps_item | 64 PAN CAN | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.2128 |
| 7 | 0.4532 | 44 | numbered_allcaps_item | 1 BABY FOOD | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.234 |
| 8 | 0.4521 | 7 | heading_real | 3.4. Day Care Treatment | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.4894 |
| 9 | 0.4489 | 46 | numbered_allcaps_item | 22 TORNIQUET | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.2553 |
| 10 | 0.4447 | 46 | numbered_allcaps_item | 16 X-RAY FILM | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.2766 |
| 11 | 0.4436 | 14 | heading_real | 4.1.1 Accident Death (AD) | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0.5319 |
| 12 | 0.4277 | 46 | numbered_allcaps_item | 13 SURGICAL DRILL | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.3617 |
| 13 | 0.4234 | 44 | numbered_allcaps_item | 11 LAUNDRY CHARGES | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.383 |
| 14 | 0.4191 | 45 | numbered_allcaps_item | 57 NEBULISATION KIT | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0.4043 |
| 15 | 0.4191 | 55 | heading_probable | 245 SURGERY FOR SUI | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0.4043 |

**Identified real heading examples (from heading-like scan):**

| Text | Score | Page |
|------|-------|------|
| 6. Exclusions | 0.4947 | 22 |
| 2. Definitions | 0.4904 | 1 |
| 3.14. HIV / AIDS | 0.4819 | 12 |
| 4.4. Hospital Cash | 0.4734 | 22 |
| 4. Optional Benefits | 0.4649 | 13 |
| 64 PAN CAN | 0.4574 | 45 |
| 1 BABY FOOD | 0.4532 | 44 |
| 3.4. Day Care Treatment | 0.4521 | 7 |
| 22 TORNIQUET | 0.4489 | 46 |
| 16 X-RAY FILM | 0.4447 | 46 |

---

## Recommended Parser Changes (Ranked by Expected Impact)

### 1. Lower heading threshold to 0.45 (HIGH IMPACT)

- Affects 9/20 inspected policies
- Would admit ~41/41 identified real heading examples at 0.45+
- Low false-positive risk for documents where top candidates ARE real headings
- **Warning:** Does NOT help documents where top candidates are TOC entries or body text

### 2. Add letter-numbering patterns to heading scorer (MEDIUM IMPACT)
- Current patterns skip letter prefixes: `A.`, `B.`, `(a)`, `(b)`, `Part I`, `Part II`
- Weight `matches_numbering` = +0.30 — biggest single boost
- Adding letter patterns would convert `A.Preamble` (score ~0.10 → ~0.40)

### 3. Reduce `is_sentence_case` penalty for bold+numbered lines (MEDIUM IMPACT)
- Current penalty: -0.30 for any sentence-case line
- Bold definition headings (`Condition Precedent: Condition Precedent means...`) get penalized
- Suggestion: reduce penalty to -0.10 or -0.15 when `is_bold=1` AND `matches_numbering=1`

### 4. Suppress TOC entries in heading scorer (LOW-MEDIUM IMPACT)
- Several documents have TOC entries dominating top candidates
- TOC lines have `has_toc_dots=1` but still score high due to numbering + dict match
- Suggestion: add `has_toc_dots` penalty or exclude early-page candidates

### 5. Add `spacing_signal` as standalone feature without requiring numbering/bold (LOW IMPACT)
- Current: `spacing_signal=1` only when `looks_heading_like AND gap_before_ratio >= 1.5`
- Some documents have well-spaced headings but no numbering/bold
- Would affect documents where spacing is the primary heading cue

## Warning: Global Threshold Lowering Safety

**Do NOT blindly lower the global threshold from 0.5 to 0.45 without evaluation.**

Reasons:
1. Documents dominated by TOC entries (like HDFC Ergo) would admit TOC lines as headings
2. Documents with procedure-code lists would admit all-caps numbered items as headings
3. The current 20-policy gold eval must not regress — verify before/after threshold change
4. Some documents need feature-level fixes (letter numbering, sentence-case penalty) not threshold changes
