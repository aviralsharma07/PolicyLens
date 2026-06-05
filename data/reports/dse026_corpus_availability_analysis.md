# DSE-026 Corpus Availability Analysis

Date: 2026-06-06  
Task ID: DSE-026

## Purpose

Measure what Product A already has for the insurer universe before external
selection criteria are applied.

This report is intentionally narrow:

- it measures **local corpus strength**;
- it does **not** decide final MVP desirability on its own.

External market and source-availability research is handled separately in
`data/reports/dse026_market_trust_evidence.md`.

## Inputs

- `data/manifests/active_policy_wordings_v1.json`
- `data/manifests/uin_match_report_v1.json`
- `data/manifests/product_source_bundles_v1.draft.json`
- `scripts/analyze_dse026_insurer_universe.py`

## High-Level Finding

The local corpus is deep enough to support insurer selection, but it is still
heavily weighted toward **policy wordings without PBT/CIS**.

That means:

- Product A has strong starting coverage for wording-driven parsing.
- Product A does **not** yet have launch-grade source bundles for most insurers.
- Corpus size alone should not drive DSE-026 ranking.

## Global Baseline

- Active corpus documents: **647**
- DSE-025 draft product bundles: **507**
- Bundles with known PBT: **1** (Aditya Birla Activ Care)
- Bundles with known CIS: **1** (Aditya Birla Activ Care)
- Most bundle entries remain `missing_pbt`.

## Target-Insurer Summary

The table below separates starting readiness from final MVP desirability.

| Insurer | Active wordings | Bundles | Known PBT bundles | Known CIS bundles | Readiness band | Noise risk | Notes |
|---|---:|---:|---:|---:|---|---|---|
| HDFC ERGO | 67 | 60 | 0 | 0 | medium | high | Strong local depth, but many group-like or duplicate-version entries. |
| ICICI Lombard | 40 | 34 | 0 | 0 | medium | high | Good local coverage; still wording-heavy. |
| Star Health | 101 | 68 | 0 | 0 | medium | high | Deepest local retail corpus, but also the noisiest due to legacy/group variants. |
| Niva Bupa | 13 | 10 | 0 | 0 | medium | high | Good retail relevance, thinner local base than peers. |
| Care Health | 22 | 18 | 0 | 0 | medium | high | Good starter corpus with brochure presence, but still no confirmed PBT/CIS bundles locally. |
| Tata AIG | 25 | 21 | 0 | 0 | medium | high | Broad enough local starting point for later expansion. |
| Bajaj Allianz | 27 | 24 | 0 | 0 | medium | medium | Reasonable breadth with slightly lower noise than some peers. |
| SBI General | 9 | 7 | 0 | 0 | far | medium | Thin local corpus; official downloads likely matter more than current local depth. |
| Aditya Birla Health | 22 | 16 | 1 | 1 | close | high | Only insurer with a known wording+CIS+PBT path already identified via DSE-025. |
| ManipalCigna | 0 | 0 | 0 | 0 | far | n/a | No usable local base yet. |
| New India Assurance | 31 | 28 | 0 | 0 | medium | high | Strong public-sector local presence; likely useful for long-tail comparison. |
| United India | 24 | 18 | 0 | 0 | medium | high | Moderate local depth, but source-bundle usability still unproven. |
| Oriental Insurance | 29 | 21 | 0 | 0 | medium | high | Local coverage exists, but current corpus is noisy and retail prioritization is weaker. |
| Future Generali | 32 | 28 | 0 | 0 | medium | high | Good local volume, but market priority needs external validation. |
| Reliance General | 21 | 14 | 0 | 0 | medium | high | Enough local documents to support later evaluation, but not an immediate MVP favorite. |

## What "Readiness Band" Means

- `close`: local corpus already includes at least one partial source-bundle path with known non-wording documents.
- `medium`: enough local coverage to support DSE-027, but still mostly wording-only.
- `far`: thin or missing local coverage; DSE-027 would need heavier discovery work.

## What "Noise Risk" Means

This is a local-corpus cleanup risk, not a consumer-risk score.

Higher noise risk usually means one or more of:

- many group products mixed with retail products;
- multiple document revisions for similar product families;
- duplicate or near-duplicate UIN bases;
- wording-heavy coverage with little bundle context.

## Important Interpretation

### Local corpus strength is not the same as MVP desirability

Examples:

- Star Health has the deepest local coverage, which helps Product A, but that does not automatically make it the best or easiest user-facing recommendation set.
- Niva Bupa has thinner local coverage, but its retail relevance and current product visibility may still justify top-5 MVP inclusion.
- Aditya Birla is locally important because it proved the PBT/CIS gap concretely, even if it may not outrank bigger retail insurers in final MVP priority.

### Source completeness is still the bottleneck

The main DSE-026 takeaway from local data is not "who has the most PDFs." It is:

> We have enough wording coverage to choose an MVP insurer universe, but DSE-027 must collect official non-wording documents before Product B can make launch-grade recommendations.

## Best-Positioned Local Starting Points

### Strong local base

- Star Health
- HDFC ERGO
- ICICI Lombard
- New India Assurance
- Future Generali

### Strong signal despite thinner local base

- Care Health
- Niva Bupa
- Aditya Birla Health
- Tata AIG
- Bajaj Allianz

### Weak local starting point

- SBI General
- ManipalCigna

## Recommendation for DSE-026

Use this report as an input, not the final answer.

The local data supports a shortlist biased toward:

- HDFC ERGO
- ICICI Lombard
- Star Health
- Care Health
- Niva Bupa
- Tata AIG
- Bajaj Allianz
- Aditya Birla Health
- New India Assurance
- SBI General

But the final top 10 and MVP top 5 should be locked only after external evidence
confirms:

- retail relevance,
- public source-document availability,
- realistic source-bundle collection effort.

## Artifact

Machine-readable output:

- `data/reports/dse026_corpus_availability_analysis.json`

Generated by:

```bash
PYTHONPATH=. .venv/bin/python scripts/analyze_dse026_insurer_universe.py
```
