# DSE-024 Phase D2 Regression Recovery
Date: 2026-06-04
Task: DSE-024

## Summary
Phase D2 removed the harmful Phase C heading penalties, kept the safe heading-pattern improvements, rebuilt DSE-020 heading/section outputs, and regenerated the scale triage report.

## Result
| Metric | Count |
|---|---:|
| Original DSE-020 zero-clause baseline | 132 |
| Phase D1 regressed zero-clause count | 156 |
| Phase D2 recovered zero-clause count | 122 |
| Delta vs baseline | -10 |
| Delta vs D1 | -34 |
| D2 zero-heading count | 122 |
| D2 zero-fact count | 133 |

D2 passed the recovery gate: zero-clause count is `<=132` and no new zero-clause regressions appeared relative to the Phase A baseline.

## Changes Reverted
- Restored `has_toc_dots` to the prior non-harmful positive behavior instead of the Phase C negative penalty.
- Removed the Phase C `short_all_caps_numbered` penalty.
- Removed the Phase C `has_tab_char` penalty.

## Changes Retained
- Letter-numbering support for headings such as `A. Definitions`.
- Guard against treating `S. No.` serial-number/table rows as letter headings.
- Reduced sentence-case penalty for bold numbered headings.

## Baseline Comparison
- Improved policies vs Phase A baseline: `10`
- New zero-clause regressions vs Phase A baseline: `0`

Improved policies:
- `02_star_health_star_group_accident_insurance`
- `02_star_health_star_health_star_cancer_benefit`
- `02_star_health_star_health_star_group_health_insurance_benefit_plus`
- `02_star_health_star_health_star_group_health_insurance_policy_platinum`
- `02_star_health_star_policy_star_cancer_care_platinum_insurance_policy`
- `02_star_health_star_policy_star_critical_illness_multipay_insurance_policyweb`
- `03_care_health_assure_critical_illness_product_prospectus_cum_sales_literature`
- `14_universal_sompo_universal_sompo_corona_rakshak_corona_rakshak_policy_wordings`
- `14_universal_sompo_universal_sompo_group_mashak_rakshak_group_mashak_rakshak_policy_wordings`
- `21_royal_sundaram_royal_sundaram_micro_health_shield_pw`

## Gold Evals
- Heading scorer: `20/20` pass, overall `PASS`. Artifact: `runs/evals/2026-06-04-heading-scorer-dse024-phase-d2.json`.
- Section tree: `19/20` pass, overall `FAIL`. Artifact: `runs/evals/2026-06-04-section-tree-dse024-phase-d2.json`.
- Section tree failure remains `oriental_cancer_protect`, the known pre-existing tree-accuracy issue.

## Acceptance
- `zero_clause_count_lte_132`: `True`
- `gold_heading_eval_20_of_20`: `True`
- `section_tree_recorded_honestly`: `True`
- `no_threshold_lowering`: `True`
- `no_db_or_export_rerun`: `True`
- `raw_pdfs_untouched`: `True`
- `product_b_untouched`: `True`

## Next Decision
Stop global weight tuning and threshold lowering. The next DSE-024 strategy should be a separate fallback heading promotion layer for low-confidence but structurally plausible headings, with explicit false-positive controls and no weakening of the 20-policy gold gates.
