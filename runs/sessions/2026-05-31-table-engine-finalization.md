# Session: Table Engine v1 Finalization

Date: 2026-05-31
Task ID: DSE-009
Project: doc-structure-engine
Branch: fix/dse-009-table-engine-gates
AI executor: Codex GPT-5
Human reviewer: Avi

## Goal

Complete DSE-009 by splitting physical table labels from semantic/prose table summaries, improving the table engine, and passing strict physical table gates.

## Relevant Docs Read

- AGENTS.md
- IMPLEMENTATION_PLAN.md
- docs/tasks.md
- docs/evaluation.md
- docs/data_contracts.md
- docs/decisions.md
- docs/changelog.md
- runs/evals/2026-05-31-table-engine-dse009-v2.json
- data/reports/dse009_gold_table_annotation_audit.json

## Files Changed

- gold_corpus/policies/*/physical_table_labels.json
- table_engine/models.py
- table_engine/cell_extractor.py
- table_engine/table_detector.py
- table_engine/table_type_classifier.py
- scripts/run_table_engine.py
- scripts/eval_table_engine.py
- scripts/validate_gold_corpus.py
- tests/test_table_engine.py
- docs/tasks.md
- docs/evaluation.md
- docs/data_contracts.md
- docs/decisions.md
- docs/changelog.md

## Commands Run

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/test_table_engine.py -v -m "not slow" --tb=short
PYTHONPATH=. .venv/bin/python scripts/run_table_engine.py --gold-corpus gold_corpus --policy-data-root ../policy_data --physical-root data/interim/physical --section-root data/interim/logical --output-root data/interim/tables --pipeline-run-id table_v1_final_2026_05_31
PYTHONPATH=. .venv/bin/python scripts/eval_table_engine.py --gold-corpus gold_corpus --tables-root data/interim/tables --output runs/evals/2026-05-31-table-engine-dse009-v3.json
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
```

## Results

- 5/5 gold policies processed by table engine.
- 18/18 physical table labels detected.
- Priority physical table detection recall: 100%.
- Header lineage pass rate: 100%.
- Type accuracy on matched physical labels: 94.44%.
- Unrecorded missing cell bboxes: 0.
- Focused non-slow DSE-009 tests passed: 57/57.
- Full pytest suite passed: 172/172.
- Gold corpus validator passed with 35 policy JSON files and 18 physical table labels.
- `git diff --check` passed.

## Generated Artifacts

- runs/evals/2026-05-31-table-engine-dse009-v3.json
- data/reports/dse009_gold_table_source_review.json
- data/reports/dse009_gold_table_source_review.md
- data/reports/dse009_table_bbox_review_candidates.json
- data/reports/dse009_header_lineage_review.json
- data/reports/dse009_gold_table_annotation_audit.json

## Decisions Made

- DSE-009 hard gates evaluate `physical_table_labels.json`; DSE-003 `tables.json` remains semantic/manual annotation history.
- Conservative `pdfplumber_text` extraction is available but retained only for small headered grids.
- Prose-derived table summaries should be handled by clause/fact extraction, not by fake physical table cells.

## Issues / Limitations

- Parent clause assignment remains provisional until DSE-010 bbox/source-span overlap.
- DSE-012 should expand physical table labels beyond the initial 5-policy gold set.
- Legacy DSE-003 semantic table labels remain useful but are not physical table parser labels.

## Next Step

DSE-010 — Clause Store + Source Spans can proceed after review/merge of DSE-009.
