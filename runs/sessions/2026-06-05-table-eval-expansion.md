# Session: DSE-022 Packet 0 — Roadmap Hygiene

Date: 2026-06-05
Task ID: DSE-022
Project: doc-structure-engine
Branch: fix/dse-022-table-eval-20-policy
AI executor: opencode
Human reviewer: Avi

## Goal

Update docs to reflect current project state before DSE-022 table eval work begins. Move DSE-022 from Backlog to Active Sprint, update IMPLEMENTATION_PLAN.md with all 20 concepts active and DSE-021/DSE-024 done, create session log.

## Relevant Docs Read

- docs/tasks.md
- IMPLEMENTATION_PLAN.md
- runs/sessions/2026-06-04-extractor-wave2.md

## Files Changed

- docs/tasks.md — Packet 0: removed DSE-022 from Backlog; changed DSE-022 detail status to in_progress; changed "full-corpus eval gates" to "20-policy gold benchmark gates"
- IMPLEMENTATION_PLAN.md — Packet 0: replaced "full-corpus eval gates" with "20-policy gold benchmark gates"
- scripts/eval_table_engine.py — Packet 1: dynamic reviewed-policy discovery; zero-label policy handling (no_physical_labels); automated legacy disposition for all 395 rows across 20 policies; DSE-022 eval gate replacing hardcoded 5-policy gate
- tests/test_table_engine.py — Packet 1: tests for discover_reviewed_policies, physical label mapping, legacy dispositions (physical_table_eval, diagnostic_nonpriority_table, deferred_needs_pdf_review), no legacy rows without disposition
- tests/test_gold_corpus_validator.py — Packet 1: updated physical_table_labels assertion from >=10 to ==387
- docs/evaluation.md — Packet 1: updated Table Extraction eval section (hard gates now say "all reviewed policies evaluated"; DSE-022 baseline section added; summary table updated)
- runs/sessions/2026-06-05-table-eval-expansion.md — Packet 0 + Packet 1 session log
- data/reports/dse022_legacy_table_dispositions_v1.json — new: all 395 legacy rows classified
- data/reports/dse022_legacy_table_dispositions_v1.md — new: markdown disposition report
- runs/evals/2026-06-05-table-engine-dse022-baseline.json — new: DSE-022 baseline eval artifact
- data/reports/dse009_gold_table_source_review.json — regenerated (20-policy dispositions now)
- data/reports/dse009_gold_table_source_review.md — regenerated (20-policy dispositions now)

## Commands Run

```bash
git checkout -b fix/dse-022-table-eval-20-policy
scripts/validate_gold_corpus.py

# Packet 1
PYTHONPATH=. .venv/bin/python scripts/eval_table_engine.py \
  --gold-corpus gold_corpus \
  --tables-root data/interim/tables \
  --output runs/evals/2026-06-05-table-engine-dse022-baseline.json

PYTHONPATH=. .venv/bin/python -m pytest tests/test_table_engine.py tests/test_gold_corpus_validator.py --tb=short
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
git diff --check
git status --short
```

## Results

Packet 0 — Roadmap hygiene:
- DSE-022 moved to Active Sprint, status in_progress.
- "full-corpus eval gates" replaced with "20-policy gold benchmark gates" in tasks.md and IMPLEMENTATION_PLAN.md.

Packet 1 — DSE-022 baseline:
- Eval accounts for all 20 reviewed policies: PASSED.
- 19 policies with physical labels evaluated, 1 policy (tata_aig_arogya_sanjeevani) explicitly recorded as `no_physical_labels`.
- 387/387 physical table labels detected (100% recall).
- Type accuracy: 99.74%. Priority detection recall: 100%.
- Header lineage pass rate: 100%.
- 0 unrecorded missing cell bboxes.
- All 395 legacy `tables.json` rows have a documented disposition:
  - 373 physical_table_eval (linked to physical labels)
  - 11 prose_summary_not_table
  - 4 wrong_page_or_wrong_type
  - 7 deferred_needs_pdf_review (all with explicit DSE-009 reasons)
- 73/73 tests pass.
- Gold corpus validator: PASSED.
- No table extraction behavior changed.

## Generated Artifacts

- runs/sessions/2026-06-05-table-eval-expansion.md

## Decisions Made

- DSE-022 active sprint; DSE-021 and DSE-024 marked done.
- Scale triage reports and evaluation.md left as-is (timestamped artifacts, Packet 0 scope only).

## Issues / Limitations

- Integration tests skipped unless `data/interim/tables/` is populated and `@pytest.mark.slow` is enabled.
- DSE-009 source review files overwritten during eval (they now reflect 20-policy dispositions).
- 196 tables across the 20-policy corpus have recorded missing cell bbox issues (pdfplumber limitation, not a gold gap).
- 7 legacy rows remain `deferred_needs_pdf_review` from the original DSE-009 manual review; all have explicit reasons.

## Next Step

Packet 2: Run targeted table extraction fixes if the honest gate exposes real failures.
