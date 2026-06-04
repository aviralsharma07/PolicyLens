# Session: DSE-024 Phase E2 — Section Tree Rebuild for 44 section_tree_fail Policies

Date: 2026-06-04
Task ID: DSE-024
Project: doc-structure-engine
Branch: feat/dse-024-parser-remediation
AI executor: opencode + deepseek-v4-flash-free
Human reviewer: Avi

## Goal

Fix the 44 `section_tree_fail` policies from DSE-024 Phase E1 classification by rebuilding the section tree from post-fallback heading candidates. Verify no regression, update docs.

## Relevant Docs Read

- AGENTS.md, docs/tasks.md, docs/changelog.md
- DSE-024 phase E1 classification report
- structure_parser/section_tree.py
- structure_parser/clause_segmenter.py
- scripts/run_section_tree.py
- DSE-020 fallback session log

## Investigation

No code changes were found necessary. Section tree builder already:
- Filters by `decision == "heading"` — fallback-promoted headings consumed identically to normal headings.
- Handles compact headings (`10.Renewal`) via `ARABIC_NUMBER_RE` regex.
- Handles alpha headings (`D. BENEFITS:`) — `_infer_level` returns 1; `_extract_number_from_heading` returns None.
- Handles ICICI Lombard `0.25 years` edge case (numbering_token=0.25) without error.

## Files Changed

- `data/interim/dse020/logical/*/section_tree.json` — 647 files regenerated (overwritten).
- `data/interim/dse020/logical/section_tree_run_summary.json` — regenerated summary.
- `data/reports/dse020_scale_triage_report_v1.json` — regenerated.
- `data/reports/dse020_scale_triage_report_v1.md` — regenerated.
- `data/reports/dse024_section_tree_fail_investigation_v1.md` — created (investigation report).
- `runs/evals/2026-06-04-heading-scorer-dse024-e2.json` — new gold heading eval.
- `runs/evals/2026-06-04-section-tree-dse024-e2.json` — new gold section tree eval.
- `docs/changelog.md` — updated with E2 results.
- `docs/tasks.md` — updated with E2 results and acceptance criteria.
- `runs/sessions/2026-06-04-dse024-phase-e2-section-tree-rebuild.md` — this file.

## Commands Run

```bash
PYTHONPATH=. .venv/bin/python scripts/run_section_tree.py \
  --heading-root data/interim/dse020/logical \
  --physical-root data/interim/dse020/physical \
  --output-root data/interim/dse020/logical

PYTHONPATH=. .venv/bin/python scripts/dse020_triage_report.py \
  --manifest data/manifests/dse020_run_manifest_v1.json \
  --progress-summary data/interim/dse020/progress/summary.json \
  --output-root data/interim/dse020 \
  --db data/engine_dse020.sqlite \
  --export-root data/export/dse020 \
  --json-output data/reports/dse020_scale_triage_report_v1.json \
  --md-output data/reports/dse020_scale_triage_report_v1.md \
  --date 2026-06-04

PYTHONPATH=. .venv/bin/python scripts/eval_heading_scorer.py \
  --candidates-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-04-heading-scorer-dse024-e2.json

PYTHONPATH=. .venv/bin/python scripts/eval_section_tree.py \
  --output-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-04-section-tree-dse024-e2.json

PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
```

## Results

| Metric | E1 (before) | E2 (after) |
|---|---|---:|
| section_tree_fail policies | 44 | **0** (resolved) |
| Zero-clause policies | 110 | **58** |
| Zero-heading policies | 84 | **58** |
| Gold heading eval | 20/20 PASS | **20/20 PASS** |
| Gold section tree eval | 19/20 FAIL | **19/20 FAIL** (pre-existing) |
| Gold corpus validation | PASS | **PASS** |
| Full pytest | 400/400 PASS | **400/400 PASS** |
| Section tree errors | N/A | **0/647** |

## Generated Artifacts

- `data/reports/dse024_section_tree_fail_investigation_v1.md` — investigation report.
- `runs/evals/2026-06-04-heading-scorer-dse024-e2.json` — heading eval.
- `runs/evals/2026-06-04-section-tree-dse024-e2.json` — section tree eval.
- Regenerated `data/reports/dse020_scale_triage_report_v1.json` and `.md`.

## Decisions Made

- No code changes needed. Section tree builder already handles fallback-promoted headings correctly.
- Gold evals use `data/interim/logical` (gold-pipeline outputs) to test code correctness, not full-corpus pipeline quality.
- Stop E2 here. Do NOT start heading_miss fixes (Phase E3).

## Issues / Limitations

- 58 policies still have zero clauses (heading_miss: 34, duplicate: 14, needs_review: 10, non_policy: 6, unsupported: 2).
- Full-corpus pipeline heading quality for gold policies (aditya_birla_activ_care, tata_aig_arogya_sanjeevani) is worse than gold-pipeline — pre-existing issue, not caused by section tree rebuild.

## Next Step

Tackle 34 heading_miss policies with format-specific heading pattern additions.
