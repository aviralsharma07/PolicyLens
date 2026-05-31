# Session: Table Engine v1 Remediation

Date: 2026-05-31
Task ID: DSE-009
Project: doc-structure-engine
Branch: fix/dse-009-table-engine-gates
AI executor: Codex GPT-5
Human reviewer: Avi

## Goal

Review and remediate DSE-009 so the table engine, eval, docs, and acceptance status are honest and aligned with AGENTS.md table rules.

## Relevant Docs Read

- AGENTS.md
- docs/tasks.md
- docs/evaluation.md
- docs/data_contracts.md
- docs/decisions.md
- docs/changelog.md
- runs/sessions/2026-05-31-table-engine-v1.md

## Files Changed

- table_engine/cell_extractor.py
- table_engine/models.py
- table_engine/table_detector.py
- table_engine/text_alignment_detector.py
- scripts/run_table_engine.py
- scripts/eval_table_engine.py
- tests/test_table_engine.py
- docs/tasks.md
- docs/evaluation.md
- docs/data_contracts.md
- docs/decisions.md
- docs/changelog.md
- runs/sessions/2026-05-31-table-engine-remediation.md

## Commands Run

```bash
git checkout -b fix/dse-009-table-engine-gates
PYTHONPATH=. .venv/bin/python -m pytest tests/test_table_engine.py -v -m "not slow" --tb=short
PYTHONPATH=. .venv/bin/python scripts/run_table_engine.py --gold-corpus gold_corpus --policy-data-root ../policy_data --physical-root data/interim/physical --section-root data/interim/logical --output-root data/interim/tables --pipeline-run-id table_v1_remediation_2026_05_31
PYTHONPATH=. .venv/bin/python scripts/eval_table_engine.py --gold-corpus gold_corpus --tables-root data/interim/tables --output runs/evals/2026-05-31-table-engine-dse009-v2.json
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
git status --short
```

## Results

- Focused non-slow DSE-009 tests passed: 49/49.
- Full pytest suite passed: 164/164.
- Gold corpus validator passed.
- `git diff --check` passed.
- Table extraction processed 5/5 gold policies.
- Strict DSE-009 v2 eval failed:
  - Priority content detection recall: 57.1% vs 85% gate.
  - Header lineage pass rate: 20% vs 85% gate.
  - Page-region recall: 92.3% diagnostic only.
  - Type accuracy on strict content-detected tables: 81.25%.

## Generated Artifacts

- data/interim/tables/*/document_tables.json
- data/interim/tables/*/document_table_cells.json
- data/interim/tables/table_run_summary.json
- runs/evals/2026-05-31-table-engine-dse009-v2.json
- data/reports/dse009_table_bbox_review_candidates.json
- data/reports/dse009_header_lineage_review.json
- data/reports/dse009_gold_table_annotation_audit.json

## Decisions Made

- Strict table detection must require type/content signature matching; same-page table presence is diagnostic only.
- DSE-009 remains in_progress because strict gates fail.

## Issues / Limitations

- Some gold `tables.json` entries are manual summaries over prose/definition sections rather than physical tables with headers/cells.
- Borderless candidates preserve raw physical lines, but do not fabricate cells when column splitting is unreliable.
- Gold table bboxes are still null and require manual review before bbox accuracy can be gated.
- Parent clause IDs remain provisional until DSE-010 source-span/bbox overlap.

## Next Step

Superseded by `runs/sessions/2026-05-31-table-engine-finalization.md`, which added physical table labels and passed the v3 physical-table gate.
