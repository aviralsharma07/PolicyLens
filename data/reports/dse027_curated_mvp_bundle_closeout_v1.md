# DSE-027 Curated MVP Bundle Closeout v1

Date: 2026-06-06
Task ID: DSE-027

## Purpose

Verify the 30-product DSE-026 MVP shortlist against current official insurer surfaces before treating it as a launch-target corpus, then assemble a curated MVP source-bundle registry that keeps current URLs, local reviewed files, and source-quality gaps explicit.

## What DSE-027 Added

- A verified-candidate manifest with current official product pages and current/latest document links where available.
- A latest-version audit for all 30 MVP candidates.
- A curated MVP source-bundle registry separate from the 507-bundle full-corpus draft registry.
- A downloader/index flow for current official source documents.

## Verification Result

- Candidate count reviewed: 30
- `verified_current`: 27
- `verified_current_with_gap`: 3
- `live`: 30
- `replaced`: 0
- `unresolved`: 0
- `dropped`: 0

## Current-Version Drift Found

DSE-027 proved that relying on the older local corpus versions would have been unsafe for Product B. Notable examples:

- HDFC ERGO:
  - `Optima Secure` moved from older local wording `HDFHLIP21016...` to current official CIS `HDFHLIP26058V082526`.
  - `Optima Restore` moved to `HDFHLIP26055V102526`.
- Star Health:
  - `Star Comprehensive` current official table shows `SHAHLIP26044V092526`.
  - `Family Health Optima` current official table shows `SHAHLIP26046V092526`.
  - `Medi Classic` current official table shows `SHAHLIP26047V092526`.
  - `Senior Citizens Red Carpet` current official table shows `SHAHLIP26041V082526`.
  - `Arogya Sanjeevani` current official prospectus shows `SHAHLIP26045V042526`.
- Niva Bupa:
  - `ReAssure 2.0` current official wording confirms `NBHHLIP26042V022526`.
  - `Health Companion` moved to `NBHHLIP26051V092526`.
  - `Senior First` moved to `NBHHLIP27053V022627`.
  - `Arogya Sanjeevani` moved to `NBHHLIP26045V032526`.
- ICICI Lombard:
  - `Complete Health Insurance` now points to a newer official PDF under `ICIHLIP23144V072223`.

This is the central DSE-027 lesson: **curated MVP collection must trust current official insurer documents over older local corpus versions whenever they disagree.**

## Download Result

- Current official documents downloaded and hashed: 45
- Download failures recorded: 2

Failures:

1. `star_health_family_health_optima` brochure
   - URL: `https://web.starhealth.in/sites/default/files/brochure/FHO-Brochure.pdf`
   - Error: host-resolution failure via automated downloader
2. `star_health_super_surplus` brochure
   - URL: `https://web.starhealth.in/sites/default/files/prospectus/Super-Surplus-Insurance-Policy.pdf`
   - Error: `403 Forbidden`

These failures were recorded in `data/reports/dse027_source_download_index_v1.json` and were not silently ignored.

## Curated Bundle Registry Result

Final curated registry:

- `data/manifests/product_source_bundles_mvp_v1.json`
- bundle count: 30

Source-quality distribution:

- `acceptable_with_known_gap`: 18
- `missing_cis`: 6
- `missing_pbt`: 4
- `stale_version`: 2

By insurer:

- HDFC ERGO: 4 `missing_pbt`, 2 `stale_version`
- Star Health: 5 `acceptable_with_known_gap`, 1 `missing_cis`
- ICICI Lombard: 6 `acceptable_with_known_gap`
- Care Health: 6 `acceptable_with_known_gap`
- Niva Bupa: 5 `missing_cis`, 1 `acceptable_with_known_gap`

## Interpretation

DSE-027 is a success, but not because it made the MVP corpus “complete.” It is a success because it made the MVP corpus **truthful**:

- all 30 shortlisted products now have a current official product footprint;
- current-version drift is documented rather than hidden;
- 45 current official documents were pulled into a reproducible local cache;
- bundles now clearly separate:
  - current official URLs,
  - downloaded current docs,
  - older reviewed local docs,
  - and remaining gaps.

## What Is Now Safe To Say

- The MVP top-5 insurer universe is real and currently sellable.
- Product-level source collection can proceed without re-deciding insurer/product scope.
- Product B should not yet assume these 30 bundles are recommendation-ready.
- DSE-028 must make bundle/source quality visible in Product B export semantics.

## Next Step

Start `DSE-028 — Bundle-Aware Product B Export`.

Immediate export requirement:

- carry source bundle quality into Product B,
- carry current document provenance,
- carry variant/condition scope,
- block overconfident user-facing comparison when a bundle remains incomplete.
