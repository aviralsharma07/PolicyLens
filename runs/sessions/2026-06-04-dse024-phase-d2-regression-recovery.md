# Session: DSE-024 Phase D2 Regression Recovery

Date: 2026-06-04
Task ID: DSE-024
Project: doc-structure-engine
Branch: feat/dse-024-parser-remediation
AI executor: Codex
Human reviewer: Avi

## Goal

Recover from the Phase C heading scorer regression where DSE-020 zero-clause policies worsened from 132 to 156.

The recovery scope was intentionally narrow:
- remove harmful Phase C penalties,
- keep safe heading-pattern improvements,
- rebuild DSE-020 heading and section outputs,
- regenerate triage,
- verify gold heading/section evals honestly,
- do not lower thresholds,
- do not rerun SQLite/export,
- do not touch raw PDFs or Product B.

## Relevant Docs Read

- `AGENTS.md`
- `docs/tasks.md`
- `docs/changelog.md`
- `docs/risk_register.md`
- `data/reports/dse024_phase_d1_zero_clause_revalidation.json`
- `data/reports/dse024_zero_clause_classification_v1.json`
- `data/reports/dse020_scale_triage_report_v1.json`

## Files Changed

- `structure_parser/heading_scorer.py`
- `tests/test_heading_scorer.py`
- `data/reports/dse020_scale_triage_report_v1.json`
- `data/reports/dse020_scale_triage_report_v1.md`
- `data/reports/dse024_phase_d2_regression_recovery.json`
- `data/reports/dse024_phase_d2_regression_recovery.md`
- `data/interim/dse020/logical/*/heading_candidates.json`
- `data/interim/dse020/logical/*/section_tree.json`
- `data/interim/dse020/logical/heading_run_summary.json`
- `data/interim/dse020/logical/section_tree_run_summary.json`
- `runs/evals/2026-06-04-heading-scorer-dse024-phase-d2.json`
- `runs/evals/2026-06-04-section-tree-dse024-phase-d2.json`
- `docs/tasks.md`
- `docs/changelog.md`
- `docs/risk_register.md`

## Commands Run

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/test_heading_scorer.py tests/test_dse020_manifest.py --tb=short

PYTHONPATH=. .venv/bin/python scripts/run_heading_scorer.py \
  --physical-root data/interim/dse020/physical \
  --output-root data/interim/dse020/logical \
  --threshold 0.5

PYTHONPATH=. .venv/bin/python scripts/run_section_tree.py \
  --heading-root data/interim/dse020/logical \
  --physical-root data/interim/dse020/physical \
  --output-root data/interim/dse020/logical

PYTHONPATH=. .venv/bin/python scripts/dse020_triage_report.py \
  --manifest data/manifests/dse020_run_manifest_v1.json \
  --progress-summary data/interim/dse020/progress/summary.json \
  --output-root data/interim/dse020 \
  --db data/engine_dse020.sqlite \
  --export-root data/export/dse020 \
  --json-output data/reports/dse020_scale_triage_report_v1.json \
  --md-output data/reports/dse020_scale_triage_report_v1.md \
  --date 2026-06-04

PYTHONPATH=. .venv/bin/python scripts/eval_heading_scorer.py \
  --candidates-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-04-heading-scorer-dse024-phase-d2.json

PYTHONPATH=. .venv/bin/python scripts/eval_section_tree.py \
  --output-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-04-section-tree-dse024-phase-d2.json

git diff --check
```

## Results

| Metric | Result |
|---|---:|
| Original DSE-020 zero-clause baseline | 132 |
| Phase D1 regressed zero-clause count | 156 |
| Phase D2 recovered zero-clause count | 122 |
| Delta vs baseline | -10 |
| Delta vs D1 | -34 |
| New zero-clause regressions vs baseline | 0 |
| Gold heading eval | 20/20 PASS |
| Gold section tree eval | 19/20 FAIL |
| Focused pytest | 41/41 PASS |

The section tree eval failure is the known pre-existing `oriental_cancer_protect` tree-accuracy failure and was recorded honestly.

## Generated Artifacts

- `data/reports/dse024_phase_d2_regression_recovery.json`
- `data/reports/dse024_phase_d2_regression_recovery.md`
- `runs/evals/2026-06-04-heading-scorer-dse024-phase-d2.json`
- `runs/evals/2026-06-04-section-tree-dse024-phase-d2.json`
- Regenerated `data/reports/dse020_scale_triage_report_v1.json`
- Regenerated `data/reports/dse020_scale_triage_report_v1.md`

## Decisions Made

- Restored `has_toc_dots` to the earlier non-harmful positive behavior.
- Removed `short_all_caps_numbered` and `has_tab_char` penalties because they caused broad full-corpus regressions.
- Retained letter-numbered heading support and reduced sentence-case penalty for bold numbered headings.
- Stopped global threshold/weight tuning for DSE-024 after D2; next remediation should be a fallback heading promotion layer with explicit false-positive controls.

## Issues / Limitations

- 122 policies still have zero headings and zero clauses.
- `oriental_cancer_protect` remains a pre-existing section-tree eval failure at 83.33% tree accuracy.
- D2 did not rerun SQLite/export by design.

## Next Step

Implement the next DSE-024 packet as a fallback heading promotion layer for low-confidence but structurally plausible headings. The layer should be conservative, source-auditable, and evaluated against both the 20-policy gold corpus and DSE-020 zero-clause set.
