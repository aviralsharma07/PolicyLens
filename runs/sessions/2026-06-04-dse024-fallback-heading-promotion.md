# Session: DSE-024 Fallback Heading Promotion Layer

Date: 2026-06-04
Task ID: DSE-024
Project: doc-structure-engine
Branch: feat/dse-020-full-corpus-scale-triage
AI executor: Codex
Human reviewer: Avi

## Goal

Reduce the remaining DSE-024 zero-heading/zero-clause policies after D2 recovery by adding a conservative fallback heading promotion layer.

The fallback must:
- activate only when normal heading scoring finds zero headings,
- avoid global threshold lowering,
- carry audit metadata,
- preserve 20-policy gold heading eval quality,
- avoid Product B, DB/export, extractor, or raw PDF changes.

## Relevant Docs Read

- `AGENTS.md`
- `docs/tasks.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/data_contracts.md`
- `docs/decisions.md`
- `data/reports/dse024_phase_d2_regression_recovery.json`
- `data/reports/dse020_scale_triage_report_v1.json`

## Files Changed

- `structure_parser/heading_scorer.py`
- `tests/test_heading_scorer.py`
- `docs/data_contracts.md`
- `docs/decisions.md`
- `docs/changelog.md`
- `docs/risk_register.md`
- `docs/tasks.md`
- `IMPLEMENTATION_PLAN.md`
- `data/reports/dse020_scale_triage_report_v1.json`
- `data/reports/dse020_scale_triage_report_v1.md`
- `data/reports/dse024_fallback_heading_promotion_report.json`
- `data/reports/dse024_fallback_heading_promotion_report.md`
- `runs/evals/2026-06-04-heading-scorer-dse024-fallback.json`
- `runs/evals/2026-06-04-section-tree-dse024-fallback.json`

## Commands Run

```bash
git add structure_parser tests docs data/reports runs/evals runs/sessions scripts IMPLEMENTATION_PLAN.md
git commit -m "fix(parser): recover DSE-024 heading regression"

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
  --output runs/evals/2026-06-04-heading-scorer-dse024-fallback.json

PYTHONPATH=. .venv/bin/python scripts/eval_section_tree.py \
  --output-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-04-section-tree-dse024-fallback.json

PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
```

## Results

| Metric | Result |
|---|---:|
| D2 zero-clause count | 122 |
| Fallback zero-clause count | 110 |
| Improvement vs D2 | 12 |
| New zero-clause regressions vs D2 | 0 |
| D2 zero-heading count | 122 |
| Fallback zero-heading count | 84 |
| Policies with fallback promotions | 52 |
| Total promoted headings | 207 |
| Gold heading eval | 20/20 PASS |
| Gold section tree eval | 19/20 FAIL |
| Gold corpus validator | PASS |
| Full pytest | 400/400 PASS |
| `git diff --check` | PASS |

The section tree failure remains the known pre-existing `oriental_cancer_protect` tree-accuracy issue.

## Generated Artifacts

- `data/reports/dse024_fallback_heading_promotion_report.json`
- `data/reports/dse024_fallback_heading_promotion_report.md`
- `runs/evals/2026-06-04-heading-scorer-dse024-fallback.json`
- `runs/evals/2026-06-04-section-tree-dse024-fallback.json`
- Regenerated `data/reports/dse020_scale_triage_report_v1.json`
- Regenerated `data/reports/dse020_scale_triage_report_v1.md`

## Decisions Made

- Use zero-heading-only fallback promotion instead of lowering the global heading threshold.
- Store fallback audit fields on promoted heading candidates.
- Keep DSE-021 blocked because 110 policies still have no clauses.

## Issues / Limitations

- 110 policies still have zero headings and zero clauses.
- 133 policies still have zero fact candidates.
- No DB/export rerun was performed by design.

## Next Step

Continue DSE-024 with remaining zero-clause analysis: split the 110 into true parser misses, non-policy/unsupported documents, duplicate/corpus issues, and product-format families needing targeted rules.
