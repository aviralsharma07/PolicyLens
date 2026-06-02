# DSE-018 Wave 1 Mismatch Audit

Date: 2026-06-02
Task: DSE-018
Reviewer: Codex acting for Avi

## Summary

DSE-018 expanded deterministic extraction from 5 concepts to 13 Wave 1 concepts across the 20-policy reviewed gold corpus. The final mismatch pass reviewed the last 10 concept-policy rows against source PDF text, current gold evidence, and extracted evidence.

Final fact extraction result:

- Policies passed: 20/20
- Precision: 100.00%
- Recall: 99.49%
- Normalized value accuracy: 100.00%
- Status accuracy: 98.46%
- Evidence accuracy: 100.00%
- False-present count: 0

## Review Table

| Policy | Concept | Gold before | Predicted before | Pages checked | Classification | Final action |
|---|---|---:|---:|---|---|---|
| aditya_birla_activ_care | claim_settlement_timeline | 15 days | 30 days | 14-15 | gold_fix | Gold corrected to primary 30-day settlement. Prior evidence was pre-authorisation validity, not claim settlement. Evidence also notes the 45-day investigation extension. |
| aditya_birla_activ_care | specific_disease_waiting_periods | [24] | [24, 48] | 10 | gold_fix | Gold corrected to [24, 48]. Source includes 24-month two-year waiting list and 48-month Standard Plan/four-year listed conditions. |
| care_health_care_plus | claim_settlement_timeline | 30 + investigation 45, wrong evidence | 30 days | 22, 34 | gold_fix | Gold evidence corrected from health-check submission text to the claim settlement clause. Canonical Wave 1 value uses primary settlement days where investigation extension is separately segmented. |
| future_generali_health_elite | specific_disease_waiting_periods | [48] | [24, 48] | 15 | gold_fix | Gold corrected to [24, 48]. Excl02 source text explicitly states 24/48 months and lists both 48-month and 24-month groups. |
| new_india_floater | specific_disease_waiting_periods | [24, 48] | [48] | 16-17 | extractor_fix | Extractor now parses slash-separated options such as `Ninety Days / 24 / 48 months`; gold unchanged. |
| niva_bupa_health_recharge | specific_disease_waiting_periods | [48] | [24] | 21, 23 | gold_fix | Gold corrected to [24]. Prior 48-month evidence was PED/critical-illness optional benefit text, not base specific disease/procedure waiting. |
| reliance_health_gain | claim_settlement_timeline | 30 days | 45 days | 20 | extractor_fix | Extractor now rejects investigation-only 45-day fragments as accepted primary settlement values. Current section-tree clauses lost the source 30-day normal settlement line, so final extraction is `not_found` rather than wrong-present. |
| sbi_general_arogya_sanjeevani | specific_disease_waiting_periods | [48] | [24, 48] | 10 | gold_fix | Gold corrected to [24, 48]. Existing evidence itself says 24/48 months. |
| tata_aig_arogya_sanjeevani | claim_settlement_timeline | 30 days | not_found / 45-day investigation fragment | 13-14 | gold_fix + extractor_fix | Gold corrected to normal 15-day settlement based on source text. Extractor now handles noisy `15 ... days` PDF text and rejects cancellation notice periods. |
| kotak_mahindra_health_premier | maternity_waiting | 36 months | explicitly_not_covered | 17 | extractor_fix | Extractor now treats `not covered until 36 months` as a waiting-period fact before applying absolute-exclusion logic. |

## Final Scoring-Audit Addendum

The first DSE-018 fact-scoring eval exposed a stricter Product B semantic issue than the extractor eval: `explicitly_not_covered` against gold `not_found` counted as false-present. Source review split those rows into true exclusions and extractor false positives.

| Policy | Concept | Issue | Pages checked | Classification | Final action |
|---|---|---|---|---|---|
| bajaj_allianz_silver_health | maternity_waiting | Extractor found explicit Excl18 maternity exclusion while gold said not_found. | 12 | gold_fix | Gold corrected to `explicitly_not_covered` with Excl18 evidence. |
| reliance_health_gain | maternity_waiting | Extractor found explicit Excl18 maternity exclusion while gold said not_found. | 19 | gold_fix | Gold corrected to `explicitly_not_covered` with Excl18 evidence. |
| united_india_individual_health | maternity_waiting | Extractor found explicit Excl18 maternity exclusion while gold said not_found. | 11 | gold_fix | Gold corrected to `explicitly_not_covered` with Excl18 evidence. |
| aditya_birla_activ_care | maternity_waiting | Extractor matched `delivery kit` in an excluded-expense list, not maternity benefit/exclusion. | 27 | extractor_fix | Removed bare `delivery` as a maternity trigger. |
| tata_aig_arogya_sanjeevani | maternity_waiting | Extractor matched excluded-expense table text, not maternity benefit/exclusion. | 23 | extractor_fix | Removed bare `delivery` as a maternity trigger and retained gold `not_found`. |

## Source Findings

- Aditya Birla claim settlement: source clause says settlement/repudiation within 30 days of last necessary information/documentation, with 45 days when investigation is carried out.
- Care claim settlement: source clause says settlement/rejection within 30 days. The 45-day investigation extension appears in the next clause, but Wave 1 accepted facts remain single-evidence-clause facts.
- Reliance claim settlement: source PDF text contains normal 30-day settlement and 45-day investigation settlement, but current section-tree clauses retain only the 45-day investigation fragment. The extractor now prefers precision and emits `not_found` instead of accepting the 45-day fragment as the primary value.
- Tata AIG claim settlement: source text says normal settlement/rejection within 15 days; the prior 30-day gold value was investigation-completion timing.
- Specific disease waiting periods: New India, Future Generali, and SBI use compact slash notation or grouped 24/48-month disease lists; Niva Bupa uses 24 months for Excl02 while its 48-month text belongs to PED/critical-illness context.

## Residual Limitation

Reliance Health Gain exposes a DSE-006 clause-fragmentation issue: the source-correct 30-day settlement value is present in the PDF but absent from the clause text consumed by DSE-018. This is a recall miss, not a false present, and is retained as a parser-quality follow-up rather than patched into gold or inferred without evidence.

`explicitly_not_covered` facts are now resolved as evidence-bearing facts in the clause store, not left with provisional `clause:{id}` references.
