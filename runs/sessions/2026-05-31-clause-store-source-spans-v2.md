# Session: Clause Store + Source Spans v2 Remediation

Date: 2026-05-31
Task ID: DSE-010
Project: doc-structure-engine
Branch: fix/dse-010-global-sqlite-ids
AI executor: Codex
Human reviewer: Avi

## Goal

Fix DSE-010 SQLite identity corruption by namespacing document-local IDs, preserving source-local IDs for audit, and adding source-artifact parity gates so cross-policy overwrites cannot pass again.

## Relevant Docs Read

- `AGENTS.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/evaluation.md`
- `docs/data_contracts.md`
- `docs/database_strategy.md`
- `docs/tasks.md`
- `docs/decisions.md`
- DSE-010 session/eval artifacts

## Files Changed

- `.gitignore`
- `clause_store/schema.sql`
- `clause_store/models.py`
- `clause_store/repository.py`
- `clause_store/span_builder.py`
- `clause_store/fact_resolver.py`
- `scripts/run_clause_store.py`
- `scripts/validate_source_spans.py`
- `scripts/eval_clause_store.py`
- `tests/test_clause_store.py`
- `docs/tasks.md`
- `docs/evaluation.md`
- `docs/data_contracts.md`
- `docs/decisions.md`
- `docs/changelog.md`
- `runs/evals/2026-05-31-clause-store-dse010-v2.json`
- `data/reports/dse010_sqlite_build_summary.json`

## Commands Run

```bash
git checkout -b fix/dse-010-global-sqlite-ids
PYTHONPATH=. .venv/bin/python -m pytest tests/test_clause_store.py --tb=short
rm -f data/engine.sqlite data/engine.sqlite-wal data/engine.sqlite-shm
PYTHONPATH=. .venv/bin/python scripts/run_clause_store.py --gold-corpus gold_corpus --physical-root data/interim/physical --logical-root data/interim/logical --tables-root data/interim/tables --facts-root data/interim/facts --output-db data/engine.sqlite --output-facts-resolved data/interim/facts_resolved --pipeline-run-id dse010_v2_review
PYTHONPATH=. .venv/bin/python scripts/validate_source_spans.py --db data/engine.sqlite --facts-root data/interim/facts_resolved
PYTHONPATH=. .venv/bin/python scripts/eval_clause_store.py --db data/engine.sqlite --facts-root data/interim/facts_resolved --gold-corpus gold_corpus --output runs/evals/2026-05-31-clause-store-dse010-v2.json
sqlite3 data/engine.sqlite "SELECT 'lines', COUNT(*) FROM document_lines UNION ALL SELECT 'sections', COUNT(*) FROM document_sections UNION ALL SELECT 'clauses', COUNT(*) FROM policy_clauses UNION ALL SELECT 'source_spans', COUNT(*) FROM source_spans UNION ALL SELECT 'fk', COUNT(*) FROM pragma_foreign_key_check;"
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
```

## Results

- SQLite now stores all source rows:
  - `document_lines`: 12,715
  - `document_sections`: 1,156
  - `policy_clauses`: 2,522
  - `source_spans`: 6,136
- FK violations: 0
- Source artifact count parity: PASS
- Cross-document source span mismatches: 0
- Resolved fact span mismatches: 0
- Provisional IDs remaining in resolved present facts: 0
- DB size: 18.42 MB
- Gold corpus validator: PASS
- Full regression: 232 passed

## Generated Artifacts

- `data/engine.sqlite` (gitignored, reproducible)
- `data/interim/facts_resolved/*/accepted_facts.json` (gitignored, reproducible)
- `data/reports/dse010_sqlite_build_summary.json`
- `runs/evals/2026-05-31-clause-store-dse010-v2.json`

## Decisions Made

- ADR-0022: DSE-010 namespaces document-local IDs in SQLite and preserves original IDs in `source_*` columns.
- Clause source spans with no resolvable line IDs are retained with page-range fallback regions and a recorded issue instead of being dropped.
- SQLite uses rollback journal mode to avoid WAL/SHM sidecars in `git status`.

## Issues / Limitations

- 16/23 fact evidence spans still have clause-level char offsets due DSE-007 evidence text and DSE-010 clause text boundary mismatch.
- `document_text_spans` remains intentionally empty per ADR-0017.

## Next Step

DSE-011 can proceed only after DSE-010 v2 is reviewed and merged.
