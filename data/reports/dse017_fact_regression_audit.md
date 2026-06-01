# DSE-017 Fact Regression Audit

Date: 2026-06-02
Task: DSE-017
Reviewer: Codex acting for Avi

## Summary

DSE-017 initially proved the 20-policy SQLite/export pipeline structurally, but the 5 deterministic concepts failed expanded gold comparison. The audit reviewed every failing concept-policy pair using the current gold fact, extracted fact evidence, section-tree clauses, and targeted source PDF text where the values disagreed.

Final result after remediation:

- Fact extraction eval: 20/20 policies passed.
- Fact scoring eval: 100/100 status matches, 83/83 value matches, 83/83 evidence matches.
- Export eval: 20/20 exports passed with 100% gold status/value accuracy for the implemented concepts.
- False-present count: 0.

## Fix Classes

| Class | Meaning |
|---|---|
| `gold_fix` | Gold annotation value/status pointed at the wrong source fact and was corrected from source evidence. |
| `extractor_fix` | Extractor/parser behavior was wrong or too brittle and was fixed without changing gold. |
| `eval_equivalence_fix` | Predicted value carried harmless extra metadata while matching the gold scalar value. |

## Pair Review

| Policy | Concept | Initial issue | Pages checked | Classification | Final decision |
|---|---|---:|---|---|---|
| aditya_birla_activ_care | ped_waiting_period | gold schedule-dependent vs extracted 24 months | 10, 12, 18 | extractor_fix | Added schedule-dependent PED candidate and rejected instalment-continuity false match. |
| aditya_birla_activ_care | initial_waiting_period | extracted not_found | 10 | extractor_fix | Accepted actual first 30 days waiting clause despite diagnosis/treatment wording. |
| bajaj_allianz_silver_health | free_look_period | gold 3 months vs extracted 15 days | 14 | gold_fix | Corrected gold to 15 days; 3 months was refund schedule duration. |
| bajaj_allianz_silver_health | ped_waiting_period | extracted not_found | 10 | extractor_fix | Raised strong 12-month PED waiting evidence above acceptance threshold. |
| cholamandalam_flexi_max_protect | initial_waiting_period | false present from claim timeline | 29 | extractor_fix | Rejected claim notification/document timelines for initial waiting. |
| cholamandalam_flexi_max_protect | co_pay | gold schedule-dependent vs extracted not_found | 28 | gold_fix | Corrected gold to not_found; wording was boilerplate without usable co-pay value. |
| future_generali_health_elite | free_look_period | extracted not_found | 17 | extractor_fix | Preserved pre-heading body pages in section tree. |
| future_generali_health_elite | grace_period | gold 15 days vs extracted 30 days | 20, 23 | gold_fix | Corrected gold to 30-day renewal grace; 15 days is instalment-premium grace. |
| future_generali_health_elite | ped_waiting_period | extracted not_found | 7 | extractor_fix | Preserved pre-heading body pages in section tree. |
| future_generali_health_elite | initial_waiting_period | extracted not_found | 15 | extractor_fix | Preserved pre-heading body pages in section tree. |
| future_generali_health_elite | co_pay | gold 50% vs extracted 20% | 7, 25 | gold_fix | Corrected gold to 20%; 50% was liability limit, not co-pay percentage. |
| iffco_tokio_health_protector | free_look_period | gold 3 months vs extracted 15 days | 34 | gold_fix | Corrected gold to 15 days; 3 months came from premium-rate revision wording. |
| kotak_mahindra_health_premier | free_look_period | gold 24 months vs extracted 15 days | 38 | gold_fix | Corrected gold to 15 days; 24 months was unrelated waiting-period context. |
| kotak_mahindra_health_premier | ped_waiting_period | gold 24 months vs extracted 48 months | 21 | extractor_fix | Rejected PED definition/incidental specific-waiting references; final matched schedule clause. |
| liberty_critical_connect | initial_waiting_period | false present from claim documents timeline | 40 | extractor_fix | Rejected claim-document 30-day timelines. |
| niva_bupa_health_recharge | free_look_period | gold 36 months vs extracted 15 days | 27 | gold_fix | Corrected gold to 15 days; 36 months was policy term/distance-marketing context. |
| oriental_cancer_protect | ped_waiting_period | false present from PED definition | 17 | extractor_fix | Rejected PED definition clauses such as “diagnosed within 48 months prior.” |
| reliance_health_gain | ped_waiting_period | gold 3 months vs extracted 36 months | 4, 13 | gold_fix | Corrected gold to 36 months; 3 months came from eligibility/age text. |
| royal_sundaram_advanced_topup | free_look_period | gold 3 months vs extracted 15 days | 28 | gold_fix | Corrected gold to 15 days; 3 months was premium-rate revision notice. |
| sbi_general_arogya_sanjeevani | free_look_period | gold 3 months vs extracted 15 days | 20 | gold_fix | Corrected gold to 15 days; 3 months was premium-rate revision notice. |
| sbi_general_arogya_sanjeevani | grace_period | extracted wrong/not_found after rejecting pre-hospital 30 days | 20, 21 | extractor_fix | Accepted 15-day instalment grace and rejected pre-hospitalisation 30-day context. |
| sbi_general_arogya_sanjeevani | co_pay | predicted included basis metadata | 15 | eval_equivalence_fix | Allowed gold scalar value to match predicted metadata superset. |
| star_medi_classic_accident | ped_waiting_period | gold 48 months vs extracted 24 months/not_found | 6 | extractor_fix | Parsed 48 consecutive months and rejected incidental specific-waiting reference. |
| star_medi_classic_accident | initial_waiting_period | extracted not_found | 6 | extractor_fix | Normalized PDF ligature `ﬁrst` and accepted exclusion wording. |
| tata_aig_arogya_sanjeevani | free_look_period | extracted not_found | 15 | extractor_fix | Accepted policy-specific 30-day free-look period. |
| tata_aig_arogya_sanjeevani | ped_waiting_period | gold schedule-dependent vs extracted 36 months | 9, 22 | gold_fix + extractor_fix | Corrected gold to 36 months and added loose PED duration parsing for column-interleaved text. |
| tata_aig_arogya_sanjeevani | co_pay | predicted included basis metadata | 21 | eval_equivalence_fix | Allowed gold scalar value to match predicted metadata superset. |
| united_india_individual_health | free_look_period | gold 3 months vs extracted 15 days | 14 | gold_fix | Corrected gold to 15 days; 3 months was premium-rate revision notice. |
| universal_sompo_loan_secure | free_look_period | extracted not_found | 30 | extractor_fix | Used adjacent “Free Look period” heading context with following 15-day clause. |
| universal_sompo_loan_secure | grace_period | gold not_found vs extracted 30 days | 30 | gold_fix | Corrected gold to 30-day renewal delay/grace wording. |
| universal_sompo_loan_secure | ped_waiting_period | gold 24 months vs extracted not_found | 11 | gold_fix | Corrected gold to not_found; source has pre-existing illness exclusion but no PED waiting-period duration. |
| universal_sompo_loan_secure | initial_waiting_period | false present from claim timeline | 14 | extractor_fix | Rejected claim intimation/submission timelines. |

## Implementation Notes

- Section tree now preserves a synthetic pre-heading body section when the first detected heading appears very late, preventing early pages from disappearing from clause/fact extraction.
- Duration normalization now supports `30-day waiting period` and `48 consecutive months`.
- Deterministic extractors normalize common PDF ligatures before matching.
- PED extraction rejects definition-only durations and incidental specific-waiting references, but parses column-interleaved PED waiting text.
- Free-look extraction can use adjacent heading context when clause segmentation splits the heading from the duration.
- Value comparison allows predicted metadata supersets only when all gold scalar keys match exactly.

## Residual Limitations

- Evidence spans for some facts are clause-level degraded because source text is column-interleaved; source-span validation records these as resolved but not exact substring offsets.
- DSE-017 still evaluates only the 5 implemented deterministic concepts. The remaining 15 Product B export fields remain explicit `not_found` until extractor expansion.
- Table-engine 20-policy hard-gate modernization remains tracked separately under R20.
