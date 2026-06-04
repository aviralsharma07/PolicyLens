# DSE-024 Phase E3A — Residual 58 Zero-Clause Classification

Date: 2026-06-04

## Context

After DSE-024 Phase E2 section tree rebuild, 44 section_tree_fail policies were resolved. This report classifies the remaining **58 zero-clause policies** into actionable buckets.

## Summary

Total policies classified: **58**

| Classification | Count | Action |
|---|---|---|
| heading_miss | 33 | Parser fix needed — add format-specific heading patterns |
| duplicate_or_superseded | 8 | Corpus filter — deduplicate by file hash |
| physical_text_issue | 8 | Parser fix needed — investigate pdfplumber extraction |
| non_policy_or_rider | 4 | Corpus filter — exclude from extraction |
| unsupported_format | 3 | Corpus filter — document-level filtering |
| manual_review_required | 2 | Manual review needed |

**Fix parser vs filter corpus breakdown:**

- **Fix parser:** 41 (heading_miss + physical_text_issue)
- **Filter/defer corpus:** 15 (duplicate + non_policy + unsupported)
- **Manual review needed:** 2

## Parser-Fix Candidates (heading_miss, sorted by max_score)

Highest-confidence cases where heading scorer pattern additions could resolve zero-clause.

| # | Insurer | Max Score | >0.3 | Pages | Top Candidate | Confidence |
|---|---|---|---|---|---|---|
| 1 | SBI_General | 0.4957 | 24 | 12 | "1" (0.4957) | medium |
| 2 | Future_Generali | 0.4802 | 94 | 33 | "POLICY WORDINGS" (0.4802) | medium |
| 3 | HDFC_ERGO | 0.475 | 91 | 41 | "Contents" (0.475) | medium |
| 4 | IFFCO_Tokio | 0.431 | 9 | 25 | "4) Body Mass Index (BMI);" (0.431) | medium |
| 5 | Star_Health | 0.4233 | 19 | 22 | "4    80%" (0.4233) | medium |
| 6 | Star_Health | 0.4229 | 20 | 18 | "4    80%" (0.4229) | medium |
| 7 | Oriental_Insurance | 0.4194 | 22 | 44 | "Part 4:GENERAL TERMS AND CLAUSES" (0.4194) | medium |
| 8 | HDFC_ERGO | 0.4132 | 34 | 30 | "S. V. Road, Santacruz (W)," (0.4132) | medium |
| 9 | Future_Generali | 0.4089 | 9 | 20 | "POLICY WORDINGS" (0.4089) | medium |
| 10 | Aditya_Birla | 0.4083 | 23 | 37 | "I. PREAMBLE" (0.4083) | medium |
| 11 | IFFCO_Tokio | 0.4047 | 8 | 25 | "1 Month  75%" (0.4047) | medium |
| 12 | Star_Health | 0.4 | 8 | 10 | "SUPER SURPLUS INSURANCE POLICY" (0.4) | medium |
| 13 | Kotak_Mahindra | 0.4 | 1 | 13 | "PART I" (0.4) | medium |
| 14 | HDFC_ERGO | 0.3967 | 5 | 41 | "X. Fraud" (0.3967) | medium |
| 15 | Tata_AIG | 0.3955 | 7 | 16 | "B. Copayment" (0.3955) | medium |
| 16 | HDFC_ERGO | 0.3944 | 4 | 22 | "S. Item S. Item" (0.3944) | medium |
| 17 | Aditya_Birla | 0.387 | 12 | 25 | "37.Co-Payment" (0.387) | medium |
| 18 | Bajaj_Allianz | 0.3818 | 2 | 13 | "Policy Wordings" (0.3818) | medium |
| 19 | ICICI_Lombard | 0.3792 | 5 | 29 | "2.FIR" (0.3792) | medium |
| 20 | HDFC_ERGO | 0.3778 | 57 | 33 | "5 BUDS" (0.3778) | medium |
| 21 | Future_Generali | 0.3705 | 18 | 19 | "32. Other" (0.3705) | medium |
| 22 | HDFC_ERGO | 0.3682 | 4 | 12 | "Section I. Inpatient Benefits" (0.3682) | medium |
| 23 | Aditya_Birla | 0.3667 | 24 | 67 | "25. Grace Period" (0.3667) | medium |
| 24 | Future_Generali | 0.3667 | 14 | 21 | "1. Migration" (0.3667) | medium |
| 25 | Aditya_Birla | 0.3643 | 3 | 48 | "Section A. PREAMBLE" (0.3643) | medium |
| 26 | Aditya_Birla | 0.3643 | 3 | 48 | "Section A. PREAMBLE" (0.3643) | medium |
| 27 | Oriental_Insurance | 0.3607 | 14 | 29 | "2. AYUSH Day Care Centre:" (0.3607) | medium |
| 28 | Kotak_Mahindra | 0.35 | 1 | 30 | "PART I" (0.35) | medium |
| 29 | Aditya_Birla | 0.348 | 2 | 23 | "Section A. PREAMBLE" (0.348) | medium |
| 30 | Aditya_Birla | 0.3471 | 8 | 39 | "13. BLINDNESS" (0.3471) | medium |
| 31 | HDFC_ERGO | 0.3459 | 5 | 35 | "Section 1;" (0.3459) | medium |
| 32 | Star_Health | 0.3326 | 4 | 10 | "III. COVERAGE - GOLD PLAN" (0.3326) | medium |
| 33 | HDFC_ERGO | 0.308 | 1 | 28 | "5 BUDS 39 STEAM INHALER" (0.308) | medium |

## Insurer Distribution

| Insurer | Zero-Clause Policies |
|---|---:|
| Aditya_Birla | 17 |
| HDFC_ERGO | 8 |
| Kotak_Mahindra | 7 |
| Star_Health | 6 |
| Future_Generali | 6 |
| Care_Health | 2 |
| Oriental_Insurance | 2 |
| IFFCO_Tokio | 2 |
| ICICI_Lombard | 1 |
| Bajaj_Allianz | 1 |
| Tata_AIG | 1 |
| Universal_Sompo | 1 |
| SBI_General | 1 |
| Edelweiss | 1 |
| Raheja_QBE | 1 |
| non_policy_wordings | 1 |

## Classification by Insurer

### heading_miss

| Insurer | Count |
|---|---:|
| HDFC_ERGO | 8 |
| Aditya_Birla | 7 |
| Star_Health | 4 |
| Future_Generali | 4 |
| Oriental_Insurance | 2 |
| IFFCO_Tokio | 2 |
| Kotak_Mahindra | 2 |
| ICICI_Lombard | 1 |
| Bajaj_Allianz | 1 |
| Tata_AIG | 1 |
| SBI_General | 1 |

### duplicate_or_superseded

| Insurer | Count |
|---|---:|
| Aditya_Birla | 6 |
| Future_Generali | 2 |

### physical_text_issue

| Insurer | Count |
|---|---:|
| Kotak_Mahindra | 4 |
| Aditya_Birla | 3 |
| Universal_Sompo | 1 |

### non_policy_or_rider

| Insurer | Count |
|---|---:|
| Care_Health | 2 |
| Edelweiss | 1 |
| non_policy_wordings | 1 |

### unsupported_format

| Insurer | Count |
|---|---:|
| Star_Health | 1 |
| Kotak_Mahindra | 1 |
| Raheja_QBE | 1 |

### manual_review_required

| Insurer | Count |
|---|---:|
| Star_Health | 1 |
| Aditya_Birla | 1 |

## Per-Policy Detail

| Slug | Insurer | Pages | Max Score | >0.3 | Classification | Confidence | Evidence |
|---|---|---|---|---|---|---|---|
| 13_future_generali_future_generali_future_poo | Future_Generali | 45 | 0.368 | 104 | duplicate_or_superseded | high | Duplicate hash with: 13_future_generali_future_generali_poorna_suraksha_group_pw |
| 13_future_generali_future_generali_poorna_sur | Future_Generali | 45 | 0.368 | 104 | duplicate_or_superseded | high | Duplicate hash with: 13_future_generali_future_generali_future_poorna_suraksha_g |
| aditya_birla_activ_care | Aditya_Birla | 34 | 0.3593 | 5 | duplicate_or_superseded | high | Duplicate hash with: 11_aditya_birla_aditya_birla_active_care |
| 11_aditya_birla_aditya_birla_active_care | Aditya_Birla | 34 | 0.3593 | 5 | duplicate_or_superseded | high | Duplicate hash with: aditya_birla_activ_care |
| 11_aditya_birla_aditya_birla_global_health_se | Aditya_Birla | 18 | 0.3538 | 2 | duplicate_or_superseded | high | Duplicate hash with: 11_aditya_birla_aditya_birla_global_health_secure_2021 |
| 11_aditya_birla_aditya_birla_global_health_se | Aditya_Birla | 18 | 0.3538 | 2 | duplicate_or_superseded | high | Duplicate hash with: 11_aditya_birla_aditya_birla_global_health_secure |
| 11_aditya_birla_aditya_birla_arogyasanjeevani | Aditya_Birla | 11 | -0.2 | 0 | duplicate_or_superseded | high | Duplicate hash with: 11_aditya_birla_aditya_birla_arogya_sanjeevani_irdai |
| 11_aditya_birla_aditya_birla_arogya_sanjeevan | Aditya_Birla | 11 | -0.2 | 0 | duplicate_or_superseded | high | Duplicate hash with: 11_aditya_birla_aditya_birla_arogyasanjeevani_policy_aditya |
| 20_sbi_general_sbi_retail_health_pw | SBI_General | 12 | 0.4957 | 24 | heading_miss | medium | max_score=0.4957, >0.3=24; Top: "1" (0.4957) |
| 13_future_generali_future_generali_health_tot | Future_Generali | 33 | 0.4802 | 94 | heading_miss | medium | max_score=0.4802, >0.3=94; Top: "POLICY WORDINGS" (0.4802) |
| 09_hdfc_ergo_hdfc_ergo_hdfc_ergo_group_protec | HDFC_ERGO | 41 | 0.475 | 91 | heading_miss | medium | max_score=0.475, >0.3=91; Top: "Contents" (0.475) |
| 12_iffco_tokio_iffco_tokio_iffco_tokio_hospit | IFFCO_Tokio | 25 | 0.431 | 9 | heading_miss | medium | max_score=0.431, >0.3=9; Top: "4) Body Mass Index (BMI);" (0.431) |
| 02_star_health_star_health_star_group_critica | Star_Health | 22 | 0.4233 | 19 | heading_miss | medium | max_score=0.4233, >0.3=19; Top: "4    80%" (0.4233) |
| 02_star_health_star_health_star_group_cirtica | Star_Health | 18 | 0.4229 | 20 | heading_miss | medium | max_score=0.4229, >0.3=20; Top: "4    80%" (0.4229) |
| 07_oriental_insurance_oriental_oriental_secur | Oriental_Insura | 44 | 0.4194 | 22 | heading_miss | medium | max_score=0.4194, >0.3=22; Top: "Part 4:GENERAL TERMS AND CLAUSES" (0.4194) |
| 09_hdfc_ergo_hdfc_ergo_health_on | HDFC_ERGO | 30 | 0.4132 | 34 | heading_miss | medium | max_score=0.4132, >0.3=34; Top: "S. V. Road, Santacruz (W)," (0.4132) |
| 13_future_generali_future_generali_alpa_bima_ | Future_Generali | 20 | 0.4089 | 9 | heading_miss | medium | max_score=0.4089, >0.3=9; Top: "POLICY WORDINGS" (0.4089) |
| 11_aditya_birla_aditya_birla_group_protect | Aditya_Birla | 37 | 0.4083 | 23 | heading_miss | medium | max_score=0.4083, >0.3=23; Top: "I. PREAMBLE" (0.4083) |
| 12_iffco_tokio_iffco_tokio_swasthya_kavach_fa | IFFCO_Tokio | 25 | 0.4047 | 8 | heading_miss | medium | max_score=0.4047, >0.3=8; Top: "1 Month  75%" (0.4047) |
| 02_star_health_star_policy_super_surplus_insu | Star_Health | 10 | 0.4 | 8 | heading_miss | medium | max_score=0.4, >0.3=8; Top: "SUPER SURPLUS INSURANCE POLICY" (0.4) |
| 16_kotak_mahindra_kotak_kotak_covid_19_secure | Kotak_Mahindra | 13 | 0.4 | 1 | heading_miss | medium | max_score=0.4, >0.3=1; Top: "PART I" (0.4) |
| 09_hdfc_ergo_hdfc_ergo_health_suraksha_top_up | HDFC_ERGO | 41 | 0.3967 | 5 | heading_miss | medium | max_score=0.3967, >0.3=5; Top: "X. Fraud" (0.3967) |
| 10_tata_aig_tata_aig_mediraksha | Tata_AIG | 16 | 0.3955 | 7 | heading_miss | medium | max_score=0.3955, >0.3=7; Top: "B. Copayment" (0.3955) |
| 09_hdfc_ergo_hdfc_ergo_hdfc_ergo_hospital_cas | HDFC_ERGO | 22 | 0.3944 | 4 | heading_miss | medium | max_score=0.3944, >0.3=4; Top: "S. Item S. Item" (0.3944) |
| 11_aditya_birla_aditya_birla_group_activ_hela | Aditya_Birla | 25 | 0.387 | 12 | heading_miss | medium | max_score=0.387, >0.3=12; Top: "37.Co-Payment" (0.387) |
| 08_bajaj_allianz_bajaj_allianz_personal_accid | Bajaj_Allianz | 13 | 0.3818 | 2 | heading_miss | medium | max_score=0.3818, >0.3=2; Top: "Policy Wordings" (0.3818) |
| 04_icici_lombard_icici_lombard_crtical_illnes | ICICI_Lombard | 29 | 0.3792 | 5 | heading_miss | medium | max_score=0.3792, >0.3=5; Top: "2.FIR" (0.3792) |
| 09_hdfc_ergo_hdfc_ergo_optima_plus | HDFC_ERGO | 33 | 0.3778 | 57 | heading_miss | medium | max_score=0.3778, >0.3=57; Top: "5 BUDS" (0.3778) |
| 13_future_generali_future_generali_future_hos | Future_Generali | 19 | 0.3705 | 18 | heading_miss | medium | max_score=0.3705, >0.3=18; Top: "32. Other" (0.3705) |
| 09_hdfc_ergo_hdfc_ergo_total_health | HDFC_ERGO | 12 | 0.3682 | 4 | heading_miss | medium | max_score=0.3682, >0.3=4; Top: "Section I. Inpatient Benefits" (0.3682) |
| 11_aditya_birla_aditya_birla_activ_health_202 | Aditya_Birla | 67 | 0.3667 | 24 | heading_miss | medium | max_score=0.3667, >0.3=24; Top: "25. Grace Period" (0.3667) |
| 13_future_generali_future_generali_future_hea | Future_Generali | 21 | 0.3667 | 14 | heading_miss | medium | max_score=0.3667, >0.3=14; Top: "1. Migration" (0.3667) |
| 11_aditya_birla_aditya_birla_activ_health | Aditya_Birla | 48 | 0.3643 | 3 | heading_miss | medium | max_score=0.3643, >0.3=3; Top: "Section A. PREAMBLE" (0.3643) |
| 11_aditya_birla_aditya_birla_activ_health_pla | Aditya_Birla | 48 | 0.3643 | 3 | heading_miss | medium | max_score=0.3643, >0.3=3; Top: "Section A. PREAMBLE" (0.3643) |
| 07_oriental_insurance_oriental_health_of_priv | Oriental_Insura | 29 | 0.3607 | 14 | heading_miss | medium | max_score=0.3607, >0.3=14; Top: "2. AYUSH Day Care Centre:" (0.3607) |
| 16_kotak_mahindra_kotak_kotak_group_hospital_ | Kotak_Mahindra | 30 | 0.35 | 1 | heading_miss | medium | max_score=0.35, >0.3=1; Top: "PART I" (0.35) |
| 11_aditya_birla_aditya_birla_global_health_se | Aditya_Birla | 23 | 0.348 | 2 | heading_miss | medium | max_score=0.348, >0.3=2; Top: "Section A. PREAMBLE" (0.348) |
| 11_aditya_birla_aditya_birla_activ_assure | Aditya_Birla | 39 | 0.3471 | 8 | heading_miss | medium | max_score=0.3471, >0.3=8; Top: "13. BLINDNESS" (0.3471) |
| 09_hdfc_ergo_hdfc_ergo_health_wallet | HDFC_ERGO | 35 | 0.3459 | 5 | heading_miss | medium | max_score=0.3459, >0.3=5; Top: "Section 1;" (0.3459) |
| 02_star_health_star_policy_star_super_surplus | Star_Health | 10 | 0.3326 | 4 | heading_miss | medium | max_score=0.3326, >0.3=4; Top: "III. COVERAGE - GOLD PLAN" (0.3326) |
| 09_hdfc_ergo_hdfc_ergo_optima_super | HDFC_ERGO | 28 | 0.308 | 1 | heading_miss | medium | max_score=0.308, >0.3=1; Top: "5 BUDS 39 STEAM INHALER" (0.308) |
| 11_aditya_birla_aditya_birla_super_health_plu | Aditya_Birla | 20 | 0.2933 | 0 | manual_review_required | low | max_score=0.2933, >0.3=0, pages=20 |
| 02_star_health_star_health_senior_citizens_re | Star_Health | 12 | 0.21 | 0 | manual_review_required | low | max_score=0.21, >0.3=0, pages=12 |
| non_policy_wordings_nivabupa_health_recharge_ | non_policy_word | 42 | 0.4198 | 4 | non_policy_or_rider | high | Document type: brochure; Keyword match: prospectus |
| 03_care_health_care_plus_health_insurance_pro | Care_Health | 4 | 0.3929 | 1 | non_policy_or_rider | high | Document type: brochure; Keyword match: brochure |
| 03_care_health_senior_health_advantage_brochu | Care_Health | 4 | 0.3688 | 1 | non_policy_or_rider | high | Document type: brochure; Keyword match: brochure |
| 22_edelweiss_edelweiss_well_baby_well_mother_ | Edelweiss | 2 | 0.1573 | 0 | non_policy_or_rider | high | Document type: brochure |
| 14_universal_sompo_universal_sompo_csc_comple | Universal_Sompo | 40 | 0.2 | 0 | physical_text_issue | medium | max_score=0.2, >0.3=0, >0.25=0, >0.2=0; Top: "t" (0.2) |
| 16_kotak_mahindra_kotak_corona_kavach_group_p | Kotak_Mahindra | 12 | 0.05 | 0 | physical_text_issue | medium | max_score=0.05, >0.3=0, >0.25=0, >0.2=0; Top: "n" (0.05) |
| 16_kotak_mahindra_kotak_corona_kavach_policy_ | Kotak_Mahindra | 12 | 0.05 | 0 | physical_text_issue | medium | max_score=0.05, >0.3=0, >0.25=0, >0.2=0; Top: "n" (0.05) |
| 16_kotak_mahindra_kotak_corona_kavach_group_p | Kotak_Mahindra | 12 | 0.0 | 0 | physical_text_issue | medium | max_score=0.0, >0.3=0, >0.25=0, >0.2=0; Top: "v1" (0.0) |
| 16_kotak_mahindra_kotak_kotak_group_health_ca | Kotak_Mahindra | 28 | -0.05 | 0 | physical_text_issue | medium | max_score=-0.05, >0.3=0, >0.25=0, >0.2=0; Top: "–" (-0.05) |
| 11_aditya_birla_aditya_birla_group_assure_cov | Aditya_Birla | 14 | -0.1 | 0 | physical_text_issue | medium | max_score=-0.1, >0.3=0, >0.25=0, >0.2=0; Top: "." (-0.1) |
| 11_aditya_birla_aditya_birla_corona_kavach_po | Aditya_Birla | 12 | -0.2 | 0 | physical_text_issue | medium | max_score=-0.2, >0.3=0, >0.25=0, >0.2=0; Top: "." (-0.2) |
| 11_aditya_birla_aditya_birla_saral_suraksha_b | Aditya_Birla | 15 | -0.2 | 0 | physical_text_issue | medium | max_score=-0.2, >0.3=0, >0.25=0, >0.2=0; Top: "." (-0.2) |
| 02_star_health_star_health_star_novel_corona_ | Star_Health | 4 | 0.4121 | 11 | unsupported_format | medium | pages=4, candidates=502, max_score=0.4121 |
| 23_raheja_qbe_raheja_qbe_product_list | Raheja_QBE | 4 | 0.1424 | 0 | unsupported_format | medium | pages=4, candidates=540, max_score=0.1424 |
| 16_kotak_mahindra_kotak_corona_rakshak_policy | Kotak_Mahindra | 6 | 0.05 | 0 | unsupported_format | medium | pages=6, candidates=1505, max_score=0.05 |

