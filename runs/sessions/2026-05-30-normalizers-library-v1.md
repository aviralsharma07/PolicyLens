# Session: Normalizers Library v1

Date: 2026-05-30
Task ID: DSE-008
Project: doc-structure-engine
Branch: feat/dse-008-normalizers-v1
AI executor: Codex GPT-5
Human reviewer: Avi

## Goal

Expand the minimal DSE-007 duration and percentage helpers into a reusable normalizer library for future deterministic extractors.

## Relevant Docs Read

- `/Users/aviralsharma/Personal Projects/AGENTS.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/evaluation.md`
- `docs/data_contracts.md`
- `docs/tasks.md`
- `runs/sessions/2026-05-30-first-five-extractors-v1.md`
- `runs/evals/2026-05-30-fact-extraction-dse007-v1.json`
- `normalizers/`
- `extractors/deterministic.py`
- `tests/test_fact_extractors.py`

## Files Changed

- `normalizers/__init__.py`
- `normalizers/age.py`
- `normalizers/coverage_status.py`
- `normalizers/duration.py`
- `normalizers/indian_number_words.py`
- `normalizers/money.py`
- `normalizers/percentage.py`
- `scripts/eval_normalizers.py`
- `tests/test_normalizers/test_normalizers.py`
- `docs/changelog.md`
- `docs/data_contracts.md`
- `docs/evaluation.md`
- `docs/tasks.md`
- `runs/evals/2026-05-30-normalizers-dse008-v1.json`
- `runs/evals/2026-05-30-fact-extraction-dse007-regression-after-dse008.json`
- `runs/sessions/2026-05-30-normalizers-library-v1.md`

## Commands Run

```bash
git checkout -b feat/dse-008-normalizers-v1
PYTHONPATH=. .venv/bin/python -m pytest tests/test_normalizers/ -v --tb=short
PYTHONPATH=. .venv/bin/python scripts/eval_normalizers.py --output runs/evals/2026-05-30-normalizers-dse008-v1.json
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
PYTHONPATH=. .venv/bin/python scripts/run_fact_extractors.py --section-root data/interim/logical --output-root data/interim/facts
PYTHONPATH=. .venv/bin/python scripts/eval_fact_extractors.py --facts-root data/interim/facts --gold-corpus gold_corpus --section-root data/interim/logical --output runs/evals/2026-05-30-fact-extraction-dse007-regression-after-dse008.json
```

## Results

- Normalizer eval passed: 35/35 fixed vectors, 100% pass rate.
- Normalizer tests passed: 7/7.
- Full pytest suite passed: 110/110.
- Gold corpus validator passed.
- DSE-007 fact extraction regression passed with no metric regression:
  - deterministic present precision: 100%
  - present recall: 100%
  - normalized value accuracy: 100%
  - status accuracy: 100%
  - evidence accuracy: 100%
  - false present for gold `not_found`: 0

## Generated Artifacts

- `runs/evals/2026-05-30-normalizers-dse008-v1.json`
- `runs/evals/2026-05-30-fact-extraction-dse007-regression-after-dse008.json`

## Decisions Made

- Use a shared normalizer result shape with `value`, `normalized`, `span`, and `text`.
- Preserve DSE-007 duration and percentage function names for extractor compatibility.
- Emit special money values as symbolic normalized statuses, not as `0` or `null`.
- Give coverage negations precedence over positive coverage words.

## Issues / Limitations

- DSE-008 implements normalizers only.
- No new fact extractors, table engine, SQLite/source-span store, LLM refinement, derived export, or Product B integration was added.
- Money special values require future extractors/export code to decide display semantics.

## Next Step

DSE-009 Table Engine v1 is the next planned task in `docs/tasks.md`.

