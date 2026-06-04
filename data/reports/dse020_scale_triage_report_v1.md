# DSE-020 Scale Triage Report

Date: 2026-06-04
Manifest policies: 647
Attempted: 647
Per-policy completed: 647
Exports: 566
DB size MB: 1963.63

## Per-Stage Counts

```json
{
  "physical": {
    "ok": 647,
    "failed": 0
  },
  "heading": {
    "ok": 647,
    "failed": 0
  },
  "section": {
    "ok": 647,
    "failed": 0
  },
  "tables": {
    "ok": 647,
    "failed": 0
  },
  "facts": {
    "ok": 647,
    "failed": 0
  }
}
```

## Top Not Found Concepts

```json
{
  "claim_intimation_timeline": 566,
  "deductible": 566,
  "icu_limit": 566,
  "modern_treatment_coverage": 566,
  "newborn_coverage": 566,
  "restoration_benefit": 566,
  "room_rent_limit": 566,
  "co_pay": 417,
  "cumulative_bonus_ncb": 393,
  "organ_donor_coverage": 389,
  "maternity_waiting": 338,
  "initial_waiting_period": 310,
  "ambulance_coverage": 303,
  "specific_disease_waiting_periods": 296,
  "ayush_coverage": 290,
  "free_look_period": 259,
  "ped_waiting_period": 240,
  "grace_period": 198,
  "claim_settlement_timeline": 177,
  "renewability": 160
}
```

## Structural Warnings

- Zero headings: 84
- Zero clauses: 110
- Zero fact candidates: 133

## Top Recommended Fixes

1. Fix parser/section-tree failures for 110 policies with zero clauses.
2. Audit heading scorer for 84 policies with zero headings.
3. Audit extractor recall/parser inputs for 133 policies with zero candidates.
4. Prioritize extractor/LLM strategy for top not_found concept `claim_intimation_timeline` (566).
5. Continue full-corpus run and classify the next largest failure cluster.
