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
