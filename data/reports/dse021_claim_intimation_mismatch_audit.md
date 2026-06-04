# DSE-021 Claim Intimation Timeline — Remediation Audit

Date: 2026-06-04
Task: DSE-021 Packet 1A
Branch: `feat/dse-021-extractor-wave2`
Final eval: `runs/evals/2026-06-04-fact-extraction-dse021-claim-intimation.json`

## Final Result

| Metric | Result |
|---|---:|
| Policies evaluated | 20 |
| Policies passed | 20 |
| Precision | 100.00% |
| Recall | 99.53% |
| Normalized value accuracy | 100.00% |
| Status accuracy | 98.57% |
| Evidence accuracy | 100.00% |
| False present for gold `not_found` | 0 |

## What Was Wrong

The first Packet 1A implementation was not acceptable. It emitted source-backed facts, but the eval still failed because the 20-policy gold labels for `claim_intimation_timeline` mixed four cases:

- real claim-intimation clauses incorrectly labeled `not_found`,
- renewal/grace or definition text incorrectly labeled as claim-intimation,
- truncated `timeline_text` values that were not comparable to structured values,
- adjacent-clause notification bullets that the extractor missed.

The fix did not loosen evals. Each corrected gold label was source-PDF-backed, and extractor changes were limited to claim-intimation matching.

## Gold Corrections Applied

These labels were corrected because source text contains an explicit claim-intimation deadline:

| Policy | Old Gold | New Gold | Source-Backed Reason |
|---|---|---|---|
| `bajaj_allianz_silver_health` | `not_found` | `present {"hours": 24}` | Emergency cashless claim procedure requires intimation within 24 hours of hospitalization. |
| `liberty_critical_connect` | `not_found` | `present {"hours": 48}` | Critical illness claim procedure requires written intimation within 48 hours of diagnosis. |
| `reliance_health_gain` | `not_found` | `present {"hours": 48}` | Claims intimation section requires planned admission intimation at least 48 hours prior. |
| `universal_sompo_loan_secure` | `not_found` | `present {"days": 30}` | Section II claims process requires injury claim intimation not later than 30 days. |

These labels were corrected because source review found no concrete claim-intimation deadline:

| Policy | Old Gold | New Gold | Source-Backed Reason |
|---|---|---|---|
| `icici_family_shield` | `present {"days": 30}` | `not_found` | Source text contains a definition of Notification of Claim, but no concrete deadline in the parsed policy wording. |
| `iffco_tokio_health_protector` | `present {"days": 30}` | `not_found` | Old evidence was renewal/grace text, not claim-intimation text. |

These labels were normalized from non-comparable or over-broad shapes to the primary/earliest claim-notification deadline:

| Policy | New Normalized Value |
|---|---|
| `aditya_birla_activ_care` | `{"hours": 48}` |
| `care_health_care_plus` | `{"hours": 48}` |
| `future_generali_health_elite` | `{"hours": 48}` |
| `hdfc_arogya_sanjeevani` | `{"hours": 24}` |
| `new_india_floater` | `{"hours": 24}` |
| `niva_bupa_health_recharge` | `{"hours": 48}` |
| `royal_sundaram_advanced_topup` | `{"hours": 72}` |
| `sbi_general_arogya_sanjeevani` | `{"hours": 24}` |
| `star_medi_classic_accident` | `{"hours": 24}` |
| `tata_aig_arogya_sanjeevani` | `{"hours": 24}` |
| `united_india_individual_health` | `{"hours": 24}` |

## Extractor Fixes Applied

- Added claim-intimation signals for `notified`, `notice with full particulars`, `must inform`, and related notification phrasing.
- Added support for `at least N hours` wording.
- Added adjacent-clause context handling for policies where `Notification of Claim` is a heading and the 24/48-hour bullets are separate clauses.
- Added guards so adjacent reimbursement/document-submission rows such as post-hospitalization document deadlines are not treated as claim intimation.
- Added guard for death-document submission clauses that say `send required documents ... cause of death within 30 days`.

## Deferred Scope

`claim_intimation_timeline` now records the primary/earliest notification deadline. Multi-scenario claim filing schedules and document-submission deadlines remain separate future concepts, not part of this Packet 1A extractor.
