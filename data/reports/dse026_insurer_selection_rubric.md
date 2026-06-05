# DSE-026 Insurer Selection Rubric

Date: 2026-06-06  
Task ID: DSE-026

## Purpose

Lock a defensible insurer universe for the curated Product B MVP.

This rubric is intentionally product-strategy oriented. It does **not** answer
"which insurer is best in India." It answers:

1. Which insurers are most worth covering first for a citation-first consumer MVP?
2. Which insurers are realistic for source-bundle collection in DSE-027?
3. Which insurers are likely to produce the highest trust-adjusted user value per unit of QA effort?

## Scoring Model

Total score: **100**

| Dimension | Weight | What it measures |
|---|---:|---|
| Retail relevance | 25 | Whether normal retail buyers actually encounter and consider the insurer for individual/family health cover. |
| Market presence / userbase | 20 | Whether the insurer has meaningful scale, visible distribution, and a large enough footprint to matter for MVP. |
| Public source-document availability | 20 | Whether official policy wordings, CIS pages, brochures, or download centers appear publicly usable for source-bundle collection. |
| Product breadth for retail buyers | 15 | Whether the insurer has enough breadth across flagship, family, senior, top-up, standard, and premium use cases. |
| Trust / service / claim signal | 10 | Directional signal from public-company transparency, institutional backing, hospital/branch footprint, and official service posture. This is not a final claims-quality verdict. |
| Existing Product A corpus readiness | 10 | How much local corpus coverage already exists, and whether DSE-025 shows the insurer is close or far from a usable bundle set. |

## Evidence Policy

### Primary evidence first

Preferred sources:

1. IRDAI / regulator pages
2. Official insurer product pages
3. Official insurer downloads / CIS / brochure / policy wording pages
4. Official company annual reports / investor materials

### Secondary evidence allowed, but explicitly weaker

Allowed as support only:

1. Reputable business press
2. Industry research summaries
3. Large financial-information platforms

Secondary sources may support market-relevance claims, but they must not override
official source-availability reality.

## Scoring Guidance

### 1. Retail relevance — 25

High score:
- insurer is common in actual retail buying journeys;
- offers clear individual/family floater products;
- has active online purchase/discovery pages;
- appears repeatedly in real shortlist scenarios.

Low score:
- mostly corporate/group or niche;
- weak retail visibility;
- low fit for a first consumer MVP.

### 2. Market presence / userbase — 20

High score:
- large customer footprint;
- broad hospital/branch/distribution network;
- material presence in Indian health insurance conversations or market summaries.

Low score:
- thin public footprint;
- niche product relevance;
- weak scale evidence.

### 3. Public source-document availability — 20

High score:
- official product pages expose brochure/CIS/policy wording or explicit download center;
- URLs are stable and discoverable;
- multiple current products are visible without login or opaque flows.

Low score:
- product docs are hidden, fragmented, or difficult to discover;
- only wording is easy to find while CIS/PBT is absent;
- official navigation is inconsistent.

### 4. Product breadth for retail buyers — 15

High score:
- insurer has strong product coverage across:
  - flagship comprehensive plan
  - family floater
  - senior plan
  - top-up / super top-up
  - standard Arogya Sanjeevani
  - premium / differentiated plan

Low score:
- too few relevant retail products;
- weak senior/top-up coverage;
- limited variation for Product B recommendations.

### 5. Trust / service / claim signal — 10

This is intentionally conservative.

We are **not** using marketing claims as truth. We are using them only as directional
signals when supported by:

- official hospital network size
- branch/distribution presence
- listed-company or institutional disclosure culture
- standalone health focus where relevant
- public-service positioning for PSU insurers

This score must be written with caveats. It is not a final recommendation score for end users.

### 6. Existing Product A corpus readiness — 10

High score:
- insurer already has a meaningful local wording corpus;
- bundle count is non-trivial;
- noise can be triaged;
- DSE-027 can start without discovering the insurer from scratch.

Low score:
- very little local coverage;
- missing from current bundle draft;
- source-bundle sprint would start from near-zero.

## Tie-Break Rules

If two insurers score closely:

1. Prefer the insurer with better official source-document availability.
2. Then prefer the insurer with stronger retail relevance.
3. Then prefer the insurer with cleaner Product A starting coverage.

## Exclusion / Defer Rules

An insurer may be deferred even with solid market presence if:

- public source discovery is weak enough to slow DSE-027 materially;
- local corpus is too noisy relative to MVP value;
- product lineup is less relevant than other options in the same score band.

## Deliverables This Rubric Supports

- `data/reports/dse026_market_trust_evidence.md`
- `data/reports/dse026_top10_top5_selection.md`
- `data/manifests/mvp_insurer_selection_v1.json`
- `data/manifests/mvp_product_candidates_v1.json`

## Known Limits

- This rubric is designed for MVP scoping, not investor-grade market ranking.
- "Trust" is the weakest dimension and should be interpreted cautiously.
- Some official source pages can drift; DSE-027 must re-verify every live URL before collection.
