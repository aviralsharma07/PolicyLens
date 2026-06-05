# Session: Product B Export v1 Freeze

Date: 2026-06-05  
Task ID: DSE-023  
Project: doc-structure-engine  
Branch: feat/dse-023-product-b-export-v1  
AI executor: Codex  
Human reviewer: Avi

## Goal

Freeze the first Product B-consumable export contract and create a reproducible handoff package from Product A reviewed benchmark exports.

## Relevant Docs Read

- `docs/tasks.md`
- `docs/export_contract.md`
- `docs/data_contracts.md`
- `docs/database_strategy.md`
- `ontology/concepts.v1.json`
- `derived/field_mapping.py`
- `derived/export_builder.py`
- `derived/schema_validator.py`
- `scripts/run_export.py`
- `scripts/eval_export.py`

## Packet -1 — DSE-022 Hygiene Cleanup

Restored dirty DSE-009 historical/generated reports left by the final DSE-022 table eval rerun:

```bash
git restore data/reports/dse009_gold_table_annotation_audit.json data/reports/dse009_gold_table_source_review.json data/reports/dse009_gold_table_source_review.md data/reports/dse009_table_bbox_review_candidates.json
git status --short
```

Result: working tree clean before DSE-023 audit work.

## Packet 0 — Export Freeze Audit

Created an audit report before changing export behavior:

- `data/reports/dse023_export_freeze_audit.md`

Findings:

- Current exports are 20-policy benchmark exports with all 20 ontology concepts.
- Product identity keys are present.
- Every feature includes value/status/evidence fields.
- `not_found` remains explicitly different from `explicitly_not_covered`.
- Current docs still contain stale 91-field language that must be reframed in Packet 1.

## Commands Run

```bash
git status --short
sed -n '1,260p' docs/export_contract.md
sed -n '1,260p' docs/data_contracts.md
sed -n '1,240p' docs/database_strategy.md
sed -n '1,220p' derived/field_mapping.py
sed -n '1,280p' derived/export_builder.py
sed -n '1,260p' derived/schema_validator.py
sed -n '1,260p' scripts/run_export.py
sed -n '1,320p' scripts/eval_export.py
.venv/bin/python - <<'PY'
import json, pathlib
root=pathlib.Path('data/export')
for p in sorted(root.glob('*/policy_features.json'))[:5]:
    data=json.loads(p.read_text())
    print(p, len(data.get('features', {})), data.get('parse_quality'))
PY
```

## Results

Packet 0 audit confirms DSE-023 should proceed as a contract/package freeze task, not as an extractor, parser, or Product B implementation task.

## Generated Artifacts

- `data/reports/dse023_export_freeze_audit.md`

## Decisions Made

- No export behavior changes in Packet 0.
- DSE-023 v1 should package the reviewed 20-policy benchmark first.
- Full 647-policy package remains a follow-up after the v1 handoff package is stable.

## Issues / Limitations

- Current docs and a few docstrings still use “91-field” language for the active export. Packet 1 must clarify that v1 is the 20-concept ontology-backed schema.

## Next Step

Packet 1 — freeze the Product B export v1 contract in docs and decision history.

## Packet 1 — Export Contract Freeze

Updated the active Product A → Product B contract docs:

- `docs/export_contract.md`
- `docs/data_contracts.md`
- `docs/database_strategy.md`
- `docs/evaluation.md`
- `docs/tasks.md`
- `docs/changelog.md`

Clarifications:

- `export_schema_version = "1.0"` is the 20-concept ontology-backed JSON contract.
- The earlier 91-field language is future expansion, not part of v1.
- Product B consumes compiled JSON only.
- SQLite, raw parser tables, physical/logical/table interim outputs, and raw PDFs remain Product A internals.

Next step: Packet 2 — implement the reproducible Product B handoff package builder.

## Packet 2 — Handoff Package Builder

Added:

- `scripts/build_product_b_handoff.py`
- handoff tests in `tests/test_export.py`

Builder behavior:

- Reads reviewed policy metadata from `gold_corpus/policies/*/metadata.json`.
- Copies only compiled export JSON files from `data/export/{policy_id}/`.
- Writes `manifest.json`, `README.md`, `export_contract.md`, `ontology_concepts.v1.json`, `quality/coverage_summary.json`, and `checksums.sha256`.
- Refuses missing `policy_features.json` or schema-invalid exports.
- Refuses forbidden package contents such as raw PDFs, SQLite files, or interim parser paths.

Important fix:

- Original 5 gold policies do not all carry the newer `label_status: reviewed` marker. The builder now excludes only `label_status: draft`, matching the reviewed benchmark reality and packaging all 20 policies.

Commands:

```bash
PYTHONPATH=. .venv/bin/python scripts/build_product_b_handoff.py --export-root data/export --gold-corpus gold_corpus --output-root data/processed/product_b_export_v1
PYTHONPATH=. .venv/bin/python -m pytest tests/test_export.py --tb=short
git diff --check
```

Results:

- Builder produced `data/processed/product_b_export_v1` with 20 reviewed policies.
- `tests/test_export.py`: 47/47 passed.
- `git diff --check`: passed.

Next step: Packet 3 — run final export eval, rebuild package with the eval artifact, run full gates, then mark DSE-023 done.

## Packet 3 — Final Export Eval + Handoff Acceptance

Commands:

```bash
PYTHONPATH=. .venv/bin/python scripts/eval_export.py --db data/engine.sqlite --export-root data/export --gold-corpus gold_corpus --output runs/evals/2026-06-05-export-dse023-final.json
PYTHONPATH=. .venv/bin/python scripts/build_product_b_handoff.py --export-root data/export --gold-corpus gold_corpus --output-root data/processed/product_b_export_v1 --export-eval runs/evals/2026-06-05-export-dse023-final.json
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
```

Results:

- Export eval: PASS.
- Policies exported: 20.
- Concepts per policy: 20/20.
- Schema validation errors: 0.
- Present missing evidence: 0.
- Span IDs missing from DB: 0/280.
- Gold status accuracy: 97.8%.
- Gold value accuracy: 98.2%.
- False present: 0.
- Cross-file page disagreement: 0.
- Handoff package: `data/processed/product_b_export_v1`, 20 policies, 67 files, checksums generated.
- Gold corpus validator: PASS.
- Full pytest: 480/480 PASS.

Generated artifacts:

- `runs/evals/2026-06-05-export-dse023-final.json`
- `data/processed/product_b_export_v1/`

DSE-023 is complete.
