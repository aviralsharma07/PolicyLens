# Session: DSE-005 — Heading Candidate Scorer v1

Date: 2026-05-30
Task ID: DSE-005
Project: doc-structure-engine
Branch: fix/dse-005-heading-scorer-gates
AI executor: opencode + Codex review/remediation
Human reviewer: Avi

## Goal
Implement scored heading detection with weighted features to identify visual headings from physical layout lines, per ADR-0004. Remediate the failed v1 eval by separating visual heading labels from logical section labels and making the eval one-to-one/page-aware.

## Relevant Docs Read
- IMPLEMENTATION_PLAN.md (Day 5 spec, lines 554-581)
- docs/adr/0004-scored-heading-detection.md
- docs/data_contracts.md (Contract 3)
- docs/evaluation.md (Heading/Section Parser eval)
- scripts/eval_heading_scorer.py
- scripts/run_heading_scorer.py
- scripts/validate_gold_corpus.py
- pdf_parser/models.py (Span, Line, Page, PhysicalDocument)

## Files Changed
- `structure_parser/__init__.py` — package init
- `structure_parser/heading_patterns.py` — numbering regexes, heading dictionary, text classification helpers
- `structure_parser/heading_scorer.py` — scorer with spacing feature, boilerplate penalty, and enriched candidate metadata
- `scripts/run_heading_scorer.py` — CLI entry point with run summary and non-zero exit on missing inputs
- `scripts/eval_heading_scorer.py` — one-to-one page-aware eval against visual heading labels
- `scripts/validate_gold_corpus.py` — validates heading label files
- `tests/test_heading_scorer.py` — unit, eval matching, CLI, and gold integration tests
- `tests/test_gold_corpus_validator.py` — updated expected JSON/heading-label counts
- `gold_corpus/policies/*/heading_labels.json` — 101 visual-heading labels
- `docs/tasks.md` — DSE-005 marked done after v2 gates passed
- `docs/changelog.md` — DSE-005 entry added
- `docs/evaluation.md` — DSE-005 visual heading gates split from DSE-006 section/clause gates
- `docs/data_contracts.md` — Heading Scorer Output contract added for DSE-006
- `docs/decisions.md` — decision to separate visual heading labels from logical sections
- `pyproject.toml` — registered `slow` pytest marker

## Commands Run
```bash
# Tests
.venv/bin/python -m pytest tests/test_heading_scorer.py -v
PYTHONPATH=/private/tmp/dse004_deps:. python3 -m pytest tests/ --tb=short

# Score all 5 gold policies at threshold 0.5
PYTHONPATH=. .venv/bin/python scripts/run_heading_scorer.py \
  --physical-root data/interim/physical \
  --output-root data/interim/logical \
  --threshold 0.5

# Eval against gold corpus
PYTHONPATH=. .venv/bin/python scripts/eval_heading_scorer.py \
  --candidates-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-05-30-heading-scorer-v1.json

# Remediated eval against visual-heading labels
PYTHONPATH=/private/tmp/dse004_deps:. python3 scripts/eval_heading_scorer.py \
  --candidates-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-05-30-heading-scorer-v2.json

python3 scripts/validate_gold_corpus.py
PYTHONPATH=/private/tmp/dse004_deps:. python3 scripts/validate_physical_outputs.py \
  --gold-corpus gold_corpus \
  --physical-root data/interim/physical \
  --debug-root data/reports/physical_debug
git diff --check
```

## Results
- v1 eval failed: 0/5 policies passed. The eval target was wrong because it matched visual heading candidates against all logical section rows.
- v2 eval passed: 5/5 policies passed.
- DSE-005 v2 precision/recall/F1: 100.00% for all 5 policies against 101 visual-heading labels.
- Tests: full suite passed.
- Gold corpus validator passed with 30 policy JSON files and 101 heading labels.
- Physical output validator passed for all 5 policies.

## Generated Artifacts
- `data/interim/logical/care_health_care_plus/heading_candidates.json`
- `data/interim/logical/hdfc_arogya_sanjeevani/heading_candidates.json`
- `data/interim/logical/icici_family_shield/heading_candidates.json`
- `data/interim/logical/new_india_floater/heading_candidates.json`
- `data/interim/logical/star_medi_classic_accident/heading_candidates.json`
- `data/interim/logical/heading_run_summary.json`
- `gold_corpus/policies/*/heading_labels.json`
- `runs/evals/2026-05-30-heading-scorer-v1.json`
- `runs/evals/2026-05-30-heading-scorer-v2.json`

## Decisions Made
- font_size_ratio changed from continuous to binary: scored lines get +0.25 only if ratio > 1.0 (avoids giving body-sized lines free points)
- Numbering patterns expanded: compact patterns (`1.TEXT`, `3.2TEXT`), SECTION/PART prefix (no length restriction)
- Heading dict tightened: only match on text start after stripping leading number
- Numbered definition penalty (-0.15): fires when line is numbered AND long AND not all caps
- DSE-005 now uses visual-heading labels separate from DSE-003 logical sections.
- DSE-006 should handle section tree and logical definition/list entries via hierarchical context.

## Issues / Limitations
- DSE-005 only evaluates visual heading candidate detection. DSE-006 still needs section tree accuracy and clause boundary F1 gates.
- ICICI headings same font size as body, so the scorer relies heavily on bold/spacing/numbering.
- Visual-heading labels were introduced in remediation and should be reviewed again when gold corpus expands to 20 policies.

## Next Step
DSE-005 is ready for user review. If accepted, commit this branch and then plan DSE-006 Section Tree Builder.
