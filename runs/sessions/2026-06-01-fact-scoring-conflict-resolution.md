# Session: Fact Candidate Scoring + Conflict Resolution

Date: 2026-06-01
Task ID: DSE-011
Project: doc-structure-engine
Branch: feat/dse-011-fact-scoring-conflict-resolution
AI executor: opencode + claude-sonnet-4-6
Human reviewer: Avi

## Goal

Persist the existing 5-concept fact candidate/fact pipeline into SQLite,
build composite scoring infrastructure, implement conflict detection machinery
(proven with synthetic tests), and validate against gold facts with hard gates
that compare against external sources (not DB self-consistency).

## Files Changed

### Created
- `extractors/scoring.py` — composite score: confidence × evidence quality × pattern specificity × source priority
- `extractors/conflict_detector.py` — value/status/scope conflict detection + resolution strategies
- `scripts/run_fact_scoring.py` — batch ingest CLI
- `scripts/eval_fact_scoring.py` — 12 hard gates (including accepted_candidate_min_score)
- `tests/test_fact_scoring.py` — 48 unit tests
- `data/reports/dse011_fact_scoring_summary.json`
- `runs/evals/2026-06-01-fact-scoring-dse011-v1.json`

### Modified
- `clause_store/schema.sql` — refined extracted_fact_candidates (14→22 cols), extracted_facts (+source columns, CHECK), fact_conflicts (+document_id, concept, CHECKs)
- `clause_store/models.py` — ExtractedFactCandidate, ExtractedFact, FactConflict dataclasses
- `clause_store/repository.py` — 7 new functions for fact table CRUD
- `docs/changelog.md`, `docs/decisions.md` (ADR-0023–0026), `docs/evaluation.md`, `docs/tasks.md`

## Commands Run

```bash
sqlite3 :memory: < clause_store/schema.sql  # Schema OK
pytest tests/test_fact_scoring.py -v -m "not slow"  # 46/46 PASS
rm -f data/engine.sqlite
PYTHONPATH=. .venv/bin/python scripts/run_clause_store.py \
  --gold-corpus gold_corpus \
  --physical-root data/interim/physical \
  --logical-root data/interim/logical \
  --tables-root data/interim/tables \
  --facts-root data/interim/facts \
  --output-db data/engine.sqlite \
  --output-facts-resolved data/interim/facts_resolved  # DSE-010 rebuild
PYTHONPATH=. .venv/bin/python scripts/run_fact_scoring.py \
  --gold-corpus gold_corpus \
  --candidates-root data/interim/facts \
  --resolved-root data/interim/facts_resolved \
  --db data/engine.sqlite  # 5/5 OK, 76 candidates, 23 facts, 0 conflicts
PYTHONPATH=. .venv/bin/python scripts/eval_fact_scoring.py \
  --db data/engine.sqlite \
  --candidates-root data/interim/facts \
  --resolved-root data/interim/facts_resolved \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-01-fact-scoring-dse011-v2.json  # ALL GATES PASS
pytest tests/ --tb=short  # 280/280 PASS (269 non-slow + 11 slow integration)
python scripts/validate_gold_corpus.py  # PASS
python scripts/validate_source_spans.py  # PASS
```

## Results

| Gate | Target | Actual | Status |
|------|--------|--------|--------|
| Policies evaluated | 5 | 5 | PASS |
| Candidate parity | 100% | 100% (76=76) | PASS |
| Fact parity | 100% | 100% (23=23) | PASS |
| FK violations | 0 | 0 | PASS |
| Fact status accuracy | >=95% | 100% (25/25) | PASS |
| Value accuracy | >=95% | 100% (23/23) | PASS |
| Evidence accuracy | >=95% | 100% (23/23) | PASS |
| False present | 0 | 0 | PASS |
| Conflicts resolved or zero | yes | 0 total | PASS |
| Cross-doc fact links | 0 | 0 | PASS |
| Accepted min score | >=0.85 | 0.9800 | PASS |
| Unit tests | 48/48 | 48/48 | PASS |
| Full regression | 280/280 | 280/280 | PASS |

## Decisions Made

- ADR-0023: Refined deferred DDL (tables were empty, no migration)
- ADR-0024: extracted_facts stores only present/explicitly_not_covered; not_found derived
- ADR-0025: Composite scoring formula (0.50 conf + 0.30 evidence + 0.15 pattern + 0.05 source)
- ADR-0026: Conflict detection for value/status/scope disagreements (0 production conflicts, proven via synthetic tests)

## Issues / Limitations

1. **0 production conflicts** — only synthetic tests exercise the conflict machinery (1 extractor per concept). Future multi-extractor scenarios will produce real conflicts.
2. **Only 5/20 concepts** — remaining 15 need new extractors (separate task).
3. **Composite score weights not empirically tuned** — reasonable defaults, no training data for optimization.
4. **`not_found` derived, not stored** — ADR-0024; consumers must check absence.

## Next Step

DSE-012 — Expand gold corpus 5→20 or a new task to expand extractors from 5→15-20 concepts.
Both can now safely plug into the scoring/conflict infrastructure built here.
