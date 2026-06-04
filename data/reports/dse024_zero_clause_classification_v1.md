# DSE-024: Zero-Clause Policy Classification (Phase A)

**Date:** 2026-06-04
**Total Policies:** 132
**Errors:** 0

## Category Summary

| Category | Count | % |
|----------|-------|---|
| NON_POLICY | 9 | 6.8% |
| HEADING_MISS | 117 | 88.6% |
| DUPLICATE | 6 | 4.5% |
| SECTION_FAIL | 0 | 0.0% |
| PHYSICAL_BAD | 0 | 0.0% |
| UNSUPPORTED | 0 | 0.0% |
| UNKNOWN | 0 | 0.0% |

## Top Insurers Affected

| Insurer | Count | Categories |
|---------|-------|------------|
| HDFC_ERGO | 21 | HEADING_MISS=20, NON_POLICY=1 |
| Star_Health | 18 | HEADING_MISS=18 |
| Aditya_Birla | 17 | DUPLICATE=3, HEADING_MISS=14 |
| Future_Generali | 9 | DUPLICATE=1, HEADING_MISS=8 |
| Tata_AIG | 7 | HEADING_MISS=7 |
| Kotak_Mahindra | 7 | HEADING_MISS=7 |
| Care_Health | 6 | HEADING_MISS=3, NON_POLICY=3 |
| ICICI_Lombard | 6 | HEADING_MISS=6 |
| Bajaj_Allianz | 6 | HEADING_MISS=6 |
| IFFCO_Tokio | 6 | DUPLICATE=1, HEADING_MISS=5 |
| Oriental_Insurance | 4 | HEADING_MISS=4 |
| Universal_Sompo | 4 | HEADING_MISS=4 |
| Liberty | 3 | DUPLICATE=1, HEADING_MISS=2 |
| Royal_Sundaram | 3 | HEADING_MISS=3 |
| Edelweiss | 3 | HEADING_MISS=2, NON_POLICY=1 |

## Recommended Parser Fixes

- Lower heading threshold from 0.50 to ~0.45 (53/117 HEADING_MISS have max score >= 0.45)
- Improve ALL-CAPS / sentence-case detection for 117 policies where heading scorer produces candidates below threshold
- Increase bold-weight / font-size-ratio signal for policies where headings use bold or larger font but scorer under-weighs visual features
- Review corpus lockdown — 9 NON_POLICY documents may need exclusion from active policy set

## Recommended 20-Policy Sample for Phase B

| # | Slug | Category | Insurer | Pages | Max Heading Score |
|---|------|----------|---------|-------|-------------------|
| 1 | 05_niva_bupa_niva_bupa_health_plus | HEADING_MISS | Niva_Bupa | 126 | 0.469 |
| 2 | non_policy_wordings_nivabupa_health_recharge_prospectus | NON_POLICY | non_policy_wordings | 42 | 0.4198 |
| 3 | 12_iffco_tokio_iffco_tokio_family_health_protector_irdai | DUPLICATE | IFFCO_Tokio | 47 | 0.4967 |
| 4 | 09_hdfc_ergo_hdfc_ergo_my_optima_secure | HEADING_MISS | HDFC_ERGO | 42 | 0.4699 |
| 5 | 02_star_health_star_health_star_group_health_insurance_benefit_plus | HEADING_MISS | Star_Health | 50 | 0.4867 |
| 6 | 11_aditya_birla_aditya_birla_activ_health_2021 | HEADING_MISS | Aditya_Birla | 67 | 0.3667 |
| 7 | 13_future_generali_future_generali_future_poorna_suraksha_group_0bc8ea4f | HEADING_MISS | Future_Generali | 45 | 0.368 |
| 8 | 16_kotak_mahindra_kotak_kotak_group_hospital_cash | HEADING_MISS | Kotak_Mahindra | 30 | 0.35 |
| 9 | tata_aig_arogya_sanjeevani | HEADING_MISS | Tata_AIG | 28 | 0.4738 |
| 10 | 04_icici_lombard_icici_lombard_group_take_care_insurance | HEADING_MISS | ICICI_Lombard | 41 | 0.4481 |
| 11 | 08_bajaj_allianz_bajaj_allianz_family_health_care | HEADING_MISS | Bajaj_Allianz | 37 | 0.3862 |
| 12 | 12_iffco_tokio_iffco_tokio_family_health_protector | HEADING_MISS | IFFCO_Tokio | 47 | 0.4967 |
| 13 | 07_oriental_insurance_oriental_oriental_secure_credit | HEADING_MISS | Oriental_Insurance | 44 | 0.4194 |
| 14 | 14_universal_sompo_universal_sompo_csc_complete_healthcare_insurance | HEADING_MISS | Universal_Sompo | 40 | 0.2 |
| 15 | 21_royal_sundaram_royal_sundaram_ace_health_advantage_pw | HEADING_MISS | Royal_Sundaram | 56 | 0.4817 |
| 16 | 03_care_health_care_freedom_policy | HEADING_MISS | Care_Health | 45 | 0.4905 |
| 17 | 19_liberty_liberty_79fc880c_2c03_e5e9_3a02_dc751307afff | HEADING_MISS | Liberty | 46 | 0.4987 |
| 18 | 18_cholamandalam_cholamandalam_chola_classic_health_individual | HEADING_MISS | Cholamandalam | 35 | 0.4942 |
| 19 | 22_edelweiss_edelweiss_group_corona_pw | HEADING_MISS | Edelweiss | 17 | 0.4639 |
| 20 | 05_niva_bupa_niva_bupa_health_pulse | HEADING_MISS | Niva_Bupa | 63 | 0.4947 |

## All 132 Classifications

| Slug | Category | Insurer | Pages | Headings | Max Score | Sections | Clauses | Tables | Facts | Notes |
|------|----------|---------|-------|----------|-----------|---------|---------|--------|-------|-------|
| tata_aig_arogya_sanjeevani | HEADING_MISS | Tata_AIG | 28 | 3847 | 0.4738 | 1 | 0 | 28 | 0 |  |
| aditya_birla_activ_care | DUPLICATE | Aditya_Birla | 34 | 3486 | 0.3593 | 1 | 0 | 37 | 0 | dup=2 |
| 02_star_health_star_group_accident_insurance | HEADING_MISS | Star_Health | 24 | 1092 | 0.4944 | 1 | 0 | 41 | 0 |  |
| 02_star_health_star_health_medi_classic_insurance_policy_individual | HEADING_MISS | Star_Health | 12 | 2493 | 0.4794 | 1 | 0 | 28 | 0 |  |
| 02_star_health_star_health_senior_citizens_red_carpet_health_insurance_policy | HEADING_MISS | Star_Health | 12 | 2752 | 0.21 | 1 | 0 | 30 | 0 |  |
| 02_star_health_star_health_star_cancer_benefit | HEADING_MISS | Star_Health | 8 | 496 | 0.4914 | 1 | 0 | 11 | 0 |  |
| 02_star_health_star_health_star_care_micro_insurance_policy | HEADING_MISS | Star_Health | 10 | 1415 | 0.4988 | 1 | 0 | 17 | 0 |  |
| 02_star_health_star_health_star_group_cirticare_gold | HEADING_MISS | Star_Health | 18 | 918 | 0.4229 | 1 | 0 | 9 | 0 |  |
| 02_star_health_star_health_star_group_criticare_platinum | HEADING_MISS | Star_Health | 22 | 1165 | 0.4233 | 1 | 0 | 17 | 0 |  |
| 02_star_health_star_health_star_group_health_insurance_benefit_plus | HEADING_MISS | Star_Health | 50 | 2560 | 0.4867 | 1 | 0 | 29 | 0 |  |
| 02_star_health_star_health_star_group_health_insurance_policy_platinum | HEADING_MISS | Star_Health | 31 | 1438 | 0.4975 | 1 | 0 | 53 | 0 |  |
| 02_star_health_star_health_star_health_assure_insurance_policy | HEADING_MISS | Star_Health | 20 | 3516 | 0.4269 | 1 | 0 | 48 | 0 |  |
| 02_star_health_star_health_star_novel_corona_virus_n_covcovid_19_insurance_policypilot_product | HEADING_MISS | Star_Health | 4 | 502 | 0.4121 | 1 | 0 | 6 | 0 |  |
| 02_star_health_star_health_young_star_insurance_policy | HEADING_MISS | Star_Health | 12 | 2138 | 0.4878 | 1 | 0 | 30 | 0 |  |
| 02_star_health_star_policy_star_cancer_care_platinum_insurance_policy | HEADING_MISS | Star_Health | 10 | 1249 | 0.48 | 1 | 0 | 21 | 0 |  |
| 02_star_health_star_policy_star_critical_illness_multipay_insurance_policyweb | HEADING_MISS | Star_Health | 10 | 1408 | 0.4897 | 1 | 0 | 21 | 0 |  |
| 02_star_health_star_policy_star_health_gain_insurance_policy | HEADING_MISS | Star_Health | 8 | 1443 | 0.49 | 1 | 0 | 17 | 0 |  |
| 02_star_health_star_policy_star_super_surplus_floater_insurance_policy | HEADING_MISS | Star_Health | 10 | 2121 | 0.3326 | 1 | 0 | 18 | 0 |  |
| 02_star_health_star_policy_super_surplus_insurance_policy | HEADING_MISS | Star_Health | 10 | 2015 | 0.4 | 1 | 0 | 21 | 0 |  |
| 02_star_health_star_star_care_micro_insurance_policy | HEADING_MISS | Star_Health | 12 | 1558 | 0.4878 | 1 | 0 | 22 | 0 |  |
| 03_care_health_care_freedom_policy | HEADING_MISS | Care_Health | 45 | 3473 | 0.4905 | 1 | 0 | 86 | 0 |  |
| 03_care_health_add_on_explore_plus_policy_terms_conditions | HEADING_MISS | Care_Health | 11 | 868 | 0.4904 | 1 | 0 | 21 | 0 |  |
| 03_care_health_assure_critical_illness_product_prospectus_cum_sales_literature | NON_POLICY | Care_Health | 14 | 774 | 0.4894 | 1 | 0 | 35 | 0 | brochure; document_type_brochure |
| 03_care_health_care_plus_health_insurance_product_brochure | NON_POLICY | Care_Health | 4 | 224 | 0.3929 | 1 | 0 | 7 | 0 | brochure; document_type_brochure |
| 03_care_health_enhance_t_c_effective_from_12_september_2024 | HEADING_MISS | Care_Health | 45 | 3550 | 0.485 | 1 | 0 | 82 | 0 |  |
| 03_care_health_senior_health_advantage_brochure | NON_POLICY | Care_Health | 4 | 138 | 0.3688 | 1 | 0 | 6 | 0 | brochure; document_type_brochure |
| 04_icici_lombard_befit_rider_policy_wording | HEADING_MISS | ICICI_Lombard | 22 | 1055 | 0.4802 | 1 | 0 | 26 | 0 |  |
| 04_icici_lombard_icici_lombard_corona_kavach_policy_icici_lombard | HEADING_MISS | ICICI_Lombard | 12 | 1215 | 0.4574 | 1 | 0 | 16 | 0 |  |
| 04_icici_lombard_icici_lombard_crtical_illness | HEADING_MISS | ICICI_Lombard | 29 | 1106 | 0.3792 | 1 | 0 | 7 | 0 |  |
| 04_icici_lombard_icici_lombard_golden_shield | HEADING_MISS | ICICI_Lombard | 31 | 3133 | 0.4904 | 1 | 0 | 38 | 0 |  |
| 04_icici_lombard_icici_lombard_group_take_care_insurance | HEADING_MISS | ICICI_Lombard | 41 | 1956 | 0.4481 | 1 | 0 | 25 | 0 |  |
| 04_icici_lombard_icici_lombard_health_care_plus_policy | HEADING_MISS | ICICI_Lombard | 30 | 1575 | 0.4974 | 1 | 0 | 27 | 0 |  |
| 05_niva_bupa_niva_bupa_health_plus | HEADING_MISS | Niva_Bupa | 126 | 5296 | 0.469 | 1 | 0 | 157 | 0 |  |
| 05_niva_bupa_niva_bupa_health_pulse | HEADING_MISS | Niva_Bupa | 63 | 3117 | 0.4947 | 1 | 0 | 54 | 0 |  |
| 06_united_india_unitedindia_arogya_sanjeevani_irdai | NON_POLICY | United_India | 2 | 127 | 0.4674 | 1 | 0 | 3 | 0 | dup=2; brochure; document_type_brochure |
| 06_united_india_united_india_arogya_sanjeevani_policy_united_india_insurance_company_limited | NON_POLICY | United_India | 2 | 127 | 0.4674 | 1 | 0 | 3 | 0 | dup=2; brochure; document_type_brochure,possible_duplicate |
| 07_oriental_insurance_oriental_health_of_privileged_elders | HEADING_MISS | Oriental_Insurance | 29 | 1230 | 0.3607 | 1 | 0 | 18 | 0 |  |
| 07_oriental_insurance_oriental_mediclaim_individual_policy | HEADING_MISS | Oriental_Insurance | 35 | 1867 | 0.4211 | 1 | 0 | 28 | 0 |  |
| 07_oriental_insurance_oriental_mediclaim_insurance_policy_individual | HEADING_MISS | Oriental_Insurance | 35 | 1869 | 0.4211 | 1 | 0 | 28 | 0 |  |
| 07_oriental_insurance_oriental_oriental_secure_credit | HEADING_MISS | Oriental_Insurance | 44 | 2178 | 0.4194 | 1 | 0 | 29 | 0 |  |
| 08_bajaj_allianz_bajaj_allianz_extra_care | HEADING_MISS | Bajaj_Allianz | 24 | 1018 | 0.4447 | 1 | 0 | 14 | 0 |  |
| 08_bajaj_allianz_bajaj_allianz_extra_care_plus | HEADING_MISS | Bajaj_Allianz | 24 | 1719 | 0.4455 | 1 | 0 | 17 | 0 |  |
| 08_bajaj_allianz_bajaj_allianz_family_health_care | HEADING_MISS | Bajaj_Allianz | 37 | 2225 | 0.3862 | 1 | 0 | 45 | 0 |  |
| 08_bajaj_allianz_bajaj_allianz_m_care | HEADING_MISS | Bajaj_Allianz | 13 | 709 | 0.4288 | 1 | 0 | 7 | 0 |  |
| 08_bajaj_allianz_bajaj_allianz_m_care_group | HEADING_MISS | Bajaj_Allianz | 16 | 830 | 0.4222 | 1 | 0 | 10 | 0 |  |
| 08_bajaj_allianz_bajaj_allianz_personal_accident_insurance_policy | HEADING_MISS | Bajaj_Allianz | 13 | 832 | 0.3818 | 1 | 0 | 14 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_critical_advantage_rider | HEADING_MISS | HDFC_ERGO | 15 | 784 | 0.4324 | 1 | 0 | 10 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_critical_illness_insurance | HEADING_MISS | HDFC_ERGO | 22 | 1011 | 0.499 | 1 | 0 | 19 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_day2daycare | HEADING_MISS | HDFC_ERGO | 18 | 864 | 0.4524 | 1 | 0 | 18 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_hdfc_ergo_group_protect | HEADING_MISS | HDFC_ERGO | 41 | 2034 | 0.475 | 1 | 0 | 47 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_hdfc_ergo_hospital_cash_insurance | HEADING_MISS | HDFC_ERGO | 22 | 987 | 0.3148 | 1 | 0 | 22 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_health_on | HEADING_MISS | HDFC_ERGO | 30 | 1718 | 0.4079 | 1 | 0 | 30 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_health_suraksha_top_up_plus | HEADING_MISS | HDFC_ERGO | 41 | 2418 | 0.3967 | 1 | 0 | 48 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_health_wallet | HEADING_MISS | HDFC_ERGO | 35 | 1917 | 0.3459 | 1 | 0 | 29 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_individual_personal_accident | HEADING_MISS | HDFC_ERGO | 33 | 1579 | 0.4708 | 1 | 0 | 30 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_maxima_insurance | HEADING_MISS | HDFC_ERGO | 37 | 1330 | 0.4798 | 1 | 0 | 34 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_mosquito_disease_protection_policy_group_71442893 | HEADING_MISS | HDFC_ERGO | 28 | 1316 | 0.4511 | 1 | 0 | 32 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_optima_cash | HEADING_MISS | HDFC_ERGO | 20 | 1037 | 0.4833 | 1 | 0 | 22 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_optima_plus | HEADING_MISS | HDFC_ERGO | 33 | 1400 | 0.3778 | 1 | 0 | 29 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_optima_senior | HEADING_MISS | HDFC_ERGO | 25 | 1470 | 0.4414 | 1 | 0 | 25 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_optima_super | HEADING_MISS | HDFC_ERGO | 28 | 1405 | 0.308 | 1 | 0 | 26 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_protector_rider | HEADING_MISS | HDFC_ERGO | 14 | 826 | 0.4971 | 1 | 0 | 14 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_total_health | HEADING_MISS | HDFC_ERGO | 12 | 1560 | 0.3682 | 1 | 0 | 19 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_icanenhance | HEADING_MISS | HDFC_ERGO | 21 | 1193 | 0.2686 | 1 | 0 | 17 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_my_optima_secure | HEADING_MISS | HDFC_ERGO | 42 | 1917 | 0.4699 | 1 | 0 | 50 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_my_health_medisure_super_topup | HEADING_MISS | HDFC_ERGO | 34 | 1445 | 0.4633 | 1 | 0 | 35 | 0 |  |
| 09_hdfc_ergo_hdfc_ergo_optima_restore_cis | NON_POLICY | HDFC_ERGO | 33 | 2545 | 0.4895 | 1 | 0 | 46 | 0 |  |
| 10_tata_aig_tata_aig_individual_accident_and_sickness_hospital_cash_policy | HEADING_MISS | Tata_AIG | 13 | 1376 | 0.4847 | 1 | 0 | 16 | 0 |  |
| 10_tata_aig_tata_aig_medicare_plus_topup | HEADING_MISS | Tata_AIG | 26 | 4740 | 0.425 | 1 | 0 | 25 | 0 |  |
| 10_tata_aig_tata_aig_mediraksha | HEADING_MISS | Tata_AIG | 16 | 1754 | 0.3909 | 1 | 0 | 22 | 0 |  |
| 10_tata_aig_tata_aig_wellsurance_executive_policy | HEADING_MISS | Tata_AIG | 12 | 1084 | 0.4615 | 1 | 0 | 9 | 0 |  |
| 10_tata_aig_tata_aig_wellsurance_family_policy | HEADING_MISS | Tata_AIG | 14 | 1305 | 0.4964 | 1 | 0 | 16 | 0 |  |
| 10_tata_aig_tata_aig_wellsurance_woman_policy | HEADING_MISS | Tata_AIG | 12 | 1378 | 0.4896 | 1 | 0 | 16 | 0 |  |
| 11_aditya_birla_aditya_birla_activ_assure | HEADING_MISS | Aditya_Birla | 39 | 4152 | 0.3471 | 1 | 0 | 47 | 0 |  |
| 11_aditya_birla_aditya_birla_activ_health | HEADING_MISS | Aditya_Birla | 48 | 5535 | 0.3643 | 1 | 0 | 54 | 0 |  |
| 11_aditya_birla_aditya_birla_activ_health_2021 | HEADING_MISS | Aditya_Birla | 67 | 6916 | 0.3667 | 1 | 0 | 82 | 0 |  |
| 11_aditya_birla_aditya_birla_activ_health_platinum | HEADING_MISS | Aditya_Birla | 48 | 5535 | 0.3643 | 1 | 0 | 54 | 0 |  |
| 11_aditya_birla_aditya_birla_active_care | HEADING_MISS | Aditya_Birla | 34 | 3486 | 0.3593 | 1 | 0 | 37 | 0 | dup=2; possible_duplicate |
| 11_aditya_birla_aditya_birla_arogyasanjeevani_policy_aditya_birla_health_insurance_company_limited | DUPLICATE | Aditya_Birla | 11 | 1880 | 0.0 | 1 | 0 | 12 | 0 | dup=2; possible_duplicate |
| 11_aditya_birla_aditya_birla_arogya_sanjeevani_irdai | HEADING_MISS | Aditya_Birla | 11 | 1880 | 0.0 | 1 | 0 | 12 | 0 | dup=2 |
| 11_aditya_birla_aditya_birla_corona_kavach_policy_aditya_birla_health_insurance_company_limited | HEADING_MISS | Aditya_Birla | 12 | 1908 | 0.0 | 1 | 0 | 15 | 0 |  |
| 11_aditya_birla_aditya_birla_global_health_secure | HEADING_MISS | Aditya_Birla | 18 | 2046 | 0.3538 | 1 | 0 | 18 | 0 | dup=2; possible_duplicate |
| 11_aditya_birla_aditya_birla_global_health_secure_2021 | DUPLICATE | Aditya_Birla | 18 | 2046 | 0.3538 | 1 | 0 | 18 | 0 | dup=2; possible_duplicate |
| 11_aditya_birla_aditya_birla_global_health_secure_older | HEADING_MISS | Aditya_Birla | 23 | 2553 | 0.348 | 1 | 0 | 24 | 0 |  |
| 11_aditya_birla_aditya_birla_group_activ_helath | HEADING_MISS | Aditya_Birla | 25 | 2790 | 0.387 | 1 | 0 | 26 | 0 |  |
| 11_aditya_birla_aditya_birla_group_assure_covid_19 | HEADING_MISS | Aditya_Birla | 14 | 1776 | 0.0 | 1 | 0 | 19 | 0 |  |
| 11_aditya_birla_aditya_birla_group_protect | HEADING_MISS | Aditya_Birla | 37 | 3911 | 0.4083 | 1 | 0 | 46 | 0 |  |
| 11_aditya_birla_aditya_birla_saral_suraksha_bima | HEADING_MISS | Aditya_Birla | 15 | 2267 | 0.0 | 1 | 0 | 19 | 0 |  |
| 11_aditya_birla_aditya_birla_super_health_plus_top_up | HEADING_MISS | Aditya_Birla | 20 | 2292 | 0.14 | 1 | 0 | 21 | 0 |  |
| 12_iffco_tokio_iffco_tokio_critical_illness_insurance_policy | HEADING_MISS | IFFCO_Tokio | 20 | 954 | 0.4885 | 1 | 0 | 19 | 0 |  |
| 12_iffco_tokio_iffco_tokio_family_health_protector | HEADING_MISS | IFFCO_Tokio | 47 | 2133 | 0.4967 | 1 | 0 | 40 | 0 | dup=2; possible_duplicate |
| 12_iffco_tokio_iffco_tokio_family_health_protector_irdai | DUPLICATE | IFFCO_Tokio | 47 | 2133 | 0.4967 | 1 | 0 | 40 | 0 | dup=2 |
| 12_iffco_tokio_iffco_tokio_group_medishield_insurance_policy | HEADING_MISS | IFFCO_Tokio | 23 | 1091 | 0.4976 | 1 | 0 | 20 | 0 |  |
| 12_iffco_tokio_iffco_tokio_iffco_tokio_hospital_daily_cash_policy | HEADING_MISS | IFFCO_Tokio | 25 | 1076 | 0.431 | 1 | 0 | 17 | 0 |  |
| 12_iffco_tokio_iffco_tokio_swasthya_kavach_family_health_policy_47fde468 | HEADING_MISS | IFFCO_Tokio | 25 | 1351 | 0.4047 | 1 | 0 | 19 | 0 |  |
| 13_future_generali_future_generali_alpa_bima_group_48186b84 | HEADING_MISS | Future_Generali | 20 | 1123 | 0.4089 | 1 | 0 | 22 | 0 |  |
| 13_future_generali_future_generali_arogya_sanjeevani_policy_future_generali_india_insurance_company_limited | HEADING_MISS | Future_Generali | 25 | 1387 | 0.4529 | 1 | 0 | 24 | 0 |  |
| 13_future_generali_future_generali_future_advantage_top_up_group | HEADING_MISS | Future_Generali | 23 | 1711 | 0.445 | 1 | 0 | 29 | 0 |  |
| 13_future_generali_future_generali_future_health_protect_group | HEADING_MISS | Future_Generali | 21 | 1234 | 0.3667 | 1 | 0 | 27 | 0 |  |
| 13_future_generali_future_generali_future_hospicash | HEADING_MISS | Future_Generali | 19 | 1084 | 0.3705 | 1 | 0 | 40 | 0 |  |
| 13_future_generali_future_generali_future_poorna_suraksha_group_0bc8ea4f | HEADING_MISS | Future_Generali | 45 | 2668 | 0.368 | 1 | 0 | 39 | 0 | dup=2; possible_duplicate |
| 13_future_generali_future_generali_future_vector_care | HEADING_MISS | Future_Generali | 9 | 602 | 0.4212 | 1 | 0 | 4 | 0 |  |
| 13_future_generali_future_generali_health_total | HEADING_MISS | Future_Generali | 33 | 2405 | 0.4802 | 1 | 0 | 57 | 0 |  |
| 13_future_generali_future_generali_poorna_suraksha_group_pw | DUPLICATE | Future_Generali | 45 | 2668 | 0.368 | 1 | 0 | 39 | 0 | dup=2; possible_duplicate |
| 14_universal_sompo_universal_sompo_csc_complete_healthcare_insurance | HEADING_MISS | Universal_Sompo | 40 | 15756 | 0.2 | 1 | 0 | 40 | 0 |  |
| 14_universal_sompo_universal_sompo_bancassurance_indianbank_policy_wordings | HEADING_MISS | Universal_Sompo | 33 | 1674 | 0.4368 | 1 | 0 | 37 | 0 |  |
| 14_universal_sompo_universal_sompo_corona_rakshak_corona_rakshak_policy_wordings | HEADING_MISS | Universal_Sompo | 18 | 714 | 0.4845 | 1 | 0 | 26 | 0 |  |
| 14_universal_sompo_universal_sompo_group_mashak_rakshak_group_mashak_rakshak_policy_wordings | HEADING_MISS | Universal_Sompo | 22 | 882 | 0.4978 | 1 | 0 | 25 | 0 |  |
| 15_magma_hdi_magma_hdi_corona_kavach_policy_magma_hdi | HEADING_MISS | Magma_HDI | 19 | 984 | 0.4487 | 1 | 0 | 19 | 0 |  |
| 16_kotak_mahindra_kotak_corona_kavach_group_policykotak_mahindra_general_insurance_company_ltd | HEADING_MISS | Kotak_Mahindra | 12 | 2869 | 0.0 | 1 | 0 | 15 | 0 |  |
| 16_kotak_mahindra_kotak_kotak_covid_19_secure_policy_wording | HEADING_MISS | Kotak_Mahindra | 13 | 3161 | 0.4 | 1 | 0 | 20 | 0 |  |
| 16_kotak_mahindra_kotak_kotak_group_health_care | HEADING_MISS | Kotak_Mahindra | 28 | 4859 | 0.0 | 1 | 0 | 35 | 0 |  |
| 16_kotak_mahindra_kotak_kotak_group_hospital_cash | HEADING_MISS | Kotak_Mahindra | 30 | 6301 | 0.35 | 1 | 0 | 36 | 0 |  |
| 16_kotak_mahindra_kotak_corona_kavach_group_policy_policy_wording | HEADING_MISS | Kotak_Mahindra | 12 | 3051 | 0.05 | 1 | 0 | 15 | 0 |  |
| 16_kotak_mahindra_kotak_corona_kavach_policy_policy_wording | HEADING_MISS | Kotak_Mahindra | 12 | 2975 | 0.05 | 1 | 0 | 15 | 0 |  |
| 16_kotak_mahindra_kotak_corona_rakshak_policy_policy_wording | HEADING_MISS | Kotak_Mahindra | 6 | 1505 | 0.05 | 1 | 0 | 7 | 0 |  |
| 17_reliance_reliance_reliance_group_hospi_cash_insurance | HEADING_MISS | Reliance | 25 | 2418 | 0.4849 | 1 | 0 | 43 | 0 |  |
| 18_cholamandalam_cholamandalam_chola_classic_health_family_floater | HEADING_MISS | Cholamandalam | 29 | 1747 | 0.4978 | 1 | 0 | 31 | 0 |  |
| 18_cholamandalam_cholamandalam_chola_classic_health_individual | HEADING_MISS | Cholamandalam | 35 | 1902 | 0.4942 | 1 | 0 | 39 | 0 |  |
| 19_liberty_liberty_02c526cb_d2a3_3706_729e_cc645ca06934 | HEADING_MISS | Liberty | 43 | 1853 | 0.4905 | 1 | 0 | 34 | 0 | dup=2; possible_duplicate |
| 19_liberty_liberty_79fc880c_2c03_e5e9_3a02_dc751307afff | HEADING_MISS | Liberty | 46 | 1849 | 0.4987 | 1 | 0 | 29 | 0 |  |
| 19_liberty_liberty_liberty_group_health_policy | DUPLICATE | Liberty | 43 | 1853 | 0.4905 | 1 | 0 | 34 | 0 | dup=2; possible_duplicate |
| 20_sbi_general_sbi_retail_health_pw | HEADING_MISS | SBI_General | 12 | 683 | 0.4957 | 1 | 0 | 12 | 0 |  |
| 21_royal_sundaram_royal_sundaram_ace_health_advantage_pw | HEADING_MISS | Royal_Sundaram | 56 | 2888 | 0.4817 | 1 | 0 | 59 | 0 |  |
| 21_royal_sundaram_royal_sundaram_group_health_irdai_pw | HEADING_MISS | Royal_Sundaram | 50 | 2867 | 0.3769 | 1 | 0 | 53 | 0 |  |
| 21_royal_sundaram_royal_sundaram_micro_health_shield_pw | HEADING_MISS | Royal_Sundaram | 24 | 1372 | 0.4915 | 1 | 0 | 15 | 0 |  |
| 22_edelweiss_edelweiss_group_corona_pw | HEADING_MISS | Edelweiss | 17 | 2495 | 0.4639 | 1 | 0 | 20 | 0 |  |
| 22_edelweiss_edelweiss_saral_suraksha_bima_pw | HEADING_MISS | Edelweiss | 17 | 1240 | 0.4569 | 1 | 0 | 18 | 0 |  |
| 22_edelweiss_edelweiss_well_baby_well_mother_addon_pw | NON_POLICY | Edelweiss | 2 | 89 | 0.1573 | 1 | 0 | 4 | 0 | brochure; document_type_brochure |
| 23_raheja_qbe_raheja_qbe_group_health_super_top_up_pw | HEADING_MISS | Raheja_QBE | 49 | 1997 | 0.4692 | 1 | 0 | 51 | 0 |  |
| 23_raheja_qbe_raheja_qbe_product_list | NON_POLICY | Raheja_QBE | 4 | 540 | 0.1424 | 1 | 0 | 4 | 0 |  |
| non_policy_wordings_nivabupa_health_recharge_prospectus | NON_POLICY | non_policy_wordings | 42 | 1794 | 0.4198 | 1 | 0 | 23 | 0 | brochure; document_type_brochure |
