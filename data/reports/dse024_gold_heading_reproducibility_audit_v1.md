# DSE-024 Gold Heading Reproducibility Audit v1

Date: 2026-06-04
Task: DSE-024 Phase E3C1

## Summary

Regenerating `data/interim/logical/*/heading_candidates.json` from the restored scorer produced a 20-policy heading eval of **17/20 PASS**, while older DSE-024 artifacts reported **20/20 PASS**. The failure is real in the regenerated artifacts and is not caused by changed gold labels.

| Policy | Current Result | Prior Passing Result | Classification | Conclusion |
|---|---:|---:|---|---|
| `aditya_birla_activ_care` | 0 TP / 80 FN | 70 TP / 10 FN | `needs_parser_fix` | Low-font same-style headings need explicit section/roman/lettered/colon structural handling. |
| `care_health_care_plus` | 49 TP / 8 FP / 0 FN | 49 TP / 0 FP / 0 FN | `gold_label_incompatibility` | All current gold heading labels are found; 8 extra visual structural headings are missing from heading labels or require an eval exclusion decision. |
| `tata_aig_arogya_sanjeevani` | 0 TP / 5 FP / 25 FN | 23 TP / 2 FN | `needs_parser_fix` | True headings are low-font bold/dictionary/section headings below fallback floor; current fallback promotes definition-list items instead. |

## Evidence

### `aditya_birla_activ_care`

Current scorer output:
- `total_candidates_above_threshold`: 0
- `true_positives`: 0
- `false_negatives`: 80

Representative missed labels:

| Label | Line | Score | Key Contributions |
|---|---|---:|---|
| `Section A. PREAMBLE` | `p1l_4` | 0.3593 | numbering + dictionary + spacing, but no font/bold boost. |
| `Section B. BENEFITS UNDER THE POLICY` | `p1l_15` | 0.0833 | structural heading penalized as a long numbered definition. |
| `Section I: Basic Covers:` | `p1l_16` | 0.1722 | structural section token penalized as long numbered definition. |
| `(a) In-patient Hospitalization:` | `p1l_25` | -0.2296 | parenthesized letter heading not recognized. |

Decision: **parser fix required.** This format uses same-font legal headings where the only strong signals are textual structure: `Section A.`, `Section I:`, `(a)`, and short colon labels.

### `care_health_care_plus`

Current scorer output:
- `total_candidates_above_threshold`: 57
- `true_positives`: 49
- `false_positives`: 8
- `false_negatives`: 0

Representative current false positives:
- `5.1.1Disclosure of Information`
- `5.1.10Renewal of Policy`
- `5.1.11Withdrawal of Policy`
- `5.1.13Premium Payment in Installments`
- `5.2.2Records to be maintained`
- `5.2.3No constructive Notice`
- `5.2.5Limitation of liability`
- `5.2.7Alterations in the Policy`

Decision: **gold label incompatibility / eval-label gap.** These are not random scorer noise; they are compact numbered, bold structural headings in the policy wording. The current gold `heading_labels.json` finds all existing labels but does not include these additional visual subheadings. Do not suppress this class globally just to pass the heading eval.

### `tata_aig_arogya_sanjeevani`

Current scorer output:
- `total_candidates_above_threshold`: 5
- `true_positives`: 0
- `false_positives`: 5
- `false_negatives`: 25

Representative missed labels:

| Label | Line | Score | Key Contributions |
|---|---|---:|---|
| `Preamble` | `p1l_3` | 0.1738 | bold + dictionary, but font ratio below body mode and no numbering. |
| `Operative Clause` | `p1l_16` | 0.1976 | bold + dictionary + spacing, still below fallback floor. |
| `Section 1 -Definitions` | `p1l_34` | 0.1905 | section token + bold + dictionary, but penalized as long numbered definition. |
| `Section 2 -Benefits` | `p7l_9` | 0.2190 | section token + bold + dictionary, but below fallback floor. |

Current fallback instead promotes definition-list entries such as `2.Family`, `18.Hospital`, `38. Renewal:`, `39. Room Rent`, and `5. Co-payment`.

Decision: **parser fix required.** Fallback needs a separate lower-band path for source-backed section/dictionary headings, plus guards that prevent definition-list entries from winning over true document headings.

## E3C Implications

- E3C safe fixes must include the gold parser gaps for Aditya and Tata, otherwise the regenerated gold heading eval remains below the prior acceptance bar.
- Care should not be “fixed” by suppressing compact numbered visual subheadings. Either update heading labels in a separate gold-maintenance task or document the eval-label gap.
- E3C must keep fallback zero-heading-only and must not lower the global threshold.

