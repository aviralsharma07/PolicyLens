# DSE-024: Zero-Clause Policy Audit Plan

## Purpose

Classify 132 policies from DSE-020 scale triage that produce zero headings and zero clauses. This audit must complete before any parser code changes.

## Source

- `data/reports/dse020_scale_triage_report_v1.json` → `metrics.zero_headings` (132 slugs)

## Classification Categories

| Category | Code | Description |
|----------|------|-------------|
| Non-policy / brochure | NON_POLICY | Document is not a policy wording (brochure, prospectus, circular) |
| Heading scorer missed | HEADING_MISS | Physical text extracted but heading scorer failed to detect headings |
| Section tree failed | SECTION_FAIL | Headings detected but section tree builder failed to produce clauses |
| Physical extraction malformed | PHYSICAL_BAD | pdfplumber extracted garbled/missing text |
| Duplicate / non-canonical | DUPLICATE | Document is a duplicate or withdrawn version |
| Unsupported format | UNSUPPORTED | Tables-only format, image-based text, non-standard layout |
| Unknown | UNKNOWN | Cannot determine without deeper investigation |

## Audit Process

1. For each slug, read the physical JSON (`data/interim/dse020/physical/{slug}/document_physical.json`).
2. Check page count, line count, text content quality.
3. If physical text looks reasonable, check heading candidates (`data/interim/dse020/logical/{slug}/heading_candidates.json`).
4. Check section tree output (`data/interim/dse020/logical/{slug}/section_tree.json`).
5. Optionally inspect PDF text via `pdftotext` or pdfplumber for hard cases.
6. Record classification and notes.

## Output Format

```json
{
  "schema_version": "dse024_audit.v1",
  "date": "2026-06-04",
  "total_policies": 132,
  "classifications": [
    {
      "slug": "tata_aig_arogya_sanjeevani",
      "category": "HEADING_MISS",
      "notes": "Headings same font size as body text (11pt), no bold, no numbering",
      "insurer": "tata_aig",
      "page_count": 24,
      "physical_line_count": 1200
    }
  ],
  "category_summary": {
    "NON_POLICY": 0,
    "HEADING_MISS": 0,
    "SECTION_FAIL": 0,
    "PHYSICAL_BAD": 0,
    "DUPLICATE": 0,
    "UNSUPPORTED": 0,
    "UNKNOWN": 132
  }
}
```

## Phase A Results (2026-06-04)

Classification complete. See `dse024_zero_clause_classification_v1.json` and `.md` for full data.

| Category | Count | % |
|----------|-------|---|
| HEADING_MISS | 117 | 88.6% |
| NON_POLICY | 9 | 6.8% |
| DUPLICATE | 6 | 4.5% |
| SECTION_FAIL | 0 | 0.0% |
| PHYSICAL_BAD | 0 | 0.0% |
| UNSUPPORTED | 0 | 0.0% |
| UNKNOWN | 0 | 0.0% |

Key finding: 117/132 (88.6%) are real policy wordings where the heading scorer
produces candidates but none score above the 0.5 threshold. 53 of these have
a max score >= 0.45, meaning a small threshold reduction would capture many.
9 are true non-policy documents (brochures, CIS, prospectus, product list).
6 are duplicate-hash entries.

Script: `scripts/dse024_classify_zero_clause_policies.py`

## Sample Selection (Phase B)

Select 20 policies for deep inspection:
- At least 1 from each insurer represented in the zero-clause list.
- At least 1 from each expected category (once categories are known).
- Priority to high-volume insurers (Star Health, New India, etc.).

Recommended 20-policy sample (from Phase A classification):

| # | Slug | Category | Insurer | Pages | Max Heading Score |
|---|------|----------|---------|-------|-------------------|
| 1 | 05_niva_bupa_niva_bupa_health_plus | HEADING_MISS | Niva_Bupa | 126 | 0.4690 |
| 2 | non_policy_wordings_nivabupa_health_recharge_prospectus | NON_POLICY | non_policy_wordings | 42 | 0.4198 |
| 3 | 12_iffco_tokio_iffco_tokio_family_health_protector_irdai | DUPLICATE | IFFCO_Tokio | 47 | 0.4967 |
| 4 | 09_hdfc_ergo_hdfc_ergo_my_optima_secure | HEADING_MISS | HDFC_ERGO | 42 | 0.4699 |
| 5 | 02_star_health_star_health_star_group_health_insurance_benefit_plus | HEADING_MISS | Star_Health | 50 | 0.4867 |
| 6 | 11_aditya_birla_aditya_birla_activ_health_2021 | HEADING_MISS | Aditya_Birla | 67 | 0.3667 |
| 7 | 13_future_generali_future_generali_future_poorna_suraksha_group_0bc8ea4f | HEADING_MISS | Future_Generali | 45 | 0.3680 |
| 8 | 16_kotak_mahindra_kotak_kotak_group_hospital_cash | HEADING_MISS | Kotak_Mahindra | 30 | 0.3500 |
| 9 | tata_aig_arogya_sanjeevani | HEADING_MISS | Tata_AIG | 28 | 0.4738 |
| 10 | 04_icici_lombard_icici_lombard_group_take_care_insurance | HEADING_MISS | ICICI_Lombard | 41 | 0.4481 |
| 11 | 08_bajaj_allianz_bajaj_allianz_family_health_care | HEADING_MISS | Bajaj_Allianz | 37 | 0.3862 |
| 12 | 12_iffco_tokio_iffco_tokio_family_health_protector | HEADING_MISS | IFFCO_Tokio | 47 | 0.4967 |
| 13 | 07_oriental_insurance_oriental_oriental_secure_credit | HEADING_MISS | Oriental_Insurance | 44 | 0.4194 |
| 14 | 14_universal_sompo_universal_sompo_csc_complete_healthcare_insurance | HEADING_MISS | Universal_Sompo | 40 | 0.2000 |
| 15 | 21_royal_sundaram_royal_sundaram_ace_health_advantage_pw | HEADING_MISS | Royal_Sundaram | 56 | 0.4817 |
| 16 | 03_care_health_care_freedom_policy | HEADING_MISS | Care_Health | 45 | 0.4905 |
| 17 | 19_liberty_liberty_79fc880c_2c03_e5e9_3a02_dc751307afff | HEADING_MISS | Liberty | 46 | 0.4987 |
| 18 | 18_cholamandalam_cholamandalam_chola_classic_health_individual | HEADING_MISS | Cholamandalam | 35 | 0.4942 |
| 19 | 22_edelweiss_edelweiss_group_corona_pw | HEADING_MISS | Edelweiss | 17 | 0.4639 |
| 20 | 05_niva_bupa_niva_bupa_health_pulse | HEADING_MISS | Niva_Bupa | 63 | 0.4947 |

## Phase B Results (2026-06-04)

Deep inspection of 20 representative policies complete. See `dse024_zero_clause_sample_inspection_v1.json` and `.md`.

### Root Cause Distribution (Sample of 20)

| Root Cause | Count |
|------------|-------|
| threshold_too_high | 9 |
| needs_manual_review | 5 |
| missing_feature_spacing | 2 |
| non_policy_should_exclude | 1 |
| duplicate_should_skip | 1 |
| missing_feature_numbered_heading | 1 |
| missing_feature_all_caps | 1 |

### Key Findings

- **Threshold too high**: 9/20 policies have real headings scoring 0.45-0.499 but missing 0.5. These would benefit from a threshold reduction to 0.45.
- **Low false-positive risk**: In 9 threshold_too_high cases, 7 have low false-positive risk (all candidates ≥ 0.45 are real headings).
- **Letter numbering missing**: Policies using `A.`, `B.`, `Part I`, `Part II` prefixes lose +0.30 `matches_numbering` weight because patterns don't match letters.
- **TOC domination**: Some documents (e.g., HDFC Ergo) have TOC entries scoring highest. Threshold reduction alone won't fix these — TOC entries would be misclassified as headings.
- **Procedure-code noise**: Documents with non-payable-items lists produce all-caps numbered items (`43 SPLINT`) scoring 0.45+, creating false-positive risk at lower thresholds.
- **Sentence-case penalty**: Bold definition headings (`Condition Precedent: Condition Precedent means...`) get -0.30 `is_sentence_case` penalty even though they are clearly headings by other features.

### Recommended Parser Changes (Ranked by Impact)

1. **Lower heading threshold to 0.45** — HIGH IMPACT, helps 9/20 inspected. Low FP risk for documents where top candidates are real headings.
2. **Add letter-numbering patterns** — MEDIUM IMPACT. Current patterns skip `A.`, `B.`, `(a)`, `(b)`, `Part I`, `Part II`.
3. **Reduce is_sentence_case penalty for bold+numbered lines** — MEDIUM IMPACT. Current -0.30 applies to bold definition headings.
4. **Suppress TOC entries** — LOW-MEDIUM IMPACT. Add `has_toc_dots` penalty or exclude early-page candidates.
5. **Suppress procedure-code list items** — LOW IMPACT. All-caps numbered items from appendices score 0.45+.

**Warning:** Do NOT blindly lower the global threshold without evaluation. TOC-dominated and procedure-code-dominated documents would admit false positives at 0.45.

Script: `scripts/dse024_inspect_zero_clause_sample.py`
Outputs: `data/reports/dse024_zero_clause_sample_inspection_v1.json` + `.md`
