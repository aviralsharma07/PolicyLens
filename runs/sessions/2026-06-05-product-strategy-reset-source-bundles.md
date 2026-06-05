# Session: Product Strategy Reset — Source Bundles and Curated MVP

Date: 2026-06-05
Task ID: DSE-025 planning reset
Project: doc-structure-engine
Branch: main
AI executor: Codex
Human reviewer: Avi

## Goal

Record the strategic pivot discovered during Product B prototype review:

- Product A's 647-policy pipeline is valuable diagnostic infrastructure.
- Product B should not launch as a 647-policy comparison product.
- Launch-grade recommendations require curated top-insurer products with complete official source bundles.
- Product identity must move from one PDF to a bundle of policy wording, Product Benefit Table, CIS, brochure/prospectus, and rider/add-on sources.

## Relevant Docs Read

- `docs/tasks.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/export_contract.md`
- `docs/data_contracts.md`
- `docs/decisions.md`
- `docs/risk_register.md`
- `docs/changelog.md`

## Triggering Finding

The Product B prototype showed Aditya Birla Activ Care co-pay as a single high-confidence 15% value.

Source review showed the actual issue:

- The local source PDF was a policy wording document.
- The policy wording supported a conditional 15% co-pay for treatment outside the Preferred Provider Network.
- Separate Product Benefit Table / brochure material exposed variant-level co-pay provisions such as Standard/Classic/Premier values.
- Therefore the extracted fact was evidence-backed but Product B display flattened a conditional value into a misleading generic scalar.

This is not a small UI bug. It is a product-model issue.

## What We Learned About PBT / CIS

Policy wordings often do not contain the full product truth needed for comparison. They frequently delegate numeric values to:

- Product Benefit Table / table of benefits;
- Policy Schedule;
- CIS;
- brochure/prospectus tables;
- rider/add-on documents.

Policy schedule values are customer-specific and usually unavailable publicly. PBT/CIS/brochure sources are therefore critical for public product comparison.

Product A currently parses policy wordings well, but policy wording alone is not enough for launch-grade Product B recommendations.

## Why 647-Policy Breadth Is Not MVP Scope

DSE-020 proved the engine can run across 647 active policy wordings, with 566 unique documents exported. That matters for scale confidence.

But launch value does not come from showing hundreds of products. A real buyer needs:

- fewer choices;
- trusted insurers;
- official citations;
- clear caveats;
- variant-aware values;
- profile-aware recommendation;
- honest unknowns.

The correct MVP scope is therefore:

- top 5 insurers first;
- roughly 6-7 important retail products/variants per insurer;
- 30-40 source-bundled product choices;
- 1-3 user recommendations, not a giant table.

## Strategic Decisions Recorded

- ADR-0041 — Curated top-insurer MVP over 647-policy launch.
- ADR-0042 — Product identity is a source bundle, not one PDF.
- ADR-0043 — Product B recommendations require variant/condition-scoped facts.

## Files Changed

- `docs/tasks.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/product_b_mvp_gtm_strategy.md`
- `docs/decisions.md`
- `docs/risk_register.md`
- `docs/export_contract.md`
- `docs/data_contracts.md`
- `docs/changelog.md`
- `runs/sessions/2026-06-05-product-strategy-reset-source-bundles.md`

## Decisions Made

1. Product B should not pursue all 647 policies for MVP.
2. Product B should focus on a top-insurer curated corpus.
3. Product A needs a source-bundle registry before launch-grade recommendations.
4. PBT/CIS/brochure completeness must become a source-quality gate.
5. Variant-specific and conditional facts must not be flattened into scalar displays.
6. LLM refinement remains useful later, but it cannot replace missing official source documents.

## Next Tasks

1. DSE-025 — Product Source Bundle Registry.
2. DSE-026 — Top 10 Insurer Universe + MVP Top 5 Selection.
3. DSE-027 — MVP Source Bundle Sprint: Insurer 1.
4. DSE-028 — Bundle-Aware Product B Export.
5. Product B advisor flow over curated source-bundled products.

## Issues / Limitations

- Current Product B export v1 remains useful for prototype evidence exploration, but not final recommendation-grade product comparison when PBT/CIS/source bundles are missing.
- No source-bundle registry exists yet.
- Top 10 / top 5 insurer selection still needs evidence-backed finalization.
- Public source collection may be incomplete for old, group, custom, or discontinued products.

## Next Step

Implement DSE-025 as a docs/schema-first Product A task, then run a focused source-bundle sprint for one insurer before scaling to all top 5 MVP insurers.

