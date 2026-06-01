# Session: Derived Export (20-Concept Skeleton)

Date: 2026-06-01
Task ID: DSE-013
Project: doc-structure-engine
Branch: feat/dse-013-derived-export
AI executor: opencode + claude-sonnet-4-6
Human reviewer: Avi

## Goal

Complete the end-to-end pipeline by building the Product B consumable export:
PDF -> physical -> sections -> clauses -> facts -> SQLite -> scored facts -> **Export JSON**

Produce three files per policy: policy_features.json (20-concept derived view),
policy_fact_sources.json (full provenance), policy_clauses_minimal.json (lightweight context).

## Files Changed

### Created
- `derived/__init__.py`
- `derived/field_mapping.py` — 20-concept field map with scalar/compound extraction
- `derived/export_builder.py` — builds 3 export JSON files per policy from SQLite
- `derived/schema_validator.py` — validates export against contract shape
- `scripts/run_export.py` — batch export CLI
- `scripts/eval_export.py` — 14 hard gates (including evidence_clause and cross-file page consistency)
- `tests/test_export.py` — 41 unit tests
- `data/reports/dse013_export_summary.json`
- `runs/evals/2026-06-01-export-dse013-v1.json` (initial, pre-evidence_clause gate)
- `runs/evals/2026-06-01-export-dse013-v2.json` (final, 14 gates)

### Modified
- `docs/changelog.md` — DSE-013 entry
- `docs/decisions.md` — ADR-0027 through ADR-0029
- `docs/evaluation.md` — Derived Export eval layer
- `docs/export_contract.md` — status: draft -> active
- `docs/tasks.md` — DSE-013 done

## Commands Run

```bash
# Rebuild DB
rm -f data/engine.sqlite
PYTHONPATH=. .venv/bin/python scripts/run_clause_store.py \
  --gold-corpus gold_corpus \
  --physical-root data/interim/physical \
  --logical-root data/interim/logical \
  --tables-root data/interim/tables \
  --facts-root data/interim/facts \
  --output-db data/engine.sqlite \
  --output-facts-resolved data/interim/facts_resolved

PYTHONPATH=. .venv/bin/python scripts/run_fact_scoring.py \
  --gold-corpus gold_corpus \
  --candidates-root data/interim/facts \
  --resolved-root data/interim/facts_resolved \
  --db data/engine.sqlite

# Export
PYTHONPATH=. .venv/bin/python scripts/run_export.py \
  --db data/engine.sqlite \
  --output-root data/export

# Eval
PYTHONPATH=. .venv/bin/python scripts/eval_export.py \
  --db data/engine.sqlite \
  --export-root data/export \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-01-export-dse013-v1.json

# Tests
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short  # 321/321 PASS
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py  # PASS
PYTHONPATH=. .venv/bin/python scripts/validate_source_spans.py \
  --db data/engine.sqlite --facts-root data/interim/facts_resolved  # PASS
```

## Results

| Gate | Target | Actual | Status |
|------|--------|--------|--------|
| Policies exported | 5 | 5 | PASS |
| 20 concepts per policy | 20/20 | 20/20 | PASS |
| Schema validation errors | 0 | 0 | PASS |
| Present facts have evidence | 100% | 23/23 | PASS |
| Not-found have null value | 100% | yes | PASS |
| Valid fact statuses | 7 only | yes | PASS |
| Evidence span IDs in DB | 100% | 23/23 | PASS |
| Gold value accuracy (5 concepts) | >=95% | 100% (23/23) | PASS |
| Gold status accuracy (5 concepts) | >=95% | 100% (25/25) | PASS |
| False present | 0 | 0 | PASS |
| Schema version | "1.0" | yes | PASS |
| derived_policy_features parity | 5 | 5 | PASS |
| Evidence clause missing | 0 | 0 | PASS |
| Cross-file page disagree | 0 | 0 | PASS |
| Unit tests | 41/41 | 41/41 | PASS |
| Full regression | 321/321 | 321/321 | PASS |

## Decisions Made

- ADR-0027: All 20 concepts emitted in every export, even if not_found
- ADR-0028: Scalar value for simple types, full JSON for compound types
- ADR-0029: data/export/ is gitignored; build summary committed

## Issues / Limitations

1. 15/20 concepts are not_found — fill rate is 25%. This is correct (only 5 extractors exist).
2. evidence_clause shows source-local clause number, not a globally stable ID.
3. policy_clauses_minimal truncates clause text to 500 chars.
4. value_type field is null for all extracted facts (DSE-007 doesn't set it).

## Next Step

DSE-015 — Insurer/Plan Normalizer Library (improve product_identity quality in exports)
or DSE-012 — Expand gold corpus 5->20 (test pipeline at scale).
