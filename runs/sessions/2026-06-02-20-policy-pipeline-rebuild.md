# Session: 20-Policy End-to-End Pipeline Rebuild

Date: 2026-06-02
Task ID: DSE-017
Project: doc-structure-engine
Branch: fix/dse-017-20-policy-pipeline-rebuild
AI executor: opencode + claude-sonnet-4-6
Human reviewer: Avi

## Goal

Prove the full Product A pipeline works at 20-policy scale. Remove hardcoded
5-policy constants from all eval scripts. Rebuild SQLite, fact scoring, and
exports for all 20 reviewed gold policies.

## Changes Made

### Eval scripts — dynamic policy counts (ADR-0035)
- `eval_clause_store.py`: removed `_EXPECTED_COUNTS` hardcoded constant, `!= 5` check, raised DB limit 30MB → 120MB. Policy count derived from gold_corpus.
- `eval_fact_scoring.py`: removed `!= 5` check. Dynamic from gold_corpus.
- `eval_export.py`: removed `!= 5` checks for both policies and derived_policy_features. Dynamic.
- `eval_fact_extractors.py`: removed `!= 5` checks. Uses `_discover_reviewed_policies()`.
- `validate_source_spans.py`: removed hardcoded `_EXPECTED_POLICY_COUNT = 5`. Dynamic from gold_corpus.

### Runner docstrings
- `run_clause_store.py`: "all 5 gold-policy" → "all reviewed gold-policy"
- `run_fact_scoring.py`: "all 5 policies" → "all policies"

## Pipeline Rebuild Results

| Stage | Result |
|-------|--------|
| Gold corpus validator | 20 reviewed policies |
| Fact extractors (5 concepts × 20 policies) | 20/20 processed |
| SQLite clause store | 20/20 ingested, 79.20 MB |
| Fact scoring | 273 candidates, 78 facts, 0 conflicts |
| Export | 20/20 policies exported |

### Structural Eval Results (PASS)

| Eval | Result |
|------|--------|
| Clause store (20 policies) | **PASS** — 20 source_documents, 0 FK violations, 100% span coverage, 79.20 MB |
| Source spans validator | **PASS** — 0 FK violations, 0 provisional IDs, parity matched |

### Initial Gold-Comparison Eval Results (FAIL — superseded by remediation below)

| Eval | Result | Root Cause |
|------|--------|------------|
| Fact extraction | **FAIL** — precision 76.9%, value accuracy 82.2%, 5 false present | Extractor values disagree with 15 new gold annotations |
| Fact scoring | **FAIL** — status accuracy 84%, value accuracy 82.2%, 5 false present | Same root cause |
| Export | **FAIL** — gold_value_accuracy 82.2%, gold_status_accuracy 84%, 5 false present | Same root cause |

### Root Cause Analysis

The 5 deterministic extractors (free_look, grace_period, ped_waiting, initial_waiting, co_pay) were tuned on the original 5 gold policies. On the 15 new policies:

- 5 **false present**: extractor finds a value but gold says not_found (e.g., oriental_cancer_protect/ped_waiting_period, cholamandalam/initial_waiting_period)
- 13 **wrong values**: extractor finds a different value than gold (e.g., Bajaj free_look gold says `{"months": 3}` but extractor correctly finds `{"days": 15}` — gold annotation appears to have annotated the premium refund schedule, not the free look period)

Some of these are genuine extractor errors (over-matching on unfamiliar policy structures). Some are gold annotation quality issues (the pipeline-generated + human-reviewed annotations for the 15 new policies use different value formats or annotated the wrong clause).

**This is NOT a DSE-017 code bug.** It's a known quality gap between:
1. Extractors tuned for 5 policies
2. Gold annotations human-reviewed but not extractor-verified for value accuracy

### Initial Resolution Before Remediation

DSE-017 initially achieved its structural goal but did not meet semantic acceptance. The gold-comparison failures required a remediation pass to either:
- Correct the gold annotations (re-review the 18 disagreeing concept-policy pairs)
- Improve the 5 extractors for broader policy diversity
- Or both

## Commands Run

```bash
git checkout -b fix/dse-017-20-policy-pipeline-rebuild
# [eval script updates]
PYTHONPATH=. python scripts/run_fact_extractors.py --section-root data/interim/logical --output-root data/interim/facts
rm -f data/engine.sqlite
PYTHONPATH=. python scripts/run_clause_store.py --gold-corpus gold_corpus --physical-root data/interim/physical --logical-root data/interim/logical --tables-root data/interim/tables --facts-root data/interim/facts --output-db data/engine.sqlite --output-facts-resolved data/interim/facts_resolved --pipeline-run-id clause_store_dse017_2026_06_02
PYTHONPATH=. python scripts/run_fact_scoring.py --gold-corpus gold_corpus --candidates-root data/interim/facts --resolved-root data/interim/facts_resolved --db data/engine.sqlite --pipeline-run-id fact_scoring_dse017_2026_06_02
PYTHONPATH=. python scripts/run_export.py --db data/engine.sqlite --output-root data/export --pipeline-run-id export_dse017_2026_06_02
# [eval runs]
pytest tests/ --tb=short  # 367 passed
```

## Known Limitations

1. Fact extractor precision drops from ~100% (5 policies) to 77% (20 policies)
2. Gold annotation quality for 15 new policies needs re-verification
3. Table engine eval (R20) still uses 5-policy assumptions — deferred

## Initial Next Step

1. Re-verify gold annotations for the 18 disagreeing concept-policy pairs
2. Improve extractor robustness for diverse policy formats
3. Or: proceed to DSE-014 (LLM refinement) which may supersede narrow extractor fixes

---

## Remediation Pass

### Goal

Resolve the DSE-017 semantic regression without weakening gates:
- audit every failed concept-policy pair against source evidence,
- correct gold only when demonstrably wrong,
- fix extractor behavior only where demonstrably wrong,
- allow value-equivalence only for harmless metadata supersets.

### Files Changed

- `data/reports/dse017_fact_regression_audit.md`
- `extractors/base.py`
- `extractors/deterministic.py`
- `extractors/registry.py`
- `extractors/scoring.py`
- `normalizers/duration.py`
- `structure_parser/section_tree.py`
- `scripts/eval_fact_extractors.py`
- `scripts/eval_fact_scoring.py`
- `scripts/eval_export.py`
- selected `gold_corpus/policies/*/facts.json`
- `tests/test_fact_extractors.py`
- `tests/test_section_tree.py`
- docs/eval/changelog/decisions/risk/tasks updates

### Commands Run

```bash
PYTHONPATH=. .venv/bin/python scripts/run_section_tree.py --heading-root data/interim/logical --physical-root data/interim/physical --output-root data/interim/logical
PYTHONPATH=. .venv/bin/python scripts/run_fact_extractors.py --section-root data/interim/logical --output-root data/interim/facts
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python scripts/eval_fact_extractors.py --facts-root data/interim/facts --gold-corpus gold_corpus --section-root data/interim/logical --output runs/evals/2026-06-02-fact-extraction-dse017-remediation.json
PYTHONPATH=. .venv/bin/python scripts/eval_section_tree.py --output-root data/interim/logical --gold-corpus gold_corpus --output runs/evals/2026-06-02-section-tree-dse017-regression.json
rm -f data/engine.sqlite data/engine.sqlite-wal data/engine.sqlite-shm
PYTHONPATH=. .venv/bin/python scripts/run_clause_store.py --gold-corpus gold_corpus --physical-root data/interim/physical --logical-root data/interim/logical --tables-root data/interim/tables --facts-root data/interim/facts --output-db data/engine.sqlite --output-facts-resolved data/interim/facts_resolved --pipeline-run-id clause_store_dse017_remediation_2026_06_02
PYTHONPATH=. .venv/bin/python scripts/validate_source_spans.py --db data/engine.sqlite --facts-root data/interim/facts_resolved
PYTHONPATH=. .venv/bin/python scripts/eval_clause_store.py --db data/engine.sqlite --facts-root data/interim/facts_resolved --gold-corpus gold_corpus --physical-root data/interim/physical --logical-root data/interim/logical --output runs/evals/2026-06-02-clause-store-dse017-remediation.json
PYTHONPATH=. .venv/bin/python scripts/run_fact_scoring.py --gold-corpus gold_corpus --candidates-root data/interim/facts --resolved-root data/interim/facts_resolved --db data/engine.sqlite --pipeline-run-id fact_scoring_dse017_remediation_2026_06_02
PYTHONPATH=. .venv/bin/python scripts/eval_fact_scoring.py --db data/engine.sqlite --candidates-root data/interim/facts --resolved-root data/interim/facts_resolved --gold-corpus gold_corpus --output runs/evals/2026-06-02-fact-scoring-dse017-remediation.json
PYTHONPATH=. .venv/bin/python scripts/run_export.py --db data/engine.sqlite --output-root data/export --pipeline-run-id export_dse017_remediation_2026_06_02
PYTHONPATH=. .venv/bin/python scripts/eval_export.py --db data/engine.sqlite --export-root data/export --gold-corpus gold_corpus --output runs/evals/2026-06-02-export-dse017-remediation.json
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
```

### Results

| Eval | Result |
|------|--------|
| Gold corpus validator | PASS — 20 reviewed policies, 400 facts |
| Section tree diagnostic | FAIL — 19/20 pass; Oriental Cancer Protect remains below tree-accuracy threshold with 100% section/clauses F1 |
| Source spans validator | PASS — 0 FK violations, source count parity matched |
| Clause store | PASS — 20 policies, 56,854 lines, 4,190 sections, 10,330 clauses, 26,405 source spans, 82.31 MB |
| Fact extraction | PASS — 83/83 present facts matched, 0 false present |
| Fact scoring | PASS — 282 candidates, 83 facts, 100% status/value/evidence accuracy |
| Export | PASS — 20 exports, all 20 concept fields present, 100% gold status/value accuracy for implemented concepts |

### Decisions Made

- DSE-017 remains a 5-concept scale-validation task. The remaining 15 concept extractors are deferred.
- Source-PDF-backed gold fixes are allowed only when the prior annotation points to the wrong fact.
- Predicted metadata supersets are equivalent only when every gold scalar key matches exactly.

### Issues / Limitations

- Some fact evidence uses clause-level degraded spans because column-interleaved PDF text prevents exact substring offsets.
- The diagnostic section-tree eval still fails Oriental Cancer Protect tree accuracy; this is not a DSE-017 acceptance gate and remains a parser-quality follow-up.
- Table engine 20-policy eval modernization remains tracked separately under R20.
- Coverage is still limited to the 5 deterministic concepts implemented in DSE-007.

### Next Step

Proceed to the next scoped task after review/commit. The strongest next options are expanding deterministic extractors beyond 5 concepts or modernizing the 20-policy table eval.
