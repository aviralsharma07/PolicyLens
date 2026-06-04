# DSE-024 Phase D1: Zero-Clause Revalidation Report

**Date:** 2026-06-04
**Threshold:** 0.5 (unchanged)
**Gold policies:** 20
**Full corpus:** 647

## Summary

Phase C heading scorer feature changes at threshold 0.5 **do not reduce** zero-clause count. Zero-clause policies **increased** from 132 to 156 (+24).

## Key Numbers

| Metric | Pre-Phase-C | Post-Phase-C | Delta |
|--------|-------------|--------------|-------|
| Zero-heading policies | 132 | 156 | +24 |
| Zero-clause policies | 132 | 156 | +24 |
| Zero-fact-candidate policies | 133 | 133 | 0 |
| Gold heading eval | 20/20 PASS | 20/20 PASS | 0 |
| Gold section tree eval | 19/20 FAIL | 19/20 FAIL | 0 |
| Total headings (all 647) | TBD | TBD | TBD |

## Regressed Policies (24)

**By Insurer:**
- Star Health: 15 (62.5%)
- United India: 2
- Bajaj Allianz: 2
- IFFCO Tokio: 2
- Niva Bupa: 1
- HDFC ERGO: 1
- Raheja QBE: 1

**Profile:** 24 policies that previously had 1-2 marginal headings (score 0.48-0.50) now score below 0.5. Typical examples:
- `"5. Cancellation:"` → score 0.4948
- `"FAMILY ACCIDENT CARE INSURANCE POLICY"` → score 0.4844
- `"2. Claim Procedure:"` → score 0.4821

## Why Phase C Changes Didn't Help

**Stricter changes (more impactful at t=0.5):**
1. **TOC dot penalty:** +0.10 → -0.30 (net -0.40). Marginal numbered items with dots lose 0.40.
2. **Tab character penalty:** -0.30. Lines with tab indentation lose 0.30.
3. **Short all-caps penalty:** -0.25. Short all-caps lines lose additional 0.25.

**Permissive changes (didn't affect zero-heading policies):**
4. **Letter-numbering pattern (+0.30):** Requires `^[A-Z]\.\s` prefix — none of the 132 zero-heading policies use this format.
5. **Reduced sentence-case penalty (-0.10):** Requires bold+numbered+sentence-case combo — rare in zero-heading policies.

**Net effect:** Stricter penalties outweigh permissive additions for non-gold policies. Gold policies unaffected (20/20 PASS).

## Gold Eval Results

### Heading Scorer: 20/20 PASS
- Precision: 99.7%, Recall: 96.3%, F1: 98.0
- FP: 1, FN: 12
- No regression vs pre-Phase-C baseline.

### Section Tree: 19/20 FAIL (pre-existing)
- Only `oriental_cancer_protect` fails (TreeAcc=83.33%, SectionF1=100.0%, ClauseF1=100.0%)
- Pre-existing failure confirmed: identical TreeAcc across Jun 1, Jun 2, Jun 4 baselines.

## Triage Report (Regenerated)

- Per-stage: 647/647 OK (all 5 stages)
- Zero clauses: 156 (was 132)
- Zero fact candidates: 133 (unchanged)
- DB/Export: unchanged (566 exported)

## Acceptance Criteria Status

| Criterion | Status | Note |
|-----------|--------|------|
| Zero-clause reduction | FAIL | Increased by 24 (132 → 156) |
| Gold heading no regression | PASS | 20/20, same metrics |
| Gold section tree no regression | PASS | 19/20, pre-existing failure identical |
| Triage report regenerated | PASS | Updated with section tree rerun |
| Full pytest | PENDING | |

## Path Forward

Three options:

1. **Phase D2: Format-specific heading additions** — Add heading detectors tailored to top-zero-heading insurer formats (Star Health, HDFC ERGO, Aditya Birla). Risk: may add FPs.

2. **Phase E: Threshold lowering with FP suppression** — Lower threshold to 0.45 with classifier-based TOC/list-item filtering. Threshold experiment shows 56/132 gain ≥1 heading but FP ratio is 44.4%. Requires building FP suppression infra.

3. **Close DSE-024, move to DSE-021** — Accept that zero-clause reduction at t=0.5 is not achievable with current heading scorer architecture. Begin extractor Wave 2 on the 515 non-zero-clause policies.
