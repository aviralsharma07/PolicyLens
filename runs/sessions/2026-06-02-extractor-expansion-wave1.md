# Session: Deterministic Extractor Expansion Wave 1

Date: 2026-06-02
Task ID: DSE-018
Project: doc-structure-engine
Branch: feat/dse-018-extractor-expansion-wave1
AI executor: opencode + Codex
Human reviewer: Avi

## Goal

Finish DSE-018 by closing the final Wave 1 extractor mismatches, fixing stale tests, auditing source-backed gold/extractor decisions, and running the full acceptance chain.

## Relevant Docs Read

- AGENTS.md
- docs/tasks.md
- docs/evaluation.md
- docs/changelog.md
- docs/decisions.md
- docs/risk_register.md
- runs/sessions/2026-06-02-20-policy-pipeline-rebuild.md
- data/reports/dse017_fact_regression_audit.md

## Files Changed

- extractors/deterministic.py
- tests/test_fact_extractors.py
- selected gold_corpus/policies/*/facts.json
- clause_store/span_builder.py
- clause_store/fact_resolver.py
- data/reports/dse018_wave1_mismatch_audit.md
- docs/tasks.md
- docs/evaluation.md
- docs/changelog.md
- docs/decisions.md
- docs/risk_register.md
- runs/sessions/2026-06-02-extractor-expansion-wave1.md

## Commands Run

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/test_fact_extractors.py tests/test_normalizers/test_normalizers.py --tb=short
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python scripts/run_fact_extractors.py --section-root data/interim/logical --output-root data/interim/facts
PYTHONPATH=. .venv/bin/python scripts/eval_fact_extractors.py --facts-root data/interim/facts --gold-corpus gold_corpus --section-root data/interim/logical --output runs/evals/2026-06-02-fact-extraction-dse018-final.json
rm -f data/engine.sqlite data/engine.sqlite-wal data/engine.sqlite-shm
PYTHONPATH=. .venv/bin/python scripts/run_clause_store.py --gold-corpus gold_corpus --physical-root data/interim/physical --logical-root data/interim/logical --tables-root data/interim/tables --facts-root data/interim/facts --output-db data/engine.sqlite --output-facts-resolved data/interim/facts_resolved --pipeline-run-id clause_store_dse018_final_2026_06_02
PYTHONPATH=. .venv/bin/python scripts/validate_source_spans.py --db data/engine.sqlite --facts-root data/interim/facts_resolved
PYTHONPATH=. .venv/bin/python scripts/eval_clause_store.py --db data/engine.sqlite --facts-root data/interim/facts_resolved --gold-corpus gold_corpus --physical-root data/interim/physical --logical-root data/interim/logical --output runs/evals/2026-06-02-clause-store-dse018-final.json
PYTHONPATH=. .venv/bin/python scripts/run_fact_scoring.py --gold-corpus gold_corpus --candidates-root data/interim/facts --resolved-root data/interim/facts_resolved --db data/engine.sqlite --pipeline-run-id fact_scoring_dse018_final_2026_06_02
PYTHONPATH=. .venv/bin/python scripts/eval_fact_scoring.py --db data/engine.sqlite --candidates-root data/interim/facts --resolved-root data/interim/facts_resolved --gold-corpus gold_corpus --output runs/evals/2026-06-02-fact-scoring-dse018-final.json
PYTHONPATH=. .venv/bin/python scripts/run_export.py --db data/engine.sqlite --output-root data/export --pipeline-run-id export_dse018_final_2026_06_02
PYTHONPATH=. .venv/bin/python scripts/eval_export.py --db data/engine.sqlite --export-root data/export --gold-corpus gold_corpus --output runs/evals/2026-06-02-export-dse018-final.json
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
```

## Results

Focused tests passed:

```text
33 passed
```

Gold corpus validator passed:

```text
20 reviewed policies
400 facts
140 annotation JSON files
```

Fact extraction final eval passed:

```json
{
  "policies_passed": 20,
  "deterministic_present_precision": 1.0,
  "deterministic_present_recall": 0.994924,
  "normalized_value_accuracy": 1.0,
  "status_accuracy": 0.984615,
  "evidence_accuracy": 1.0,
  "false_present_for_gold_not_found": 0
}
```

Full acceptance chain:

| Gate | Result |
|---|---|
| Source-span validator | PASS — 20 docs, 0 FK violations, source-count parity matched, 203 fact evidence spans with offsets |
| Clause-store eval | PASS — 20 policies, 56,854 lines, 4,190 sections, 10,330 clauses, 0 provisional resolved evidence IDs, DB 82.45 MB |
| Fact scoring eval | PASS — 746 candidates, 203 facts, status accuracy 98.5%, normalized value accuracy 97.5%, evidence accuracy 100.0%, false-present 0 |
| Export eval | PASS — 20 exports, 20/20 concepts per policy, gold status accuracy 98.5%, gold value accuracy 97.5%, false-present 0 |
| Full pytest | PASS — 382/382 |

## Decisions Made

- Claim settlement Wave 1 canonical value is primary settlement/rejection days. Investigation extension is included only when the accepted evidence safely supports it.
- Specific disease waiting periods use `months_options` and parse compact slash notation.
- Maternity waiting treats `not covered until N months` as a waiting period, not as an absolute exclusion.
- Reliance Health Gain claim settlement remains a precision-first `not_found` because the source-correct 30-day value is missing from current section-tree clauses.
- `explicitly_not_covered` facts with evidence are resolved to source spans in DSE-010 outputs, same as `present` facts.

## Issues / Limitations

- Reliance Health Gain exposes clause fragmentation: the source PDF has the 30-day settlement line, but current DSE-006 output omits that duration from clauses consumed by extractors.
- Some earlier DSE-018 iteration eval files are diagnostic artifacts from the executor and are not the final gate.

## Next Step

Commit after final `git diff --check` and `git status --short` review.
