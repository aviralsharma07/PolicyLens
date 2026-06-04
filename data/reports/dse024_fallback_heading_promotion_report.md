# DSE-024 Fallback Heading Promotion Report

Date: 2026-06-04

## Summary
A zero-heading-only fallback promotion layer was added after normal heading scoring. It promotes low-confidence but structurally plausible headings only when the document would otherwise have no headings.

## Result
| Metric | Count |
|---|---:|
| Original DSE-020 zero-clause baseline | 132 |
| D2 zero-clause count | 122 |
| Fallback zero-clause count | 110 |
| Improvement vs D2 | 12 |
| New regressions vs D2 | 0 |
| Zero-heading count after fallback | 84 |
| Zero-fact count after fallback | 133 |

## Promotion Audit
- Policies with fallback promotions: `52`
- Total promoted headings: `207`
- Improved policies vs D2: `12`

Promotion reasons:
- `bold_numbered_heading`: 158
- `numbered_dictionary_heading`: 127
- `all_caps_numbered_heading`: 62
- `numbered_spacing_signal`: 59
- `section_or_part_token`: 40
- `letter_heading_with_support`: 34
- `compact_numbered_heading`: 11
- `numbered_enlarged_font`: 2

Guarded false-positive reasons:
- `procedure_or_item_list`: 28
- `price_or_benefit_value_row`: 2
- `boilerplate_or_page_artifact`: 1

## Improved Policies
- `02_star_health_star_health_medi_classic_insurance_policy_individual` (Star_Health) — promoted headings: 5
- `02_star_health_star_health_star_care_micro_insurance_policy` (Star_Health) — promoted headings: 4
- `02_star_health_star_health_star_health_assure_insurance_policy` (Star_Health) — promoted headings: 6
- `02_star_health_star_health_young_star_insurance_policy` (Star_Health) — promoted headings: 5
- `02_star_health_star_policy_star_health_gain_insurance_policy` (Star_Health) — promoted headings: 3
- `02_star_health_star_star_care_micro_insurance_policy` (Star_Health) — promoted headings: 3
- `03_care_health_add_on_explore_plus_policy_terms_conditions` (Care_Health) — promoted headings: 3
- `03_care_health_care_freedom_policy` (Care_Health) — promoted headings: 10
- `03_care_health_enhance_t_c_effective_from_12_september_2024` (Care_Health) — promoted headings: 6
- `04_icici_lombard_befit_rider_policy_wording` (ICICI_Lombard) — promoted headings: 10
- `04_icici_lombard_icici_lombard_corona_kavach_policy_icici_lombard` (ICICI_Lombard) — promoted headings: 4
- `04_icici_lombard_icici_lombard_golden_shield` (ICICI_Lombard) — promoted headings: 7

## Gold Evals
- Heading scorer: `20/20` pass, overall `PASS`.
- Section tree: `19/20` pass, overall `FAIL`.
- Section tree failure remains `oriental_cancer_protect`, the known pre-existing tree-accuracy issue.

## Acceptance
- `zero_clause_improved_below_122`: `True`
- `no_new_zero_clause_regressions_vs_d2`: `True`
- `gold_heading_eval_20_of_20`: `True`
- `section_tree_recorded_honestly`: `True`
- `no_global_threshold_lowering`: `True`
- `no_db_or_export_rerun`: `True`
- `raw_pdfs_untouched`: `True`
- `product_b_untouched`: `True`

## Next Step
Do not lower the global heading threshold. The remaining 110 zero-clause policies need either more format-specific promotion guards or corpus filtering for non-policy/unsupported documents.
