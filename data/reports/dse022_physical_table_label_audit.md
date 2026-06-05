# DSE-022 Packet 2 — Physical Table Label Quality Audit

**Date:** 2026-06-05
**Task ID:** DSE-022
**Input:** 20 reviewed policies, `physical_table_labels.json`, baseline eval `2026-06-05-table-engine-dse022-baseline.json`

## Summary

- **20 policies audited**, **387 physical labels** examined, **79 priority labels**
- **1 type mismatch** found: `new_india_floater` phys_table_002 (gold: `schedule_of_benefits`, extractor: `premium`)
- **1 zero-label policy**: `tata_aig_arogya_sanjeevani` — genuinely no tables
- **0 gold label corrections needed**
- **370 labels** (DSE-012 bulk-reviewed) have empty `headers: []` and `rows: []` — known annotation limitation

### Classification Breakdown

| Classification | Count | Policies |
|---|---|---|
| `label_ok` | 14 | aditya_birla, bajaj_allianz, care, future_generali, icici, iffco_tokio, kotak, liberty, niva_bupa, oriental, reliance, sbi, star, united_india |
| `needs_extractor_review` | 1 | new_india_floater |
| `needs_gold_label_review` | 0 | — |
| `reviewed_no_physical_labels` | 1 | tata_aig_arogya_sanjeevani |
| `nonpriority_diagnostic_only` | 4 | cholamandalam, hdfc, royal_sundaram, universal_sompo |

---

## Policy-by-Policy Audit

### aditya_birla_activ_care — `label_ok`

- **24 physical labels**, **3 priority** (waiting_period + schedule_of_benefits)
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid. No priority type anomalies.
- All priority labels typed as `waiting_period` or `schedule_of_benefits`.

### bajaj_allianz_silver_health — `label_ok`

- **51 physical labels**, **21 priority** — highest in corpus
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. 1 bbox plausibility flag:
  - `phys_table_0046`: full-width bbox (34.56–577.54) but only 23.36pt tall. Likely a tiny single-row structure. Low severity.
- All priority labels typed correctly.

### care_health_care_plus — `label_ok`

- **4 physical labels**, **1 priority**
- DSE-009 original: headers/rows fully populated
- Type accuracy: 100%. Bboxes valid.

### cholamandalam_flexi_max_protect — `nonpriority_diagnostic_only`

- **10 physical labels**, **0 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.
- No priority labels — does not affect priority gate.

### future_generali_health_elite — `label_ok`

- **38 physical labels**, **4 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.

### hdfc_arogya_sanjeevani — `nonpriority_diagnostic_only`

- **2 physical labels**, **0 priority**
- DSE-009 original: headers/rows fully populated
- Type accuracy: 100%. Bboxes valid.
- No priority labels — does not affect priority gate.

### icici_family_shield — `label_ok`

- **4 physical labels**, **3 priority**
- DSE-009 original: headers/rows fully populated
- Type accuracy: 100%. Bboxes valid.

### iffco_tokio_health_protector — `label_ok`

- **28 physical labels**, **4 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.

### kotak_mahindra_health_premier — `label_ok`

- **34 physical labels**, **10 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.

### liberty_critical_connect — `label_ok`

- **41 physical labels**, **3 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.

### new_india_floater — `needs_extractor_review`

- **4 physical labels**, **3 priority**
- DSE-009 original: 3/4 labels have populated headers/rows
- **1 type mismatch:**
  - `phys_table_002` (page 14, cataract sublimit table): gold says `schedule_of_benefits`, extractor classified as `premium`
  - This is an extractor type classifier issue, not a gold label issue.
- `phys_table_001` has empty headers — genuine (table has no separate header row)
- Bboxes valid.

### niva_bupa_health_recharge — `label_ok`

- **18 physical labels**, **2 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.

### oriental_cancer_protect — `label_ok`

- **18 physical labels**, **5 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.

### reliance_health_gain — `label_ok`

- **36 physical labels**, **9 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.

### royal_sundaram_advanced_topup — `nonpriority_diagnostic_only`

- **18 physical labels**, **0 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.
- No priority labels — does not affect priority gate.

### sbi_general_arogya_sanjeevani — `label_ok`

- **17 physical labels**, **2 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.

### star_medi_classic_accident — `label_ok`

- **4 physical labels**, **2 priority**
- DSE-009 original: headers/rows fully populated
- Type accuracy: 100%. Bboxes valid.

### tata_aig_arogya_sanjeevani — `reviewed_no_physical_labels`

- **0 physical labels**, **0 priority** — genuine zero-table policy
- `physical_table_labels.json` is empty `[]`
- Confirmed by source-PDF human review during DSE-012: no tabular structures exist in this policy.
- Correctly handled by eval as `no_physical_labels` — no annotation gap.

### united_india_individual_health — `label_ok`

- **20 physical labels**, **7 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.

### universal_sompo_loan_secure — `nonpriority_diagnostic_only`

- **16 physical labels**, **0 priority**
- DSE-012 bulk-reviewed: all headers/rows empty (known limitation)
- Type accuracy: 100%. Bboxes valid.
- No priority labels — does not affect priority gate.

---

## Cross-Cutting Findings

### Type Mismatches

Only 1 type mismatch across 387 labels (99.74% type accuracy):

| Policy | Label | Gold Type | Extractor Type | Action |
|---|---|---|---|---|
| new_india_floater | phys_table_002 | schedule_of_benefits | premium | Fix extractor classifier |

The cataract sublimit table on page 14 is a small two-column schedule-of-benefits table. The extractor's `table_type_classifier` should recognize this pattern.

### Empty Headers/Rows

- **370 of 387 labels** have empty `headers: []` and `rows: []`
- All 370 are DSE-012 bulk-reviewed labels — the reviewer confirmed type, bbox, row_count, column_count but did not populate cell data
- The remaining 17 labels with populated headers/rows are DSE-009 original labels for care, icici, star, hdfc, and new_india
- This is a known annotation limitation, not an error

### Bbox Issues

- **1 low-severity flag**: `bajaj_allianz_silver_health_phys_table_0046` has a very flat full-width bbox (height ~23pt)
- No null, missing, or invalid bboxes across all 387 labels
- All bboxes within page bounds

### Priority Label Type Check

All 79 priority labels have type `waiting_period` or `schedule_of_benefits`. No anomalies.

### Legacy Row Dispositions

- 373 of 395 legacy rows auto-mapped to physical labels via `source_table_id`
- Confirms `physical_table_eval` disposition is correct and not too broad
- 11 prose summaries, 4 wrong page/type, 7 deferred — unchanged

### No Prose-Summary Labels

All 387 physical labels represent genuine physical tables on PDF pages. No labels appear to describe prose summaries.

---

## Recommendations

1. **Fix extractor type classifier** for `new_india_floater` phys_table_002: cataract sublimit tables should be `schedule_of_benefits`, not `premium`
2. **No gold label corrections needed** — all physical gold labels are accurate
3. **No bbox corrections needed** — 1 plausibility issue is low severity
4. **Future option**: populate cell-level detail for DSE-012 bulk-reviewed labels if header lineage eval needs improvement
5. **All 14 label_ok policies** can proceed with no changes — labels are eval-ready
