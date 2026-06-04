# Session: DSE-024 — Full-Corpus Parser Remediation for Zero-Clause Policies

Date: 2026-06-04
Task ID: DSE-024
Project: doc-structure-engine
Branch: feat/dse-024-parser-remediation
AI executor: opencode
Human reviewer: Avi

## Goal

Plan and prepare DSE-024 based on DSE-020 findings. Do not implement parser fixes yet.

## Context

DSE-020 scale triage revealed:
- 132 policies with zero headings and zero clauses (20.4% of corpus)
- 133 policies with zero fact candidates (132 overlap with zero-heading)
- Parser/section-tree failures are the primary bottleneck to extraction coverage

DSE-021 (extractor wave 2) is blocked until DSE-024 reduces zero-clause failures.

## Plan

### Phase A — Classification (100% of 132 policies)
Classify each zero-clause policy into one of:
- true non-policy / brochure / prospectus
- heading scorer missed headings
- section tree failed despite headings
- physical text extraction malformed
- duplicate/non-canonical document
- unsupported product format

### Phase B — Sample Inspection (20 representative)
Select 20 policies across insurers and product types. Inspect physical JSON + debug HTML + PDF raw text. Document exact failure mechanism.

### Phase C — Targeted Fixes
Heading scorer and/or section tree improvements. Must not regress 20-policy gold evals.

### Phase D — Re-validation
Rerun parser stages for affected policies. Regenerate DSE-020 triage. Full pytest.

## Relevant Docs Read
- AGENTS.md
- docs/tasks.md (DSE-020, DSE-021, DSE-024)
- IMPLEMENTATION_PLAN.md
- data/reports/dse020_scale_triage_report_v1.md
- data/reports/dse020_scale_triage_report_v1.json
- runs/sessions/2026-06-03-dse020-full-corpus-scale-triage.md
- docs/risk_register.md
- docs/changelog.md

## Files Changed (this session)
- `docs/tasks.md` — DSE-020 moved to Completed; DSE-024 added active; DSE-021 blocked
- `IMPLEMENTATION_PLAN.md` — roadmap reordered; rationale for parser-before-extractors
- `docs/risk_register.md` — added R25
- `docs/changelog.md` — DSE-024 planning entry
- `runs/sessions/2026-06-04-dse024-full-corpus-parser-remediation-plan.md` — this file
- `data/reports/dse024_zero_clause_policy_audit_plan.md` — audit plan

## Generated Artifacts
- `data/reports/dse024_zero_clause_policy_audit_plan.md`

## Phase A Results (2026-06-04)

Classification complete. Results:
- HEADING_MISS: 117 (88.6%) — heading scorer fails below 0.5 threshold
- NON_POLICY: 9 (6.8%) — brochures, CIS, prospectus, product list
- DUPLICATE: 6 (4.5%) — duplicate-hash entries
- SECTION_FAIL / PHYSICAL_BAD / UNSUPPORTED / UNKNOWN: 0

Key finding: 53/117 HEADING_MISS policies have max heading score >= 0.45,
so a small threshold reduction would capture nearly half.

Script: `scripts/dse024_classify_zero_clause_policies.py`
Outputs: `data/reports/dse024_zero_clause_classification_v1.json` + `.md`
Tests: `pytest tests/test_dse020_manifest.py` — 4/4 PASSED

## Decisions Made
- DSE-021 explicitly blocked by DSE-024 in task tracking.
- Parser remediation prioritized over new extractors based on DSE-020 evidence.
- DSE-024 Phase A (classification) must complete before any code changes.
- Classification confirmed: majority (88.6%) are genuine heading scorer failures,
  not unsupported formats or physical extraction issues.
- Highest-leverage fix: lower heading threshold from 0.50 to ~0.45 (captures 53/117).
- Phase B confirmed: threshold reduction is the single highest-impact change (9/20 sample), but feature-level fixes are needed for remaining cases.
- **Do NOT blindly lower threshold**: TOC-dominated and procedure-code-dominated documents would admit false positives at 0.45.
- Multiple targeted features needed: letter-numbering patterns, reduced sentence-case penalty for bold lines, TOC suppression.

## Phase B Results (2026-06-04)

Sample inspection complete. 20/20 representative policies inspected.

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

### Concrete Heading Examples Missed
- "8. Migration" (score 0.4967, IFFCO Tokio)
- "10.Renewal" (score 0.4987, Liberty)
- "Part I: Definitions" (score 0.4526, Liberty)
- "1. Preamble" (score 0.4699, HDFC Ergo)
- "5.1.6 Fraud" (score 0.4905, Care Health)
- "12. Important Note:" (score 0.4867, Star Health)
- "2.Definitions & Interpretation" (score 0.4466, Niva Bupa)

### Recommended Parser Changes (Ranked by Impact)
1. **Lower heading threshold to 0.45** — HIGH IMPACT, helps 12/20 sample policies
2. **Add letter-numbering patterns** — MEDIUM IMPACT (`A.`, `B.`, `Part I`, `Part II`)
3. **Reduce is_sentence_case penalty for bold+numbered lines** — MEDIUM IMPACT
4. **Suppress TOC entries** — LOW-MEDIUM IMPACT (has_toc_dots penalty)
5. **Suppress procedure-code list items** — LOW IMPACT (numbered all-caps items in appendices)

### False-Positive Risk Assessment
- 7/9 threshold_too_high cases: **low risk** (all candidates ≥ 0.45 are real headings)
- 2/9 cases: **medium-high risk** (TOC entries or procedure-code items dominate ≥ 0.45 candidates)
- Global threshold lowering without further filtering is NOT safe.

### Files Created (Phase B)
- `scripts/dse024_inspect_zero_clause_sample.py`
- `data/reports/dse024_zero_clause_sample_inspection_v1.json`
- `data/reports/dse024_zero_clause_sample_inspection_v1.md`

### Files Modified (Phase B)
- `data/reports/dse024_zero_clause_policy_audit_plan.md` — appended Phase B results

### Tests
- `pytest tests/test_dse020_manifest.py` — 4/4 PASSED

## Next Step
Execute DSE-024 Phase C: implement targeted heading scorer fixes.
Prioritize: (1) threshold reduction to 0.45, (2) letter-numbering patterns,
(3) reduced sentence-case penalty for bold+numbered lines.
Do not regress 20-policy gold evals.
