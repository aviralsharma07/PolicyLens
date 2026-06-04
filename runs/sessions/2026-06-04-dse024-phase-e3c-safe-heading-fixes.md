# Session: DSE-024 Phase E3C Safe Heading Fixes

Date: 2026-06-04
Task ID: DSE-024
Project: doc-structure-engine
Branch: feat/dse-020-full-corpus-scale-triage
AI executor: Codex
Human reviewer: Avi

## Goal

Implement only E3B-backed safe heading fixes, reconcile the regenerated 20-policy heading eval result honestly, and rerun full-corpus parser triage without lowering global heading thresholds.

## Relevant Docs Read

- AGENTS.md
- docs/tasks.md
- docs/changelog.md
- data/reports/dse024_heading_miss_safe_candidates_v1.md
- data/reports/dse024_gold_heading_reproducibility_audit_v1.md
- data/reports/dse020_scale_triage_report_v1.md

## Files Changed

- structure_parser/heading_patterns.py
- structure_parser/heading_scorer.py
- tests/test_heading_scorer.py
- data/reports/dse020_scale_triage_report_v1.json
- data/reports/dse020_scale_triage_report_v1.md
- data/reports/dse024_phase_e3c_safe_heading_fixes.md
- runs/evals/2026-06-04-heading-scorer-dse024-e3c-safe-fixes.json
- runs/evals/2026-06-04-section-tree-dse024-e3c-safe-fixes.json
- runs/sessions/2026-06-04-dse024-phase-e3c1-gold-heading-repro.md
- runs/sessions/2026-06-04-dse024-phase-e3c-safe-heading-fixes.md

## Commands Run

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/test_heading_scorer.py --tb=short
PYTHONPATH=. .venv/bin/python -m pytest tests/test_heading_scorer.py tests/test_dse020_manifest.py --tb=short -q
PYTHONPATH=. .venv/bin/python scripts/run_heading_scorer.py --physical-root data/interim/physical --output-root data/interim/logical --threshold 0.5
PYTHONPATH=. .venv/bin/python scripts/eval_heading_scorer.py --candidates-root data/interim/logical --gold-corpus gold_corpus --output runs/evals/2026-06-04-heading-scorer-dse024-e3c-safe-fixes.json
PYTHONPATH=. .venv/bin/python scripts/eval_section_tree.py --output-root data/interim/logical --gold-corpus gold_corpus --output runs/evals/2026-06-04-section-tree-dse024-e3c-safe-fixes.json
PYTHONPATH=. .venv/bin/python scripts/run_heading_scorer.py --physical-root data/interim/dse020/physical --output-root data/interim/dse020/logical --threshold 0.5
PYTHONPATH=. .venv/bin/python scripts/run_section_tree.py --heading-root data/interim/dse020/logical --physical-root data/interim/dse020/physical --output-root data/interim/dse020/logical
PYTHONPATH=. .venv/bin/python scripts/dse020_triage_report.py --manifest data/manifests/dse020_run_manifest_v1.json --progress-summary data/interim/dse020/progress/summary.json --output-root data/interim/dse020 --db data/engine_dse020.sqlite --export-root data/export/dse020 --json-output data/reports/dse020_scale_triage_report_v1.json --md-output data/reports/dse020_scale_triage_report_v1.md --date 2026-06-04
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
```

## Results

- Focused heading tests passed.
- Full-corpus heading scorer completed for 647 policies.
- Full-corpus section tree completed for 647 policies.
- DSE-020 triage regenerated.
- Zero-heading policies: 58 → 1.
- Zero-clause policies: 58 → 1.
- Remaining zero-clause policy: `23_raheja_qbe_raheja_qbe_product_list`.
- Gold heading eval: 17/20 PASS, documented as a real reproducibility/eval-label issue.
- Gold section tree eval: 19/20 PASS, with only pre-existing `oriental_cancer_protect` failure.
- Gold corpus validation passed.
- Full pytest passed: 404/404.
- `git diff --check` passed.

## Generated Artifacts

- data/reports/dse024_phase_e3c_safe_heading_fixes.md
- runs/evals/2026-06-04-heading-scorer-dse024-e3c-safe-fixes.json
- runs/evals/2026-06-04-section-tree-dse024-e3c-safe-fixes.json
- data/reports/dse020_scale_triage_report_v1.json
- data/reports/dse020_scale_triage_report_v1.md

## Decisions Made

- New structural heading signals remain fallback-only and have zero global heading score weight.
- Do not lower global threshold.
- Do not continue broad heading-score tuning after zero-clause dropped to 1.
- Treat `Raheja_QBE_Product_List.pdf` as a corpus/identity filtering follow-up, not a parser-scoring target.

## Issues / Limitations

- Gold heading eval is 17/20 after regenerated artifacts; earlier 20/20 artifacts are not reproducible and should not be cited as current.
- `care_health_care_plus` appears to need heading-label maintenance because all existing labels match but compact visual subheads are counted as false positives.
- `tata_aig_arogya_sanjeevani` still has heading-label precision issues from fallback-promoted definition entries, though section-tree quality passes.
- DSE-020 DB/export was not rerun; this packet only changed parser artifacts and triage.

## Next Step

Close DSE-024 with a small corpus-filter packet for the single remaining `Raheja_QBE_Product_List.pdf`, then unblock DSE-021 extractor Wave 2.
