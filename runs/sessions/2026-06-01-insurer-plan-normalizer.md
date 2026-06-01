# Session: Insurer/Plan Normalizer Library

Date: 2026-06-01
Task ID: DSE-015
Project: doc-structure-engine
Branch: feat/dse-015-insurer-plan-normalizer
AI executor: opencode + claude-sonnet-4-6
Human reviewer: Avi

## Goal

Make product_identity contract-complete, display-ready, and correct:
1. Fix uin_base truncation bug ([:11] → V-delimiter)
2. Add missing export fields (product_version, effective_date, match_confidence, match_method)
3. Clean plan names (strip insurer suffixes, generic boilerplate)
4. Build formal insurer registry (32 insurers) and plan normalizer library
5. Add 45 unit tests for the identity module

## Files Changed

### Created
- `identity/uin_utils.py` — UIN parsing via V-delimiter
- `identity/insurer_registry.py` — 32-insurer registry
- `identity/plan_normalizer.py` — plan name cleanup + display_name
- `tests/test_identity.py` — 45 unit tests
- `runs/evals/2026-06-01-export-dse015-v1.json`

### Modified
- `identity/__init__.py` — updated docstring
- `clause_store/schema.sql` — products +4 cols, product_versions +3 cols
- `clause_store/models.py` — Product +4 fields, ProductVersion +3 fields
- `clause_store/repository.py` — updated insert functions
- `scripts/run_clause_store.py` — fixed uin_base, uses identity library
- `derived/export_builder.py` — emits 9-field product_identity
- `derived/schema_validator.py` — validates identity completeness
- `tests/test_export.py` — updated fixture
- `docs/changelog.md`, `docs/decisions.md`, `docs/tasks.md`

## Results

| Check | Result |
|-------|--------|
| uin_base length (all 5) | 12 chars (was 11) |
| plan_name no insurer | 0 violations (was 2) |
| display_name populated | 5/5 |
| product_version from lifecycle | populated for all 5 |
| effective_date from lifecycle | populated for all 5 |
| Export eval (14 gates) | ALL PASS |
| Fact scoring eval (12 gates) | ALL PASS |
| Source spans validator | PASS |
| Gold corpus validator | PASS |
| Identity tests | 45/45 |
| Full regression | 366/366 |

## Decisions Made

- ADR-0030: UIN base extraction via V-delimiter, not fixed-length slice
- ADR-0031: Plan name normalization strips insurer suffix and boilerplate
- ADR-0032: Insurer registry is canonical source of truth (subsumes DSE-002)

## Next Step

DSE-012 — Expand gold corpus 5→20 policies. The identity library is ready for 24 corpus insurers.
