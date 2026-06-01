# DSE-012: Gold Corpus Expansion — Human Review Report

Generated: 2026-06-01 15:01
Policies: 15

## Summary

| # | Priority | Slug | Insurer | Pages | Sections | Clauses | Facts Present | Issues |
|---|----------|------|---------|-------|----------|---------|---------------|--------|
| 1 | **CRITICAL** | tata_aig_arogya_sanjeevani | Tata AIG | 28 | 1 | 0 | 0/20 | section_tree_failed_or_degenerate, no_clauses_segmented |
| 2 | **CRITICAL** | aditya_birla_activ_care | Aditya Birla | 34 | 1 | 0 | 0/20 | section_tree_failed_or_degenerate, no_clauses_segmented |
| 3 | **HIGH** | niva_bupa_health_recharge | Niva Bupa | 45 | 232 | 516 | 4/20 | none |
| 4 | **HIGH** | royal_sundaram_advanced_topup | Royal Sundaram | 45 | 184 | 503 | 3/20 | none |
| 5 | **NORMAL** | bajaj_allianz_silver_health | Bajaj Allianz | 33 | 253 | 590 | 4/20 | none |
| 6 | **NORMAL** | reliance_health_gain | Reliance | 36 | 391 | 747 | 5/20 | none |
| 7 | **NORMAL** | united_india_individual_health | United India | 26 | 185 | 407 | 4/20 | none |
| 8 | **NORMAL** | oriental_cancer_protect | Oriental | 44 | 49 | 403 | 2/20 | none |
| 9 | **NORMAL** | cholamandalam_flexi_max_protect | Cholamandalam | 40 | 174 | 462 | 3/20 | none |
| 10 | **NORMAL** | future_generali_health_elite | Future Generali | 38 | 63 | 414 | 1/20 | none |
| 11 | **NORMAL** | iffco_tokio_health_protector | IFFCO Tokio | 45 | 249 | 485 | 5/20 | none |
| 12 | **NORMAL** | kotak_mahindra_health_premier | Kotak Mahindra | 60 | 136 | 860 | 5/20 | none |
| 13 | **NORMAL** | sbi_general_arogya_sanjeevani | SBI General | 29 | 216 | 408 | 5/20 | none |
| 14 | **NORMAL** | universal_sompo_loan_secure | Universal Sompo | 40 | 64 | 124 | 2/20 | none |
| 15 | **NORMAL** | liberty_critical_connect | Liberty | 52 | 38 | 360 | 4/20 | none |

## Recommended Review Order

1. **CRITICAL** policies first (degenerate section tree — need manual structure)
2. **HIGH** priority (unusual section/heading counts)
3. **NORMAL** priority (pipeline output looks reasonable)

## Per-Policy Findings

### tata_aig_arogya_sanjeevani
**Insurer:** Tata AIG | **Plan:** Arogya Sanjeevani | **Pages:** 28 | **Priority:** CRITICAL

**Known issues:** section_tree_failed_or_degenerate, no_clauses_segmented

| Metric | Value |
|--------|-------|
| Sections | 1 |
| Clauses | 0 |
| Tables (semantic) | 0 |
| Physical table labels | 0 |
| Heading labels | 0 |
| Facts present | 0/20 |
| Facts not_found | 20/20 |

**Findings:**

- [CRITICAL] Section tree is degenerate (1 sections, 0 clauses). Heading scorer found no visual headings. All sections/clauses need manual annotation.
- [CRITICAL] Zero clauses segmented. All clauses need manual annotation.
- [INFO] 0 present, 20 not_found. 0 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 0 semantic tables, 0 physical table labels detected.
- [INFO] 0 visual heading labels detected.
- [WARNING] Zero heading labels. Heading scorer may have failed for this document format.

---

### aditya_birla_activ_care
**Insurer:** Aditya Birla | **Plan:** Active Care | **Pages:** 34 | **Priority:** CRITICAL

**Known issues:** section_tree_failed_or_degenerate, no_clauses_segmented

| Metric | Value |
|--------|-------|
| Sections | 1 |
| Clauses | 0 |
| Tables (semantic) | 24 |
| Physical table labels | 24 |
| Heading labels | 0 |
| Facts present | 0/20 |
| Facts not_found | 20/20 |

**Findings:**

- [CRITICAL] Section tree is degenerate (1 sections, 0 clauses). Heading scorer found no visual headings. All sections/clauses need manual annotation.
- [CRITICAL] Zero clauses segmented. All clauses need manual annotation.
- [INFO] 0 present, 20 not_found. 0 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 24 semantic tables, 24 physical table labels detected.
- [INFO] 0 visual heading labels detected.
- [WARNING] Zero heading labels. Heading scorer may have failed for this document format.

---

### niva_bupa_health_recharge
**Insurer:** Niva Bupa | **Plan:** Health Recharge | **Pages:** 45 | **Priority:** HIGH

| Metric | Value |
|--------|-------|
| Sections | 232 |
| Clauses | 516 |
| Tables (semantic) | 18 |
| Physical table labels | 18 |
| Heading labels | 2 |
| Facts present | 4/20 |
| Facts not_found | 16/20 |

**Findings:**

- [INFO] 4 present, 16 not_found. 4 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 18 semantic tables, 18 physical table labels detected.
- [INFO] 2 visual heading labels detected.
- [WARNING] Only 2 heading labels detected despite 232 sections. Heading scorer may have missed visual headings in this document format.

---

### royal_sundaram_advanced_topup
**Insurer:** Royal Sundaram | **Plan:** Advanced Topup Health Insurance | **Pages:** 45 | **Priority:** HIGH

| Metric | Value |
|--------|-------|
| Sections | 184 |
| Clauses | 503 |
| Tables (semantic) | 18 |
| Physical table labels | 18 |
| Heading labels | 1 |
| Facts present | 3/20 |
| Facts not_found | 17/20 |

**Findings:**

- [INFO] 3 present, 17 not_found. 3 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 18 semantic tables, 18 physical table labels detected.
- [INFO] 1 visual heading labels detected.
- [WARNING] Only 1 heading labels detected despite 184 sections. Heading scorer may have missed visual headings in this document format.

---

### bajaj_allianz_silver_health
**Insurer:** Bajaj Allianz | **Plan:** Silver Health | **Pages:** 33 | **Priority:** NORMAL

| Metric | Value |
|--------|-------|
| Sections | 253 |
| Clauses | 590 |
| Tables (semantic) | 51 |
| Physical table labels | 51 |
| Heading labels | 13 |
| Facts present | 4/20 |
| Facts not_found | 16/20 |

**Findings:**

- [INFO] 4 present, 16 not_found. 4 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 51 semantic tables, 51 physical table labels detected.
- [INFO] 13 visual heading labels detected.

---

### reliance_health_gain
**Insurer:** Reliance | **Plan:** Health Gain | **Pages:** 36 | **Priority:** NORMAL

| Metric | Value |
|--------|-------|
| Sections | 391 |
| Clauses | 747 |
| Tables (semantic) | 36 |
| Physical table labels | 36 |
| Heading labels | 11 |
| Facts present | 5/20 |
| Facts not_found | 15/20 |

**Findings:**

- [WARNING] Unusually many sections (391). May indicate over-segmentation.
- [INFO] 5 present, 15 not_found. 5 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 36 semantic tables, 36 physical table labels detected.
- [INFO] 11 visual heading labels detected.

---

### united_india_individual_health
**Insurer:** United India | **Plan:** Individual Health Insurance Policy - Platinum / Gold / Senior Citizen | **Pages:** 26 | **Priority:** NORMAL

| Metric | Value |
|--------|-------|
| Sections | 185 |
| Clauses | 407 |
| Tables (semantic) | 20 |
| Physical table labels | 20 |
| Heading labels | 10 |
| Facts present | 4/20 |
| Facts not_found | 16/20 |

**Findings:**

- [INFO] 4 present, 16 not_found. 4 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 20 semantic tables, 20 physical table labels detected.
- [INFO] 10 visual heading labels detected.

---

### oriental_cancer_protect
**Insurer:** Oriental | **Plan:** Cancer Protect | **Pages:** 44 | **Priority:** NORMAL

| Metric | Value |
|--------|-------|
| Sections | 49 |
| Clauses | 403 |
| Tables (semantic) | 18 |
| Physical table labels | 18 |
| Heading labels | 26 |
| Facts present | 2/20 |
| Facts not_found | 18/20 |

**Findings:**

- [INFO] 2 present, 18 not_found. 2 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 18 semantic tables, 18 physical table labels detected.
- [INFO] 26 visual heading labels detected.

---

### cholamandalam_flexi_max_protect
**Insurer:** Cholamandalam | **Plan:** Flexi Max Protect | **Pages:** 40 | **Priority:** NORMAL

| Metric | Value |
|--------|-------|
| Sections | 174 |
| Clauses | 462 |
| Tables (semantic) | 10 |
| Physical table labels | 10 |
| Heading labels | 16 |
| Facts present | 3/20 |
| Facts not_found | 17/20 |

**Findings:**

- [INFO] 3 present, 17 not_found. 3 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 10 semantic tables, 10 physical table labels detected.
- [INFO] 16 visual heading labels detected.

---

### future_generali_health_elite
**Insurer:** Future Generali | **Plan:** FG Health Elite | **Pages:** 38 | **Priority:** NORMAL

| Metric | Value |
|--------|-------|
| Sections | 63 |
| Clauses | 414 |
| Tables (semantic) | 38 |
| Physical table labels | 38 |
| Heading labels | 10 |
| Facts present | 1/20 |
| Facts not_found | 19/20 |

**Findings:**

- [INFO] 1 present, 19 not_found. 1 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 38 semantic tables, 38 physical table labels detected.
- [INFO] 10 visual heading labels detected.

---

### iffco_tokio_health_protector
**Insurer:** IFFCO Tokio | **Plan:** Health Protector | **Pages:** 45 | **Priority:** NORMAL

| Metric | Value |
|--------|-------|
| Sections | 249 |
| Clauses | 485 |
| Tables (semantic) | 28 |
| Physical table labels | 28 |
| Heading labels | 9 |
| Facts present | 5/20 |
| Facts not_found | 15/20 |

**Findings:**

- [INFO] 5 present, 15 not_found. 5 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 28 semantic tables, 28 physical table labels detected.
- [INFO] 9 visual heading labels detected.

---

### kotak_mahindra_health_premier
**Insurer:** Kotak Mahindra | **Plan:** Kotak Health premier | **Pages:** 60 | **Priority:** NORMAL

| Metric | Value |
|--------|-------|
| Sections | 136 |
| Clauses | 860 |
| Tables (semantic) | 34 |
| Physical table labels | 34 |
| Heading labels | 6 |
| Facts present | 5/20 |
| Facts not_found | 15/20 |

**Findings:**

- [INFO] 5 present, 15 not_found. 5 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 34 semantic tables, 34 physical table labels detected.
- [INFO] 6 visual heading labels detected.

---

### sbi_general_arogya_sanjeevani
**Insurer:** SBI General | **Plan:** Arogya Sanjeevani | **Pages:** 29 | **Priority:** NORMAL

| Metric | Value |
|--------|-------|
| Sections | 216 |
| Clauses | 408 |
| Tables (semantic) | 17 |
| Physical table labels | 17 |
| Heading labels | 3 |
| Facts present | 5/20 |
| Facts not_found | 15/20 |

**Findings:**

- [INFO] 5 present, 15 not_found. 5 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 17 semantic tables, 17 physical table labels detected.
- [INFO] 3 visual heading labels detected.

---

### universal_sompo_loan_secure
**Insurer:** Universal Sompo | **Plan:** Loan Secure | **Pages:** 40 | **Priority:** NORMAL

| Metric | Value |
|--------|-------|
| Sections | 64 |
| Clauses | 124 |
| Tables (semantic) | 16 |
| Physical table labels | 16 |
| Heading labels | 4 |
| Facts present | 2/20 |
| Facts not_found | 18/20 |

**Findings:**

- [INFO] 2 present, 18 not_found. 2 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 16 semantic tables, 16 physical table labels detected.
- [INFO] 4 visual heading labels detected.

---

### liberty_critical_connect
**Insurer:** Liberty | **Plan:** Critical Connect | **Pages:** 52 | **Priority:** NORMAL

| Metric | Value |
|--------|-------|
| Sections | 38 |
| Clauses | 360 |
| Tables (semantic) | 41 |
| Physical table labels | 41 |
| Heading labels | 5 |
| Facts present | 4/20 |
| Facts not_found | 16/20 |

**Findings:**

- [INFO] 4 present, 16 not_found. 4 from extractors, 15 need manual annotation.
- [ACTION] 15 concepts have no extractor. All are marked not_found and need manual search: specific_disease_waiting_periods, room_rent_limit, icu_limit, deductible, cumulative_bonus_ncb...
- [INFO] 41 semantic tables, 41 physical table labels detected.
- [INFO] 5 visual heading labels detected.

---
