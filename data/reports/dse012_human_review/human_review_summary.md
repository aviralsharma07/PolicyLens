# DSE-012 Human Review Consolidated Report

Date: 2026-06-01
Reviewer: Avi-authorized Codex reviewer

## Summary

| Policy | Sections rebuilt | Removed pseudo-sections | Added headings | Fact statuses | Known issues |
|---|---:|---:|---:|---|---|
| `tata_aig_arogya_sanjeevani` | true | 0 | 25 | not_found:8, present:12 | section_tree_manually_rebuilt_from_source_pdf |
| `aditya_birla_activ_care` | true | 0 | 80 | explicitly_not_covered:1, not_found:3, present:16 | section_tree_manually_rebuilt_from_source_pdf |
| `niva_bupa_health_recharge` | false | 0 | 0 | explicitly_not_covered:1, not_found:5, present:14 | none |
| `royal_sundaram_advanced_topup` | false | 0 | 0 | not_found:6, present:14 | none |
| `bajaj_allianz_silver_health` | false | 0 | 0 | not_found:6, present:14 | none |
| `reliance_health_gain` | false | 0 | 0 | not_found:6, present:14 | none |
| `united_india_individual_health` | false | 0 | 0 | not_found:6, present:14 | none |
| `oriental_cancer_protect` | false | 0 | 0 | not_applicable:1, not_found:10, present:9 | none |
| `cholamandalam_flexi_max_protect` | false | 0 | 0 | not_found:14, present:6 | none |
| `future_generali_health_elite` | false | 0 | 0 | explicitly_not_covered:2, not_found:3, present:15 | none |
| `iffco_tokio_health_protector` | false | 0 | 0 | explicitly_not_covered:1, not_found:6, present:13 | none |
| `kotak_mahindra_health_premier` | false | 0 | 0 | explicitly_not_covered:2, not_found:2, present:16 | none |
| `sbi_general_arogya_sanjeevani` | false | 0 | 0 | not_found:7, present:13 | none |
| `universal_sompo_loan_secure` | false | 0 | 0 | not_applicable:1, not_found:15, present:4 | none |
| `liberty_critical_connect` | false | 0 | 0 | explicitly_not_covered:1, not_applicable:1, not_found:12, present:6 | none |

## Review Method

- Source PDFs were read through `pdftotext -layout`, one page at a time.
- Existing pipeline sections, clauses, table labels, and extracted facts were used as drafts only.
- Present and explicitly-not-covered facts were retained only with a page-level source excerpt.
- Tata AIG and Aditya Birla had degenerate draft section trees; their section and clause files were rebuilt from source-PDF/physical-line review.
- Obvious footer/UIN pseudo-sections were removed or remapped where detected.

## Limitations

- This pass is a source-text review and does not attempt parser remediation.
- Page-render visual review is represented by physical-line and table bbox review; unresolved parser failures are documented as known issues.
