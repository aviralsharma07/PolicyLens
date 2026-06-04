# Session: DSE-024 Phase E3B Recovery + Heading-Miss Inspection

Date: 2026-06-04
Task ID: DSE-024
Project: doc-structure-engine
Branch: feat/dse-020-full-corpus-scale-triage
AI executor: Codex
Human reviewer: Avi

## Goal

Recover from a failed E3B parser attempt, restore the clean E3A/E2 baseline, and inspect the 33 residual `heading_miss` policies before making any further scorer changes.

## Relevant Docs Read
- `AGENTS.md`
- `docs/tasks.md`
- `data/reports/dse024_residual58_classification_v1.md`
- Current git diff and DSE-020 triage artifacts

## Files Changed
- `data/reports/dse020_scale_triage_report_v1.json`
- `data/reports/dse024_heading_miss_safe_candidates_v1.json`
- `data/reports/dse024_heading_miss_safe_candidates_v1.md`
- `runs/evals/2026-06-04-heading-scorer-dse024-e3b-recovery-baseline.json`
- `docs/changelog.md`
- `docs/tasks.md`
- `runs/sessions/2026-06-04-dse024-phase-e3b-heading-miss-inspection.md`

## Commands Run

```bash
git restore structure_parser/heading_patterns.py structure_parser/heading_scorer.py tests/test_heading_scorer.py
rm -rf data/reports/reports data/reports/eval_dse024_phase_e3b_heading.json

PYTHONPATH=. .venv/bin/python scripts/eval_heading_scorer.py \
  --candidates-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-04-heading-scorer-dse024-e3b-recovery-baseline.json

PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short

PYTHONPATH=. .venv/bin/python scripts/run_heading_scorer.py \
  --physical-root data/interim/physical \
  --output-root data/interim/logical \
  --threshold 0.5

PYTHONPATH=. .venv/bin/python scripts/eval_heading_scorer.py \
  --candidates-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-04-heading-scorer-dse024-e3b-recovery-baseline.json

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
```

## Results

- Failed E3B scorer/test edits were removed and are not part of this packet.
- Failed stray report artifacts were removed.
- DSE-020 heading candidates, section trees, and triage were regenerated from the restored scorer state.
- DSE-020 triage returned to **58 zero-heading / 58 zero-clause policies**.
- All 33 residual `heading_miss` policies were audited:
  - `safe_pattern_fix`: 27
  - `false_top_candidate`: 6

## Generated Artifacts
- `data/reports/dse024_heading_miss_safe_candidates_v1.json`
- `data/reports/dse024_heading_miss_safe_candidates_v1.md`
- `runs/evals/2026-06-04-heading-scorer-dse024-e3b-recovery-baseline.json`

## Decisions Made
- The failed broad E3B attempt is abandoned.
- Top candidates are not assumed to be headings. Percentage rows, table fragments, procedure/item rows, bare numbers, and generic document titles are rejected unless later evidence proves otherwise.
- E3C should implement only narrow, inspection-backed parser fixes.

## Issues / Limitations
- Regenerating the 20-policy gold heading candidates from the restored scorer produced **17/20 PASS**, not the previously reported 20/20. Failing policies are `aditya_birla_activ_care`, `care_health_care_plus`, and `tata_aig_arogya_sanjeevani`.
- This means the prior 20/20 heading eval was artifact-dependent and not currently reproducible from regenerated artifacts.
- No parser behavior change was implemented in this packet.

## Next Step

Run a narrow E3C packet only after accepting this audit. E3C must first handle the gold heading reproducibility gap, then implement only safe patterns from `data/reports/dse024_heading_miss_safe_candidates_v1.md` with full gold and DSE-020 triage validation.
