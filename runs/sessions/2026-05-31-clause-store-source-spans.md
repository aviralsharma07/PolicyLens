# Session: Clause Store + Source Spans

Date: 2026-05-31
Task ID: DSE-010
Project: doc-structure-engine
Branch: feat/dse-010-clause-store-source-spans
AI executor: opencode + claude-sonnet-4-6
Human reviewer: Avi

## Goal

Build the provenance layer:
1. Persist all 5 gold-policy interim JSON outputs into `data/engine.sqlite` (19-table SQLite schema)
2. Build real `source_spans` records: clause → lines → bbox coordinates
3. Replace provisional `"clause:{id}"` evidence IDs with real span IDs in resolved facts
4. Resolve table `parent_clause_id` from page-range heuristic to bbox spatial overlap
5. Pass all 6 hard gates

## Relevant Docs Read

- `IMPLEMENTATION_PLAN.md` — 18-table schema, Phase 4 spec
- `docs/tasks.md` — DSE-010 backlog entry
- `docs/database_strategy.md` — SQLite strategy, `engine.sqlite` path
- `docs/data_contracts.md` — Contract 3C, Contract 4
- `docs/decisions.md` — ADR-0001 through ADR-0016
- `docs/evaluation.md` — Physical Parser evidence coverage gate (deferred here)
- `docs/open_questions.md` — OQ-001 (heading score in sections vs separate table)
- `data/interim/physical/*/document_physical.json` — 12,715 lines, 617K char-level spans across 5 policies
- `data/interim/logical/*/section_tree.json` — 2,522 sections, 2,522 clauses
- `data/interim/facts/*/accepted_facts.json` — 25 accepted facts (5 per policy)

## Files Changed

### Created
- `clause_store/__init__.py`
- `clause_store/schema.sql` — 19-table DDL (15 populated, 4 deferred)
- `clause_store/models.py` — Python dataclasses for row types
- `clause_store/repository.py` — init_db(), insert_*, query_*, backfill_table_parent_clauses()
- `clause_store/span_builder.py` — clause/evidence/cell span construction
- `clause_store/fact_resolver.py` — provisional → real ID resolution
- `scripts/run_clause_store.py` — batch ingest CLI
- `scripts/validate_source_spans.py` — structural integrity validator
- `scripts/eval_clause_store.py` — hard gate eval
- `tests/test_clause_store.py` — 59 unit tests
- `data/reports/dse010_sqlite_build_summary.json` — committed build summary

### Modified
- `docs/decisions.md` — ADR-0017 through ADR-0021
- `docs/evaluation.md` — Clause Store + Source Spans eval layer
- `docs/tasks.md` — DSE-010 done, detail block added
- `docs/changelog.md` — DSE-010 entry
- `docs/open_questions.md` — OQ-001 answered (ADR-0021)

## Commands Run

```bash
# Schema validation
sqlite3 :memory: < clause_store/schema.sql

# Unit tests
PYTHONPATH=. .venv/bin/python -m pytest tests/test_clause_store.py -v -m "not slow"
# Result: 59/59 PASS

# Batch ingest
PYTHONPATH=. python scripts/run_clause_store.py \
  --gold-corpus gold_corpus \
  --physical-root data/interim/physical \
  --logical-root data/interim/logical \
  --tables-root data/interim/tables \
  --facts-root data/interim/facts \
  --output-db data/engine.sqlite \
  --output-facts-resolved data/interim/facts_resolved
# Result: 5/5 policies ingested

# Validation
PYTHONPATH=. python scripts/validate_source_spans.py \
  --db data/engine.sqlite \
  --facts-root data/interim/facts_resolved
# Result: all checks PASS

# Eval
PYTHONPATH=. python scripts/eval_clause_store.py \
  --db data/engine.sqlite \
  --facts-root data/interim/facts_resolved \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-05-31-clause-store-dse010-v1.json
# Result: all 6 hard gates PASS

# Full regression
PYTHONPATH=. .venv/bin/python -m pytest tests/ -v -m "not slow" -q
# Result: 220/220 PASS

# Gold corpus validator
PYTHONPATH=. python scripts/validate_gold_corpus.py
# Result: PASS (35 JSON files, 18 physical labels, 100 facts)
```

## Results

### Hard Gates

| Gate | Target | Actual | Status |
|------|--------|--------|--------|
| Policies ingested | 5 | 5 | PASS |
| FK violations | 0 | 0 | PASS |
| Unresolved present facts | 0 | 0 | PASS |
| Clause span coverage | >= 95% | 100% | PASS |
| Provisional IDs in resolved | 0 | 0 | PASS |
| DB size | < 30 MB | 7.92 MB | PASS |
| Unit tests | 59/59 | 59/59 | PASS |
| Full regression | 220/220 | 220/220 | PASS |
| Gold corpus validator | PASS | PASS | PASS |

### Key Metrics

| Metric | Value |
|--------|-------|
| Total source_spans | 5,915 |
| clause_body spans | 2,301 |
| table_cell spans | 3,591 |
| fact_evidence spans | 23 |
| Tables with bbox-resolved parent clause | 192/197 (97.5%) |
| Average IoU of resolved parents | 0.67 |
| Cross-page clause spans | 113 |
| Evidence exact match | 7/23 (30.4%) |
| Evidence clause-level precision | 16/23 (69.6%) |

## Generated Artifacts

- `data/engine.sqlite` (gitignored, reproduced by `run_clause_store.py`)
- `data/interim/facts_resolved/*/accepted_facts.json` (gitignored, reproduced)
- `data/reports/dse010_sqlite_build_summary.json` (committed)
- `runs/evals/2026-05-31-clause-store-dse010-v1.json` (committed)

## Decisions Made

### ADR-0017: Defer document_text_spans
617K character-level spans not loaded into SQLite. Physical JSON is source of truth. DB stays bounded (7.92 MB for 5 policies).

### ADR-0018: page_regions_json for cross-page spans
`source_spans` uses `page_regions_json` array instead of flat `page_number + bbox_json`. Handles 37 cross-page clauses in care_health (and 113 total cross-page spans across all policies).

### ADR-0019: char_start/char_end are clause-text offsets
Evidence position measured within clause.text, not PDF character stream. 16/23 facts have clause-level precision (char_start=0) because DSE-007 evidence_text boundaries predate current clause segmentation.

### ADR-0020: Resolved facts are a separate artifact
`data/interim/facts/{slug}/accepted_facts.json` (DSE-007) never overwritten. DSE-010 writes `data/interim/facts_resolved/{slug}/accepted_facts.json` with real span IDs and audit fields (`provisional_evidence_span_id`, `evidence_resolution_status`).

### ADR-0021: OQ-001 closed — heading score in document_sections
No separate `heading_candidates` SQLite table. `document_sections.heading_score` and `document_sections.heading_type` store the scorer output for accepted headings.

## Issues / Limitations

1. **Evidence char offset degradation**: 16/23 accepted facts have clause-level char offsets (char_start=0, char_end=len(clause_text)) because the DSE-007 extractor captured evidence_text that includes section heading prefixes not present in the current clause_text boundary. This is a DSE-007/DSE-006 alignment issue — the physical location (clause_id, page, bbox) is correct; only the precise subspan position within the clause is approximate. Resolved via graceful degradation in `span_builder._find_char_offsets()`.

2. **document_text_spans deferred**: Character-level font signals (bold, italic per character) not queryable from SQLite. Available in physical JSON on demand.

3. **One block per page**: Physical parser creates one Block per page. `document_blocks` reflects this accurately but coarsely. Granular block segmentation deferred.

4. **extracted_facts, fact_conflicts, derived_policy_features**: DDL exists; not populated until DSE-011/DSE-013.

5. **HDFC bbox parent clause resolution 0/0**: HDFC tables are primarily text_alignment_candidates without reliable bboxes; lattice tables on HDFC have non-overlapping clause bboxes. 0 tables resolved — correct behavior (null is better than wrong assignment).

## Next Step

**DSE-011 — Fact Candidate Scoring + Conflict Resolution:**
- Consumes `data/interim/facts_resolved/*/accepted_facts.json`
- Persists `extracted_fact_candidates` and `extracted_facts` tables in SQLite
- Implements multi-candidate conflict resolution
- Enables full 20-concept extractor suite
