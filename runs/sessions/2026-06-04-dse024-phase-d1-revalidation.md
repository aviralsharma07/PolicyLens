# Session: DSE-024 Phase D1 — Zero-Clause Revalidation

Date: 2026-06-04
Task ID: DSE-024
Project: doc-structure-engine
Branch: feat/dse-024-parser-remediation
AI executor: opencode + deepseek-v4-flash-free
Human reviewer: Avi

## Goal

Revalidate DSE-020 parser outputs after Phase C heading scorer feature fixes at threshold 0.5. Measure actual zero-clause reduction. Do not lower threshold.

## Steps Executed

1. **Read context**: AGENTS.md, tasks.md, threshold experiment v3 report, zero-clause classification, Phase C cleanup session log, relevant scripts.
2. **Skip heading scorer re-run**: Already executed during Phase C (Jun 4 06:49, 647 policies at t=0.5).
3. **Re-run section tree** (647 policies): `scripts/run_section_tree.py` — completed, 647/647 OK.
4. **Gold heading eval** (20 gold policies): 20/20 PASS — no regression.
5. **Gold section tree eval** (20 gold policies): 19/20 FAIL — only `oriental_cancer_protect` (pre-existing, TreeAcc=83.33%).
6. **Regenerate DSE-020 triage report**: `scripts/dse020_triage_report.py` — zero-clause now 156 (up from 132).
7. **Produce D1 report**: `data/reports/dse024_phase_d1_zero_clause_revalidation.json` + `.md`.
8. **Run pytest**: 37/37 PASS (heading scorer + manifest).
9. **git diff --check**: clean.
10. **Update docs**: changelog.md, tasks.md, session log.

## Key Findings

### Zero-Clause Count: 132 → 156 (+24 regression)

Phase C heading scorer changes, at threshold 0.5, **increased** the zero-clause count.

| Metric | Pre-Phase-C | Post-Phase-C |
|--------|-------------|--------------|
| Zero-heading policies | 132 | 156 |
| Zero-clause policies | 132 | 156 |
| Zero-fact-candidate policies | 133 | 133 |

### Why the Increase

Phase C introduced three stricter penalties that outweighed the two permissive additions:

**Stricter penalties (net stricter by ~0.40-0.30):**
- TOC dots: +0.10 → -0.30 (net -0.40)
- Tab character: -0.30 (new)
- Short all-caps numbered: -0.25 (new)

**Permissive additions (didn't help zero-heading policies):**
- Letter-numbering pattern (+0.30): requires `A.` prefix — absent from zero-heading PDFs
- Reduced sentence-case penalty (-0.10): requires bold+numbered+title-case — rare in zero-heading policies

24 policies that previously had 1-2 marginal headings (score 0.48-0.50) lost all headings. 15/24 are Star Health.

### Insurer Breakdown (24 Regressed)

| Insurer | Count | Typical Pattern |
|---------|-------|----------------|
| Star Health | 15 | "5. Cancellation:" (0.495), "FAMILY ACCIDENT CARE..." (0.484) |
| United India | 2 | Marginal medico-legal headings |
| Bajaj Allianz | 2 | Marginal numbered items |
| IFFCO Tokio | 2 | Marginal numbered items |
| Niva Bupa | 1 | "Health Premia" prospectus |
| HDFC ERGO | 1 | "Energy" product marginal headings |
| Raheja QBE | 1 | Super top-up marginal headings |

### Gold Eval (No Regression)

- **Heading scorer: 20/20 PASS** — P=99.7%, R=96.3%, F1=98.0, FP=1, FN=12
- **Section tree: 19/20 FAIL** — `oriental_cancer_protect` TreeAcc=83.33% (pre-existing, unchanged)

## Files Changed

- `data/interim/dse020/logical/*/section_tree.json` — 647 regenerated section trees
- `data/interim/dse020/logical/section_tree_run_summary.json` — new run summary
- `data/reports/dse020_scale_triage_report_v1.json` — regenerated (zero-clause: 156)
- `data/reports/dse020_scale_triage_report_v1.md` — regenerated
- `docs/changelog.md` — D1 entry added
- `docs/tasks.md` — DSE-024 Phase D1 acceptance criteria updated

## Files Created

- `data/reports/dse024_phase_d1_zero_clause_revalidation.json` — D1 report (JSON)
- `data/reports/dse024_phase_d1_zero_clause_revalidation.md` — D1 report (Markdown)
- `runs/evals/2026-06-04-heading-scorer-dse024-phase-d1.json` — gold heading eval
- `runs/evals/2026-06-04-section-tree-dse024-phase-d1.json` — gold section tree eval

## Commands Run

```bash
# Section tree re-run
PYTHONPATH=. .venv/bin/python scripts/run_section_tree.py \
  --heading-root data/interim/dse020/logical \
  --physical-root data/interim/dse020/physical \
  --output-root data/interim/dse020/logical

# Gold heading eval
PYTHONPATH=. .venv/bin/python scripts/eval_heading_scorer.py \
  --candidates-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-04-heading-scorer-dse024-phase-d1.json

# Gold section tree eval
PYTHONPATH=. .venv/bin/python scripts/eval_section_tree.py \
  --output-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-04-section-tree-dse024-phase-d1.json

# Triage report
PYTHONPATH=. .venv/bin/python scripts/dse020_triage_report.py \
  --manifest data/manifests/dse020_run_manifest_v1.json \
  --progress-summary data/interim/dse020/progress/summary.json \
  --output-root data/interim/dse020 \
  --db data/engine_dse020.sqlite \
  --export-root data/export/dse020 \
  --json-output data/reports/dse020_scale_triage_report_v1.json \
  --md-output data/reports/dse020_scale_triage_report_v1.md

# Tests
PYTHONPATH=. .venv/bin/python -m pytest tests/test_heading_scorer.py tests/test_dse020_manifest.py --tb=short
git diff --check
```

## Results Summary

| Check | Result |
|-------|--------|
| Heading scorer re-run | Skipped (already done in Phase C) |
| Section tree re-run | 647/647 OK |
| Gold heading eval | 20/20 PASS |
| Gold section tree eval | 19/20 FAIL (pre-existing) |
| Zero-clause count | 156 (up from 132, +24) |
| Triage report | Regenerated |
| pytest | 37/37 PASS |
| git diff --check | Clean |

## Decisions Made

- **DSE-024 Phase D1 zero-clause reduction: FAILED.** Phase C heading scorer changes at threshold 0.5 increase zero-clause count. The stricter penalties that improve gold precision also kill marginal headings in non-gold policies.
- **Zero-clause reduction at t=0.5 requires format-specific heading additions**, not threshold lowering. Each top insurer (Star Health, HDFC ERGO, Aditya Birla) has distinct heading format patterns that the current scorer doesn't recognize.

## Known Limitations

- Zero-clause count at 156 is worse than original 132 baseline — Phase C introduced a net regression for this specific metric.
- Gold heading/section evals remain at pre-existing levels — no gold regression, but also no improvement.
- Section tree eval at 19/20 `oriental_cancer_protect` is a separate pre-existing issue.

## Next Recommended Step

Three paths forward:

1. **Phase D2: Format-specific heading detectors** — Investigate what heading patterns Star Health, HDFC ERGO, Aditya Birla use in their zero-heading policies (631 PDFs). Add targeted features: e.g., Star Health uses "X. Title:" with numbers, HDFC ERGO uses bold standalone numbers.

2. **Phase E: Threshold lowering (0.45) with FP filtering** — Build TOC/list-item classifier to suppress FPs. Threshold experiment shows 56/132 gain headings. FP ratio 44.4% requires classifier-based suppression.

3. **Close DSE-024, begin DSE-021** — Accept 156 zero-clause as current baseline. Begin extractor Wave 2 on 515 non-zero-clause policies. Revisit zero-clause after extractor work creates more context.
