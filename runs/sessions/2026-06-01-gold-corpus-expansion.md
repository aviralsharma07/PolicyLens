# Session: Gold Corpus Expansion — Phase A-C

Date: 2026-06-01
Task ID: DSE-012
Project: doc-structure-engine
Branch: feat/dse-012-gold-corpus-expansion
AI executor: opencode + claude-sonnet-4-6
Human reviewer: Avi
Status: in_progress — paused at human review (Phase D)

## Goal

Expand gold evaluation corpus from 5 to 20 policies. Build pipeline batch
infrastructure, select 15 new policies for diversity, run the full pipeline,
generate draft gold annotations, and create structured review reports for
targeted human review.

## Phase A: Infrastructure

Built:
- `scripts/run_pipeline_batch.py` — full pipeline orchestrator
- `scripts/generate_draft_gold.py` — pipeline output → draft gold converter
- `scripts/gold_review_report.py` — per-policy human review report generator

## Phase B: Pipeline Execution

- Selected 15 policies across 15 unrepresented insurers
- Manifest saved: `data/manifests/dse012_gold_expansion_candidates_v1.json`
- Rationale: `data/reports/dse012_policy_selection_rationale.md`
- Pipeline: **15/15 policies, 75/75 stages passed**, 0 failures
- 595 pages parsed, 44,139 lines, 6,279 clauses, 600 tables, 75 extracted facts

## Phase C: Draft Gold Generation

- 15 × 7 = 105 draft annotation files generated under `gold_corpus/policies/`
- Every file marked `label_status: draft`, `annotation_method: pipeline_draft`
- 300 draft fact annotations (20 concepts × 15 policies)
- Review reports generated: `data/reports/dse012_review/review_report.md`
- Priority breakdown: 2 CRITICAL, 2 HIGH, 11 NORMAL

## Phase D: Human Review (PENDING)

Awaiting human review of 15 draft policies. Review report has recommended
order and per-policy findings. CRITICAL policies (Tata AIG, Aditya Birla)
have degenerate section trees — heading scorer found no visual headings.

## Files Changed

### Created
- `scripts/run_pipeline_batch.py`
- `scripts/generate_draft_gold.py`
- `scripts/gold_review_report.py`
- `data/manifests/dse012_gold_expansion_candidates_v1.json`
- `data/reports/dse012_policy_selection_rationale.md`
- `data/reports/dse012_pipeline_batch_summary.json`
- `data/reports/dse012_draft_gold_summary.json`
- `data/reports/dse012_review/review_report.md` + 15 per-policy JSON reviews
- `gold_corpus/policies/{15_new_slugs}/` — 7 files each (105 total)

### Modified
- `identity/plan_normalizer.py` — NBSP normalization + broad legal entity suffix stripping
- `scripts/validate_gold_corpus.py` — 20-policy support, draft vs reviewed, structural sanity checks
- `scripts/gold_review_report.py` — elevated priority for low heading label counts
- `docs/tasks.md`, `docs/changelog.md`

## Known Issues

1. **Tata AIG + Aditya Birla**: degenerate section trees (0 clauses). Heading scorer found no visual headings in these PDF formats. Not a DSE-012 code bug — it's a DSE-005 heading scorer limitation on new formatting patterns.
2. **Niva Bupa + Royal Sundaram**: very few heading labels (1-2) despite hundreds of sections — heading detection partially worked but missed most headings.
3. **15 concepts per policy need manual annotation** — no extractors implemented for those concepts yet.
4. **NBSP in lifecycle product names** — fixed in plan_normalizer.py with `\xa0 → space` normalization.

## Commands Run

```bash
git checkout -b feat/dse-012-gold-corpus-expansion
PYTHONPATH=. python scripts/run_pipeline_batch.py --manifest data/manifests/dse012_gold_expansion_candidates_v1.json
PYTHONPATH=. python scripts/generate_draft_gold.py --manifest data/manifests/dse012_gold_expansion_candidates_v1.json
PYTHONPATH=. python scripts/gold_review_report.py --manifest data/manifests/dse012_gold_expansion_candidates_v1.json
PYTHONPATH=. python scripts/validate_gold_corpus.py  # 20 policies: 5 reviewed + 15 draft
PYTHONPATH=. python -m pytest tests/ --tb=short  # 367 passed
```

## Next Step

Human review of 15 draft policies using `data/reports/dse012_review/review_report.md`.
After review: promote labels, re-run full pipeline at 20-policy scale, update docs.
