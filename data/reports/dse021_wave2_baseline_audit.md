# DSE-021: Wave 2 Deterministic Extractor Baseline Audit

Date: 2026-06-04
Task ID: DSE-021
Source: Gold corpus (20 reviewed policies), DSE-020 triage (566 exported policies)

---

## Overview

This report audits the 7 remaining concepts not yet covered by deterministic extractors. For each concept, it reports: ontology definition, gold status counts, representative evidence snippets, DSE-020 not_found pressure, and recommended implementation approach.

---

## Reference: DSE-020 Not_Found Pressure

All 7 concepts are at the maximum not_found tier: **566 not_found each** out of 566 exported policies. None of these concepts have extractors yet. Implementing them will directly improve the full-corpus fill rate.

---

## 1. claim_intimation_timeline

### Ontology
- **value_shape:** `duration_or_components`
- **export_field:** `claim_intimation_days`
- **extractor_status:** planned

### Gold Status (20 policies)

| present | explicitly_not_covered | not_applicable | not_found |
|---|---|---|---|
| 15 | 0 | 0 | 5 |

Highest gold presence in Wave 2 (75%). Strong candidate for high recall.

### Representative Evidence Snippets

| Policy | Evidence |
|---|---|
| aditya_birla_activ_care | "We shall be given written notice of the claim... within 48 hours of admission" |
| care_health_care_plus | "notified with full particulars within 48 hours from the date of occurrence" |
| hdfc_arogya_sanjeevani | "Within thirty days of date of discharge from hospital" |
| future_generali_health_elite | "within 48 hours of the diagnosis of" |
| cholamandalam_flexi_max_protect | "It shall be a condition precedent for any claim" |

### DSE-020 Not_Found
566 / 566 exported policies = 100% not_found.

### Recommended Implementation: Packet A
**Pattern:** Duration extractor (similar to free_look_period / grace_period / waiting periods).
- Signal phrases: "notice of claim", "intimation", "notify", "notification", "within \d+ hours", "within \d+ days"
- Parse: extract duration value (hours or days) from the signal context
- Risk: Low. Signal phrases are consistent across policies. Duration formats are standard (48 hours, 30 days, 15 days).
- Confidence target: 0.85 (deterministic with duration parsing)
- Estimated recall on gold: 12-14 / 15 present

---

## 2. deductible

### Ontology
- **value_shape:** `amount_percentage_or_schedule`
- **export_field:** `deductible`
- **extractor_status:** planned

### Gold Status (20 policies)

| present | explicitly_not_covered | not_applicable | not_found |
|---|---|---|---|
| 9 | 0 | 3 | 8 |

9/20 present; 3 policies have deductible as not applicable (likely no deductible clause). Moderate gold coverage.

### Representative Evidence Snippets

| Policy | Evidence |
|---|---|
| bajaj_allianz_silver_health | "in excess of the amount of the Deductible, to indemnify the Insured" |
| care_health_care_plus | "The claim amount assessed by the Company... shall be reduced by the Deductible" |
| icici_family_shield | "Deductible shall be applicable per year, per life or per event" |

### DSE-020 Not_Found
566 / 566 exported policies = 100% not_found.

### Recommended Implementation: Packet A
**Pattern:** Amount/percentage extractor (similar to co_pay).
- Signal phrases: "deductible", "deductible option", "subject to deductible"
- Parse: extract numeric amount or percentage or structured deductible schedule
- Risk: Low-Medium. Some policies define deductible as a simple amount, others as a structured schedule. The "not_applicable" cases need to be distinguished from "not_found".
- Confidence target: 0.80-0.85
- Estimated recall on gold: 7-8 / 9 present

---

## 3. room_rent_limit

### Ontology
- **value_shape:** `room_rent_limit`
- **export_field:** `room_rent_limit`
- **extractor_status:** planned

### Gold Status (20 policies)

| present | explicitly_not_covered | not_applicable | not_found |
|---|---|---|---|
| 13 | 0 | 1 | 6 |

13/20 present (65%). Second-highest gold presence in Wave 2.

### Representative Evidence Snippets

| Policy | Evidence |
|---|---|
| aditya_birla_activ_care | "Room Rent for accommodation... up to the limits as specified in the Policy Schedule" |
| bajaj_allianz_silver_health | "Room Rent Actual Up to Single Private Air Conditioned room" |
| iffco_tokio_health_protector | "Room Rent Expenses... up to" |
| hdfc_arogya_sanjeevani | Room rent covered under hospitalization benefits |

### DSE-020 Not_Found
566 / 566 exported policies = 100% not_found.

### Recommended Implementation: Packet B
**Pattern:** Amount extractor + table-aware extraction.
- Signal phrases: "room rent", "room rent limit", "accommodation"
- Challenge: Limits are often embedded in benefit tables (room_rent column) rather than prose. Table extraction may be needed for full coverage.
- Risk: Medium. Nontrivial if room rent limits live in tables without a standalone clause.
- Confidence target: 0.80
- Estimated recall on gold: 10-12 / 13 present

---

## 4. icu_limit

### Ontology
- **value_shape:** `icu_limit`
- **export_field:** `icu_limit`
- **extractor_status:** planned

### Gold Status (20 policies)

| present | explicitly_not_covered | not_applicable | not_found |
|---|---|---|---|
| 9 | 0 | 0 | 11 |

9/20 present (45%). Moderate gold coverage. 11 not_found suggests many policies don't have a standalone ICU limit clause; ICU may be covered under room_rent or aggregate limits.

### Representative Evidence Snippets

| Policy | Evidence |
|---|---|
| aditya_birla_activ_care | "ICU Charges" mentioned alongside room rent limits |
| hdfc_arogya_sanjeevani | ICU covered under hospitalization benefits |
| icici_family_shield | "Intensive Care Unit (ICU) Cash Benefit" |
| care_health_care_plus | ICU mentioned in room rent modification optional benefit |

### DSE-020 Not_Found
566 / 566 exported policies = 100% not_found.

### Recommended Implementation: Packet B (paired with room_rent_limit)
**Pattern:** Amount extractor, typically paired with room_rent_limit.
- Signal phrases: "ICU", "intensive care", "ICU charges", "ICU limit"
- Challenge: Often ICU limits are expressed as "ICU charges = 2x room rent limit" or "Actual" rather than a fixed amount. Requires understanding the relationship to room_rent_limit.
- Risk: Medium. The derivable relationship (ICU = multiplier of room rent) may need to be captured.
- Estimated recall on gold: 7-8 / 9 present

---

## 5. restoration_benefit

### Ontology
- **value_shape:** `coverage_status_or_components`
- **export_field:** `restoration_benefit`
- **extractor_status:** planned

### Gold Status (20 policies)

| present | explicitly_not_covered | not_applicable | not_found |
|---|---|---|---|
| 7 | 0 | 0 | 13 |

7/20 present (35%). Low gold coverage — only a third of gold policies include this benefit.

### Representative Evidence Snippets

| Policy | Evidence |
|---|---|
| aditya_birla_activ_care | "Reload of Sum Insured: Once in the Policy Year, We shall provide" |
| care_health_care_plus | "Unlimited Automatic Recharge: reinstatement of up to the base Sum Insured" |
| kotak_mahindra_health_premier | "Restoration Benefit: 100% restoration of the Base Sum Insured" |
| future_generali_health_elite | "Restoration of Sum insured is not applicable for this cover" (explicitly_not_covered) |

### DSE-020 Not_Found
566 / 566 exported policies = 100% not_found.

### Recommended Implementation: Packet C
**Pattern:** Coverage-status extractor (similar to co_pay presence check).
- Signal phrases: "restoration", "reload", "recharge", "restoration of sum insured", "automatic recharge"
- Challenge: Benefit names vary widely: "Restoration Benefit", "Reload of Sum Insured", "Automatic Recharge". Requires flexible signal matching.
- Risk: Low-Medium. Signal variety is manageable, but low gold presence makes recall validation harder.
- Estimated recall on gold: 5-6 / 7 present

---

## 6. modern_treatment_coverage

### Ontology
- **value_shape:** `coverage_status_or_limit`
- **export_field:** `modern_treatment_coverage`
- **extractor_status:** planned

### Gold Status (20 policies)

| present | explicitly_not_covered | not_applicable | not_found |
|---|---|---|---|
| 8 | 0 | 0 | 12 |

8/20 present (40%). Moderate gold coverage. Often appears as a listed section with specific procedures (UAE, IMRT, etc.).

### Representative Evidence Snippets

| Policy | Evidence |
|---|---|
| bajaj_allianz_silver_health | "Modern Treatment Methods and Covered, up to 50% of Sum Insured" |
| hdfc_arogya_sanjeevani | "Uterine Artery Embolization, IMRT, Gamma Knife, etc." |
| iffco_tokio_health_protector | "Modern Treatment Methods and Advancement in Technologies: The following procedures" |
| niva_bupa_health_recharge | "Modern Treatments: What is covered" |

### DSE-020 Not_Found
566 / 566 exported policies = 100% not_found.

### Recommended Implementation: Packet C
**Pattern:** Coverage-list extractor (similar to ayush_coverage).
- Signal phrases: "modern treatment", "modern treatment methods", "advancement in technologies"
- Parse: extract list of covered procedures; determine sub-limit if stated
- Risk: Medium. The list of covered procedures varies significantly; the core "covered / not covered" signal is strong but extraction of individual procedures may be complex.
- Estimated recall on gold: 6-7 / 8 present

---

## 7. newborn_coverage

### Ontology
- **value_shape:** `coverage_status_or_limit`
- **export_field:** `newborn_coverage`
- **extractor_status:** planned

### Gold Status (20 policies)

| present | explicitly_not_covered | not_applicable | not_found |
|---|---|---|---|
| 3 | 3 | 0 | 14 |

3/20 present + 3/20 explicitly_not_covered. Only 15% have coverage; 15% explicitly exclude it; 70% don't mention it (not_found). The hardest concept in Wave 2 for recall.

### Representative Evidence Snippets

| Policy | Evidence |
|---|---|
| care_health_care_plus | Newborn baby covered (optional benefit reference) |
| new_india_floater | "No coverage for the New Born Baby would be available during subsequent renewals" (explicitly_not_covered) |
| reliance_health_gain | "Newborn baby covered from 90 days" |

### DSE-020 Not_Found
566 / 566 exported policies = 100% not_found.

### Recommended Implementation: Packet C
**Pattern:** Coverage-status extractor with explicit_not_covered detection.
- Signal phrases: "newborn", "new born", "new-born", "baby"
- Detect: Look for coverage statements AND explicit exclusion statements (e.g., "No coverage for newborn")
- Challenge: Very low gold presence. Need careful explicit_not_covered detection to avoid false negatives.
- Risk: Medium-High. Low gold presence makes hard to validate. Most policies legitimately don't mention newborn coverage (not_found is correct).
- Estimated recall on gold: 2-3 / 3 present; precision must be prioritized

---

## Packet Summary

| Packet | Concepts | Complexity | Gold Coverage | Priority |
|---|---|---|---|---|
| **Packet A** | claim_intimation_timeline, deductible | Low | High-Medium | P0 |
| **Packet B** | room_rent_limit, icu_limit | Medium | High-Medium | P1 |
| **Packet C** | restoration_benefit, modern_treatment_coverage, newborn_coverage | Low-Medium | Low | P2 |

### Recommended Order
1. **Packet A** — claim_intimation_timeline (duration extractor), deductible (amount extractor)
2. **Packet B** — room_rent_limit + icu_limit (paired, may share table extraction logic)
3. **Packet C** — restoration_benefit, modern_treatment_coverage, newborn_coverage (coverage-status extractors)

---

## Risk Notes

- **restoration_benefit** (7/20) and **newborn_coverage** (3/20) have the lowest gold presence, making recall harder to validate. Precision-first approach recommended.
- **room_rent_limit** and **icu_limit** often live in benefit tables, not standalone clauses. May require table-aware extraction or the ability to parse "ICU = 2x room rent" relationships.
- **deductible** has 3 not_applicable gold cases — need to distinguish "no deductible" from "deductible not found".
- All 7 concepts have identical not_found=566 in DSE-020 triage. Even partial extractors will immediately improve fill rates.
