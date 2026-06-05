# DSE-026 Top 10 and MVP Top 5 Selection

Date: 2026-06-06  
Task ID: DSE-026

## Decision

The curated Product B MVP insurer universe is locked as:

### MVP top 5

1. HDFC ERGO
2. Star Health
3. ICICI Lombard
4. Care Health
5. Niva Bupa

### Top 10 later

6. Tata AIG
7. Bajaj Allianz
8. New India Assurance
9. Aditya Birla Health
10. SBI General

### Deferred

11. ManipalCigna
12. United India
13. Oriental Insurance
14. Reliance General
15. Future Generali

## Why This Ranking

The ranking is **not** a blanket consumer recommendation list.

It is a build-order list optimized for:

- high retail relevance,
- strong official source-document discoverability,
- realistic DSE-027 collection effort,
- enough product breadth to support a useful MVP.

## Score Table

| Rank | Insurer | Tier | Total | Retail | Market | Source docs | Breadth | Trust | Corpus | Key reason |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | HDFC ERGO | `mvp_top5` | 88 | 23 | 18 | 19 | 12 | 8 | 8 | Very strong source collectability and broad retail fit. |
| 2 | Star Health | `mvp_top5` | 87 | 25 | 18 | 19 | 13 | 6 | 6 | Deepest retail health relevance and strong downloads surface. |
| 3 | ICICI Lombard | `mvp_top5` | 84 | 22 | 18 | 17 | 12 | 8 | 7 | Major private retail presence with enough document visibility to justify early inclusion. |
| 4 | Care Health | `mvp_top5` | 83 | 24 | 16 | 20 | 13 | 6 | 4 | Excellent CIS/public-disclosure surface and strong family-health relevance. |
| 5 | Niva Bupa | `mvp_top5` | 78 | 23 | 15 | 16 | 12 | 7 | 5 | High retail importance despite slightly less centralized document discovery. |
| 6 | Tata AIG | `top10_later` | 76 | 18 | 15 | 18 | 12 | 8 | 5 | Good official downloads and useful breadth, but lower first-wave urgency than the top 5. |
| 7 | Bajaj Allianz | `top10_later` | 74 | 18 | 15 | 18 | 12 | 6 | 5 | Strong product documents and broad retail reach. |
| 8 | New India Assurance | `top10_later` | 72 | 17 | 16 | 20 | 11 | 4 | 4 | Best-in-class current public download structure among PSU candidates. |
| 9 | Aditya Birla Health | `top10_later` | 71 | 18 | 12 | 18 | 11 | 5 | 7 | Strategically important because it already proved the source-bundle problem and a working PBT/CIS path. |
| 10 | SBI General | `top10_later` | 68 | 17 | 14 | 18 | 10 | 5 | 4 | Good official downloads and strong SBI distribution, but thinner local base. |
| 11 | ManipalCigna | `deferred` | 57 | 16 | 11 | 14 | 11 | 5 | 0 | Valid health-specialist candidate, but weaker document ergonomics and no local corpus foothold. |
| 12 | United India | `deferred` | 56 | 13 | 14 | 17 | 10 | 2 | 0 | Official docs exist, but MVP value per QA hour is lower than selected top 10. |
| 13 | Oriental Insurance | `deferred` | 54 | 12 | 13 | 16 | 9 | 2 | 2 | Source navigation is usable but older and less MVP-friendly. |
| 14 | Reliance General | `deferred` | 53 | 14 | 12 | 15 | 10 | 1 | 1 | Some public source availability, but weaker first-wave priority. |
| 15 | Future Generali | `deferred` | 52 | 13 | 11 | 15 | 9 | 1 | 3 | Usable CIS path, but lower market pull and weaker MVP urgency. |

## Why The MVP Top 5 Won

### HDFC ERGO

- Strong official download/CIS structure
- Broad product lineup
- High user encounter probability
- Good Product A starting base

### Star Health

- One of the clearest pure-play health insurers for users
- Strong public downloads presence
- Major product breadth for family/senior/top-up use cases

### ICICI Lombard

- Big private retail insurer users actively encounter
- Enough document visibility to justify collection effort
- Broad enough product menu for comparison UX

### Care Health

- Excellent source-document ergonomics
- Strong standalone health relevance
- Good fit for family-floater-heavy recommendation use cases

### Niva Bupa

- Too important in actual health-insurance buying flows to omit
- Good current product visibility even if source discovery is less centralized
- Strong enough breadth for flagship, premium, value, and senior-oriented paths

## Why These Five Did Not Make MVP Top 5

### Tata AIG

Strong candidate, but lower retail centrality than the selected five.

### Bajaj Allianz

Strong document surface, but slightly lower first-wave retail pressure than Tata or the selected five.

### New India Assurance

Good source availability and public-sector relevance, but less attractive as a first-wave private-retail comparison anchor.

### Aditya Birla Health

Strategically important and likely high-value later, but the consumer MVP gets more coverage benefit from larger first-wave brands.

### SBI General

High distribution credibility, but thinner local corpus and lower immediate product depth than the chosen five.

## Why The Deferred Group Was Deferred

### ManipalCigna

Deferred because the source-collection path is less mature and local Product A coverage is absent.

### United India and Oriental

Deferred because they are still viable later, but their source ergonomics and MVP value per QA hour are weaker than New India and SBI.

### Reliance and Future Generali

Deferred because they do not currently beat the selected top-10 set on the combined score of:

- retail relevance,
- source-document collectability,
- Product A readiness.

## Consequence for DSE-027

DSE-027 should collect source bundles in this order:

1. HDFC ERGO
2. Star Health
3. ICICI Lombard
4. Care Health
5. Niva Bupa

The rest of the top 10 should wait until one insurer sprint proves the end-to-end bundle workflow.

## Artifact

Machine-readable manifest:

- `data/manifests/mvp_insurer_selection_v1.json`
