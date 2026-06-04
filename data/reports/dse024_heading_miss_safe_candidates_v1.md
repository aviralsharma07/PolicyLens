# DSE-024 E3B Heading-Miss Safe Candidate Audit

Date: 2026-06-04

## Summary

Total `heading_miss` policies audited: **33**

| Classification | Count |
|---|---:|
| safe_pattern_fix | 27 |
| false_top_candidate | 6 |

## Safe Pattern Counts

| Pattern | Candidate Count |
|---|---:|
| numbered_short_title_heading | 80 |
| section_token_heading | 22 |
| roman_policy_section_heading | 10 |
| numbered_named_policy_heading | 8 |
| lettered_named_heading | 4 |
| part_roman_heading | 3 |
| part_number_colon_heading | 1 |

## Key Findings

- This was inspection-only; no parser behavior changed.
- The safe fix list is intentionally smaller than the 33 heading-miss policies.
- High-risk top candidates include percentage rows, address fragments, item/procedure rows, duration-percentage rows, and generic document titles.
- Generic `POLICY WORDINGS`, `Contents`, and product title lines should not be promoted without stronger context guards.

## Policy Audit

| Slug | Insurer | Max Score | Classification | Safe Candidates | False Top | Recommendation |
|---|---|---:|---|---:|---|---|
| `02_star_health_star_health_star_group_cirticare_gold` | Star_Health | 0.4229 | false_top_candidate | 0 | percentage_table_row | Do not promote top candidate; inspect lower lines or route to physical/parser review. |
| `02_star_health_star_health_star_group_criticare_platinum` | Star_Health | 0.4233 | false_top_candidate | 0 | percentage_table_row | Do not promote top candidate; inspect lower lines or route to physical/parser review. |
| `02_star_health_star_policy_star_super_surplus_floater_insurance_policy` | Star_Health | 0.3326 | safe_pattern_fix | 4 |  | Implement narrow pattern(s): numbered_short_title_heading, roman_policy_section_heading |
| `02_star_health_star_policy_super_surplus_insurance_policy` | Star_Health | 0.4 | safe_pattern_fix | 7 | generic_document_title_or_contents | Implement narrow pattern(s): numbered_short_title_heading, roman_policy_section_heading |
| `04_icici_lombard_icici_lombard_crtical_illness` | ICICI_Lombard | 0.3792 | safe_pattern_fix | 6 |  | Implement narrow pattern(s): numbered_short_title_heading |
| `07_oriental_insurance_oriental_health_of_privileged_elders` | Oriental_Insurance | 0.3607 | safe_pattern_fix | 2 |  | Implement narrow pattern(s): numbered_named_policy_heading, numbered_short_title_heading |
| `07_oriental_insurance_oriental_oriental_secure_credit` | Oriental_Insurance | 0.4194 | safe_pattern_fix | 5 |  | Implement narrow pattern(s): numbered_named_policy_heading, numbered_short_title_heading, part_numbe |
| `08_bajaj_allianz_bajaj_allianz_personal_accident_insurance_policy` | Bajaj_Allianz | 0.3818 | safe_pattern_fix | 7 | generic_document_title_or_contents | Implement narrow pattern(s): numbered_short_title_heading |
| `09_hdfc_ergo_hdfc_ergo_hdfc_ergo_group_protect` | HDFC_ERGO | 0.475 | safe_pattern_fix | 1 | generic_document_title_or_contents | Implement narrow pattern(s): numbered_short_title_heading |
| `09_hdfc_ergo_hdfc_ergo_hdfc_ergo_hospital_cash_insurance` | HDFC_ERGO | 0.3944 | false_top_candidate | 0 | table_header_fragment | Do not promote top candidate; inspect lower lines or route to physical/parser review. |
| `09_hdfc_ergo_hdfc_ergo_health_on` | HDFC_ERGO | 0.4132 | safe_pattern_fix | 4 | dotted_initials_or_address | Implement narrow pattern(s): section_token_heading |
| `09_hdfc_ergo_hdfc_ergo_health_suraksha_top_up_plus` | HDFC_ERGO | 0.3967 | safe_pattern_fix | 2 |  | Implement narrow pattern(s): numbered_short_title_heading, section_token_heading |
| `09_hdfc_ergo_hdfc_ergo_health_wallet` | HDFC_ERGO | 0.3459 | safe_pattern_fix | 1 |  | Implement narrow pattern(s): section_token_heading |
| `09_hdfc_ergo_hdfc_ergo_optima_plus` | HDFC_ERGO | 0.3778 | safe_pattern_fix | 1 |  | Implement narrow pattern(s): section_token_heading |
| `09_hdfc_ergo_hdfc_ergo_optima_super` | HDFC_ERGO | 0.308 | false_top_candidate | 0 | procedure_or_item_list | Do not promote top candidate; inspect lower lines or route to physical/parser review. |
| `09_hdfc_ergo_hdfc_ergo_total_health` | HDFC_ERGO | 0.3682 | safe_pattern_fix | 14 |  | Implement narrow pattern(s): numbered_short_title_heading, section_token_heading |
| `10_tata_aig_tata_aig_mediraksha` | Tata_AIG | 0.3955 | safe_pattern_fix | 4 |  | Implement narrow pattern(s): lettered_named_heading, numbered_short_title_heading, roman_policy_sect |
| `11_aditya_birla_aditya_birla_activ_assure` | Aditya_Birla | 0.3471 | safe_pattern_fix | 2 |  | Implement narrow pattern(s): numbered_short_title_heading |
| `11_aditya_birla_aditya_birla_activ_health` | Aditya_Birla | 0.3643 | safe_pattern_fix | 4 |  | Implement narrow pattern(s): numbered_short_title_heading, section_token_heading |
| `11_aditya_birla_aditya_birla_activ_health_2021` | Aditya_Birla | 0.3667 | safe_pattern_fix | 4 |  | Implement narrow pattern(s): numbered_named_policy_heading, numbered_short_title_heading, section_to |
| `11_aditya_birla_aditya_birla_activ_health_platinum` | Aditya_Birla | 0.3643 | safe_pattern_fix | 4 |  | Implement narrow pattern(s): numbered_short_title_heading, section_token_heading |
| `11_aditya_birla_aditya_birla_global_health_secure_older` | Aditya_Birla | 0.348 | safe_pattern_fix | 3 |  | Implement narrow pattern(s): section_token_heading |
| `11_aditya_birla_aditya_birla_group_activ_helath` | Aditya_Birla | 0.387 | safe_pattern_fix | 14 |  | Implement narrow pattern(s): numbered_named_policy_heading, numbered_short_title_heading |
| `11_aditya_birla_aditya_birla_group_protect` | Aditya_Birla | 0.4083 | safe_pattern_fix | 1 |  | Implement narrow pattern(s): roman_policy_section_heading |
| `12_iffco_tokio_iffco_tokio_iffco_tokio_hospital_daily_cash_policy` | IFFCO_Tokio | 0.431 | false_top_candidate | 0 | benefit_condition_list_item | Do not promote top candidate; inspect lower lines or route to physical/parser review. |
| `12_iffco_tokio_iffco_tokio_swasthya_kavach_family_health_policy_47fde468` | IFFCO_Tokio | 0.4047 | safe_pattern_fix | 3 | duration_percentage_table_row | Implement narrow pattern(s): numbered_short_title_heading |
| `13_future_generali_future_generali_alpa_bima_group_48186b84` | Future_Generali | 0.4089 | safe_pattern_fix | 4 | generic_document_title_or_contents | Implement narrow pattern(s): lettered_named_heading, numbered_named_policy_heading, roman_policy_sec |
| `13_future_generali_future_generali_future_health_protect_group` | Future_Generali | 0.3667 | safe_pattern_fix | 4 |  | Implement narrow pattern(s): lettered_named_heading, numbered_named_policy_heading, roman_policy_sec |
| `13_future_generali_future_generali_future_hospicash` | Future_Generali | 0.3705 | safe_pattern_fix | 11 |  | Implement narrow pattern(s): lettered_named_heading, numbered_named_policy_heading, numbered_short_t |
| `13_future_generali_future_generali_health_total` | Future_Generali | 0.4802 | safe_pattern_fix | 13 | generic_document_title_or_contents | Implement narrow pattern(s): numbered_short_title_heading |
| `16_kotak_mahindra_kotak_kotak_covid_19_secure_policy_wording` | Kotak_Mahindra | 0.4 | safe_pattern_fix | 1 |  | Implement narrow pattern(s): part_roman_heading |
| `16_kotak_mahindra_kotak_kotak_group_hospital_cash` | Kotak_Mahindra | 0.35 | safe_pattern_fix | 2 |  | Implement narrow pattern(s): part_roman_heading |
| `20_sbi_general_sbi_retail_health_pw` | SBI_General | 0.4957 | false_top_candidate | 0 | bare_number | Do not promote top candidate; inspect lower lines or route to physical/parser review. |

## Top Candidates Per Policy

### `02_star_health_star_health_star_group_cirticare_gold`

Classification: **false_top_candidate**  
Recommended action: Do not promote top candidate; inspect lower lines or route to physical/parser review.  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.4229 | 13 | `p13l_57` | 4    80% | False |  | percentage_table_row |
| 0.4127 | 13 | `p13l_56` | 3   75% 60% | False |  | percentage_table_row |
| 0.4025 | 13 | `p13l_55` | 2  67% 50% 40% | False |  | percentage_table_row |
| 0.3924 | 13 | `p13l_54` | 1 50% 33% 25% 20% | False |  | percentage_table_row |
| 0.3364 | 18 | `p18l_50` | PUNE | False |  | address_or_city |
| 0.3331 | 16 | `p16l_46` | DELHI | False |  | address_or_city |
| 0.3331 | 18 | `p18l_43` | PATNA | False |  | address_or_city |
| 0.3314 | 1 | `p1l_59` | 14 Aplastic Anemia 30 Brain Surgery | False |  |  |
| 0.3297 | 16 | `p16l_15` | BHOPAL | False |  | address_or_city |
| 0.3297 | 17 | `p17l_32` | JAIPUR | False |  |  |
| 0.3297 | 18 | `p18l_21` | MUMBAI | False |  | address_or_city |
| 0.3263 | 16 | `p16l_37` | CHENNAI | False |  |  |
| 0.3263 | 17 | `p17l_37` | KOLKATA | False |  |  |
| 0.3229 | 17 | `p17l_16` | GUWAHATI | False |  |  |
| 0.3195 | 15 | `p15l_53` | AHMEDABAD | False |  |  |

### `02_star_health_star_health_star_group_criticare_platinum`

Classification: **false_top_candidate**  
Recommended action: Do not promote top candidate; inspect lower lines or route to physical/parser review.  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.4233 | 17 | `p17l_32` | 4    80% | False |  | percentage_table_row |
| 0.4133 | 17 | `p17l_31` | 3   75% 60% | False |  | percentage_table_row |
| 0.4033 | 17 | `p17l_30` | 2  67% 50% 40% | False |  | percentage_table_row |
| 0.3933 | 17 | `p17l_29` | 1 50% 33% 25% 20% | False |  | percentage_table_row |
| 0.3367 | 22 | `p22l_17` | PUNE | False |  | address_or_city |
| 0.3333 | 20 | `p20l_28` | DELHI | False |  | address_or_city |
| 0.3333 | 22 | `p22l_10` | PATNA | False |  | address_or_city |
| 0.33 | 19 | `p19l_38` | BHOPAL | False |  | address_or_city |
| 0.33 | 21 | `p21l_9` | JAIPUR | False |  |  |
| 0.33 | 21 | `p21l_33` | MUMBAI | False |  | address_or_city |
| 0.3267 | 20 | `p20l_19` | CHENNAI | False |  |  |
| 0.3267 | 21 | `p21l_14` | KOLKATA | False |  |  |
| 0.3233 | 20 | `p20l_41` | GUWAHATI | False |  |  |
| 0.32 | 19 | `p19l_23` | AHMEDABAD | False |  |  |
| 0.32 | 19 | `p19l_31` | BENGALURU | False |  |  |

### `02_star_health_star_policy_star_super_surplus_floater_insurance_policy`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading, roman_policy_section_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3326 | 3 | `p3l_24` | III. COVERAGE - GOLD PLAN | True | roman_policy_section_heading |  |
| 0.3239 | 2 | `p2l_120` | II. COVERAGE - SILVER PLAN | True | roman_policy_section_heading |  |
| 0.3196 | 6 | `p6l_140` | 6. Cancellation | True | numbered_short_title_heading |  |
| 0.3065 | 9 | `p9l_86` | PATNA | False |  | address_or_city |
| 0.2935 | 8 | `p8l_30` | 28. Important Note | True | numbered_short_title_heading |  |
| 0.2804 | 1 | `p1l_3` | PREAMBLE | False |  |  |
| 0.2717 | 9 | `p9l_43` | HYDERABAD | False |  |  |
| 0.263 | 9 | `p9l_19` | CHANDIGARH | False |  |  |
| 0.2152 | 1 | `p1l_136` | «««« | False |  |  |
| 0.2152 | 9 | `p9l_93` | PUNE | False |  | address_or_city |
| 0.2087 | 1 | `p1l_138` | STAR SUPER SURPLUS (FLOATER) INSURANCE POLICY | False |  | generic_document_title_or_contents |
| 0.2065 | 9 | `p9l_84` | NOIDA | False |  |  |
| 0.1978 | 9 | `p9l_75` | MUMBAI | False |  | address_or_city |
| 0.1891 | 9 | `p9l_55` | LUCKNOW | False |  |  |
| 0.1804 | 9 | `p9l_33` | GUWAHATI | False |  |  |

### `02_star_health_star_policy_super_surplus_insurance_policy`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading, roman_policy_section_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.4 | 1 | `p1l_133` | SUPER SURPLUS INSURANCE POLICY | False |  | generic_document_title_or_contents |
| 0.3833 | 3 | `p3l_33` | III. COVERAGE - GOLD PLAN | True | roman_policy_section_heading |  |
| 0.3767 | 2 | `p2l_126` | II. COVERAGE - SILVER PLAN | True | roman_policy_section_heading |  |
| 0.35 | 6 | `p6l_134` | 6. Cancellation | True | numbered_short_title_heading |  |
| 0.33 | 8 | `p8l_29` | 28. Important Note | True | numbered_short_title_heading |  |
| 0.3233 | 6 | `p6l_18` | 2. Claim Settlement | True | numbered_short_title_heading |  |
| 0.3167 | 6 | `p6l_94` | 4. Multiple Policies | True | numbered_short_title_heading |  |
| 0.3167 | 9 | `p9l_86` | PATNA | False |  | address_or_city |
| 0.2967 | 1 | `p1l_3` | PREAMBLE | False |  |  |
| 0.2967 | 7 | `p7l_128` | 10.Withdrawal of policy | True | numbered_short_title_heading |  |
| 0.29 | 9 | `p9l_43` | HYDERABAD | False |  |  |
| 0.2833 | 9 | `p9l_19` | CHANDIGARH | False |  |  |
| 0.27 | 7 | `p7l_116` | portability. | False |  |  |
| 0.2233 | 1 | `p1l_131` | «««« | False |  |  |
| 0.2233 | 9 | `p9l_93` | PUNE | False |  | address_or_city |

### `04_icici_lombard_icici_lombard_crtical_illness`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3792 | 19 | `p19l_35` | 2.FIR | False |  |  |
| 0.3458 | 5 | `p5l_12` | 17) Deafness: | False |  |  |
| 0.3375 | 3 | `p3l_56` | 12) MAJOR BURNS | False |  |  |
| 0.325 | 2 | `p2l_8` | 2) OPEN CHEST CABG | False |  |  |
| 0.3042 | 5 | `p5l_18` | 18) MULTIPLE SCLEROSIS WITH PERSISTING SYMPTOMS | False |  |  |
| 0.275 | 4 | `p4l_9` | 13) COMA OF SPECIFIED SEVERITY | False |  |  |
| 0.2708 | 25 | `p25l_16` | 8.Fraud | True | numbered_short_title_heading |  |
| 0.2542 | 19 | `p19l_38` | 3.Panchnama | True | numbered_short_title_heading |  |
| 0.2542 | 25 | `p25l_38` | 10. Notices | True | numbered_short_title_heading |  |
| 0.2458 | 18 | `p18l_16` | 9.Blood Tests | True | numbered_short_title_heading |  |
| 0.2417 | 2 | `p2l_45` | 5) MAJOR ORGAN /BONE MARROW TRANSPLANT | False |  |  |
| 0.2417 | 4 | `p4l_28` | 15) Blindness: | False |  |  |
| 0.2417 | 24 | `p24l_42` | 5.Contribution | True | numbered_short_title_heading |  |
| 0.2375 | 13 | `p13l_7` | 10.Blood Tests. | False |  |  |
| 0.2333 | 11 | `p11l_61` | 1.Due Observance | True | numbered_short_title_heading |  |

### `07_oriental_insurance_oriental_health_of_privileged_elders`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_named_policy_heading, numbered_short_title_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3607 | 5 | `p5l_24` | 2. AYUSH Day Care Centre: | True | numbered_named_policy_heading |  |
| 0.3536 | 11 | `p11l_16` | 4 disease and | False |  |  |
| 0.35 | 1 | `p1l_49` | 5. Cancer 50% of Sum Insured | False |  |  |
| 0.35 | 1 | `p1l_52` | 8. Stroke 20% of Sum Insured | False |  |  |
| 0.3429 | 12 | `p12l_32` | 15. Papulosquamo | True | numbered_short_title_heading |  |
| 0.3286 | 28 | `p28l_53` | part of Pondicherry) | False |  |  |
| 0.3214 | 8 | `p8l_38` | 30 day waiting period- code – ExcI03 | False |  |  |
| 0.3179 | 10 | `p10l_60` | 3 Epilepsy G40 Epilepsy | False |  |  |
| 0.3143 | 1 | `p1l_46` | 2. Knee Replacement 70% of Sum Insured | False |  |  |
| 0.3143 | 1 | `p1l_53` | 9. Benign Prostrate 15% of Sum Insured | False |  |  |
| 0.3107 | 10 | `p10l_35` | 1 Sarcoidosis D86.0-D86.9 | False |  |  |
| 0.3107 | 12 | `p12l_43` | 5CONDITIONS | False |  |  |
| 0.3071 | 7 | `p7l_38` | 4EXCLUSIONS: | False |  |  |
| 0.3036 | 3 | `p3l_21` | 2DEFINITIONS: | False |  |  |
| 0.3 | 1 | `p1l_55` | 11. Ophthalmic Diseases 10% of Sum Insured | False |  |  |

### `07_oriental_insurance_oriental_oriental_secure_credit`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_named_policy_heading, numbered_short_title_heading, part_number_colon_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.4194 | 34 | `p34l_21` | Part 4:GENERAL TERMS AND CLAUSES | True | part_number_colon_heading |  |
| 0.4143 | 32 | `p32l_36` | 1.5.1 CLAIM PROCEDURE | False |  |  |
| 0.3888 | 1 | `p1l_12` | POLICY WORDINGS | False |  | generic_document_title_or_contents |
| 0.3857 | 31 | `p31l_28` | 1.4.2CLAIMSSETTLEMENTPROCESS | False |  |  |
| 0.3776 | 7 | `p7l_30` | 1.1SECTION I: CRITICAL ILLNESS | False |  |  |
| 0.3694 | 22 | `p22l_7` | 1.2SECTION II: PERSONAL ACCIDENT | False |  |  |
| 0.3592 | 39 | `p39l_26` | 20.Renewal | True | numbered_named_policy_heading |  |
| 0.351 | 36 | `p36l_52` | 18.Age Limit | True | numbered_short_title_heading |  |
| 0.349 | 32 | `p32l_19` | 1.5SECTION V: CHILD EDUCATION BENEFIT | False |  |  |
| 0.3429 | 36 | `p36l_36` | 17.Sum Insured | True | numbered_short_title_heading |  |
| 0.3408 | 20 | `p20l_15` | 1.1.3EXCLUSIONS APPLICABLE TO SECTION I | False |  |  |
| 0.3388 | 40 | `p40l_33` | 2.Policy Number | True | numbered_short_title_heading |  |
| 0.3367 | 25 | `p25l_29` | 1.2.3EXCLUSIONS APPLICABLE TO SECTION II | False |  |  |
| 0.3367 | 27 | `p27l_48` | 1.3SECTION III:  INVOLUNTARY LOSS OF JOB | False |  |  |
| 0.3327 | 28 | `p28l_45` | 1.3.2EXCLUSIONS APPLICABLE TO SECTION III | False |  |  |

### `08_bajaj_allianz_bajaj_allianz_personal_accident_insurance_policy`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3818 | 1 | `p1l_55` | Policy Wordings | False |  | generic_document_title_or_contents |
| 0.3409 | 5 | `p5l_37` | D. Conditions | False |  |  |
| 0.2955 | 2 | `p2l_6` | 5. Additional Insurance | True | numbered_short_title_heading |  |
| 0.2682 | 7 | `p7l_37` | 30 days | False |  |  |
| 0.2636 | 1 | `p1l_13` | 1. Death | True | numbered_short_title_heading |  |
| 0.2636 | 6 | `p6l_8` | 30 days. | False |  |  |
| 0.2364 | 7 | `p7l_12` | 4. Arbitration | True | numbered_short_title_heading |  |
| 0.1818 | 13 | `p13l_41` | S. V. Road, Santacruz (W), | False |  | dotted_initials_or_address |
| 0.1818 | 13 | `p13l_77` | S. V. Road, Santacruz (W), | False |  | dotted_initials_or_address |
| 0.1682 | 1 | `p1l_47` | 4. Temporary Total Disability | True | numbered_short_title_heading |  |
| 0.1682 | 3 | `p3l_30` | 4.  it continues indefinitely | False |  |  |
| 0.1682 | 5 | `p5l_5` | Surgery | False |  |  |
| 0.1682 | 9 | `p9l_4` | 2. Long Term Policy Discount: | True | numbered_short_title_heading |  |
| 0.1636 | 1 | `p1l_16` | 2.  Permanent Total Disability | True | numbered_short_title_heading |  |
| 0.1591 | 1 | `p1l_19` | 3. Permanent Partial Disability | True | numbered_short_title_heading |  |

### `09_hdfc_ergo_hdfc_ergo_hdfc_ergo_group_protect`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.475 | 1 | `p1l_13` | Contents | False |  | generic_document_title_or_contents |
| 0.3969 | 9 | `p9l_76` | 2.Open Chest CABG | True | numbered_short_title_heading |  |
| 0.3969 | 40 | `p40l_12` | 30 MEDICAL CERTIFICATE 64 PAN CAN | False |  |  |
| 0.3969 | 40 | `p40l_15` | 33 MORTUARY CHARGES  67 AMBULANCE | False |  |  |
| 0.3938 | 40 | `p40l_13` | 31 MEDICAL RECORDS 65 TROLLY COVER | False |  |  |
| 0.3812 | 40 | `p40l_21` | 4 CAPS | False |  |  |
| 0.3812 | 40 | `p40l_23` | 6 COMB | False |  |  |
| 0.3812 | 40 | `p40l_26` | 9 GOWN | False |  |  |
| 0.3781 | 40 | `p40l_38` | 21 HVAC | False |  |  |
| 0.3781 | 41 | `p41l_20` | 8 GAUZE | False |  |  |
| 0.375 | 41 | `p41l_33` | 21 APRON | False |  |  |
| 0.3719 | 40 | `p40l_16` | 34 WALKING AIDS CHARGES 68 VASOFIX SAFETY | False |  |  |
| 0.3719 | 41 | `p41l_15` | 3 EYE PAD | False |  |  |
| 0.3719 | 41 | `p41l_30` | 18 COTTON | False |  |  |
| 0.3688 | 40 | `p40l_31` | 14 BED PAN | False |  |  |

### `09_hdfc_ergo_hdfc_ergo_hdfc_ergo_hospital_cash_insurance`

Classification: **false_top_candidate**  
Recommended action: Do not promote top candidate; inspect lower lines or route to physical/parser review.  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3944 | 21 | `p21l_24` | S. Item S. Item | False |  | table_header_fragment |
| 0.3833 | 1 | `p1l_46` | A. Waiting Periods | False |  |  |
| 0.3722 | 3 | `p3l_14` | B. General Exclusions | False |  |  |
| 0.3148 | 21 | `p21l_31` | 5 BUDS 39 STEAM INHALER | False |  | procedure_or_item_list |
| 0.3 | 21 | `p21l_33` | 7 CARRY BAGS 41 THERMOMETER | False |  |  |
| 0.2963 | 13 | `p13l_47` | 4. it continues indefinitely | False |  |  |
| 0.2963 | 22 | `p22l_18` | 26 BIRTH CERTIFICATE 60 MASK | False |  |  |
| 0.2889 | 14 | `p14l_37` | part of stay in Hospital which | False |  |  |
| 0.2852 | 21 | `p21l_29` | 3 BEAUTY SERVICES 37 SPIROMETRE | False |  |  |
| 0.2852 | 21 | `p21l_58` | 22 TELEVISION CHARGES 56 GLOVES | False |  |  |
| 0.2815 | 21 | `p21l_30` | 4 BELTS/ BRACES 38 NEBULIZER KIT | False |  |  |
| 0.2815 | 21 | `p21l_32` | 6 COLD PACK/HOT PACK 40 ARMSLING | False |  |  |
| 0.2815 | 21 | `p21l_50` | 19 SLINGS 53  SUGAR FREE TABLETS | False |  | procedure_or_item_list |
| 0.2778 | 19 | `p19l_32` | part of Territory of Pondicherry. | False |  |  |
| 0.2778 | 21 | `p21l_38` | 10 LEGGINGS 44 DIABETIC FOOT WEAR | False |  |  |

### `09_hdfc_ergo_hdfc_ergo_health_on`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): section_token_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.4132 | 26 | `p26l_34` | S. V. Road, Santacruz (W), | False |  | dotted_initials_or_address |
| 0.4079 | 3 | `p3l_69` | Section II. Restore Benefit | True | section_token_heading |  |
| 0.4 | 27 | `p27l_12` | PUNE - ShriVinaySah | False |  | address_or_city |
| 0.3974 | 1 | `p1l_14` | Section I. Inpatient Benefits | True | section_token_heading |  |
| 0.3974 | 4 | `p4l_34` | Section IV Multiplier Benefit | True | section_token_heading |  |
| 0.3921 | 9 | `p9l_47` | Section VI. General Conditions | True | section_token_heading |  |
| 0.3737 | 24 | `p24l_17` | BHOPAL - Shri Guru Saran | False |  | address_or_city |
| 0.3737 | 24 | `p24l_37` | Verma | False |  |  |
| 0.3737 | 26 | `p26l_65` | PATNA - Shri N. K. Singh | False |  | address_or_city |
| 0.3711 | 28 | `p28l_16` | S. Item S. Item | False |  | table_header_fragment |
| 0.3684 | 25 | `p25l_54` | KOLKATA - Shri P. K. Rath | False |  |  |
| 0.3684 | 26 | `p26l_43` | Prasad | False |  |  |
| 0.3632 | 24 | `p24l_27` | BHUBANESHWAR - Shri Suresh | False |  | address_or_city |
| 0.3632 | 24 | `p24l_52` | CHENNAI - Shri M. Vasantha | False |  |  |
| 0.3632 | 24 | `p24l_53` | Krishna | False |  |  |

### `09_hdfc_ergo_hdfc_ergo_health_suraksha_top_up_plus`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading, section_token_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3967 | 11 | `p11l_22` | X. Fraud | False |  |  |
| 0.37 | 7 | `p7l_83` | IV. Loadings | False |  |  |
| 0.3233 | 7 | `p7l_71` | III. Insured Person | False |  |  |
| 0.3133 | 8 | `p8l_49` | Section 1)a): | True | section_token_heading |  |
| 0.3033 | 10 | `p10l_75` | IX. Complete Discharge | False |  |  |
| 0.25 | 1 | `p1l_16` | POLICY WORDINGS | False |  | generic_document_title_or_contents |
| 0.2467 | 26 | `p26l_78` | G. Road, | False |  | address_or_city |
| 0.2467 | 29 | `p29l_20` | 5 BUDS 39 STEAM INHALER | False |  | procedure_or_item_list |
| 0.24 | 24 | `p24l_72` | 6234 6234 | False |  |  |
| 0.2367 | 14 | `p14l_58` | i. | False |  |  |
| 0.2333 | 5 | `p5l_47` | 1. Obesity | True | numbered_short_title_heading |  |
| 0.23 | 14 | `p14l_103` | ii. | False |  |  |
| 0.2267 | 5 | `p5l_51` | 2. coronary | False |  |  |
| 0.22 | 29 | `p29l_22` | 7 CARRY BAGS 41 THERMOMETER | False |  |  |
| 0.2167 | 40 | `p40l_23` | SCHEDULE OF BENEFITS | False |  |  |

### `09_hdfc_ergo_hdfc_ergo_health_wallet`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): section_token_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3459 | 4 | `p4l_59` | Section 1; | True | section_token_heading |  |
| 0.3095 | 32 | `p32l_10` | S. V. Road, Santacruz (W), | False |  | dotted_initials_or_address |
| 0.3054 | 35 | `p35l_10` | 9 FOOD CHARGES (OTHER THAN 43 SPLINT | False |  |  |
| 0.3027 | 33 | `p33l_40` | 5) Reserve Benefit | False |  |  |
| 0.3027 | 34 | `p34l_38` | 5) Reserve Benefit | False |  |  |
| 0.2986 | 31 | `p31l_27` | A. C. Guards, Lakdi-Ka-Pool, | False |  | dotted_initials_or_address |
| 0.2757 | 34 | `p34l_54` | 5 BUDS 39 STEAM INHALER | False |  | procedure_or_item_list |
| 0.2541 | 34 | `p34l_56` | 7 CARRY BAGS 41 THERMOMETER | False |  |  |
| 0.2486 | 35 | `p35l_36` | 26 BIRTH CERTIFICATE 60 MASK | False |  |  |
| 0.2432 | 33 | `p33l_34` | 3) Preventive Health Check-up | False |  |  |
| 0.2432 | 34 | `p34l_32` | 3) Preventive Health Check-up | False |  |  |
| 0.2324 | 34 | `p34l_52` | 3 BEAUTY SERVICES 37 SPIROMETRE | False |  |  |
| 0.2324 | 35 | `p35l_29` | 22 TELEVISION CHARGES 56 GLOVES | False |  |  |
| 0.227 | 34 | `p34l_53` | 4 BELTS/ BRACES 38 NEBULIZER KIT | False |  |  |
| 0.227 | 34 | `p34l_55` | 6 COLD PACK/HOT PACK 40 ARMSLING | False |  |  |

### `09_hdfc_ergo_hdfc_ergo_optima_plus`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): section_token_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3778 | 30 | `p30l_15` | 5 BUDS | False |  |  |
| 0.3741 | 31 | `p31l_28` | 58 ETC] | False |  |  |
| 0.3741 | 31 | `p31l_31` | 60 MASK | False |  |  |
| 0.3667 | 30 | `p30l_29` | 19 SLINGS | False |  |  |
| 0.3667 | 30 | `p30l_46` | 36 SPACER | False |  |  |
| 0.3667 | 31 | `p31l_12` | 43 SPLINT | False |  |  |
| 0.3667 | 31 | `p31l_26` | 56 GLOVES | False |  |  |
| 0.363 | 31 | `p31l_35` | 64 PAN CAN | False |  |  |
| 0.3593 | 30 | `p30l_11` | 1 BABY FOOD | False |  |  |
| 0.3593 | 30 | `p30l_20` | 10 LEGGINGS | False |  |  |
| 0.3593 | 31 | `p31l_9` | 40 ARMSLING | False |  |  |
| 0.3556 | 30 | `p30l_17` | 7 CARRY BAGS | False |  |  |
| 0.3556 | 31 | `p31l_38` | 67 AMBULANCE | False |  |  |
| 0.3519 | 11 | `p11l_40` | Section 1)a): | True | section_token_heading |  |
| 0.3519 | 30 | `p30l_33` | 23 SURCHARGES | False |  |  |

### `09_hdfc_ergo_hdfc_ergo_optima_super`

Classification: **false_top_candidate**  
Recommended action: Do not promote top candidate; inspect lower lines or route to physical/parser review.  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.308 | 27 | `p27l_18` | 5 BUDS 39 STEAM INHALER | False |  | procedure_or_item_list |
| 0.292 | 27 | `p27l_20` | 7 CARRY BAGS 41 THERMOMETER | False |  |  |
| 0.288 | 27 | `p27l_47` | 26 BIRTH CERTIFICATE 60 MASK | False |  |  |
| 0.276 | 27 | `p27l_16` | 3 BEAUTY SERVICES 37 SPIROMETRE | False |  |  |
| 0.276 | 27 | `p27l_40` | 22 TELEVISION CHARGES 56 GLOVES | False |  |  |
| 0.272 | 27 | `p27l_17` | 4 BELTS/ BRACES 38 NEBULIZER KIT | False |  |  |
| 0.272 | 27 | `p27l_19` | 6 COLD PACK/HOT PACK 40 ARMSLING | False |  |  |
| 0.272 | 27 | `p27l_34` | 19 SLINGS 53  SUGAR FREE TABLETS | False |  | procedure_or_item_list |
| 0.268 | 27 | `p27l_24` | 10 LEGGINGS 44 DIABETIC FOOT WEAR | False |  |  |
| 0.268 | 27 | `p27l_41` | 23 SURCHARGES 57 NEBULISATION KIT | False |  | procedure_or_item_list |
| 0.268 | 27 | `p27l_49` | 28 COURIER CHARGES 62 OXYGEN MASK | False |  |  |
| 0.268 | 27 | `p27l_51` | 30 MEDICAL CERTIFICATE 64 PAN CAN | False |  |  |
| 0.268 | 27 | `p27l_54` | 33 MORTUARY CHARGES  67 AMBULANCE | False |  |  |
| 0.264 | 27 | `p27l_15` | 2 BABY UTILITIES CHARGES 36 SPACER | False |  |  |
| 0.264 | 27 | `p27l_52` | 31 MEDICAL RECORDS 65 TROLLY COVER | False |  |  |

### `09_hdfc_ergo_hdfc_ergo_total_health`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading, section_token_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3682 | 1 | `p1l_9` | Section I. Inpatient Benefits | True | section_token_heading |  |
| 0.3545 | 2 | `p2l_35` | Section 2. | True | section_token_heading |  |
| 0.3409 | 11 | `p11l_19` | 9.Myringotomy | True | numbered_short_title_heading |  |
| 0.3227 | 2 | `p2l_66` | A. Waiting Period | False |  |  |
| 0.2682 | 4 | `p4l_65` | Section 4. General Conditions | True | section_token_heading |  |
| 0.2409 | 11 | `p11l_8` | 1.Stapedotomy | True | numbered_short_title_heading |  |
| 0.2364 | 11 | `p11l_9` | 2.Stapedectomy | True | numbered_short_title_heading |  |
| 0.2364 | 11 | `p11l_73` | 54.Glossectomy | True | numbered_short_title_heading |  |
| 0.2318 | 11 | `p11l_88` | 67.Palatoplasty | True | numbered_short_title_heading |  |
| 0.2318 | 12 | `p12l_56` | 137.Lithotripsy | True | numbered_short_title_heading |  |
| 0.2318 | 12 | `p12l_34` | 119.Orchidopexy | True | numbered_short_title_heading |  |
| 0.2273 | 11 | `p11l_22` | 12.Mastoidectomy | True | numbered_short_title_heading |  |
| 0.2227 | 12 | `p12l_58` | 139.Haemodialysis | True | numbered_short_title_heading |  |
| 0.2182 | 7 | `p7l_53` | 2. Open Chest CABG | True | numbered_short_title_heading |  |
| 0.2182 | 12 | `p12l_43` | 127.Epididymectomy | True | numbered_short_title_heading |  |

### `10_tata_aig_tata_aig_mediraksha`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): lettered_named_heading, numbered_short_title_heading, roman_policy_section_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3955 | 2 | `p2l_99` | B. Copayment | True | lettered_named_heading |  |
| 0.3909 | 1 | `p1l_74` | UIN: TATHLIP21259V022021 | False |  |  |
| 0.3818 | 1 | `p1l_57` | POLICY WORDINGS | False |  | generic_document_title_or_contents |
| 0.3545 | 1 | `p1l_73` | MediRaksha | False |  |  |
| 0.35 | 2 | `p2l_102` | C.  General Exclusions | True | roman_policy_section_heading |  |
| 0.3364 | 14 | `p14l_86` | 9. Myringotomy | True | numbered_short_title_heading |  |
| 0.3318 | 15 | `p15l_38` | 54. Glossectomy | True | numbered_short_title_heading |  |
| 0.2591 | 8 | `p8l_49` | 18 Months | False |  |  |
| 0.2455 | 3 | `p3l_118` |  | False |  |  |
| 0.2455 | 3 | `p3l_125` |  | False |  |  |
| 0.2455 | 3 | `p3l_128` |  | False |  |  |
| 0.2455 | 3 | `p3l_134` |  | False |  |  |
| 0.2455 | 3 | `p3l_138` |  | False |  |  |
| 0.2455 | 3 | `p3l_157` |  | False |  |  |
| 0.2455 | 3 | `p3l_38` |  | False |  |  |

### `11_aditya_birla_aditya_birla_activ_assure`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3471 | 7 | `p7l_35` | 13. BLINDNESS | True | numbered_short_title_heading |  |
| 0.3294 | 24 | `p24l_54` | 5 BUDS | False |  |  |
| 0.3294 | 26 | `p26l_5` | 4 CAPS | False |  |  |
| 0.3294 | 26 | `p26l_7` | 6 COMB | False |  |  |
| 0.3294 | 26 | `p26l_12` | 9 GOWN | False |  |  |
| 0.3176 | 25 | `p25l_47` | 60 MASK | False |  |  |
| 0.3176 | 26 | `p26l_19` | 21 HVAC | False |  |  |
| 0.3059 | 27 | `p27l_14` | 21 APRON | False |  |  |
| 0.2941 | 25 | `p25l_23` | 36 SPACER | False |  |  |
| 0.2941 | 25 | `p25l_28` | 43 SPLINT | False |  |  |
| 0.2941 | 25 | `p25l_37` | 56 GLOVES | False |  |  |
| 0.2941 | 27 | `p27l_7` | 18 COTTON | False |  |  |
| 0.2882 | 6 | `p6l_50` | 3. OPEN CHEST CABG | True | numbered_short_title_heading |  |
| 0.2824 | 26 | `p26l_21` | 14 BED PAN | False |  |  |
| 0.2824 | 27 | `p27l_15` | 14 EYE KIT | False |  | procedure_or_item_list |

### `11_aditya_birla_aditya_birla_activ_health`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading, section_token_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3643 | 1 | `p1l_1` | Section A. PREAMBLE | True | section_token_heading |  |
| 0.3429 | 43 | `p43l_23` | SECTION D. DEFINITIONS | True | section_token_heading |  |
| 0.3143 | 39 | `p39l_38` | D. Migration | False |  |  |
| 0.3 | 39 | `p39l_51` | C. Portability | False |  |  |
| 0.3 | 43 | `p43l_15` | Z. Nomination: | False |  |  |
| 0.2714 | 39 | `p39l_8` | G. Material Change | False |  |  |
| 0.2643 | 12 | `p12l_41` | 2) Nutrition Coach: | False |  |  |
| 0.2643 | 39 | `p39l_56` | E. Free Look Period | False |  |  |
| 0.2643 | 47 | `p47l_58` | 3.  Open Chest CABG | True | numbered_short_title_heading |  |
| 0.2571 | 42 | `p42l_38` | U. Moratorium Period | False |  |  |
| 0.25 | 40 | `p40l_64` | 1 Month | False |  |  |
| 0.2429 | 40 | `p40l_65` | 3 months | False |  |  |
| 0.2429 | 40 | `p40l_73` | 6 months | False |  |  |
| 0.2429 | 48 | `p48l_59` | 20. Muscular Dystrophy | True | numbered_short_title_heading |  |
| 0.2357 | 40 | `p40l_74` | 12 months | False |  |  |

### `11_aditya_birla_aditya_birla_activ_health_2021`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_named_policy_heading, numbered_short_title_heading, section_token_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3667 | 43 | `p43l_74` | 25. Grace Period | True | numbered_named_policy_heading |  |
| 0.35 | 43 | `p43l_99` | 28. Policy Dispute | True | numbered_short_title_heading |  |
| 0.35 | 50 | `p50l_8` | 5 BUDS | False |  |  |
| 0.35 | 51 | `p51l_38` | 4 CAPS | False |  |  |
| 0.35 | 51 | `p51l_36` | 6 COMB | False |  |  |
| 0.35 | 51 | `p51l_49` | 9 GOWN | False |  |  |
| 0.3417 | 1 | `p1l_1` | Section A. PREAMBLE | True | section_token_heading |  |
| 0.3417 | 51 | `p51l_20` | 60 MASK | False |  |  |
| 0.3417 | 52 | `p52l_39` | 8 GAUZE | False |  |  |
| 0.3333 | 39 | `p39l_101` | 5. Fraud | True | numbered_short_title_heading |  |
| 0.3333 | 52 | `p52l_42` | 21 APRON | False |  |  |
| 0.325 | 50 | `p50l_33` | 19 SLINGS | False |  |  |
| 0.325 | 51 | `p51l_15` | 56 GLOVES | False |  |  |
| 0.325 | 52 | `p52l_37` | 3 EYE PAD | False |  |  |
| 0.325 | 52 | `p52l_28` | 18 COTTON | False |  |  |

### `11_aditya_birla_aditya_birla_activ_health_platinum`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading, section_token_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3643 | 1 | `p1l_1` | Section A. PREAMBLE | True | section_token_heading |  |
| 0.3429 | 43 | `p43l_23` | SECTION D. DEFINITIONS | True | section_token_heading |  |
| 0.3143 | 39 | `p39l_38` | D. Migration | False |  |  |
| 0.3 | 39 | `p39l_51` | C. Portability | False |  |  |
| 0.3 | 43 | `p43l_15` | Z. Nomination: | False |  |  |
| 0.2714 | 39 | `p39l_8` | G. Material Change | False |  |  |
| 0.2643 | 12 | `p12l_41` | 2) Nutrition Coach: | False |  |  |
| 0.2643 | 39 | `p39l_56` | E. Free Look Period | False |  |  |
| 0.2643 | 47 | `p47l_58` | 3.  Open Chest CABG | True | numbered_short_title_heading |  |
| 0.2571 | 42 | `p42l_38` | U. Moratorium Period | False |  |  |
| 0.25 | 40 | `p40l_64` | 1 Month | False |  |  |
| 0.2429 | 40 | `p40l_65` | 3 months | False |  |  |
| 0.2429 | 40 | `p40l_73` | 6 months | False |  |  |
| 0.2429 | 48 | `p48l_59` | 20. Muscular Dystrophy | True | numbered_short_title_heading |  |
| 0.2357 | 40 | `p40l_74` | 12 months | False |  |  |

### `11_aditya_birla_aditya_birla_global_health_secure_older`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): section_token_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.348 | 1 | `p1l_4` | Section A. PREAMBLE | True | section_token_heading |  |
| 0.348 | 21 | `p21l_9` | PART OF BED CHARGE) | False |  |  |
| 0.296 | 14 | `p14l_10` | U. Assignment | False |  |  |
| 0.28 | 12 | `p12l_48` | M. Endorsements | False |  |  |
| 0.28 | 13 | `p13l_11` | N. Grace Period | False |  |  |
| 0.248 | 9 | `p9l_12` | I. Claims Procedure | False |  |  |
| 0.248 | 11 | `p11l_46` | D. Free Look Period | False |  |  |
| 0.24 | 11 | `p11l_53` | E. Fraudulent Claims | False |  |  |
| 0.18 | 12 | `p12l_34` | 24 months30.00% | False |  |  |
| 0.18 | 12 | `p12l_35` | 30 months15.00% | False |  |  |
| 0.174 | 14 | `p14l_31` | Section D. DEFINITIONS | True | section_token_heading |  |
| 0.172 | 13 | `p13l_18` | O. Renewal Terms | False |  |  |
| 0.166 | 1 | `p1l_16` | Section I: Basic Covers | True | section_token_heading |  |
| 0.156 | 11 | `p11l_58` | F. Material Change | False |  |  |
| 0.156 | 13 | `p13l_62` | R. Policy Disputes | False |  |  |

### `11_aditya_birla_aditya_birla_group_activ_helath`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_named_policy_heading, numbered_short_title_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.387 | 9 | `p9l_12` | 37.Co-Payment | True | numbered_named_policy_heading |  |
| 0.3783 | 19 | `p19l_46` | 12.ANGIOPLASTY | True | numbered_short_title_heading |  |
| 0.3609 | 20 | `p20l_23` | 19.LOSS OF LIMBS | True | numbered_short_title_heading |  |
| 0.3609 | 22 | `p22l_39` | 34.POLIOMYELITIS | True | numbered_short_title_heading |  |
| 0.3522 | 20 | `p20l_18` | 18.LOSS OF SPEECH | True | numbered_short_title_heading |  |
| 0.3435 | 12 | `p12l_48` | 1.Claims Procedure | True | numbered_short_title_heading |  |
| 0.3348 | 21 | `p21l_40` | 26.APLASTIC ANAEMIA | True | numbered_short_title_heading |  |
| 0.3261 | 20 | `p20l_27` | 20.MAJOR HEAD TRAUMA | True | numbered_short_title_heading |  |
| 0.3174 | 22 | `p22l_28` | 33.MUSCULAR DYSTROPHY | True | numbered_short_title_heading |  |
| 0.3087 | 21 | `p21l_16` | 24.ALZHEIMER’S DISEASE | False |  |  |
| 0.3087 | 21 | `p21l_31` | 25.AORTA GRAFT SURGERY | True | numbered_short_title_heading |  |
| 0.3087 | 22 | `p22l_9` | 30.FULMINANT HEPATITIS | True | numbered_short_title_heading |  |
| 0.3 | 18 | `p18l_40` | 2.MYOCARDIAL INFARCTION | True | numbered_short_title_heading |  |
| 0.2957 | 5 | `p5l_34` | 15.HIV Cover | True | numbered_short_title_heading |  |
| 0.2957 | 19 | `p19l_61` | 14.BLINDNESS | True | numbered_short_title_heading |  |

### `11_aditya_birla_aditya_birla_group_protect`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): roman_policy_section_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.4083 | 1 | `p1l_2` | I. PREAMBLE | True | roman_policy_section_heading |  |
| 0.35 | 29 | `p29l_12` | 5 BUDS | False |  |  |
| 0.35 | 30 | `p30l_34` | 4 CAPS | False |  |  |
| 0.35 | 30 | `p30l_36` | 6 COMB | False |  |  |
| 0.35 | 30 | `p30l_39` | 9 GOWN | False |  |  |
| 0.3417 | 30 | `p30l_20` | 60 MASK | False |  |  |
| 0.3417 | 31 | `p31l_28` | 8 GAUZE | False |  |  |
| 0.3333 | 31 | `p31l_41` | 21 APRON | False |  |  |
| 0.325 | 29 | `p29l_26` | 19 SLINGS | False |  |  |
| 0.325 | 29 | `p29l_43` | 36 SPACER | False |  |  |
| 0.325 | 30 | `p30l_16` | 56 GLOVES | False |  |  |
| 0.325 | 31 | `p31l_23` | 3 EYE PAD | False |  |  |
| 0.325 | 31 | `p31l_38` | 18 COTTON | False |  |  |
| 0.3167 | 22 | `p22l_17` | M. Premium | False |  |  |
| 0.3167 | 30 | `p30l_24` | 64 PAN CAN | False |  |  |

### `12_iffco_tokio_iffco_tokio_iffco_tokio_hospital_daily_cash_policy`

Classification: **false_top_candidate**  
Recommended action: Do not promote top candidate; inspect lower lines or route to physical/parser review.  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.431 | 10 | `p10l_20` | 4) Body Mass Index (BMI); | False |  | benefit_condition_list_item |
| 0.3667 | 14 | `p14l_32` | 1. COA– | False |  |  |
| 0.3667 | 14 | `p14l_47` | 3. PPI– | False |  |  |
| 0.3667 | 20 | `p20l_33` | 31. PSC | False |  |  |
| 0.3524 | 13 | `p13l_44` | 6. CS(PI)- | False |  |  |
| 0.3476 | 18 | `p18l_40` | 18. W&APC - | False |  |  |
| 0.3476 | 19 | `p19l_23` | 22. E(CP) – | False |  |  |
| 0.3095 | 9 | `p9l_36` | part of medically necessary treatment to | False |  |  |
| 0.3024 | 11 | `p11l_42` | treatment. | False |  |  |
| 0.2714 | 16 | `p16l_30` | 11. C– | False |  |  |
| 0.2714 | 16 | `p16l_41` | 1 year | False |  |  |
| 0.2714 | 17 | `p17l_34` | 14. A– | False |  |  |
| 0.2714 | 18 | `p18l_15` | 16. P– | False |  |  |
| 0.2667 | 20 | `p20l_47` | 32. RG– | False |  |  |
| 0.2619 | 15 | `p15l_41` | 8. N&C - | False |  |  |

### `12_iffco_tokio_iffco_tokio_swasthya_kavach_family_health_policy_47fde468`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.4047 | 22 | `p22l_7` | 1 Month  75% | False |  | duration_percentage_table_row |
| 0.4047 | 22 | `p22l_8` | 3 Month  50% | False |  | duration_percentage_table_row |
| 0.4047 | 22 | `p22l_9` | 6 Month  25% | False |  | duration_percentage_table_row |
| 0.3858 | 7 | `p7l_74` | 65.Major Injuries | True | numbered_short_title_heading |  |
| 0.3708 | 8 | `p8l_55` | 70.Third Degree Burns | True | numbered_short_title_heading |  |
| 0.3519 | 7 | `p7l_60` | 63.End Stage Liver Disease | True | numbered_short_title_heading |  |
| 0.3368 | 6 | `p6l_7` | 46.Preferred Provider Network- | False |  |  |
| 0.3066 | 7 | `p7l_80` | 66.Major Organ /Bone Marrow Transplant | False |  |  |
| 0.2736 | 12 | `p12l_31` | 15 days | False |  |  |
| 0.2594 | 8 | `p8l_62` | COVERAGE UNDER BASE PLAN | False |  |  |
| 0.2557 | 12 | `p12l_80` | COVERAGE UNDER WIDER PLAN | False |  |  |
| 0.2425 | 20 | `p20l_20` | 1. | False |  |  |
| 0.2425 | 20 | `p20l_29` | 2. | False |  |  |
| 0.2425 | 20 | `p20l_34` | 3. | False |  |  |
| 0.2425 | 20 | `p20l_39` | 4. | False |  |  |

### `13_future_generali_future_generali_alpa_bima_group_48186b84`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): lettered_named_heading, numbered_named_policy_heading, roman_policy_section_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.4089 | 1 | `p1l_4` | POLICY WORDINGS | False |  | generic_document_title_or_contents |
| 0.3671 | 10 | `p10l_11` | 3. Migration | True | numbered_named_policy_heading |  |
| 0.3644 | 8 | `p8l_8` | C. EXCLUSIONS | True | roman_policy_section_heading |  |
| 0.3616 | 1 | `p1l_15` | A. DEFINITIONS | True | lettered_named_heading |  |
| 0.3534 | 4 | `p4l_10` | B. SCOPE OF COVER | False |  |  |
| 0.337 | 15 | `p15l_5` | E. SCHEDULE OF BENEFITS | False |  |  |
| 0.3281 | 20 | `p20l_13` | FORM FOR | False |  |  |
| 0.3233 | 9 | `p9l_68` | D. GENERAL TERMS AND CLAUSES | True | roman_policy_section_heading |  |
| 0.3007 | 20 | `p20l_9` | DD    M    M  YYYY | False |  |  |
| 0.2986 | 15 | `p15l_15` | 4 Pre-Existing Disease Cover  Covered | False |  |  |
| 0.2986 | 15 | `p15l_27` | 4 Pre-Existing Disease Cover  Covered | False |  |  |
| 0.2986 | 15 | `p15l_41` | 5 Pre-Existing Disease Cover  Covered | False |  |  |
| 0.2986 | 15 | `p15l_55` | 5 Pre-Existing Disease Cover  Covered | False |  |  |
| 0.2986 | 15 | `p15l_69` | 5 Pre-Existing Disease Cover  Covered | False |  |  |
| 0.2986 | 16 | `p16l_17` | 5 Pre-Existing Disease Cover  Covered | False |  |  |

### `13_future_generali_future_generali_future_health_protect_group`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): lettered_named_heading, numbered_named_policy_heading, roman_policy_section_heading, section_token_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3667 | 13 | `p13l_24` | 1. Migration | True | numbered_named_policy_heading |  |
| 0.3639 | 10 | `p10l_73` | C. EXCLUSIONS | True | roman_policy_section_heading |  |
| 0.3611 | 1 | `p1l_18` | A. DEFINITIONS | True | lettered_named_heading |  |
| 0.3528 | 4 | `p4l_60` | B. SCOPE OF COVER | False |  |  |
| 0.3361 | 17 | `p17l_41` | E. SCHEDULE OF BENEFITS | False |  |  |
| 0.3306 | 21 | `p21l_8` | ADDRESS | False |  |  |
| 0.3194 | 10 | `p10l_33` | III. SECTION III: LOSS OF JOB | False |  |  |
| 0.3167 | 4 | `p4l_64` | I. SECTION I: CRITICAL ILLNESS | False |  |  |
| 0.3167 | 10 | `p10l_47` | Section 2 - Personal Accident. | True | section_token_heading |  |
| 0.3167 | 21 | `p21l_16` | APPRECIATION | False |  |  |
| 0.3139 | 21 | `p21l_5` | CUSTOMER NAME | False |  |  |
| 0.3111 | 21 | `p21l_7` | NAME NAME NAME | False |  |  |
| 0.3083 | 8 | `p8l_65` | II. SECTION II: PERSONAL ACCIDENT | False |  |  |
| 0.3028 | 21 | `p21l_6` | FIRST MIDDLE LAST | False |  |  |
| 0.3 | 21 | `p21l_10` | DD    M    M  YYYY | False |  |  |

### `13_future_generali_future_generali_future_hospicash`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): lettered_named_heading, numbered_named_policy_heading, numbered_short_title_heading, roman_policy_section_heading, section_token_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.3705 | 6 | `p6l_49` | 32. Other | True | numbered_short_title_heading |  |
| 0.3672 | 13 | `p13l_64` | 8. Renewal | True | numbered_named_policy_heading |  |
| 0.3607 | 10 | `p10l_55` | 4. Migration | True | numbered_named_policy_heading |  |
| 0.3541 | 4 | `p4l_12` | A. DEFINITIONS | True | lettered_named_heading |  |
| 0.3541 | 7 | `p7l_48` | C. EXCLUSIONS: | True | roman_policy_section_heading |  |
| 0.3475 | 2 | `p2l_69` | Section D. II. 8 | True | section_token_heading |  |
| 0.3475 | 2 | `p2l_71` | Section D. I. 4. | True | section_token_heading |  |
| 0.3443 | 2 | `p2l_83` | Section D. II. 2. | True | section_token_heading |  |
| 0.3377 | 2 | `p2l_16` | 10 Policy Grievance | False |  |  |
| 0.3377 | 7 | `p7l_10` | B. POLICY BENEFITS: | False |  |  |
| 0.3377 | 10 | `p10l_42` | 3. Free Look Period | True | numbered_short_title_heading |  |
| 0.3377 | 12 | `p12l_57` | 5. Claims Procedure | True | numbered_short_title_heading |  |
| 0.3344 | 11 | `p11l_41` | 8. Moratorium Period | True | numbered_short_title_heading |  |
| 0.3246 | 2 | `p2l_9` | 9 Claims Section D II 5 | False |  |  |
| 0.3238 | 19 | `p19l_4` | FORM FOR | False |  |  |

### `13_future_generali_future_generali_health_total`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): numbered_short_title_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.4802 | 5 | `p5l_7` | POLICY WORDINGS | False |  | generic_document_title_or_contents |
| 0.3628 | 19 | `p19l_65` | 51. ERCP | True | numbered_short_title_heading |  |
| 0.3628 | 25 | `p25l_16` | 5.  BUDS | True | numbered_short_title_heading |  |
| 0.3628 | 26 | `p26l_12` | 4.  CAPS | True | numbered_short_title_heading |  |
| 0.3628 | 26 | `p26l_14` | 6.  COMB | True | numbered_short_title_heading |  |
| 0.3628 | 26 | `p26l_17` | 9.  GOWN | True | numbered_short_title_heading |  |
| 0.3581 | 21 | `p21l_130` | 384. ESWL | True | numbered_short_title_heading |  |
| 0.3581 | 25 | `p25l_71` | 60.  MASK | True | numbered_short_title_heading |  |
| 0.3581 | 26 | `p26l_29` | 21.  HVAC | True | numbered_short_title_heading |  |
| 0.3581 | 27 | `p27l_15` | 8.  GAUZE | True | numbered_short_title_heading |  |
| 0.3535 | 3 | `p3l_64` | 14 Premium | False |  |  |
| 0.3535 | 19 | `p19l_134` | 119. TURBT | True | numbered_short_title_heading |  |
| 0.3535 | 27 | `p27l_28` | 21.  APRON | True | numbered_short_title_heading |  |
| 0.3488 | 25 | `p25l_30` | 19.  SLINGS | True | numbered_short_title_heading |  |
| 0.3488 | 25 | `p25l_47` | 36.  SPACER | True | numbered_short_title_heading |  |

### `16_kotak_mahindra_kotak_kotak_covid_19_secure_policy_wording`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): part_roman_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.4 | 1 | `p1l_138` | PART I | True | part_roman_heading |  |
| 0.15 | 1 | `p1l_208` | n | False |  |  |
| 0.15 | 1 | `p1l_207` | w | False |  |  |
| 0.15 | 1 | `p1l_206` | a | False |  |  |
| 0.15 | 1 | `p1l_205` | r | False |  |  |
| 0.15 | 1 | `p1l_204` | d | False |  |  |
| 0.15 | 1 | `p1l_203` | h | False |  |  |
| 0.15 | 1 | `p1l_202` | t | False |  |  |
| 0.15 | 1 | `p1l_201` | i | False |  |  |
| 0.15 | 1 | `p1l_200` | W | False |  |  |
| 0.15 | 2 | `p2l_212` | n | False |  |  |
| 0.15 | 2 | `p2l_211` | w | False |  |  |
| 0.15 | 2 | `p2l_210` | a | False |  |  |
| 0.15 | 2 | `p2l_209` | r | False |  |  |
| 0.15 | 2 | `p2l_208` | d | False |  |  |

### `16_kotak_mahindra_kotak_kotak_group_hospital_cash`

Classification: **safe_pattern_fix**  
Recommended action: Implement narrow pattern(s): part_roman_heading  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.35 | 1 | `p1l_8` | PART I | True | part_roman_heading |  |
| 0.1833 | 6 | `p6l_285` | • | False |  |  |
| 0.1833 | 6 | `p6l_286` | • | False |  |  |
| 0.1833 | 6 | `p6l_287` | • | False |  |  |
| 0.1167 | 12 | `p12l_112` | PART III | True | part_roman_heading |  |
| 0.05 | 8 | `p8l_276` | I I | False |  |  |
| 0.05 | 8 | `p8l_278` | I I | False |  |  |
| 0.0333 | 1 | `p1l_197` | e | False |  |  |
| -0.05 | 5 | `p5l_191` | Sr. | False |  |  |
| -0.05 | 5 | `p5l_192` | No. | False |  |  |
| -0.05 | 10 | `p10l_25` | Sr. | False |  |  |
| -0.05 | 10 | `p10l_26` | No. | False |  |  |
| -0.0667 | 1 | `p1l_174` | g | False |  |  |
| -0.0667 | 1 | `p1l_173` | n | False |  |  |
| -0.0667 | 1 | `p1l_172` | i | False |  |  |

### `20_sbi_general_sbi_retail_health_pw`

Classification: **false_top_candidate**  
Recommended action: Do not promote top candidate; inspect lower lines or route to physical/parser review.  

| Score | Page | Line | Text | Plausible | Safe Pattern | False Risk |
|---:|---:|---|---|---|---|---|
| 0.4957 | 5 | `p5l_35` | 1 | False |  | bare_number |
| 0.4826 | 5 | `p5l_33` | 6518 | False |  | bare_number |
| 0.4696 | 5 | `p5l_5` | Policy? | False |  |  |
| 0.4435 | 1 | `p1l_2` | SBI GENERAL'S | False |  |  |
| 0.4217 | 8 | `p8l_35` | Two Adults Floater | False |  |  |
| 0.4217 | 10 | `p10l_34` | Two Adults Floater | False |  |  |
| 0.413 | 8 | `p8l_3` | Non Floater Policies | False |  |  |
| 0.413 | 10 | `p10l_2` | Non Floater Policies | False |  |  |
| 0.3957 | 2 | `p2l_7` | Who Can Buy This Policy? | False |  |  |
| 0.3826 | 3 | `p3l_1` | What Does The Policy Cover? | False |  |  |
| 0.3826 | 5 | `p5l_36` | Year | False |  |  |
| 0.3696 | 1 | `p1l_3` | RETAIL HEALTH INSURANCE POLICY | False |  | generic_document_title_or_contents |
| 0.3696 | 12 | `p12l_13` | Corporate & Registered Office: | False |  |  |
| 0.3609 | 6 | `p6l_39` | Hyderabad | False |  |  |
| 0.3565 | 5 | `p5l_34` | YearsYears | False |  |  |
