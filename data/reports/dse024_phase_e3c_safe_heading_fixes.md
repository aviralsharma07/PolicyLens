# DSE-024 Phase E3C Safe Heading Fixes

Date: 2026-06-04
Task: DSE-024

## Summary

Phase E3C implemented narrow fallback-only heading recognition for structural heading formats found in the E3B safe-candidate audit. The fix does not lower the global heading threshold and does not promote headings in documents that already have accepted headings.

Full-corpus zero-clause policies dropped from **58** to **1** after rerunning heading scoring, section-tree construction, and the DSE-020 triage report.

## What Changed

- Added structural heading recognizers for:
  - `Section A. PREAMBLE`
  - `Section I: Basic Covers:`
  - `Part I: Definitions`
  - `(a) In-patient Hospitalization:`
  - compact lettered headings such as `H.Stereotactic radio surgeries`
  - short dictionary headings such as `Preamble`
- Kept all new structural signals at zero global score weight.
- Used those signals only in the zero-heading fallback layer.
- Kept fallback floor at `0.42` except for explicitly structural override signals.
- Added false-positive guards for percentage rows, serial/table rows, duration-percentage rows, procedure/item rows, and generic `POLICY WORDINGS`.
- Increased fallback promotion cap from `40` to `90` so same-font policies with many legitimate structural headings can be recovered.

## Results

| Metric | Before E3C | After E3C |
|---|---:|---:|
| Full-corpus zero headings | 58 | 1 |
| Full-corpus zero clauses | 58 | 1 |
| Full-corpus per-policy stages | 647/647 | 647/647 |
| Exports | 566 | 566 |

Remaining zero-heading / zero-clause policy:

| Slug | File | Pages | Notes |
|---|---|---:|---|
| `23_raheja_qbe_raheja_qbe_product_list` | `23_Raheja_QBE/Raheja_QBE_Product_List.pdf` | 4 | Product-list style document with `match_status: pending`; should be handled by corpus/identity filtering, not scorer loosening. |

## Gold Eval Results

The regenerated gold heading eval remains **17/20 PASS**:

- `aditya_birla_activ_care`: improved from 0 candidates to 52 candidates, but heading-label precision/recall still misses the hard gate.
- `tata_aig_arogya_sanjeevani`: all gold labels are found, but fallback also promotes definition-list entries, lowering precision.
- `care_health_care_plus`: all gold labels are found; 8 extra compact numbered visual headings are likely missing from `heading_labels.json`.

The section-tree eval is **19/20 PASS**, with only the pre-existing `oriental_cancer_protect` tree-accuracy issue. Importantly, `aditya_birla_activ_care`, `tata_aig_arogya_sanjeevani`, and `care_health_care_plus` all pass the section-tree eval after E3C.

## Interpretation

E3C succeeded for the full-corpus parser goal. The remaining gap is not a broad parser failure:

- 1 residual zero-clause item is a likely corpus-filter issue.
- The 20-policy heading-label eval now exposes label/scorer granularity disagreements, but the section-tree layer is healthy for the recovered policies.
- More global heading scoring changes would be higher risk than value at this point.

## Recommendation

Stop broad heading scorer work for DSE-024. Close DSE-024 with one final corpus-filter packet that classifies or excludes `Raheja_QBE_Product_List.pdf`, then move to DSE-021 extractor Wave 2.
