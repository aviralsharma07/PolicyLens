# DSE-027 MVP Candidate Latest Audit v1

Date: 2026-06-06
Task ID: DSE-027

## Summary

- Goal: verify the full 30-product DSE-026 MVP list against current official insurer surfaces before bundle collection.
- Authority order: current official insurer sources first, cross-checked with Product A UIN evidence and IRDAI-linked evidence where available.
- Archived-only evidence is not treated as current.

## Counts

- Candidate count: 30
- Selection statuses: {'verified_current': 27, 'verified_current_with_gap': 3}
- Latest sellability: {'live': 30}

## Insurer Breakdown

- Care Health: {'verified_current': 6}
- HDFC ERGO: {'verified_current': 5, 'verified_current_with_gap': 1}
- ICICI Lombard: {'verified_current': 4, 'verified_current_with_gap': 2}
- Niva Bupa: {'verified_current': 6}
- Star Health: {'verified_current': 6}

## Notable Adjustments

- `hdfc_ergo_arogya_sanjeevani` -> `Arogya Sanjeevani Policy, HDFC ERGO`: verified_current_with_gap / live / high. Current HDFC ERGO CIS page still lists the retail Arogya Sanjeevani product and the live CIS confirms the candidate UIN. Dedicated current product page was not used.
- `icici_lombard_health_advantedge` -> `Health AdvantEdge`: verified_current_with_gap / live / medium. Current ICICI product pages still market Health AdvantEdge, but a fresh current wording URL was not locked in this packet. Local Product A UIN is retained as a cautious placeholder pending direct doc download.
- `icici_lombard_health_booster` -> `Health Booster`: verified_current_with_gap / live / medium. Current ICICI Health Booster product page is live and an official brochure remains public. Current wording URL still needs locking, so the local reviewed UIN is retained conservatively.

## Verified Candidates

### HDFC ERGO — my: Optima Secure

- Candidate ID: `hdfc_ergo_optima_secure`
- Proposed name: `Optima Secure`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `HDFHLIP26058V082526`
- Official product page: https://www.hdfcergo.com/health-insurance/optima-secure/
- Official wording: not identified yet
- Official CIS: https://customer-portal-assets.hdfcergo.com/documents/CIS_Website_myOptimaSecure-751325733632.pdf
- Official brochure/prospectus: https://www.hdfcergo.com/docs/default-source/downloads/prospectus/health/my-optima-secure-prospectus.pdf
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_doc_uin_differs_from_local_legacy_wording`
- Confidence: `high`
- Notes: Current official HDFC ERGO product page and CIS show my: Optima Secure live under UIN HDFHLIP26058V082526. Local Product A wording is an older UIN and must not be treated as current.

### HDFC ERGO — Optima Restore

- Candidate ID: `hdfc_ergo_optima_restore`
- Proposed name: `Optima Restore`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `HDFHLIP26055V102526`
- Official product page: https://www.hdfcergo.com/health-insurance/optima-restore-individual-health-insurance-plan
- Official wording: not identified yet
- Official CIS: https://customer-portal-assets.hdfcergo.com/documents/CIS_Website_OptimaRestore-207342910205.pdf
- Official brochure/prospectus: https://www.hdfcergo.com/docs/default-source/downloads/prospectus/health/optima-restore-prospectus.pdf
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_doc_uin_differs_from_candidate`
- Confidence: `high`
- Notes: Current official HDFC ERGO CIS shows Optima Restore live under UIN HDFHLIP26055V102526; candidate and local wording values were older.

### HDFC ERGO — myhealth Medisure Super Top Up Insurance

- Candidate ID: `hdfc_ergo_my_health_medisure_super_top_up`
- Proposed name: `my:health Medisure Super Top Up Insurance`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `HDFHLIP22021V042122`
- Official product page: https://www.hdfcergo.com/download/cis/health
- Official wording: not identified yet
- Official CIS: https://customer-portal-assets.hdfcergo.com/assets/v2/docs/default-source/downloads/cis/cis---myhealth-medisure-super-top-up-insurance/pdf180-872857238027.pdf
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_doc_uin_matches_candidate`
- Confidence: `high`
- Notes: Current HDFC ERGO CIS surface still lists myhealth Medisure Super Top Up Insurance and the live CIS confirms UIN HDFHLIP22021V042122.

### HDFC ERGO — my:health Koti Suraksha

- Candidate ID: `hdfc_ergo_my_health_koti_suraksha`
- Proposed name: `my:health Koti Suraksha`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `HDFHLIP21131V012021`
- Official product page: https://www.hdfcergo.com/download/cis/health
- Official wording: not identified yet
- Official CIS: https://customer-portal-assets.hdfcergo.com/assets/v2/docs/default-source/downloads/cis/cis---myhealth-koti-suraksha/PDF189-994362627141.pdf
- Official brochure/prospectus: https://www.hdfcergo.com/docs/default-source/downloads/prospectus/health/prospectus-my-health-koti-suraksha.pdf
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_doc_uin_matches_candidate`
- Confidence: `high`
- Notes: Current HDFC ERGO CIS page still lists my:health Koti Suraksha and the live CIS confirms the candidate UIN.

### HDFC ERGO — Energy

- Candidate ID: `hdfc_ergo_energy`
- Proposed name: `Energy`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `HDHHLIP21345V042021`
- Official product page: https://www.hdfcergo.com/download/cis/health
- Official wording: not identified yet
- Official CIS: https://customer-portal-assets.hdfcergo.com/assets/v2/docs/default-source/downloads/cis/cis---energy/cis---energy-475568353203.pdf
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_doc_uin_matches_candidate`
- Confidence: `high`
- Notes: Current HDFC ERGO CIS surface lists Energy and the live CIS confirms UIN HDHHLIP21345V042021.

### HDFC ERGO — Arogya Sanjeevani Policy, HDFC ERGO

- Candidate ID: `hdfc_ergo_arogya_sanjeevani`
- Proposed name: `Arogya Sanjeevani Policy, HDFC ERGO`
- Selection status: `verified_current_with_gap`
- Latest sellability: `live`
- Verified UIN: `HDFHLIP20175V011920`
- Official product page: https://www.hdfcergo.com/download/cis/health
- Official wording: not identified yet
- Official CIS: https://customer-portal-assets.hdfcergo.com/assets/v2/docs/default-source/downloads/cis/arogya-sanjeevani-policy-retail-cis/PDF294-813914878965.pdf
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_doc_uin_matches_candidate`
- Confidence: `high`
- Notes: Current HDFC ERGO CIS page still lists the retail Arogya Sanjeevani product and the live CIS confirms the candidate UIN. Dedicated current product page was not used.

### Star Health — Star Comprehensive Insurance Policy

- Candidate ID: `star_health_star_comprehensive`
- Proposed name: `Star Comprehensive Insurance Policy`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `SHAHLIP26044V092526`
- Official product page: https://www.starhealth.in/health-insurance/comprehensive/
- Official wording: not identified yet
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: https://d28c6jni2fmamz.cloudfront.net/Modern_Treatment_Star_Comprehensive_Insurance_Policy_627f5a8912.pdf
- IRDAI cross-check: `official_current_doc_uin_differs_from_local_legacy_wording`
- Confidence: `high`
- Notes: Current Star product page is live and a current official modern-treatment table shows UIN SHAHLIP26044V092526. Local Product A wording is an older version.

### Star Health — Family Health Optima Insurance Plan

- Candidate ID: `star_health_family_health_optima`
- Proposed name: `Family Health Optima Insurance Plan`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `SHAHLIP26046V092526`
- Official product page: https://www.starhealth.in/downloads/
- Official wording: not identified yet
- Official CIS: not identified yet
- Official brochure/prospectus: https://web.starhealth.in/sites/default/files/brochure/FHO-Brochure.pdf
- Official PBT/table: https://d28c6jni2fmamz.cloudfront.net/Modern_Treatment_Family_Health_Optima_Insurance_Plan_9428c181fe.pdf
- IRDAI cross-check: `official_current_doc_uin_differs_from_local_legacy_wording`
- Confidence: `high`
- Notes: Current Star downloads surface lists Family Health Optima and the current modern-treatment sheet shows UIN SHAHLIP26046V092526, newer than the local 2022 wording.

### Star Health — Medi Classic Insurance Policy (Individual)

- Candidate ID: `star_health_medi_classic`
- Proposed name: `Medi Classic Insurance Policy (Individual)`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `SHAHLIP26047V092526`
- Official product page: https://www.starhealth.in/downloads/
- Official wording: not identified yet
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: https://d28c6jni2fmamz.cloudfront.net/Modern_Treatment_Medi_classic_Insurance_Policy_Individual_7c648b3606.pdf
- IRDAI cross-check: `official_current_doc_uin_differs_from_local_legacy_wording`
- Confidence: `high`
- Notes: Current Star downloads surface lists Medi Classic and the current official modern-treatment sheet shows UIN SHAHLIP26047V092526.

### Star Health — Senior Citizens Red Carpet Health Insurance Policy

- Candidate ID: `star_health_senior_red_carpet`
- Proposed name: `Senior Citizens Red Carpet Health Insurance Policy`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `SHAHLIP26041V082526`
- Official product page: https://www.starhealth.in/downloads/
- Official wording: not identified yet
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: https://d28c6jni2fmamz.cloudfront.net/Modern_Treatment_Senior_Citizens_Red_Carpet_Health_Insurance_Policy_d9f7c83493.pdf
- IRDAI cross-check: `official_current_doc_uin_differs_from_local_legacy_wording`
- Confidence: `high`
- Notes: Current Star downloads surface lists Senior Citizens Red Carpet and the current official modern-treatment sheet shows UIN SHAHLIP26041V082526.

### Star Health — Super Surplus Insurance Policy

- Candidate ID: `star_health_super_surplus`
- Proposed name: `Super Surplus Insurance Policy`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `SHAHLIP22035V062122`
- Official product page: https://www.starhealth.in/health-insurance/top-up-health-insurance/
- Official wording: not identified yet
- Official CIS: not identified yet
- Official brochure/prospectus: https://web.starhealth.in/sites/default/files/prospectus/Super-Surplus-Insurance-Policy.pdf
- Official PBT/table: https://d28c6jni2fmamz.cloudfront.net/Modern_Treatment_Super_Surplus_Insurance_Policy_63c1008ff2.pdf
- IRDAI cross-check: `official_current_doc_uin_differs_from_candidate_generic_name`
- Confidence: `high`
- Notes: Current Star top-up product page is live. The official modern-treatment PDF confirms the current individual Super Surplus UIN SHAHLIP22035V062122; candidate naming was too generic and local wording is older.

### Star Health — Arogya Sanjeevani Policy, Star Health and Allied Insurance Co Ltd.

- Candidate ID: `star_health_arogya_sanjeevani`
- Proposed name: `Arogya Sanjeevani Policy, Star Health and Allied Insurance Co Ltd`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `SHAHLIP26045V042526`
- Official product page: https://www.starhealth.in/downloads/
- Official wording: not identified yet
- Official CIS: not identified yet
- Official brochure/prospectus: https://d28c6jni2fmamz.cloudfront.net/Prospectus_Arogya_Sanjeevani_Policy_V_8_9a95b2c87f.pdf
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_doc_uin_differs_from_local_legacy_wording`
- Confidence: `high`
- Notes: Star downloads still list Arogya Sanjeevani and the current official prospectus shows UIN SHAHLIP26045V042526, newer than the local corpus wording.

### ICICI Lombard — Elevate

- Candidate ID: `icici_lombard_elevate`
- Proposed name: `Elevate`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `None`
- Official product page: https://www.icicilombard.com/health-insurance/elevate-health-policy/
- Official wording: https://www.icicilombard.com/docs/default-source/default-document-library/elevate.pdf
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_wording_identified_uin_pending_local_capture`
- Confidence: `high`
- Notes: Current Elevate product page is live and a current official policy wording PDF is publicly accessible. Verified UIN should be read from the downloaded document rather than trusted from the older shortlist guess.

### ICICI Lombard — ICICI Lombard Complete Health Insurance

- Candidate ID: `icici_lombard_complete_health`
- Proposed name: `ICICI Lombard Complete Health Insurance`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `ICIHLIP23144V072223`
- Official product page: https://www.icicilombard.com/amp/health-insurance/complete-health-insurance/
- Official wording: https://www.icicilombard.com/docs/default-source/policy-wordings-product-brochure/icihlip23144v072223_icici-lombard-complete-health-insurance.pdf
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_doc_uin_differs_from_local_legacy_wording`
- Confidence: `high`
- Notes: ICICI’s live Complete Health product surface is active and a current official wording/brochure PDF shows a newer UIN ICIHLIP23144V072223 than the older local wording.

### ICICI Lombard — Health AdvantEdge

- Candidate ID: `icici_lombard_health_advantedge`
- Proposed name: `Health advantEDGE`
- Selection status: `verified_current_with_gap`
- Latest sellability: `live`
- Verified UIN: `ICIHLIP22206V022122`
- Official product page: https://www.icicilombard.com/health-insurance/health-advantedge-insurance-for-family
- Official wording: not identified yet
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_live_page_found_local_uin_retained_pending_current_doc`
- Confidence: `medium`
- Notes: Current ICICI product pages still market Health AdvantEdge, but a fresh current wording URL was not locked in this packet. Local Product A UIN is retained as a cautious placeholder pending direct doc download.

### ICICI Lombard — Health Booster

- Candidate ID: `icici_lombard_health_booster`
- Proposed name: `Health Booster`
- Selection status: `verified_current_with_gap`
- Latest sellability: `live`
- Verified UIN: `ICIHLIP22100V032122`
- Official product page: https://www.icicilombard.com/health-insurance/health-booster?opt=hb&source=nav
- Official wording: not identified yet
- Official CIS: not identified yet
- Official brochure/prospectus: https://www.icicilombard.com/docs/default-source/policy-wordings-product-brochure/health-booster-brochure.pdf?sfvrsn=39fd6a53_10
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_live_page_found_local_uin_retained`
- Confidence: `medium`
- Notes: Current ICICI Health Booster product page is live and an official brochure remains public. Current wording URL still needs locking, so the local reviewed UIN is retained conservatively.

### ICICI Lombard — Family Shield

- Candidate ID: `icici_lombard_family_shield`
- Proposed name: `Family Shield`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `ICIHLIP22092V032122`
- Official product page: https://www.icicilombard.com/health-insurance/family-shield
- Official wording: https://www.icicilombard.com/docs/default-source/default-document-library/family-shield8c0003ff45fd68ff8a0df0055f0bfd98.pdf
- Official CIS: not identified yet
- Official brochure/prospectus: https://www.icicilombard.com/docs/default-source/default-document-library/family-shield_prospectus8c0003ff45fd68ff8a0df0055f058306.pdf
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_page_uin_matches_candidate`
- Confidence: `high`
- Notes: Current Family Shield product page is live and explicitly shows UIN ICIHLIP22092V032122. Official policy and prospectus PDFs are public.

### ICICI Lombard — Arogya Sanjeevani Policy, ICICI Lombard

- Candidate ID: `icici_lombard_arogya_sanjeevani`
- Proposed name: `Arogya Sanjeevani Policy, ICICI Lombard`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `ICIHLIP20178V011920`
- Official product page: https://www.icicilombard.com/health-insurance/arogya-sanjeevani-policy
- Official wording: https://www.icicilombard.com/docs/default-source/policy-wordings-product-brochure/arogya-sanjeevani-policy-policy-wordings.pdf
- Official CIS: not identified yet
- Official brochure/prospectus: https://www.icicilombard.com/docs/default-source/default-document-library/aarogya-sanjeevani-brochure.pdf?sfvrsn=39fd6b30_0
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_page_uin_matches_candidate`
- Confidence: `high`
- Notes: Current ICICI Arogya Sanjeevani product page is live and the official public PDF still shows UIN ICIHLIP20178V011920.

### Care Health — Care

- Candidate ID: `care_health_care`
- Proposed name: `Care`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `CHIHLIP22184V062122`
- Official product page: https://www.careinsurance.com/product/care
- Official wording: https://cms.careinsurance.com/cms/public/uploads/download_center/care---policy-terms-%26-conditions-%28effective-from-21-march-2026%29.pdf?rv=0.39953000+1780688189
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `current_official_terms_page_live_local_uin_retained`
- Confidence: `medium`
- Notes: Care product page is live and current official terms are publicly listed with an effective date in 2026. Local UIN is retained pending first-page capture from the downloaded current PDF.

### Care Health — Care Supreme

- Candidate ID: `care_health_care_supreme`
- Proposed name: `Care Supreme`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `None`
- Official product page: https://www.careinsurance.com/product/care-supreme/
- Official wording: https://cms.careinsurance.com/cms/public/uploads/download_center/care-supreme---policy-terms-%26-conditions-%28effective-from-29-april-2026%29.pdf?rv=0.39951000+1780688189
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `current_official_terms_page_live_uin_pending_download_capture`
- Confidence: `high`
- Notes: Care Supreme has a live product page and current official 2026 policy terms. Verified UIN should be captured from the downloaded current PDF rather than inferred from older corpus data.

### Care Health — Care Classic

- Candidate ID: `care_health_care_classic`
- Proposed name: `Care Classic`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `CHIHLIP22071V012122`
- Official product page: https://www.careinsurance.com/customer-information-sheet.html
- Official wording: https://cms.careinsurance.com/cms/public/uploads/download_center/care-classic---policy-terms--conditions-%28effective-from-09-april-2025-%29.pdf?rv=0.39981300+1780688189
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `current_official_terms_page_live_local_uin_retained`
- Confidence: `medium`
- Notes: Current Care downloads page lists live 2025 policy terms for Care Classic. Local reviewed UIN is retained until the downloaded current PDF is hashed and opened.

### Care Health — Care Freedom

- Candidate ID: `care_health_care_freedom`
- Proposed name: `Care Freedom`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `RHIHLIP21519V022021`
- Official product page: https://www.careinsurance.com/customer-information-sheet.html
- Official wording: https://cms.careinsurance.com/cms/public/uploads/download_center/care-freedom----t%26c-%28effective-from-3-september-2025-%29.pdf?rv=0.40002400+1780688189
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `current_official_terms_page_live_local_uin_retained`
- Confidence: `medium`
- Notes: Current Care downloads page lists live 2025 terms for Care Freedom. The product remains in the curated MVP set with local UIN retained until direct PDF capture.

### Care Health — Enhance

- Candidate ID: `care_health_enhance`
- Proposed name: `Enhance`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `RHIHLIP21372V022021`
- Official product page: https://www.careinsurance.com/customer-information-sheet.html
- Official wording: https://cms.careinsurance.com/cms/public/uploads/download_center/enhance---t%26c-%28effective-from-12-september-2024-%29.pdf?rv=0.39999600+1780688189
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `current_official_terms_page_live_local_uin_retained`
- Confidence: `medium`
- Notes: Current Care downloads page lists Enhance policy terms effective from 2024. This is acceptable for MVP collection and keeps the super-top-up role intact.

### Care Health — Arogya Sanjeevani Policy, Care Health Insurance

- Candidate ID: `care_health_arogya_sanjeevani`
- Proposed name: `Arogya Sanjeevani Policy, Religare / Care Health`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `RHIHLIP20154V011920`
- Official product page: https://www.careinsurance.com/customer-information-sheet.html
- Official wording: https://cms.careinsurance.com/cms/public/uploads/download_center/arogya-sanjeevani-policy-care-health-insurance----t%26c-%28effective-from-12-september-2024-%29.pdf?rv=0.40005200+1780688189
- Official CIS: not identified yet
- Official brochure/prospectus: not identified yet
- Official PBT/table: not identified yet
- IRDAI cross-check: `current_official_terms_page_live_local_uin_retained`
- Confidence: `medium`
- Notes: Current Care downloads page still lists the retail Arogya Sanjeevani policy. Candidate name is normalized to current Care branding while retaining the known standard-product UIN.

### Niva Bupa — ReAssure 2.0

- Candidate ID: `niva_bupa_reassure_2_0`
- Proposed name: `ReAssure 2.0`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `NBHHLIP26042V022526`
- Official product page: https://www.nivabupa.com/health-insurance-plan/reassurev2
- Official wording: https://transactions.nivabupa.com/pages/doc/policy_wording/ReAssure-2.0-Policy-Wording.pdf?v=1.7
- Official CIS: not identified yet
- Official brochure/prospectus: https://transactions.nivabupa.com/pages/doc/prospectus/ReAssure-2.0-Prospectus-cum-Sales-Literature.pdf?v=1.8
- Official PBT/table: https://transactions.nivabupa.com/pages/doc/premium_chart/ReAssure%202.0%20-%20Combined.pdf
- IRDAI cross-check: `official_current_doc_uin_matches_candidate`
- Confidence: `high`
- Notes: Current Niva product page is live and both policy wording and prospectus confirm UIN NBHHLIP26042V022526. Premium chart provides current variant/table support.

### Niva Bupa — Health Companion

- Candidate ID: `niva_bupa_health_companion`
- Proposed name: `Health Companion`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `NBHHLIP26051V092526`
- Official product page: https://www.nivabupa.com/health-insurance-plan/health-companion
- Official wording: https://transactions.nivabupa.com/pages/doc/policy_wording/Health-Companion-Variant2022-PolicyWording.pdf?v=1.4
- Official CIS: not identified yet
- Official brochure/prospectus: https://transactions.nivabupa.com/pages/doc/brochure/Health_Companion_V2022_Br.pdf?v=1.2
- Official PBT/table: not identified yet
- IRDAI cross-check: `official_current_doc_uin_differs_from_candidate`
- Confidence: `high`
- Notes: Current Niva Health Companion page is live. Official policy wording shows a newer UIN NBHHLIP26051V092526 than the older shortlist/local corpus value.

### Niva Bupa — Health Recharge

- Candidate ID: `niva_bupa_health_recharge`
- Proposed name: `Health Recharge`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `NBHHLIP22156V032122`
- Official product page: https://www.nivabupa.com/health-insurance-plan/health-recharge/
- Official wording: https://transactions.nivabupa.com/pages/doc/policy_wording/health-recharge-t-and-c.pdf?v=1.0
- Official CIS: not identified yet
- Official brochure/prospectus: https://transactions.nivabupa.com/pages/doc/prospectus/Health-Recharge-Prospectus.pdf?v=1.0
- Official PBT/table: https://transactions.nivabupa.com/pages/doc/brochure/Health_Recharge_SS.pdf
- IRDAI cross-check: `official_current_doc_uin_matches_candidate`
- Confidence: `high`
- Notes: Current Niva Health Recharge page is live. Official wording and prospectus still use the candidate UIN and the single-sheeter supplies current table-style coverage detail.

### Niva Bupa — Health Premia

- Candidate ID: `niva_bupa_health_premia`
- Proposed name: `Health Premia`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `MAXHLIP21176V022021`
- Official product page: https://www.nivabupa.com/health-insurance-plan/health-premia
- Official wording: https://transactions.nivabupa.com/pages/doc/policy_wording/Health-Premia-Policy-Wording.pdf?v=1.0
- Official CIS: not identified yet
- Official brochure/prospectus: https://transactions.nivabupa.com/pages/doc/prospectus/Health-Premia-Prospectus.pdf?v=1.4
- Official PBT/table: https://transactions.nivabupa.com/pages/doc/brochure/Health_Premia_Br.pdf?v=1.6
- IRDAI cross-check: `official_current_doc_uin_matches_candidate`
- Confidence: `high`
- Notes: Health Premia still has a live Niva product page and current public wording/prospectus PDFs. The official docs still use the MAX-branded legacy UIN.

### Niva Bupa — Senior First

- Candidate ID: `niva_bupa_senior_first`
- Proposed name: `Senior First`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `NBHHLIP27053V022627`
- Official product page: https://www.nivabupa.com/health-insurance-plan/senior-first/
- Official wording: https://transactions.nivabupa.com/pages/doc/policy_wording/Senior-First-Policy-Wording.pdf?v=1.1
- Official CIS: not identified yet
- Official brochure/prospectus: https://transactions.nivabupa.com/pages/doc/prospectus/Senior-First-Prospectus.pdf?v=1.2
- Official PBT/table: https://transactions.nivabupa.com/pages/doc/premium_chart/Senior-First.pdf?=1.0
- IRDAI cross-check: `official_current_doc_uin_differs_from_candidate`
- Confidence: `high`
- Notes: Current Niva Senior First page is live. Official wording now shows UIN NBHHLIP27053V022627, much newer than the older shortlist/local value.

### Niva Bupa — Arogya Sanjeevani, Niva Bupa Health Insurance Co. Ltd.

- Candidate ID: `niva_bupa_arogya_sanjeevani`
- Proposed name: `Arogya Sanjeevani, Niva Bupa Health Insurance Co. Ltd.`
- Selection status: `verified_current`
- Latest sellability: `live`
- Verified UIN: `NBHHLIP26045V032526`
- Official product page: https://transactions.nivabupa.com/pages/downloads.aspx
- Official wording: https://transactions.nivabupa.com/pages/doc/policy_wording/ArogyaSanjeevani-PolicyDocument.pdf?v=1.2
- Official CIS: not identified yet
- Official brochure/prospectus: https://transactions.nivabupa.com/pages/doc/prospectus/Arogya_Sanjeevani_Prospectus.pdf?v=1.2
- Official PBT/table: https://transactions.nivabupa.com/pages/doc/brochure/Arogya_Sanjeevani_SS.pdf?v=1.1
- IRDAI cross-check: `official_current_doc_uin_differs_from_local_legacy_wording`
- Confidence: `high`
- Notes: Current Niva downloads page exposes live wording, prospectus, and single-sheeter docs for Arogya Sanjeevani. The current official UIN is NBHHLIP26045V032526, newer than the local corpus value.
