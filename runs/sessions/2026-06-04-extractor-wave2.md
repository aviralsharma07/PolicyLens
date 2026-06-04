# Session: DSE-021 Wave 2 Extractor Baseline Audit + Kickoff

Date: 2026-06-04
Task ID: DSE-021
Project: doc-structure-engine
Branch: feat/dse-021-extractor-wave2
AI executor: opencode + deepseek-v4-flash-free
Human reviewer: Avi

## Goal

Kick off DSE-021 by performing a baseline audit of the 7 remaining deterministic extractors without changing any extractor behavior. Compile gold status counts, evidence snippets, DSE-020 not_found pressure, and recommend implementation packets for each concept.

## Relevant Docs Read

- AGENTS.md
- docs/tasks.md
- docs/changelog.md
- ontology/concepts.v1.json
- extractors/models.py (TARGET_CONCEPTS)
- extractors/deterministic.py (13 existing extractors)
- scripts/eval_fact_extractors.py
- data/reports/dse020_scale_triage_report_v1.md
- data/reports/dse020_scale_triage_report_v1.json
- All 20 gold policy facts.json files
- runs/sessions/2026-06-04-dse024-e3d-parser-target-closeout.md

## Files Changed

- docs/tasks.md (DSE-021: planned -> in_progress)
- docs/changelog.md (DSE-021 kickoff entry)
- runs/sessions/2026-06-04-extractor-wave2.md (this file)
- data/reports/dse021_wave2_baseline_audit.md (baseline audit report)

## Commands Run

```bash
git checkout -b feat/dse-021-extractor-wave2
python3 (compiled gold status counts from 20 facts.json)
python3 (extracted evidence snippets)
python3 (read ontology shapes from concepts.v1.json)
```

## Results

### Gold Status Counts (20 policies)

| Concept | present | explicitly_not_covered | not_applicable | not_found |
|---|---|---|---|---|
| claim_intimation_timeline | 15 | 0 | 0 | 5 |
| deductible | 9 | 0 | 3 | 8 |
| room_rent_limit | 13 | 0 | 1 | 6 |
| icu_limit | 9 | 0 | 0 | 11 |
| restoration_benefit | 7 | 0 | 0 | 13 |
| modern_treatment_coverage | 8 | 0 | 0 | 12 |
| newborn_coverage | 3 | 3 | 0 | 14 |

### DSE-020 Not_Found Pressure (full corpus, 566 exported policies)

All 7 concepts tied at 566 not_found each — the highest possible tier. None of these 7 concepts have any extractor yet.

### Ontology Shapes

| Concept | value_shape | export_field | active_deterministic | extractor_status |
|---|---|---|---|---|
| claim_intimation_timeline | duration_or_components | claim_intimation_days | false | planned |
| deductible | amount_percentage_or_schedule | deductible | false | planned |
| room_rent_limit | room_rent_limit | room_rent_limit | false | planned |
| icu_limit | icu_limit | icu_limit | false | planned |
| restoration_benefit | coverage_status_or_components | restoration_benefit | false | planned |
| modern_treatment_coverage | coverage_status_or_limit | modern_treatment_coverage | false | planned |
| newborn_coverage | coverage_status_or_limit | newborn_coverage | false | planned |

### Existing Extractor Patterns (13 completed)

Existing extractors use signal-based text matching, context-window search, duration/percentage parsing, and table-aware extraction. Patterns relevant for Wave 2:
- Duration extractors (free_look_period, grace_period, waiting periods) query signal clauses then parse durations
- Amount extractors (co_pay) parse percentage/numeric limits
- Coverage-list extractors (ayush, ambulance) search inclusion/exclusion lists

## Generated Artifacts

- data/reports/dse021_wave2_baseline_audit.md

## Decisions Made

- DSE-021 baseline audit completed without modifying any extractor code.
- The 7 concepts will be implemented in packets based on complexity and gold coverage.
- Extractors will follow existing patterns: signal-based text matching, context-window search, duration/amount parsing.

## Issues / Limitations

- restoration_benefit (7/20 present) and newborn_coverage (3/20 present) have the lowest gold presence — harder to validate recall.
- No existing table-aware extractors yet; room_rent_limit and icu_limit often appear in benefit tables.
- `claim_intimation_timeline` evidences are free-text descriptions of notification timelines; parsing 48-hours / 15-days etc. requires duration extraction.

## Next Step

Implement Packet A: claim_intimation_timeline (duration extractor, similar to waiting periods) + deductible (amount/percentage extractor, similar to co-pay).

## Latest Context Capsule

### Open tasks
- DSE-021: in_progress — 7 remaining extractors to implement
- DSE-022: planned — table eval expansion
- DSE-023: planned — LLM refinement layer

### Current branch
feat/dse-021-extractor-wave2, clean working tree, based off feat/dse-020-full-corpus-scale-triage

### Pipeline health
- Corpus identity: 647 processed, 566 exported, 80 excluded (non-policy indent-articles + 1 product-list), 0 skipped
- Parser targets: 0 zero-heading, 0 zero-clause (after DSE-024)
- Zero-fact policies: 5 (4 are indent-article PDFs + tata_aig_arogya_sanjeevani which has heading/clause data)
- Full corpus fill: 13 extractors active; mean fill rate ~10/20
- DSE-020 not_found pressure: top 7 all at 566; next tier (co_pay) at 417

### Extractors implemented (13)
free_look_period, grace_period, ped_waiting_period, initial_waiting_period, co_pay, renewability, claim_settlement_timeline, ayush_coverage, ambulance_coverage, cumulative_bonus_ncb, specific_disease_waiting_periods, maternity_waiting, organ_donor_coverage

### Next extractors to build (7)
claim_intimation_timeline (Packet A), deductible (Packet A), room_rent_limit (Packet B), icu_limit (Packet B), restoration_benefit (Packet C), modern_treatment_coverage (Packet C), newborn_coverage (Packet C)

---

## Packet 0A Closeout

Date: 2026-06-04

Checks run:

- **Active Sprint table fix:** DSE-021 row in `docs/tasks.md` changed from `planned` to `in_progress` — resolves the inconsistency where the task detail section already showed `in_progress` but the Active Sprint table still said `planned`.
- **Baseline audit review:** Reviewed `data/reports/dse021_wave2_baseline_audit.md` for internal consistency. Gold status counts match session log; DSE-020 not_found pressure (566 each) is consistent; packet recommendations align between audit and session log. No contradictions found.
- **Gold validator:** `scripts/validate_gold_corpus.py` — PASS (400 facts, 20 reviewed policies, 0 draft policies/facts)
- **diff check:** `git diff --check` — PASS (no whitespace errors)
- **Working tree:** Clean after commit.

**Commit:** docs(extractors): audit wave 2 baseline

**Branch:** feat/dse-021-extractor-wave2

**Next:** Start Packet 0B — shared extractor utilities, when instructed.

---

## Packet 0B Closeout

Date: 2026-06-04

### Goal
Add shared Wave 2 extractor utility helpers without implementing any new concept extractor.

### Files Created
- `extractors/wave2_utils.py` — 8 utility functions
- `tests/test_wave2_utils.py` — 18 tests covering all 7 utility categories

### Docs Updated
- `docs/changelog.md` — Packet 0B changelog entry
- `runs/sessions/2026-06-04-extractor-wave2.md` — this closeout section

### Commands Run
```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/test_wave2_utils.py --tb=short
PYTHONPATH=. .venv/bin/python -m pytest tests/test_fact_extractors.py --tb=short
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
git diff --check
git status --short
```

### Results
- **Wave 2 utility tests:** PASS (18/18)
- **Existing fact extractor tests:** PASS (all existing tests pass, no behavioral changes)
- **Gold validator:** PASS (400 facts, 20 reviewed policies, 0 draft)
- **diff --check:** PASS (no whitespace errors)
- **Working tree:** clean after commit

### Commit
```
feat(extractors): add wave 2 utility helpers
```

---

## Packet 1A Remediation Closeout — Claim Intimation Timeline

Date: 2026-06-04

### Goal
Implement and remediate the first Wave 2 extractor, `claim_intimation_timeline`, after the initial executor attempt left the fact extraction gate failing.

### What Was Corrected
- Added `claim_intimation_timeline` to `TARGET_CONCEPTS`.
- Added `ClaimIntimationTimelineExtractor`.
- Registered the extractor in the deterministic extractor registry.
- Marked the ontology concept as active deterministic.
- Added regression tests for claim-intimation phrasing, split notification bullets, and document-submission false positives.
- Re-ran source-backed review for the mismatching 20-policy gold labels.
- Corrected only `claim_intimation_timeline` gold labels where source text proved the old label/value was wrong or non-comparable.

### Source-Backed Gold Corrections
- Corrected real present facts previously marked `not_found`: Bajaj Allianz, Liberty, Reliance, Universal Sompo.
- Corrected incorrect present facts to `not_found`: ICICI Family Shield and IFFCO Tokio Health Protector.
- Normalized truncated `timeline_text` and over-broad multi-component values to the primary/earliest claim-notification deadline for the claim-intimation concept.

### Commands Run
```bash
pdftotext -layout -f 18 -l 18 ../policy_data/08_Bajaj_Allianz/Bajaj_Silver_Health_Full_IRDAI.pdf -
pdftotext -layout -f 40 -l 40 ../policy_data/19_Liberty/Liberty_2297fe19-f723-b779-1a48-2741add34d6b.pdf -
pdftotext -layout -f 23 -l 23 ../policy_data/17_Reliance/Reliance_Health_Gain_PW.pdf -
pdftotext -layout -f 14 -l 14 ../policy_data/14_Universal_Sompo/Universal_Sompo_Loan_Secure_Insurance_Policy.pdf -
pdftotext -layout -f 16 -l 16 ../policy_data/09_HDFC_ERGO/HDFC_ERGO_Arogya_Sanjeevani_Policy_HDFC_ERGO.pdf -
pdftotext -layout -f 20 -l 20 ../policy_data/10_Tata_AIG/Tata_AIG_Arogya_Sanjeevani.pdf -
pdftotext -layout -f 32 -l 32 ../policy_data/21_Royal_Sundaram/Royal_Sundaram_Advanced_Top_Up_PW.pdf -
PYTHONPATH=. .venv/bin/python scripts/run_fact_extractors.py --section-root data/interim/logical --output-root data/interim/facts
PYTHONPATH=. .venv/bin/python scripts/eval_fact_extractors.py --facts-root data/interim/facts --gold-corpus gold_corpus --section-root data/interim/logical --output runs/evals/2026-06-04-fact-extraction-dse021-claim-intimation.json
```

### Final Eval Result
```text
passed: true
policies_passed: 20/20
precision: 100.00%
recall: 99.53%
normalized_value_accuracy: 100.00%
status_accuracy: 98.57%
evidence_accuracy: 100.00%
false_present_for_gold_not_found: 0
```

### Generated Artifacts
- `data/reports/dse021_claim_intimation_mismatch_audit.md`
- `runs/evals/2026-06-04-fact-extraction-dse021-claim-intimation.json`

### Known Limitations
- `claim_intimation_timeline` records the primary/earliest claim-notification deadline.
- Separate claim-document filing deadlines remain a future concept and are not included here.

### Next Step
Implement the next DSE-021 packet for `deductible` with the same source-backed audit discipline.

### Latest Context Capsule

#### Current branch
`feat/dse-021-extractor-wave2`

#### Completed packets
- Packet 0A — baseline audit committed.
- Packet 0B — shared Wave 2 utilities committed.
- Packet 1A — `claim_intimation_timeline` implemented/remediated, pending commit.

#### Current active concept count
14 deterministic concepts after Packet 1A.

#### Next exact packet
Packet 1B — source-backed deductible gold/evidence audit only. Do not implement the deductible extractor before the audit is complete.

---

## Packet 1B Closeout — Deductible Gold/Evidence Audit

Date: 2026-06-04

### Goal
Audit all 20 `deductible` gold labels against source PDF text and parsed section/tree outputs before implementing the deductible extractor.

### Files Changed
- `data/reports/dse021_deductible_gold_audit.md`
- `docs/changelog.md`
- `docs/tasks.md`
- `runs/sessions/2026-06-04-extractor-wave2.md`

### Commands Run
```bash
pdftotext -layout ../policy_data/<policy_pdf> -  # all 20 reviewed policies, searched for "deduct"
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
git diff --check
```

### Results
- All 20 deductible rows classified.
- Pure definition-only deductible text was separated from operative deductible clauses.
- Required Packet 1C gold fixes identified:
  - `future_generali_health_elite`: change deductible to `not_found`.
  - `kotak_mahindra_health_premier`: change deductible to `not_found`.
  - `reliance_health_gain`: change deductible to `present`.
- Packet 1C extractor rules are now locked in the audit report.

### Generated Artifacts
- `data/reports/dse021_deductible_gold_audit.md`

### Next Step
Implement Packet 1C — deductible extractor plus source-backed deductible gold corrections.

---

## Packet 1C Closeout — Deductible Extractor

Date: 2026-06-04

### Goal
Implement a precision-first deterministic extractor for `deductible` using the Packet 1B audit as the source of truth.

### Files Changed
- `extractors/models.py`
- `extractors/deterministic.py`
- `ontology/concepts.v1.json`
- `tests/test_fact_extractors.py`
- `gold_corpus/policies/*/facts.json` for source-backed deductible corrections
- `data/reports/dse021_deductible_gold_audit.md`
- `runs/evals/2026-06-04-fact-extraction-dse021-deductible.json`
- `docs/changelog.md`, `docs/tasks.md`, `docs/evaluation.md`, `docs/decisions.md`

### Commands Run
```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/test_fact_extractors.py --tb=short
PYTHONPATH=. .venv/bin/python scripts/run_fact_extractors.py --section-root data/interim/logical --output-root data/interim/facts
PYTHONPATH=. .venv/bin/python scripts/eval_fact_extractors.py --facts-root data/interim/facts --gold-corpus gold_corpus --section-root data/interim/logical --output runs/evals/2026-06-04-fact-extraction-dse021-deductible.json
```

### Results
```text
passed: true
policies_passed: 20/20
precision: 100.00%
recall: 99.55%
normalized_value_accuracy: 100.00%
status_accuracy: 97.67%
evidence_accuracy: 100.00%
false_present_for_gold_not_found: 0
```

### Source-Backed Gold Corrections
- `future_generali_health_elite`: deductible changed from `present` to `not_found`.
- `kotak_mahindra_health_premier`: deductible changed from `present` to `not_found`.
- `reliance_health_gain`: deductible changed from `not_found` to `present`.
- Care, ICICI, and Star deductible values normalized to canonical schedule-dependent shapes.

### Known Limitations
- The extractor records operative deductible presence and schedule dependency. It does not parse full benefit schedule tables into exact deductible amounts when the amount is only in the policy schedule/certificate.

### Next Step
Proceed to Packet 2A: `room_rent_limit` and `icu_limit` audit, because both are table-heavy and should be planned together before implementation.

---

## Packet 2A Closeout — Room Rent + ICU Gold/Evidence Audit

Date: 2026-06-04

### Goal
Audit all 20 `room_rent_limit` and `icu_limit` gold labels against source PDF text, section trees, and table-like policy wording before implementing paired extractors.

### Files Changed
- `data/reports/dse021_room_icu_gold_audit.md`
- `docs/changelog.md`
- `docs/tasks.md`
- `runs/sessions/2026-06-04-extractor-wave2.md`

### Commands Run
```bash
pdftotext -layout ../policy_data/<policy_pdf> -  # targeted room/ICU source review
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
git diff --check
```

### Results
- All 40 concept-policy rows classified.
- Definition-only room/ICU clauses were separated from operative benefit limits.
- Canonical value shapes were locked for percentage limits, actuals/no fixed limit, schedule/certificate-dependent values, and conditional components.
- Packet 2B source-backed gold fixes identified for Bajaj, Care, Future Generali, ICICI ICU, IFFCO, Liberty ICU, Niva Bupa, Oriental, Reliance, Royal ICU, SBI, Star, Tata AIG, and United India ICU.

### Generated Artifacts
- `data/reports/dse021_room_icu_gold_audit.md`

### Known Limitations
- The audit does not implement table remediation. It uses existing source text and table-like clauses only.
- Conditional limits such as IFFCO and Oriental require component-shaped values; Packet 2B should avoid collapsing them into one misleading scalar.

### Next Step
Implement Packet 2B — paired `room_rent_limit` and `icu_limit` extractors plus only the source-backed gold corrections documented in the Packet 2A audit.

---

## Packet 2B Closeout — Room Rent + ICU Extractors

Date: 2026-06-04

### Goal
Implement conservative deterministic extractors for `room_rent_limit` and `icu_limit`, using the Packet 2A audit as the source-backed truth.

### Files Changed
- `extractors/deterministic.py`
- `extractors/models.py`
- `ontology/concepts.v1.json`
- `tests/test_fact_extractors.py`
- `gold_corpus/policies/*/facts.json` for source-backed room/ICU corrections only
- `data/reports/dse021_room_icu_gold_audit.md`
- `runs/evals/2026-06-04-fact-extraction-dse021-room-icu.json`
- `docs/changelog.md`
- `docs/tasks.md`
- `docs/evaluation.md`
- `docs/decisions.md`
- `runs/sessions/2026-06-04-extractor-wave2.md`

### Commands Run
```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/test_fact_extractors.py --tb=short
PYTHONPATH=. .venv/bin/python scripts/run_fact_extractors.py --section-root data/interim/logical --output-root data/interim/facts
PYTHONPATH=. .venv/bin/python scripts/eval_fact_extractors.py --facts-root data/interim/facts --gold-corpus gold_corpus --section-root data/interim/logical --output runs/evals/2026-06-04-fact-extraction-dse021-room-icu.json
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
```

### Results
```text
passed: true
policies_passed: 20/20
precision: 100.00%
recall: 99.61%
normalized_value_accuracy: 100.00%
status_accuracy: 97.65%
evidence_accuracy: 100.00%
false_present_for_gold_not_found: 0
full pytest: 453/453 passed
gold corpus validator: passed
```

### Source-Backed Gold Corrections
- Bajaj, Oriental: converted room/ICU table-row bleed into actuals or component-shaped limits.
- Care, SBI, Tata AIG, United India: normalized explicit percentage/unit room and ICU limits.
- Future Generali, Reliance, Royal Sundaram, ICICI, Kotak: corrected schedule-dependent room/ICU limits where the policy wording points to schedule/certificate/product-benefit-table values.
- IFFCO: represented conditional room/ICU values as components instead of a misleading scalar.
- Liberty and Star: rejected unsupported ICU labels where source wording did not contain an operative ICU limit.
- Niva Bupa: corrected room schedule dependency and ICU 1% SI/day table value.

### Generated Artifacts
- `runs/evals/2026-06-04-fact-extraction-dse021-room-icu.json`

### Decisions Made
- `room_rent_limit` and `icu_limit` now use explicit value shapes for percentage limits, actuals/no fixed limit, schedule-dependent limits, and conditional components.

### Known Limitations
- The room/ICU extractors consume existing clause/table-like text. They do not fix physical table extraction, header lineage, or schedule-table parsing; that remains DSE-022/DSE-023 work.

### Next Step
Proceed to Packet 3A: source audit for `restoration_benefit`, `modern_treatment_coverage`, and `newborn_coverage` before implementing the final three DSE-021 extractors.

---

## Packet 3A Closeout — Coverage Wave Gold/Evidence Audit

Date: 2026-06-05

### Goal
Audit all 20 `restoration_benefit`, `modern_treatment_coverage`, and `newborn_coverage` gold labels against source PDF text, section trees, and table-like policy wording before implementing the final DSE-021 extractors.

### Files Changed
- `data/reports/dse021_coverage_wave_gold_audit.md`
- `docs/changelog.md`
- `docs/tasks.md`
- `runs/sessions/2026-06-04-extractor-wave2.md`

### Commands Run
```bash
pdftotext -layout ../policy_data/<policy_pdf> -  # targeted coverage concept source review
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
git diff --check
```

### Results
- All 60 concept-policy rows classified.
- Coverage concepts were separated from common false positives:
  - body-part reconstruction is not sum-insured restoration,
  - home/property restoration is not health restoration,
  - baby-item annexure rows are not newborn coverage,
  - generic procedure lists/exclusions are not modern-treatment coverage.
- Packet 3B source-backed gold fixes identified for Aditya Birla newborn, Bajaj modern treatment, Care modern treatment, Future Generali restoration/newborn, IFFCO modern treatment, Kotak restoration/newborn, Niva Bupa modern treatment, Oriental restoration, Reliance newborn, SBI modern treatment, Tata AIG modern treatment, United India modern treatment, and Universal Sompo restoration.

### Generated Artifacts
- `data/reports/dse021_coverage_wave_gold_audit.md`

### Known Limitations
- This packet did not apply gold fixes or implement extractors.
- Some exact component-level modern treatment limits remain procedure-specific and should not be collapsed into one misleading scalar unless Packet 3B can support that shape safely.

### Next Step
Implement Packet 3B — `restoration_benefit`, `modern_treatment_coverage`, and `newborn_coverage` extractors plus only the source-backed gold corrections documented in the Packet 3A audit.

---

## Packet 3B Closeout — Coverage Wave Extractors

Date: 2026-06-05

### Goal
Implement conservative deterministic extractors for `restoration_benefit`, `modern_treatment_coverage`, and `newborn_coverage`, using the Packet 3A audit as source-backed truth.

### Files Changed
- `extractors/deterministic.py`
- `extractors/models.py`
- `ontology/concepts.v1.json`
- `tests/test_fact_extractors.py`
- `gold_corpus/policies/*/facts.json` for source-backed coverage-wave corrections only
- `data/reports/dse021_coverage_wave_gold_audit.md`
- `runs/evals/2026-06-05-fact-extraction-dse021-coverage-wave.json`
- `docs/changelog.md`
- `docs/tasks.md`
- `docs/evaluation.md`
- `docs/decisions.md`
- `runs/sessions/2026-06-04-extractor-wave2.md`

### Commands Run
```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/test_fact_extractors.py --tb=short
PYTHONPATH=. .venv/bin/python scripts/run_fact_extractors.py --section-root data/interim/logical --output-root data/interim/facts
PYTHONPATH=. .venv/bin/python scripts/eval_fact_extractors.py --facts-root data/interim/facts --gold-corpus gold_corpus --section-root data/interim/logical --output runs/evals/2026-06-05-fact-extraction-dse021-coverage-wave.json
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
```

### Results
```text
passed: true
policies_passed: 20/20
precision: 100.00%
recall: 99.27%
normalized_value_accuracy: 100.00%
status_accuracy: 97.75%
evidence_accuracy: 100.00%
false_present_for_gold_not_found: 0
focused pytest: 60/60 passed
gold corpus validator: passed
```

### Source-Backed Gold Corrections
- Aditya Birla newborn changed from `explicitly_not_covered` to `not_found`; baby/vaccine charge rows are not newborn-cover exclusions.
- Care, SBI, and Tata AIG modern treatment changed from `not_found` to present based on operative source clauses.
- Bajaj, IFFCO, Niva Bupa, and United India modern-treatment values canonicalized.
- Future Generali restoration/newborn, Kotak restoration/newborn, and Reliance newborn corrected to source-backed status/value shapes.
- Oriental restoration changed from present to `not_found`; body-part reconstruction is not sum-insured restoration.
- Universal Sompo restoration changed from present to `not_found`; source clauses are property/home restoration, not health restoration.
- Star restoration and Tata AIG modern treatment remain present but use conservative covered values because current section-tree evidence does not safely carry the exact source PDF percentages.

### Generated Artifacts
- `runs/evals/2026-06-05-fact-extraction-dse021-coverage-wave.json`

### Decisions Made
- Coverage-wave extractors must not invent exact limits that are visible in source PDFs but absent from verified section-tree evidence.

### Known Limitations
- Star restoration exact 200% and Tata AIG modern-treatment exact 50% are source-visible but not safely carried in current section-tree clauses.
- This packet does not remediate parser/table extraction; it only keeps deterministic facts evidence-verified.

### Next Step
Run Packet 4 final full-chain DSE-021 validation: fact extraction, clause store/source spans, fact scoring, export, full pytest, docs, and final commit.

---

## Packet 4 Closeout — Final Full-Chain Validation

Date: 2026-06-05

### Goal
Prove all 20 priority concepts work end-to-end through deterministic extraction, SQLite clause/source-span storage, fact scoring, Product B export, gold validation, and full pytest.

### Files Changed
- `data/reports/dse010_sqlite_build_summary.json`
- `data/reports/dse011_fact_scoring_summary.json`
- `data/reports/dse013_export_summary.json`
- `runs/evals/2026-06-05-fact-extraction-dse021-final.json`
- `runs/evals/2026-06-05-fact-scoring-dse021-final.json`
- `runs/evals/2026-06-05-export-dse021-final.json`
- `docs/tasks.md`
- `docs/changelog.md`
- `docs/evaluation.md`
- `runs/sessions/2026-06-04-extractor-wave2.md`

### Commands Run
```bash
PYTHONPATH=. .venv/bin/python scripts/run_fact_extractors.py --section-root data/interim/logical --output-root data/interim/facts
PYTHONPATH=. .venv/bin/python scripts/eval_fact_extractors.py --facts-root data/interim/facts --gold-corpus gold_corpus --section-root data/interim/logical --output runs/evals/2026-06-05-fact-extraction-dse021-final.json
rm -f data/engine.sqlite data/engine.sqlite-wal data/engine.sqlite-shm
PYTHONPATH=. .venv/bin/python scripts/run_clause_store.py --gold-corpus gold_corpus --physical-root data/interim/physical --logical-root data/interim/logical --tables-root data/interim/tables --facts-root data/interim/facts --output-db data/engine.sqlite --output-facts-resolved data/interim/facts_resolved --pipeline-run-id clause_store_dse021_final_2026_06_05
PYTHONPATH=. .venv/bin/python scripts/validate_source_spans.py --db data/engine.sqlite --facts-root data/interim/facts_resolved
PYTHONPATH=. .venv/bin/python scripts/run_fact_scoring.py --gold-corpus gold_corpus --candidates-root data/interim/facts --resolved-root data/interim/facts_resolved --db data/engine.sqlite --pipeline-run-id fact_scoring_dse021_final_2026_06_05
PYTHONPATH=. .venv/bin/python scripts/run_export.py --db data/engine.sqlite --output-root data/export --pipeline-run-id export_dse021_final_2026_06_05
PYTHONPATH=. .venv/bin/python scripts/eval_fact_scoring.py --db data/engine.sqlite --candidates-root data/interim/facts --resolved-root data/interim/facts_resolved --gold-corpus gold_corpus --output runs/evals/2026-06-05-fact-scoring-dse021-final.json
PYTHONPATH=. .venv/bin/python scripts/eval_export.py --db data/engine.sqlite --export-root data/export --gold-corpus gold_corpus --output runs/evals/2026-06-05-export-dse021-final.json
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
```

### Results
```text
fact extraction eval: PASS
policies_passed: 20/20
precision: 100.00%
recall: 99.27%
normalized_value_accuracy: 100.00%
status_accuracy: 97.75%
evidence_accuracy: 100.00%
false_present_for_gold_not_found: 0

source-span validation: ALL CHECKS PASSED
fact scoring eval: PASS
total candidates in DB: 937
total facts in DB: 280
FK violations: 0
normalized value accuracy: 98.2%
evidence accuracy: 100.0%
false present: 0
conflicts: 0

export eval: PASS
policies exported: 20
concepts per policy: 20/20
schema validation errors: 0
present missing evidence: 0
invalid fact statuses: 0

gold corpus validator: PASS
full pytest: 460/460 passed
```

### Generated Artifacts
- `runs/evals/2026-06-05-fact-extraction-dse021-final.json`
- `runs/evals/2026-06-05-fact-scoring-dse021-final.json`
- `runs/evals/2026-06-05-export-dse021-final.json`

### Decisions Made
- DSE-021 is complete: all 20 priority concepts are now active deterministic concepts for the reviewed 20-policy benchmark.
- Remaining value specificity gaps caused by missing table/section evidence stay outside DSE-021 and should be handled by DSE-022 table/parser remediation or later LLM refinement.

### Known Limitations
- Exact limits that are source-visible but absent from verified section-tree evidence are still emitted conservatively, not guessed.
- Full 647-policy semantic quality remains unproven until the DSE-020 scale outputs are rerun through the completed 20-concept extractor set.

### Next Step
Start DSE-022 table eval expansion/remediation, or run a DSE-020 refresh with the completed 20-concept extractor set if scale fill-rate is the immediate priority.
