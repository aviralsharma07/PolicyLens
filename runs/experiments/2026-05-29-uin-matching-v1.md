# Experiment: 2026-05-29 — UIN Matching Strategy v1

Date: 2026-05-29
Git commit: none (no code yet)
Input manifest: active_policy_wordings.json (not yet generated)
Task ID: DSE-002
Hypothesis: Tier 2 matching (exact insurer + normalized plan name) will cover >= 60% of files. Combined with Tier 4 (source URL domain + plan name), >= 80% coverage is achievable.

## Goal

Determine the best match strategy for aligning 647 active policy wordings against 1,099 UIN records in `uin_lifecycle.json`. Validate match rates, identify failure modes, and design the match tier pipeline.

## Hypothesis

Tier 2 matching (exact insurer + normalized plan name) will cover >= 60% of files. Combined with Tier 4 (source URL domain + plan name), >= 80% coverage is achievable.

## Method

Not yet run. Experiment will be executed after `corpus_lockdown.py` produces `active_policy_wordings.json`.

### Planned tiers

1. Tier 1: Search PDF text for UIN-like patterns (e.g., `[A-Z]{3,6}\d{6,10}`)
2. Tier 2: Exact insurer + normalized plan name (after normalizer)
3. Tier 3: Fuzzy insurer + fuzzy plan name (token set ratio, partial ratio)
4. Tier 4: Source URL domain + plan name
5. Tier 5: Unmatched → manual review

### Planned metrics

- Per-tier match count and percentage
- Match confidence distribution (by insurer)
- Overlap between tiers
- False positive rate (manual audit of top 50 Tier 3 matches)
- Top reasons for unmatched files

## Commands

```bash
# Pending — corpus_lockdown.py must run first to produce active_policy_wordings.json
```

## Results

*Pending — experiment not yet executed.*

## Failure Patterns

*Pending — experiment not yet executed.*

## Decision / Next Step

1. Wait for DSE-001 (Corpus Lockdown) to complete
2. Run UIN matcher after corpus_lockdown.py produces active_policy_wordings.json
3. Evaluate per-tier match rates against 1,099 UIN records
