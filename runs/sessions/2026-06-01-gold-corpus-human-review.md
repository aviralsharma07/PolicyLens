# Session: Gold Corpus Human Review

Date: 2026-06-01
Task ID: DSE-012
Project: doc-structure-engine
Branch: feat/dse-012-gold-corpus-expansion
AI executor: Codex GPT-5
Human reviewer: Avi

## Goal

Complete the human-review phase for the 15 DSE-012 draft policies and promote them to reviewed gold annotations.

## Relevant Docs Read

- AGENTS.md
- IMPLEMENTATION_PLAN.md
- docs/evaluation.md
- docs/tasks.md
- docs/changelog.md
- docs/risk_register.md
- gold_corpus/annotation_guide.md
- data/reports/dse012_review/review_report.md

## Files Changed

- gold_corpus/policies/{15 new policy folders}/metadata.json
- gold_corpus/policies/{15 new policy folders}/sections.json
- gold_corpus/policies/{15 new policy folders}/clauses.json
- gold_corpus/policies/{15 new policy folders}/tables.json
- gold_corpus/policies/{15 new policy folders}/facts.json
- gold_corpus/policies/{15 new policy folders}/heading_labels.json
- gold_corpus/policies/{15 new policy folders}/physical_table_labels.json
- scripts/human_review_dse012_gold.py
- scripts/validate_gold_corpus.py
- docs/tasks.md
- docs/evaluation.md
- docs/changelog.md
- docs/risk_register.md

## Commands Run

```bash
PYTHONPATH=. .venv/bin/python scripts/human_review_dse012_gold.py
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python scripts/eval_heading_scorer.py --candidates-root data/interim/logical --gold-corpus gold_corpus --output runs/evals/2026-06-01-heading-scorer-dse012-reviewed.json
PYTHONPATH=. .venv/bin/python scripts/eval_section_tree.py --output-root data/interim/logical --gold-corpus gold_corpus --output runs/evals/2026-06-01-section-tree-dse012-reviewed.json
PYTHONPATH=. .venv/bin/python scripts/eval_table_engine.py --gold-corpus gold_corpus --tables-root data/interim/tables --output runs/evals/2026-06-01-table-engine-dse012-reviewed.json
PYTHONPATH=. .venv/bin/python scripts/eval_fact_extractors.py --facts-root data/interim/facts --gold-corpus gold_corpus --section-root data/interim/logical --output runs/evals/2026-06-01-fact-extraction-dse012-reviewed.json
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
```

## Results

- Gold corpus validator passed.
- 20/20 policies are reviewed.
- 140 annotation JSON files exist.
- 400 reviewed fact annotations exist.
- 0 draft policies remain.
- 0 draft markers remain in the 15 promoted policy annotation files.
- Original 5 reviewed policies were not changed.
- Full pytest passed: 367 passed.
- `git diff --check` passed.

## Generated Artifacts

- data/reports/dse012_human_review/human_review_summary.md
- data/reports/dse012_human_review/human_review_summary.json
- data/reports/dse012_human_review/*_review.md
- data/reports/dse012_human_review/*_review.json
- runs/evals/2026-06-01-gold-corpus-dse012-reviewed.json
- runs/evals/2026-06-01-heading-scorer-dse012-reviewed.json
- runs/evals/2026-06-01-section-tree-dse012-reviewed.json
- runs/evals/2026-06-01-table-engine-dse012-reviewed.json
- runs/evals/2026-06-01-fact-extraction-dse012-reviewed.json

## Decisions Made

- Treat source PDFs as authority and pipeline output as draft scaffolding.
- Promote all 15 new policies only after source-PDF text review.
- Record expanded parser eval failures as downstream parser remediation findings, not as blockers to completing the gold annotation task.

## Issues / Limitations

- Tata AIG and Aditya Birla required manual section/heading/clauses rebuilds because DSE-005/DSE-006 produced degenerate structures.
- 20-policy heading eval fails on Tata AIG and Aditya Birla.
- 20-policy section eval fails on Tata AIG, Aditya Birla, and Oriental Cancer Protect.
- Table eval script still has 5-policy-era hard-gate assumptions and needs a later reporting/gate update.

## Next Step

Use the expanded corpus to prioritize parser remediation for flattened/all-caps heading formats before relying on 20-policy parser gates.
