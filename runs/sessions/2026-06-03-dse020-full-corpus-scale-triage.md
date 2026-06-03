# Session: DSE-020 Full 647-Policy Pipeline Dry Run + Scale Triage

Date: 2026-06-03
Task ID: DSE-020
Project: doc-structure-engine
Branch: feat/dse-020-full-corpus-scale-triage
AI executor: Codex GPT-5
Human reviewer: Avi

## Goal

Prepare and execute a diagnostic full-corpus scale run across 647 active policy wordings without manual annotation, without mutating raw PDFs, and without overwriting canonical 20-policy benchmark outputs.

## Relevant Docs Read

- AGENTS.md
- IMPLEMENTATION_PLAN.md
- docs/tasks.md
- dse-020-tracking
- scripts/run_pipeline_batch.py
- scripts/run_clause_store.py
- scripts/run_fact_scoring.py
- scripts/run_export.py
- data/manifests/active_policy_wordings_v1.json

## Files Changed

- `dse-020-tracking`
- `scripts/build_dse020_manifest.py`
- `scripts/run_pipeline_batch_dse020.py`
- `scripts/run_clause_store.py`
- `scripts/run_fact_scoring.py`
- `scripts/run_export.py`
- `scripts/validate_source_spans.py`
- `scripts/dse020_triage_report.py`
- `tests/test_dse020_manifest.py`
- `data/manifests/dse020_run_manifest_v1.json`
- `data/reports/dse020_fact_scoring_smoke_summary.json`
- `data/reports/dse020_export_smoke_summary.json`
- `data/reports/dse020_scale_triage_report_smoke.json`
- `data/reports/dse020_scale_triage_report_smoke.md`
- `runs/sessions/2026-06-03-dse020-full-corpus-scale-triage.md`

## Commands Run

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/test_dse020_manifest.py --tb=short
PYTHONPYCACHEPREFIX=.pycache_dse020 PYTHONPATH=. .venv/bin/python -m py_compile scripts/build_dse020_manifest.py scripts/run_pipeline_batch_dse020.py scripts/run_clause_store.py scripts/run_fact_scoring.py
PYTHONPATH=. .venv/bin/python scripts/build_dse020_manifest.py --active-manifest data/manifests/active_policy_wordings_v1.json --gold-corpus gold_corpus --output data/manifests/dse020_run_manifest_v1.json
PYTHONPATH=. .venv/bin/python scripts/run_pipeline_batch_dse020.py --manifest data/manifests/dse020_run_manifest_v1.json --policy-data-root ../policy_data --output-root data/interim/dse020 --limit 5
PYTHONPATH=. .venv/bin/python scripts/run_pipeline_batch_dse020.py --manifest data/manifests/dse020_run_manifest_v1.json --policy-data-root ../policy_data --output-root data/interim/dse020 --limit 20 --resume
PYTHONPATH=. .venv/bin/python scripts/run_pipeline_batch_dse020.py --manifest data/manifests/dse020_run_manifest_v1.json --policy-data-root ../policy_data --output-root data/interim/dse020 --resume --slug <20 reviewed-gold slugs>
PYTHONPATH=. .venv/bin/python scripts/run_clause_store.py --manifest data/manifests/dse020_run_manifest_v1.json --physical-root data/interim/dse020/physical --logical-root data/interim/dse020/logical --tables-root data/interim/dse020/tables --facts-root data/interim/dse020/facts --output-db data/engine_dse020_smoke.sqlite --output-facts-resolved data/interim/dse020/facts_resolved_smoke --pipeline-run-id clause_store_dse020_smoke_2026_06_03 --slug <20 reviewed-gold slugs>
PYTHONPATH=. .venv/bin/python scripts/validate_source_spans.py --db data/engine_dse020_smoke.sqlite --facts-root data/interim/dse020/facts_resolved_smoke --manifest data/manifests/dse020_run_manifest_v1.json --physical-root data/interim/dse020/physical --logical-root data/interim/dse020/logical --slug <20 reviewed-gold slugs>
PYTHONPATH=. .venv/bin/python scripts/run_fact_scoring.py --manifest data/manifests/dse020_run_manifest_v1.json --candidates-root data/interim/dse020/facts --resolved-root data/interim/dse020/facts_resolved_smoke --physical-root data/interim/dse020/physical --db data/engine_dse020_smoke.sqlite --pipeline-run-id fact_scoring_dse020_smoke_2026_06_03 --summary-output data/reports/dse020_fact_scoring_smoke_summary.json --slug <20 reviewed-gold slugs>
PYTHONPATH=. .venv/bin/python scripts/run_export.py --db data/engine_dse020_smoke.sqlite --output-root data/export/dse020 --pipeline-run-id export_dse020_smoke_2026_06_03 --summary-output data/reports/dse020_export_smoke_summary.json
PYTHONPATH=. .venv/bin/python scripts/dse020_triage_report.py --manifest data/manifests/dse020_run_manifest_v1.json --progress-summary data/interim/dse020/progress/summary.json --output-root data/interim/dse020 --db data/engine_dse020_smoke.sqlite --export-root data/export/dse020 --json-output data/reports/dse020_scale_triage_report_smoke.json --md-output data/reports/dse020_scale_triage_report_smoke.md
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/test_dse020_manifest.py --tb=short
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
git status --short
PYTHONPATH=. .venv/bin/python scripts/run_pipeline_batch_dse020.py --manifest data/manifests/dse020_run_manifest_v1.json --policy-data-root ../policy_data --output-root data/interim/dse020 --resume
```

## Results

- Phase 0 tracking plan updated with DSE-020 safety rails and short-context executor protocol.
- Manifest builder created.
- DSE-020 manifest generated successfully:
  - policies: 647
  - unique slugs: 647
  - reviewed gold policies mapped: 20
  - missing PDFs: 0
  - slug collision groups recorded: 9
- Manifest-focused tests passed: 4/4.
- Syntax compile passed after redirecting Python bytecode cache into workspace.
- 5-policy per-policy smoke passed all stages.
- 20-entry New India smoke passed all stages.
- 20 reviewed-gold mixed smoke passed all stages.
- Clause-store smoke passed on 20 reviewed-gold policies.
- Source-span validation passed after adding manifest/root support to the validator.
- Fact scoring smoke passed: 20/20 policies, 665 candidates, 181 facts, 0 conflicts, 0 FK violations.
- Export smoke passed: 20/20 exports under `data/export/dse020`.
- Smoke triage report generated and identified known zero-heading/zero-clause warnings for Tata AIG and Aditya Birla.
- Gold corpus validator passed.
- Focused DSE-020 tests passed: 4/4.
- Full pytest passed: 393/393.
- `git diff --check` passed.
- Full 647-policy per-policy run completed successfully.
- Progress summary written to `data/interim/dse020/progress/summary.json`.
- Progress events written to `data/interim/dse020/progress/events.jsonl`.
- No per-policy stage failures recorded; warnings about invalid gray non-stroke color emitted by some PDFs but run continued.

## Generated Artifacts

- `data/manifests/dse020_run_manifest_v1.json`
- `data/reports/dse020_fact_scoring_smoke_summary.json`
- `data/reports/dse020_export_smoke_summary.json`
- `data/reports/dse020_scale_triage_report_smoke.json`
- `data/reports/dse020_scale_triage_report_smoke.md`
- `data/interim/dse020/progress/summary.json`
- `data/interim/dse020/progress/events.jsonl`

## Decisions Made

- DSE-020 outputs are namespaced under `data/interim/dse020`, `data/export/dse020`, and `data/engine_dse020.sqlite`.
- Exact gold source path wins for reviewed-gold slug mapping; hash fallback is used only when gold metadata has no source path, because duplicate active corpus entries can share the same hash.

## Issues / Limitations

- Full 647 run has not started yet.
- Triage report script is still pending.
- Generated smoke SQLite/interim/export artifacts are intentionally ignored and must not be committed.
- Full per-policy run emitted repeated `Cannot set gray non-stroke color ... invalid float value` warnings from PDFs; no failures recorded.

## 2026-06-04 — Packet 3A (Full DB/Export Run) + Phase 4 (Triage Report) + Phase 5 (Docs)

### Goal

Run the full DB/export chain over 647-policy outputs, fix the duplicate document identity issue, generate triage report, and close out DSE-020 docs.

### Files Changed

- `scripts/run_clause_store.py` — added duplicate-hash skip logic (`seen_document_ids`), stale resolved facts cleanup, updated summary with `policies_skipped_duplicate_hash`
- `scripts/validate_source_spans.py` — added diagnostic print showing manifest entry count vs unique document_id count
- `dse-020-tracking` — updated with Phase 3 results, fix, and re-run output
- `docs/tasks.md` — DSE-020 marked done; added to completed table
- `docs/changelog.md` — added 2026-06-04 entry with full results
- `docs/decisions.md` — added ADR-0039 (duplicate-hash skip behavior)
- `docs/risk_register.md` — added R24 (duplicate-hash risk, mitigated)
- `runs/sessions/2026-06-03-dse020-full-corpus-scale-triage.md` — updated with this session's work

### Commands Run

```bash
# Rebuild DB after duplicate-hash fix
rm -f data/engine_dse020.sqlite data/engine_dse020.sqlite-wal data/engine_dse020.sqlite-shm
PYTHONPATH=. .venv/bin/python scripts/run_clause_store.py \
  --manifest data/manifests/dse020_run_manifest_v1.json \
  --physical-root data/interim/dse020/physical \
  --logical-root data/interim/dse020/logical \
  --tables-root data/interim/dse020/tables \
  --facts-root data/interim/dse020/facts \
  --output-db data/engine_dse020.sqlite \
  --output-facts-resolved data/interim/dse020/facts_resolved \
  --pipeline-run-id clause_store_dse020_full_2026_06_04

# Source-span validation (with manifest)
PYTHONPATH=. .venv/bin/python scripts/validate_source_spans.py \
  --db data/engine_dse020.sqlite \
  --facts-root data/interim/dse020/facts_resolved \
  --manifest data/manifests/dse020_run_manifest_v1.json \
  --physical-root data/interim/dse020/physical \
  --logical-root data/interim/dse020/logical

# Fact scoring
PYTHONPATH=. .venv/bin/python scripts/run_fact_scoring.py \
  --manifest data/manifests/dse020_run_manifest_v1.json \
  --candidates-root data/interim/dse020/facts \
  --resolved-root data/interim/dse020/facts_resolved \
  --physical-root data/interim/dse020/physical \
  --db data/engine_dse020.sqlite \
  --pipeline-run-id fact_scoring_dse020_full_2026_06_04

# Export
PYTHONPATH=. .venv/bin/python scripts/run_export.py \
  --db data/engine_dse020.sqlite \
  --output-root data/export/dse020 \
  --pipeline-run-id export_dse020_full_2026_06_04

# Triage report
PYTHONPATH=. .venv/bin/python scripts/dse020_triage_report.py \
  --manifest data/manifests/dse020_run_manifest_v1.json \
  --progress-summary data/interim/dse020/progress/summary.json \
  --db data/engine_dse020.sqlite \
  --export-root data/export/dse020 \
  --json-output data/reports/dse020_scale_triage_report_v1.json \
  --md-output data/reports/dse020_scale_triage_report_v1.md \
  --date 2026-06-04
```

### Results

- Clause store: **591/647 ingested** (56 skipped duplicate hash), DB 1938.17 MB.
- Source-span validation: **ALL CHECKS PASSED** — 591 source_documents, 0 FK violations, count parity exact, 548135 valid source_spans, 3628 resolved facts verified.
- Fact scoring: **598/647 policies** processed, 14792 candidates, 3759 facts, 0 conflicts, 0 FK violations.
- Export: **566/591 policies** exported (25 had 0 resolved facts), fill rate range 5%–60%.
- Triage report key findings: 132 zero-heading/zero-clause policies, 133 zero-candidate policies, top not_found concepts identified.

### Decisions Made

- ADR-0039: Duplicate-hash entries are skipped at clause store ingestion. First slug per unique document_id wins.

### Issues / Limitations

- 56 duplicate-hash entries discovered: the same PDF appearing under two slugs (IRDAI vs website source).
- 132 policies with zero clauses/headings — fundamental parser gaps.
- 133 policies with zero fact candidates — downstream of zero-clause issue.
- The `validate_source_spans.py` `collect_source_counts_from_manifest` function loads physical/logical JSON for ALL 647 manifest entries even though only 591 unique counts are needed (minor performance issue).

## 2026-06-04 — Artifact Hygiene Fix (DSE-020 summary paths + stale exports + doc status)

### Goal

Fix DSE-020 artifact hygiene: restore generic benchmark reports overwritten by DSE-020 runs, clean stale export dirs from pre-fix first attempt, generate DSE-020-specific summary files, and correct doc status from `done` to `in_progress`.

### Discoveries

1. **Export count discrepancy (566 vs 568)**: `run_export.py` iterates `source_documents` (591 rows). Success count = 566 (25 had 0 resolved facts → skipped). But the triage report counted files on disk via glob, which found 568 — 2 stale dirs from the first (pre-fix) run remained.
2. **Generic reports overwritten**: The 2026-06-04 clause store, fact scoring, and export runs wrote to generic summary paths (`dse010_sqlite_build_summary.json`, `dse011_fact_scoring_summary.json`, `dse013_export_summary.json`), overwriting the canonical 20-policy benchmark reports.
3. **DSE-020 summary paths not used**: CLI flags support `--summary-output` but commands used defaults.
4. **docs/tasks.md incorrectly marked DSE-020 `done`** despite pending artifact hygiene.
5. **IMPLEMENTATION_PLAN.md stale**: said full run still pending.

### Files Changed

- `data/reports/dse010_sqlite_build_summary.json` — restored from git
- `data/reports/dse011_fact_scoring_summary.json` — restored from git
- `data/reports/dse013_export_summary.json` — restored from git
- `data/reports/dse020_sqlite_full_summary.json` — created (591-policy clause store summary)
- `data/reports/dse020_fact_scoring_full_summary.json` — regenerated (591-policy fact scoring summary)
- `data/reports/dse020_export_full_summary.json` — created (566-policy export summary)
- `data/reports/dse020_scale_triage_report_v1.json` — regenerated (corrected export count)
- `data/reports/dse020_scale_triage_report_v1.md` — regenerated
- `data/export/dse020/bajaj_allianz_silver_health/` — removed (stale)
- `data/export/dse020/future_generali_health_elite/` — removed (stale)
- `docs/tasks.md` — DSE-020 set back to `in_progress`
- `IMPLEMENTATION_PLAN.md` — updated current state to 2026-06-04, reflected full run is done
- `dse-020-tracking` — updated Phase 5 checklist with current status
- `runs/sessions/2026-06-03-dse020-full-corpus-scale-triage.md` — this section appended

### Commands Run

```bash
# Restore generic reports from git
git checkout -- data/reports/dse010_sqlite_build_summary.json \
                  data/reports/dse011_fact_scoring_summary.json \
                  data/reports/dse013_export_summary.json

# Identify and remove stale export dirs
rm -rf data/export/dse020/bajaj_allianz_silver_health \
       data/export/dse020/future_generali_health_elite

# Generate DSE-020-specific summaries from DB
python scripts/gen_dse020_summaries.py  # ad-hoc script

# Regenerate triage report
PYTHONPATH=. .venv/bin/python scripts/dse020_triage_report.py \
  --manifest data/manifests/dse020_run_manifest_v1.json \
  --progress-summary data/interim/dse020/progress/summary.json \
  --output-root data/interim/dse020 \
  --db data/engine_dse020.sqlite \
  --export-root data/export/dse020 \
  --json-output data/reports/dse020_scale_triage_report_v1.json \
  --md-output data/reports/dse020_scale_triage_report_v1.md
```

### Results

- Generic 20-policy benchmark reports restored from git.
- 2 stale export dirs cleaned; disk count now 566 (matches DB).
- DSE-020-specific summary files created for all 3 stages.
- Triage report regenerated with correct export count (566).
- `docs/tasks.md`: DSE-020 status corrected to `in_progress`.
- `IMPLEMENTATION_PLAN.md`: current state updated, full run status corrected.

### Issues / Limitations

- `docs/evaluation.md` not yet updated for DSE-020 — deferred.
- Session log not yet finalized.
- DSE-020 must not be marked `done` until final acceptance review.

## 2026-06-04 — Packet 5A — Final Acceptance Checks

### Goal

Run final validation gates for DSE-020: gold corpus validator, source-span validation, full pytest, git hygiene checks.

### Commands Run

```bash
# Gold corpus validator
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
# Source-span validation
PYTHONPATH=. .venv/bin/python scripts/validate_source_spans.py \
  --db data/engine_dse020.sqlite \
  --facts-root data/interim/dse020/facts_resolved \
  --manifest data/manifests/dse020_run_manifest_v1.json \
  --physical-root data/interim/dse020/physical \
  --logical-root data/interim/dse020/logical
# Full pytest
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
# Git hygiene
git diff --check
git status --short
```

### Results

- Gold corpus validator: **PASSED** — 20/20 reviewed policies, 400 facts, 140 JSON files.
- Source-span validation: **ALL CHECKS PASSED** — 591 source_documents, 0 FK violations, source artifact count parity exact (1313480 lines, 59088 sections, 187717 clauses), 548135 valid source_spans, 3759 fact evidence spans all verified, 3628 resolved facts all exist.
- Full pytest: **393/393 PASSED** in 9.55s.
- `git diff --check`: **PASSED** (no whitespace errors).

### Files Changed

- `docs/changelog.md` — added artifact hygiene entry.

### DSE-020 Final Acceptance Summary

| Metric | Value |
|--------|-------|
| Manifest entries | 647 |
| Unique source_documents | 591 |
| Per-policy stage completion | 647/647 (100%) |
| DB ingestion | 591/591 unique docs (56 duplicate-hash skipped) |
| Source-span validation | ALL PASSED |
| Fact scoring | 598/647 manifest entries, 14792 candidates, 3759 facts, 0 conflicts |
| Export | 566/591 policies |
| Policies with zero clauses | 132 |
| Policies with zero fact candidates | 133 |
| Top not_found | claim_intimation_timeline, deductible, icu_limit (566 each) |
| Gold corpus | 20/20 reviewed, PASSED |
| pytest | 393/393 PASSED |
| Generic benchmark reports | Restored from git |
| DSE-020-specific summaries | Created for all 3 stages |
| docs/tasks.md status | `in_progress` (corrected) |

### Acceptance Checklist

- [x] Every active policy attempted: 647/647 per-policy stages.
- [x] End-to-end success/failure reported per stage.
- [x] Export production count reported: 566.
- [x] Frequent not_found, parser failure modes summarized.
- [x] Failures classified (parser/extractor/table/data/human-review).
- [x] Raw PDFs remain read-only.
- [x] Product B files untouched.
- [x] Gold corpus validator passes.
- [x] Full pytest passes (393/393).
- [x] `git diff --check` passes.
- [ ] Status set to `done` in docs/tasks.md — pending Avi's final acceptance.

## 2026-06-04 — Final Consistency Fix

### Goal

Fix remaining doc/report consistency issues for DSE-020 acceptance: sqlite summary manifest/doc counts, triage report date, and validation re-check.

### Changes

1. **`data/reports/dse020_sqlite_full_summary.json`** — added `manifest_policies_total: 647`, `unique_documents_ingested: 591`, `duplicate_hash_entries_skipped: 56`; fixed `policies_skipped_duplicate_hash` from `0` to `56`; `policies_total` now reflects manifest count (647).
2. **`data/reports/dse020_scale_triage_report_v1.json`** — date corrected from `2026-06-03` to `2026-06-04` (via `--date` flag).
3. **`data/reports/dse020_scale_triage_report_v1.md`** — regenerated with correct date; numbers verified: 647 manifest, 591 DB docs, 566 exports, 132 zero-headings/clauses, 133 zero-candidates.

### Validation Re-check

- Gold corpus validator: **PASSED**
- Source-span validation: **ALL CHECKS PASSED**
- Full pytest: **393/393 PASSED** (10.23s)
- `git diff --check`: **PASSED**

### Acceptance

DSE-020 accepted by Avi on 2026-06-04. All gates passed: gold corpus validator, source-span validation, full pytest (393/393), and git hygiene. Status advanced to `done` in docs/tasks.md. Known limitations documented for follow-up tasks (DSE-021, DSE-022).
