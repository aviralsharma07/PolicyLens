# DSE-009 Gold Table Source Review

This report classifies legacy DSE-003 `tables.json` rows for the DSE-009 physical table gate.

| Policy | Legacy table | Page | Type | Classification | Reason |
|---|---|---:|---|---|---|
| care_health_care_plus | care_health_care_plus_table_001 | 4 | waiting_period | prose_summary_not_table | Waiting period summary is clause prose, not a physical cell grid. |
| care_health_care_plus | care_health_care_plus_table_002 | 12 | room_rent | prose_summary_not_table | Room-rent schedule dependency is prose/schedule reference, not a physical table on the labelled page. |
| care_health_care_plus | care_health_care_plus_table_003 | 1 | premium | deferred_needs_pdf_review | Premium region exists but cells were not annotated in DSE-003. |
| care_health_care_plus | care_health_care_plus_table_004 | 13 | claims_documents | deferred_needs_pdf_review | Claims-documents region requires physical bbox/header review. |
| care_health_care_plus | care_health_care_plus_table_005 | 57 | network_list | physical_table_eval | Mapped to network-list physical label. |
| hdfc_arogya_sanjeevani | hdfc_arogya_sanjeevani_table_001 | 24 | schedule_of_benefits | prose_summary_not_table | Room-rent/SOB values are prose/product-summary facts, not the physical table on page 24. |
| hdfc_arogya_sanjeevani | hdfc_arogya_sanjeevani_table_002 | 8 | waiting_period | prose_summary_not_table | Waiting-period definition is prose; no reliable physical table cells. |
| hdfc_arogya_sanjeevani | hdfc_arogya_sanjeevani_table_003 | 8 | room_rent | prose_summary_not_table | Room-rent value is prose/fact summary. |
| hdfc_arogya_sanjeevani | hdfc_arogya_sanjeevani_table_004 | 2 | premium | deferred_needs_pdf_review | Premium/product-summary table not part of priority physical gate. |
| hdfc_arogya_sanjeevani | hdfc_arogya_sanjeevani_table_005 | 16 | claims_documents | physical_table_eval | Mapped to claim timeline physical table. |
| hdfc_arogya_sanjeevani | hdfc_arogya_sanjeevani_table_006 | 3 | network_list | wrong_page_or_wrong_type | Legacy network-list label points to page content that is not a network-list physical table. |
| icici_family_shield | icici_family_shield_table_001 | 1 | waiting_period | prose_summary_not_table | Waiting period is a policy wording fact, not a physical table. |
| icici_family_shield | icici_family_shield_table_002 | 1 | premium | deferred_needs_pdf_review | Policy certificate/premium-like page needs separate physical schedule review. |
| icici_family_shield | icici_family_shield_table_003 | 18 | claims_documents | deferred_needs_pdf_review | Claims-documents region requires physical bbox/header review. |
| icici_family_shield | icici_family_shield_table_004 | 1 | network_list | wrong_page_or_wrong_type | Legacy network-list label is not a network-list physical table. |
| new_india_floater | new_india_floater_table_001 | 6 | waiting_period | prose_summary_not_table | Waiting period is prose/definition content, not a physical waiting-period table. |
| new_india_floater | new_india_floater_table_002 | 9 | room_rent | prose_summary_not_table | Room-rent fact is extracted from benefit-clause prose/table rows, not a legacy room-rent table. |
| new_india_floater | new_india_floater_table_003 | 25 | premium | physical_table_eval | Mapped to premium retention physical table. |
| new_india_floater | new_india_floater_table_004 | 23 | claims_documents | deferred_needs_pdf_review | Claims-documents region requires physical bbox/header review. |
| new_india_floater | new_india_floater_table_005 | 2 | network_list | wrong_page_or_wrong_type | Legacy network-list label points to non-network-list page content. |
| star_medi_classic_accident | star_medi_classic_accident_table_001 | 1 | schedule_of_benefits | prose_summary_not_table | SOB facts are embedded in policy summary/prose, not a clean physical SOB grid. |
| star_medi_classic_accident | star_medi_classic_accident_table_002 | 2 | waiting_period | prose_summary_not_table | Waiting-period facts are prose; page 2 physical table is policy-summary/coverage index. |
| star_medi_classic_accident | star_medi_classic_accident_table_003 | 5 | room_rent | prose_summary_not_table | Room-rent fact is prose/scope text, not a physical room-rent grid. |
| star_medi_classic_accident | star_medi_classic_accident_table_004 | 9 | premium | physical_table_eval | Mapped to premium retention physical table. |
| star_medi_classic_accident | star_medi_classic_accident_table_005 | 8 | claims_documents | deferred_needs_pdf_review | Claims-documents label needs source/bbox review. |
| star_medi_classic_accident | star_medi_classic_accident_table_006 | 6 | network_list | wrong_page_or_wrong_type | Legacy network-list label points to non-network-list page content. |
