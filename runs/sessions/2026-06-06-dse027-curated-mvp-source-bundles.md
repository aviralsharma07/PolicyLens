# Session: DSE-027 Curated MVP Source-Bundle Sprint with Latest-Version Safety Gate

Date: 2026-06-06
Task ID: DSE-027
Project: doc-structure-engine
Branch: main
AI executor: Codex
Human reviewer: Avi

## Goal

Verify the full 30-product DSE-026 MVP universe against current official insurer surfaces before doing source-bundle collection, then assemble a curated MVP source-bundle registry with current official provenance, downloaded current documents where possible, and explicit source-quality gaps.

## Relevant Docs Read

- `AGENTS.md`
- `docs/tasks.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/product_b_mvp_gtm_strategy.md`
- `docs/decisions.md`
- `docs/data_contracts.md`
- `schemas/product_source_bundle.schema.json`
- `source_bundles/builder.py`
- `source_bundles/validator.py`
- `data/manifests/mvp_product_candidates_v1.json`
- `data/manifests/mvp_insurer_selection_v1.json`
- `data/manifests/product_source_bundles_v1.draft.json`
- `data/manifests/active_policy_wordings_v1.json`
- `data/manifests/uin_match_report_v1.json`

## Files Changed

- `source_bundles/mvp.py`
- `scripts/verify_mvp_candidates.py`
- `scripts/build_mvp_source_bundles.py`
- `scripts/download_mvp_source_documents.py`
- `tests/test_dse027_mvp_source_bundles.py`
- `data/manifests/mvp_product_candidate_verification_manual_v1.json`
- `data/manifests/mvp_product_candidates_verified_v1.json`
- `data/manifests/product_source_bundle_mvp_manual_overrides_v1.json`
- `data/manifests/product_source_bundles_mvp_v1.json`
- `data/reports/dse027_mvp_candidate_latest_audit_v1.json`
- `data/reports/dse027_mvp_candidate_latest_audit_v1.md`
- `data/reports/dse027_source_download_index_v1.json`
- `data/reports/dse027_curated_mvp_bundle_closeout_v1.md`
- `docs/tasks.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/changelog.md`
- `docs/risk_register.md`
- `docs/decisions.md`

## Commands Run

```bash
PYTHONPATH=. .venv/bin/python scripts/verify_mvp_candidates.py
PYTHONPATH=. .venv/bin/python scripts/build_mvp_source_bundles.py
PYTHONPATH=. .venv/bin/python -m pytest tests/test_dse027_mvp_source_bundles.py tests/test_source_bundles.py --tb=short
PYTHONPATH=. .venv/bin/python scripts/download_mvp_source_documents.py
PYTHONPATH=. .venv/bin/python scripts/build_mvp_source_bundles.py
PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py data/manifests/product_source_bundles_v1.draft.json
PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py data/manifests/product_source_bundles_mvp_v1.json
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
git status --short
```

## Results

- Verified all 30 MVP candidates against current official insurer surfaces.
- Verification result:
  - `verified_current`: 27
  - `verified_current_with_gap`: 3
  - `live`: 30
  - `replaced`: 0
  - `unresolved`: 0
  - `dropped`: 0
- Built `mvp_product_candidates_verified_v1.json`.
- Built curated `product_source_bundles_mvp_v1.json` with 30 bundles.
- Downloaded and hashed 45 current official source documents into `data/processed/source_documents_mvp_v1`.
- Recorded 2 download failures without aborting the run.

## Generated Artifacts

- `data/manifests/mvp_product_candidates_verified_v1.json`
- `data/reports/dse027_mvp_candidate_latest_audit_v1.json`
- `data/reports/dse027_mvp_candidate_latest_audit_v1.md`
- `data/manifests/product_source_bundles_mvp_v1.json`
- `data/reports/dse027_source_download_index_v1.json`
- `data/reports/dse027_curated_mvp_bundle_closeout_v1.md`

## Decisions Made

- Current official insurer docs/pages override older local corpus versions when they disagree.
- Curated MVP bundle output remains separate from the 507-bundle full-corpus draft registry.
- Download failures are recorded in a tracked report instead of failing silently or being omitted from bundle status.

## Issues / Limitations

- Bundle completeness is still uneven:
  - `acceptable_with_known_gap`: 18
  - `missing_cis`: 6
  - `missing_pbt`: 4
  - `stale_version`: 2
- Two current-source downloads failed:
  - `star_health_family_health_optima` brochure: host-resolution failure
  - `star_health_super_surplus` brochure: `403 Forbidden`
- Some bundles still rely on current official URLs plus older reviewed local wording files where the current wording PDF is not yet fully locked.

## Next Step

Start `DSE-028 — Bundle-Aware Product B Export`.

The export now needs to carry:

- bundle/source quality,
- current vs legacy provenance,
- variant scope,
- condition scope,
- and blocking/warning semantics for incomplete bundles.
