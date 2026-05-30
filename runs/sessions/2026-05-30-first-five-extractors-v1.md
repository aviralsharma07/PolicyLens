# Session: First Five Deterministic Extractors

Date: 2026-05-30
Task ID: DSE-007
Project: doc-structure-engine
Branch: feat/dse-007-first-extractors-v1
AI executor: Codex GPT-5
Human reviewer: Avi

## Goal

Implement the first deterministic fact extraction layer for five concepts over the 5-policy gold corpus:

- `free_look_period`
- `grace_period`
- `ped_waiting_period`
- `initial_waiting_period`
- `co_pay`

## Relevant Docs Read

- `/Users/aviralsharma/Personal Projects/AGENTS.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/evaluation.md`
- `docs/data_contracts.md`
- `docs/tasks.md`
- `docs/adr/0005-candidate-first-extraction.md`
- `docs/adr/0007-precision-over-recall.md`
- `runs/sessions/2026-05-30-section-tree-builder-v1.md`
- `gold_corpus/policies/*/facts.json`
- `data/interim/logical/*/section_tree.json`

## Files Changed

- `normalizers/__init__.py`
- `normalizers/duration.py`
- `normalizers/percentage.py`
- `extractors/__init__.py`
- `extractors/base.py`
- `extractors/deterministic.py`
- `extractors/evidence.py`
- `extractors/models.py`
- `extractors/registry.py`
- `scripts/run_fact_extractors.py`
- `scripts/eval_fact_extractors.py`
- `tests/test_fact_extractors.py`
- `gold_corpus/policies/care_health_care_plus/facts.json`
- `docs/adr/0013-provisional-clause-evidence-for-dse007.md`
- `docs/changelog.md`
- `docs/data_contracts.md`
- `docs/decisions.md`
- `docs/evaluation.md`
- `docs/tasks.md`
- `runs/evals/2026-05-30-fact-extraction-dse007-v1.json`
- `runs/sessions/2026-05-30-first-five-extractors-v1.md`

## Commands Run

```bash
git checkout -b feat/dse-007-first-extractors-v1
PYTHONPATH=. python3 -m pytest tests/test_fact_extractors.py --tb=short
PYTHONPATH=. .venv/bin/python -m pytest tests/test_fact_extractors.py --tb=short
PYTHONPATH=. .venv/bin/python scripts/run_fact_extractors.py --section-root data/interim/logical --output-root data/interim/facts
PYTHONPATH=. .venv/bin/python scripts/eval_fact_extractors.py --facts-root data/interim/facts --gold-corpus gold_corpus --section-root data/interim/logical --output runs/evals/2026-05-30-fact-extraction-dse007-v1.json
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
```

## Results

- `python3 -m pytest` failed outside the project virtualenv because system Python did not have `pytest`.
- `.venv/bin/python -m pytest tests/test_fact_extractors.py --tb=short` passed after fixing Python 3.9 typing compatibility and percentage parsing.
- Fact extraction processed 5/5 policies.
- Initial DSE-007 eval failed because Care Health gold `ped_waiting_period` said 48 months while its evidence text said 36 months.
- Corrected the Care Health gold normalized value to 36 months with an explicit quality pass note.
- Final DSE-007 eval passed:
  - 5/5 policies passed
  - 25/25 target concepts attempted
  - deterministic present precision: 100%
  - present recall: 100%
  - normalized value accuracy: 100%
  - status accuracy: 100%
  - evidence accuracy: 100%
  - false present for gold `not_found`: 0

## Generated Artifacts

- `data/interim/facts/hdfc_arogya_sanjeevani/fact_candidates.json`
- `data/interim/facts/hdfc_arogya_sanjeevani/accepted_facts.json`
- `data/interim/facts/new_india_floater/fact_candidates.json`
- `data/interim/facts/new_india_floater/accepted_facts.json`
- `data/interim/facts/care_health_care_plus/fact_candidates.json`
- `data/interim/facts/care_health_care_plus/accepted_facts.json`
- `data/interim/facts/star_medi_classic_accident/fact_candidates.json`
- `data/interim/facts/star_medi_classic_accident/accepted_facts.json`
- `data/interim/facts/icici_family_shield/fact_candidates.json`
- `data/interim/facts/icici_family_shield/accepted_facts.json`
- `data/interim/facts/fact_extraction_run_summary.json`
- `runs/evals/2026-05-30-fact-extraction-dse007-v1.json`

## Decisions Made

- Use provisional `clause:{clause_id}` evidence span IDs until DSE-010 creates true source spans.
- Enrich clause extraction text with the owning section heading for DSE-007 because some fact-bearing values live in DSE-006 section titles.
- Correct Care Health PED gold normalized value from 48 months to 36 months because the evidence text itself says 36 months.

## Issues / Limitations

- Evidence spans are clause-level, not exact bbox/character spans, until DSE-010.
- DSE-007 includes only minimal duration and percentage normalizers required by the five extractors.
- Table extraction, SQLite clause store, source-span DB, LLM refinement, derived export, and Product B export were intentionally not touched.

## Next Step

DSE-008 should build the broader normalizer library for money, age, coverage status, limits, ranges, and policy-specific units before expanding extractors further.

