# DSE-020 Scale Triage Report

Date: 2026-06-03
Manifest policies: 647
Attempted: 39
Per-policy completed: 39
Exports: 20
DB size MB: 79.04

## Per-Stage Counts

```json
{
  "physical": {
    "ok": 39,
    "failed": 0
  },
  "heading": {
    "ok": 39,
    "failed": 0
  },
  "section": {
    "ok": 39,
    "failed": 0
  },
  "tables": {
    "ok": 39,
    "failed": 0
  },
  "facts": {
    "ok": 39,
    "failed": 0
  }
}
```

## Top Not Found Concepts

```json
{
  "claim_intimation_timeline": 20,
  "deductible": 20,
  "icu_limit": 20,
  "modern_treatment_coverage": 20,
  "newborn_coverage": 20,
  "restoration_benefit": 20,
  "room_rent_limit": 20,
  "co_pay": 11,
  "organ_donor_coverage": 11,
  "maternity_waiting": 9,
  "ayush_coverage": 8,
  "cumulative_bonus_ncb": 8,
  "initial_waiting_period": 6,
  "specific_disease_waiting_periods": 6,
  "ambulance_coverage": 5,
  "ped_waiting_period": 5,
  "claim_settlement_timeline": 3,
  "free_look_period": 3,
  "grace_period": 2,
  "renewability": 2
}
```

## Structural Warnings

- Zero headings: 2
- Zero clauses: 2
- Zero fact candidates: 2

## Top Recommended Fixes

1. Fix parser/section-tree failures for 2 policies with zero clauses.
2. Audit heading scorer for 2 policies with zero headings.
3. Audit extractor recall/parser inputs for 2 policies with zero candidates.
4. Prioritize extractor/LLM strategy for top not_found concept `claim_intimation_timeline` (20).
5. Continue full-corpus run and classify the next largest failure cluster.
