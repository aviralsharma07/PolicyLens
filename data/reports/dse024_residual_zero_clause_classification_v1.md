# DSE-024 Residual Zero-Clause Classification

Date: 2026-06-04

## Summary

Total zero-clause policies classified: **110**

| Classification | Count |
|---|---:|
| section_tree_fail | 44 |
| heading_miss | 34 |
| duplicate_or_superseded | 14 |
| needs_manual_review | 10 |
| non_policy_or_rider | 6 |
| unsupported_format | 2 |

## Top Parser-Fix Candidates (Top 20)

Highest-confidence cases where parser changes could resolve zero-clause.

| # | Insurer | Classification | Max Score | Headings | Fallback | Pages | Top Candidate |
|---|---|---|---|---|---|---|---|
| 1 | HDFC_ERGO | section_tree_fail | 0.499 | 2 | 2 | 22 | "I. Contact Us" (0.499) |
| 2 | Liberty | section_tree_fail | 0.4987 | 8 | 8 | 46 | "10.Renewal" (0.4987) |
| 3 | Cholamandalam | section_tree_fail | 0.4978 | 6 | 6 | 29 | "27.Migration" (0.4978) |
| 4 | IFFCO_Tokio | section_tree_fail | 0.4976 | 6 | 6 | 23 | "20. Illness" (0.4976) |
| 5 | ICICI_Lombard | section_tree_fail | 0.4974 | 5 | 5 | 30 | "0.25 years" (0.4974) |
| 6 | Tata_AIG | section_tree_fail | 0.4964 | 7 | 7 | 14 | "POLICY WORDINGS" (0.4964) |
| 7 | SBI_General | heading_miss | 0.4957 | 0 | 0 | 12 | "1" (0.4957) |
| 8 | Niva_Bupa | section_tree_fail | 0.4947 | 7 | 7 | 63 | "6. Exclusions" (0.4947) |
| 9 | Cholamandalam | section_tree_fail | 0.4942 | 9 | 9 | 35 | "28.Migration" (0.4942) |
| 10 | Tata_AIG | section_tree_fail | 0.4896 | 8 | 8 | 12 | "18. Limitations." (0.4896) |
| 11 | HDFC_ERGO | section_tree_fail | 0.4895 | 4 | 4 | 33 | "1 Year Policy" (0.4895) |
| 12 | IFFCO_Tokio | section_tree_fail | 0.4885 | 5 | 5 | 20 | "8. Migration" (0.4885) |
| 13 | Universal_Sompo | section_tree_fail | 0.4868 | 3 | 3 | 33 | "D. BENEFITS:" (0.4868) |
| 14 | Future_Generali | section_tree_fail | 0.485 | 3 | 3 | 23 | "C. EXCLUSIONS" (0.485) |
| 15 | Reliance | section_tree_fail | 0.4849 | 2 | 2 | 25 | "2. Definitions" (0.4849) |
| 16 | Tata_AIG | section_tree_fail | 0.4847 | 6 | 6 | 13 | "Part E: Coverage" (0.4847) |
| 17 | HDFC_ERGO | section_tree_fail | 0.4833 | 1 | 1 | 20 | "1. Waiting Periods" (0.4833) |
| 18 | Royal_Sundaram | section_tree_fail | 0.4817 | 3 | 3 | 56 | "10. Indexation" (0.4817) |
| 19 | Future_Generali | heading_miss | 0.4802 | 0 | 0 | 33 | "POLICY WORDINGS" (0.4802) |
| 20 | HDFC_ERGO | section_tree_fail | 0.4798 | 8 | 8 | 37 | "1 Year Policy Period" (0.4798) |

## Top Insurer Clusters

| Insurer | Zero-Clause |
|---|---:|
| HDFC_ERGO | 21 |
| Aditya_Birla | 17 |
| Future_Generali | 9 |
| Tata_AIG | 7 |
| Kotak_Mahindra | 7 |
| Star_Health | 6 |
| Bajaj_Allianz | 6 |
| IFFCO_Tokio | 6 |
| Oriental_Insurance | 4 |
| ICICI_Lombard | 3 |
| Liberty | 3 |
| Edelweiss | 3 |
| Care_Health | 2 |
| Niva_Bupa | 2 |
| United_India | 2 |
| Universal_Sompo | 2 |
| Cholamandalam | 2 |
| Royal_Sundaram | 2 |
| Raheja_QBE | 2 |
| Magma_HDI | 1 |
| Reliance | 1 |
| SBI_General | 1 |
| non_policy_wordings | 1 |

## Classification by Insurer

### section_tree_fail

| Insurer | Count |
|---|---:|
| HDFC_ERGO | 11 |
| Tata_AIG | 6 |
| Bajaj_Allianz | 5 |
| Future_Generali | 3 |
| ICICI_Lombard | 2 |
| Niva_Bupa | 2 |
| Oriental_Insurance | 2 |
| IFFCO_Tokio | 2 |
| Cholamandalam | 2 |
| Royal_Sundaram | 2 |
| Edelweiss | 2 |
| Universal_Sompo | 1 |
| Magma_HDI | 1 |
| Reliance | 1 |
| Liberty | 1 |
| Raheja_QBE | 1 |

### duplicate_or_superseded

| Insurer | Count |
|---|---:|
| Aditya_Birla | 6 |
| United_India | 2 |
| IFFCO_Tokio | 2 |
| Future_Generali | 2 |
| Liberty | 2 |

### needs_manual_review

| Insurer | Count |
|---|---:|
| Aditya_Birla | 4 |
| Kotak_Mahindra | 4 |
| Star_Health | 1 |
| Universal_Sompo | 1 |

### heading_miss

| Insurer | Count |
|---|---:|
| HDFC_ERGO | 8 |
| Aditya_Birla | 7 |
| Star_Health | 5 |
| Future_Generali | 4 |
| Oriental_Insurance | 2 |
| IFFCO_Tokio | 2 |
| Kotak_Mahindra | 2 |
| ICICI_Lombard | 1 |
| Bajaj_Allianz | 1 |
| Tata_AIG | 1 |
| SBI_General | 1 |

### non_policy_or_rider

| Insurer | Count |
|---|---:|
| Care_Health | 2 |
| HDFC_ERGO | 2 |
| Edelweiss | 1 |
| non_policy_wordings | 1 |

### unsupported_format

| Insurer | Count |
|---|---:|
| Kotak_Mahindra | 1 |
| Raheja_QBE | 1 |

## Per-Policy Detail

| Slug | Insurer | Pages | Zero Headings | Max Score | Classification | Confidence |
|---|---|---|---|---|---|---|
| 12_iffco_tokio_iffco_tokio_family_health_protector | IFFCO_Tokio | 47 | N | 0.4967 | duplicate_or_superseded | high |
| 12_iffco_tokio_iffco_tokio_family_health_protector | IFFCO_Tokio | 47 | N | 0.4967 | duplicate_or_superseded | high |
| 19_liberty_liberty_02c526cb_d2a3_3706_729e_cc645ca | Liberty | 43 | N | 0.4905 | duplicate_or_superseded | high |
| 19_liberty_liberty_liberty_group_health_policy | Liberty | 43 | N | 0.4905 | duplicate_or_superseded | high |
| 06_united_india_unitedindia_arogya_sanjeevani_irda | United_India | 2 | N | 0.4674 | duplicate_or_superseded | high |
| 06_united_india_united_india_arogya_sanjeevani_pol | United_India | 2 | N | 0.4674 | duplicate_or_superseded | high |
| 13_future_generali_future_generali_future_poorna_s | Future_Generali | 45 | Y | 0.368 | duplicate_or_superseded | high |
| 13_future_generali_future_generali_poorna_suraksha | Future_Generali | 45 | Y | 0.368 | duplicate_or_superseded | high |
| aditya_birla_activ_care | Aditya_Birla | 34 | Y | 0.3593 | duplicate_or_superseded | high |
| 11_aditya_birla_aditya_birla_active_care | Aditya_Birla | 34 | Y | 0.3593 | duplicate_or_superseded | high |
| 11_aditya_birla_aditya_birla_global_health_secure | Aditya_Birla | 18 | Y | 0.3538 | duplicate_or_superseded | high |
| 11_aditya_birla_aditya_birla_global_health_secure_ | Aditya_Birla | 18 | Y | 0.3538 | duplicate_or_superseded | high |
| 11_aditya_birla_aditya_birla_arogyasanjeevani_poli | Aditya_Birla | 11 | Y | -0.2 | duplicate_or_superseded | high |
| 11_aditya_birla_aditya_birla_arogya_sanjeevani_ird | Aditya_Birla | 11 | Y | -0.2 | duplicate_or_superseded | high |
| 20_sbi_general_sbi_retail_health_pw | SBI_General | 12 | Y | 0.4957 | heading_miss | medium |
| 13_future_generali_future_generali_health_total | Future_Generali | 33 | Y | 0.4802 | heading_miss | medium |
| 09_hdfc_ergo_hdfc_ergo_hdfc_ergo_group_protect | HDFC_ERGO | 41 | Y | 0.475 | heading_miss | medium |
| 12_iffco_tokio_iffco_tokio_iffco_tokio_hospital_da | IFFCO_Tokio | 25 | Y | 0.431 | heading_miss | medium |
| 02_star_health_star_health_star_group_criticare_pl | Star_Health | 22 | Y | 0.4233 | heading_miss | medium |
| 02_star_health_star_health_star_group_cirticare_go | Star_Health | 18 | Y | 0.4229 | heading_miss | medium |
| 07_oriental_insurance_oriental_oriental_secure_cre | Oriental_Insurance | 44 | Y | 0.4194 | heading_miss | medium |
| 09_hdfc_ergo_hdfc_ergo_health_on | HDFC_ERGO | 30 | Y | 0.4132 | heading_miss | medium |
| 02_star_health_star_health_star_novel_corona_virus | Star_Health | 4 | Y | 0.4121 | heading_miss | medium |
| 13_future_generali_future_generali_alpa_bima_group | Future_Generali | 20 | Y | 0.4089 | heading_miss | medium |
| 11_aditya_birla_aditya_birla_group_protect | Aditya_Birla | 37 | Y | 0.4083 | heading_miss | medium |
| 12_iffco_tokio_iffco_tokio_swasthya_kavach_family_ | IFFCO_Tokio | 25 | Y | 0.4047 | heading_miss | medium |
| 02_star_health_star_policy_super_surplus_insurance | Star_Health | 10 | Y | 0.4 | heading_miss | medium |
| 16_kotak_mahindra_kotak_kotak_covid_19_secure_poli | Kotak_Mahindra | 13 | Y | 0.4 | heading_miss | medium |
| 09_hdfc_ergo_hdfc_ergo_health_suraksha_top_up_plus | HDFC_ERGO | 41 | Y | 0.3967 | heading_miss | medium |
| 10_tata_aig_tata_aig_mediraksha | Tata_AIG | 16 | Y | 0.3955 | heading_miss | medium |
| 09_hdfc_ergo_hdfc_ergo_hdfc_ergo_hospital_cash_ins | HDFC_ERGO | 22 | Y | 0.3944 | heading_miss | medium |
| 11_aditya_birla_aditya_birla_group_activ_helath | Aditya_Birla | 25 | Y | 0.387 | heading_miss | medium |
| 08_bajaj_allianz_bajaj_allianz_personal_accident_i | Bajaj_Allianz | 13 | Y | 0.3818 | heading_miss | medium |
| 04_icici_lombard_icici_lombard_crtical_illness | ICICI_Lombard | 29 | Y | 0.3792 | heading_miss | medium |
| 09_hdfc_ergo_hdfc_ergo_optima_plus | HDFC_ERGO | 33 | Y | 0.3778 | heading_miss | medium |
| 13_future_generali_future_generali_future_hospicas | Future_Generali | 19 | Y | 0.3705 | heading_miss | medium |
| 09_hdfc_ergo_hdfc_ergo_total_health | HDFC_ERGO | 12 | Y | 0.3682 | heading_miss | medium |
| 11_aditya_birla_aditya_birla_activ_health_2021 | Aditya_Birla | 67 | Y | 0.3667 | heading_miss | medium |
| 13_future_generali_future_generali_future_health_p | Future_Generali | 21 | Y | 0.3667 | heading_miss | medium |
| 11_aditya_birla_aditya_birla_activ_health | Aditya_Birla | 48 | Y | 0.3643 | heading_miss | medium |
| 11_aditya_birla_aditya_birla_activ_health_platinum | Aditya_Birla | 48 | Y | 0.3643 | heading_miss | medium |
| 07_oriental_insurance_oriental_health_of_privilege | Oriental_Insurance | 29 | Y | 0.3607 | heading_miss | medium |
| 16_kotak_mahindra_kotak_kotak_group_hospital_cash | Kotak_Mahindra | 30 | Y | 0.35 | heading_miss | medium |
| 11_aditya_birla_aditya_birla_global_health_secure_ | Aditya_Birla | 23 | Y | 0.348 | heading_miss | medium |
| 11_aditya_birla_aditya_birla_activ_assure | Aditya_Birla | 39 | Y | 0.3471 | heading_miss | medium |
| 09_hdfc_ergo_hdfc_ergo_health_wallet | HDFC_ERGO | 35 | Y | 0.3459 | heading_miss | medium |
| 02_star_health_star_policy_star_super_surplus_floa | Star_Health | 10 | Y | 0.3326 | heading_miss | medium |
| 09_hdfc_ergo_hdfc_ergo_optima_super | HDFC_ERGO | 28 | Y | 0.308 | heading_miss | medium |
| 11_aditya_birla_aditya_birla_super_health_plus_top | Aditya_Birla | 20 | Y | 0.2933 | needs_manual_review | low |
| 02_star_health_star_health_senior_citizens_red_car | Star_Health | 12 | Y | 0.21 | needs_manual_review | low |
| 14_universal_sompo_universal_sompo_csc_complete_he | Universal_Sompo | 40 | Y | 0.2 | needs_manual_review | low |
| 16_kotak_mahindra_kotak_corona_kavach_group_policy | Kotak_Mahindra | 12 | Y | 0.05 | needs_manual_review | low |
| 16_kotak_mahindra_kotak_corona_kavach_policy_polic | Kotak_Mahindra | 12 | Y | 0.05 | needs_manual_review | low |
| 16_kotak_mahindra_kotak_corona_kavach_group_policy | Kotak_Mahindra | 12 | Y | 0.0 | needs_manual_review | low |
| 16_kotak_mahindra_kotak_kotak_group_health_care | Kotak_Mahindra | 28 | Y | -0.05 | needs_manual_review | low |
| 11_aditya_birla_aditya_birla_group_assure_covid_19 | Aditya_Birla | 14 | Y | -0.1 | needs_manual_review | low |
| 11_aditya_birla_aditya_birla_corona_kavach_policy_ | Aditya_Birla | 12 | Y | -0.2 | needs_manual_review | low |
| 11_aditya_birla_aditya_birla_saral_suraksha_bima | Aditya_Birla | 15 | Y | -0.2 | needs_manual_review | low |
| 09_hdfc_ergo_hdfc_ergo_protector_rider | HDFC_ERGO | 14 | N | 0.4971 | non_policy_or_rider | high |
| 09_hdfc_ergo_hdfc_ergo_critical_advantage_rider | HDFC_ERGO | 15 | N | 0.4324 | non_policy_or_rider | high |
| non_policy_wordings_nivabupa_health_recharge_prosp | non_policy_wordings | 42 | Y | 0.4198 | non_policy_or_rider | high |
| 03_care_health_care_plus_health_insurance_product_ | Care_Health | 4 | Y | 0.3929 | non_policy_or_rider | high |
| 03_care_health_senior_health_advantage_brochure | Care_Health | 4 | Y | 0.3688 | non_policy_or_rider | high |
| 22_edelweiss_edelweiss_well_baby_well_mother_addon | Edelweiss | 2 | Y | 0.1573 | non_policy_or_rider | high |
| 09_hdfc_ergo_hdfc_ergo_critical_illness_insurance | HDFC_ERGO | 22 | N | 0.499 | section_tree_fail | high |
| 19_liberty_liberty_79fc880c_2c03_e5e9_3a02_dc75130 | Liberty | 46 | N | 0.4987 | section_tree_fail | high |
| 18_cholamandalam_cholamandalam_chola_classic_healt | Cholamandalam | 29 | N | 0.4978 | section_tree_fail | high |
| 12_iffco_tokio_iffco_tokio_group_medishield_insura | IFFCO_Tokio | 23 | N | 0.4976 | section_tree_fail | high |
| 04_icici_lombard_icici_lombard_health_care_plus_po | ICICI_Lombard | 30 | N | 0.4974 | section_tree_fail | high |
| 10_tata_aig_tata_aig_wellsurance_family_policy | Tata_AIG | 14 | N | 0.4964 | section_tree_fail | high |
| 05_niva_bupa_niva_bupa_health_pulse | Niva_Bupa | 63 | N | 0.4947 | section_tree_fail | high |
| 18_cholamandalam_cholamandalam_chola_classic_healt | Cholamandalam | 35 | N | 0.4942 | section_tree_fail | high |
| 10_tata_aig_tata_aig_wellsurance_woman_policy | Tata_AIG | 12 | N | 0.4896 | section_tree_fail | high |
| 09_hdfc_ergo_hdfc_ergo_optima_restore_cis | HDFC_ERGO | 33 | N | 0.4895 | section_tree_fail | high |
| 12_iffco_tokio_iffco_tokio_critical_illness_insura | IFFCO_Tokio | 20 | N | 0.4885 | section_tree_fail | high |
| 14_universal_sompo_universal_sompo_bancassurance_i | Universal_Sompo | 33 | N | 0.4868 | section_tree_fail | high |
| 13_future_generali_future_generali_future_advantag | Future_Generali | 23 | N | 0.485 | section_tree_fail | high |
| 17_reliance_reliance_reliance_group_hospi_cash_ins | Reliance | 25 | N | 0.4849 | section_tree_fail | high |
| 10_tata_aig_tata_aig_individual_accident_and_sickn | Tata_AIG | 13 | N | 0.4847 | section_tree_fail | high |
| 09_hdfc_ergo_hdfc_ergo_optima_cash | HDFC_ERGO | 20 | N | 0.4833 | section_tree_fail | high |
| 21_royal_sundaram_royal_sundaram_ace_health_advant | Royal_Sundaram | 56 | N | 0.4817 | section_tree_fail | high |
| 09_hdfc_ergo_hdfc_ergo_maxima_insurance | HDFC_ERGO | 37 | N | 0.4798 | section_tree_fail | high |
| tata_aig_arogya_sanjeevani | Tata_AIG | 28 | N | 0.4738 | section_tree_fail | high |
| 09_hdfc_ergo_hdfc_ergo_individual_personal_acciden | HDFC_ERGO | 33 | N | 0.4708 | section_tree_fail | high |
| 07_oriental_insurance_oriental_mediclaim_individua | Oriental_Insurance | 35 | N | 0.47 | section_tree_fail | high |
| 07_oriental_insurance_oriental_mediclaim_insurance | Oriental_Insurance | 35 | N | 0.47 | section_tree_fail | high |
| 09_hdfc_ergo_hdfc_ergo_my_optima_secure | HDFC_ERGO | 42 | N | 0.4699 | section_tree_fail | high |
| 23_raheja_qbe_raheja_qbe_group_health_super_top_up | Raheja_QBE | 49 | N | 0.4692 | section_tree_fail | high |
| 05_niva_bupa_niva_bupa_health_plus | Niva_Bupa | 126 | N | 0.469 | section_tree_fail | high |
| 22_edelweiss_edelweiss_group_corona_pw | Edelweiss | 17 | N | 0.4639 | section_tree_fail | high |
| 09_hdfc_ergo_hdfc_ergo_my_health_medisure_super_to | HDFC_ERGO | 34 | N | 0.4633 | section_tree_fail | high |
| 10_tata_aig_tata_aig_wellsurance_executive_policy | Tata_AIG | 12 | N | 0.4615 | section_tree_fail | high |
| 22_edelweiss_edelweiss_saral_suraksha_bima_pw | Edelweiss | 17 | N | 0.4569 | section_tree_fail | high |
| 08_bajaj_allianz_bajaj_allianz_family_health_care | Bajaj_Allianz | 37 | N | 0.4532 | section_tree_fail | high |
| 13_future_generali_future_generali_arogya_sanjeeva | Future_Generali | 25 | N | 0.4529 | section_tree_fail | high |
| 09_hdfc_ergo_hdfc_ergo_day2daycare | HDFC_ERGO | 18 | N | 0.4524 | section_tree_fail | high |
| 09_hdfc_ergo_hdfc_ergo_mosquito_disease_protection | HDFC_ERGO | 28 | N | 0.4511 | section_tree_fail | high |
| 21_royal_sundaram_royal_sundaram_group_health_irda | Royal_Sundaram | 50 | N | 0.45 | section_tree_fail | high |
| 15_magma_hdi_magma_hdi_corona_kavach_policy_magma_ | Magma_HDI | 19 | N | 0.4487 | section_tree_fail | high |
| 04_icici_lombard_icici_lombard_group_take_care_ins | ICICI_Lombard | 41 | N | 0.4481 | section_tree_fail | high |
| 08_bajaj_allianz_bajaj_allianz_extra_care_plus | Bajaj_Allianz | 24 | N | 0.4455 | section_tree_fail | high |
| 08_bajaj_allianz_bajaj_allianz_extra_care | Bajaj_Allianz | 24 | N | 0.4447 | section_tree_fail | high |
| 09_hdfc_ergo_hdfc_ergo_optima_senior | HDFC_ERGO | 25 | N | 0.4414 | section_tree_fail | high |
| 09_hdfc_ergo_hdfc_ergo_icanenhance | HDFC_ERGO | 21 | N | 0.4414 | section_tree_fail | high |
| 08_bajaj_allianz_bajaj_allianz_m_care | Bajaj_Allianz | 13 | N | 0.4288 | section_tree_fail | high |
| 10_tata_aig_tata_aig_medicare_plus_topup | Tata_AIG | 26 | N | 0.425 | section_tree_fail | high |
| 08_bajaj_allianz_bajaj_allianz_m_care_group | Bajaj_Allianz | 16 | N | 0.4222 | section_tree_fail | high |
| 13_future_generali_future_generali_future_vector_c | Future_Generali | 9 | N | 0.4212 | section_tree_fail | high |
| 23_raheja_qbe_raheja_qbe_product_list | Raheja_QBE | 4 | Y | 0.1424 | unsupported_format | medium |
| 16_kotak_mahindra_kotak_corona_rakshak_policy_poli | Kotak_Mahindra | 6 | Y | 0.05 | unsupported_format | medium |

