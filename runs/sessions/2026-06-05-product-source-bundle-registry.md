# Session: Product Source Bundle Registry v1

Date: 2026-06-05
Task ID: DSE-025
Project: doc-structure-engine
Branch: main
AI executor: Codex
Human reviewer: Avi

## Goal

Implement the first Product Source Bundle Registry so Product A stops treating one PDF as one launch-grade product. The registry records product-level bundles of policy wording, Product Benefit Table, CIS, brochure/prospectus, and related source documents, with source-quality status.

## Relevant Docs Read

- `docs/tasks.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/data_contracts.md`
- `docs/product_b_mvp_gtm_strategy.md`
- `docs/export_contract.md`

## Files Changed

- `schemas/product_source_bundle.schema.json`
- `source_bundles/__init__.py`
- `source_bundles/validator.py`
- `source_bundles/builder.py`
- `scripts/build_source_bundle_registry.py`
- `scripts/validate_source_bundles.py`
- `tests/test_source_bundles.py`
- `data/manifests/product_source_bundles_v1.example.json`
- `data/manifests/product_source_bundle_manual_overrides_v1.json`
- `data/manifests/product_source_bundles_v1.draft.json`
- `data/reports/dse025_source_bundle_baseline_audit.md`
- `docs/tasks.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/changelog.md`
- `runs/sessions/2026-06-05-product-source-bundle-registry.md`

## Commands Run

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/test_source_bundles.py --tb=short -v

PYTHONPATH=. .venv/bin/python scripts/build_source_bundle_registry.py \
  --active-manifest data/manifests/active_policy_wordings_v1.json \
  --uin-report data/manifests/uin_match_report_v1.json \
  --manual-overrides data/manifests/product_source_bundle_manual_overrides_v1.json \
  --output data/manifests/product_source_bundles_v1.draft.json

PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py \
  data/manifests/product_source_bundles_v1.draft.json

PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py \
  data/manifests/product_source_bundles_v1.example.json

PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py

PYTHONPATH=. .venv/bin/python -m pytest tests/test_source_bundles.py --tb=short -v

PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short

git diff --check
```

## Results

- Source bundle schema added.
- Dependency-free validator added.
- Draft registry builder added.
- Example registry added.
- Manual source-identified override added for Aditya Birla Activ Care.
- Draft registry generated from current active manifest and UIN report.
- Source bundle draft validation passed.
- Source bundle example validation passed.
- Gold corpus validation passed.
- Focused tests passed: 7/7.
- Full pytest passed: 487/487.
- `git diff --check` passed.

Draft registry stats:

| Metric | Count |
|--------|------:|
| Product bundles | 507 |
| `missing_pbt` bundles | 504 |
| `acceptable_with_known_gap` bundles | 1 |
| `rejected` bundles | 2 |
| Policy wording documents | 630 |
| Brochure documents | 18 |
| CIS documents | 1 |
| Product Benefit Table documents | 1 |

## Decisions Made

- Source-identified remote documents may have `file_hash = null` only when `review_status = source_identified`.
- Remote documents must be downloaded, hashed, and reviewed before launch-grade Product B use.
- Current corpus-generated bundles are mostly `missing_pbt` because active manifests do not include systematic PBT/CIS sources.
- Duplicate file hashes are allowed in the registry because they represent corpus/source duplication, not schema invalidity.

## Issues / Limitations

- Current active manifest has zero `source_url` values.
- The draft registry is not a launch-ready curated MVP corpus.
- Activ Care official PBT/CIS URLs are identified but not downloaded/hash-verified yet.
- Most bundles are policy-wording-only and must not drive confident Product B recommendation.

## Next Step

DSE-026 — finalize top 10 insurer universe and MVP top 5 selection with evidence and source-availability rationale.
