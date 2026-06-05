# Session: MVP Insurer Selection

Date: 2026-06-06
Task ID: DSE-026
Project: doc-structure-engine
Branch: main
AI executor: Codex
Human reviewer: Avi

## Goal

Define the long-term top 10 insurer universe and the first top 5 MVP insurers
for Product B, using a reproducible rubric plus evidence from:

- Product A local corpus readiness
- current public source-document availability
- current retail/market relevance signals

## Relevant Docs Read

- `AGENTS.md`
- `docs/tasks.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/product_b_mvp_gtm_strategy.md`
- `docs/changelog.md`
- `docs/decisions.md`
- `docs/risk_register.md`
- `runs/sessions/2026-06-05-product-source-bundle-registry.md`
- `data/reports/dse025_source_bundle_baseline_audit.md`

## Files Changed

- `scripts/analyze_dse026_insurer_universe.py`
- `data/reports/dse026_insurer_selection_rubric.md`
- `data/reports/dse026_corpus_availability_analysis.json`
- `data/reports/dse026_corpus_availability_analysis.md`
- `data/reports/dse026_market_trust_evidence.md`
- `data/reports/dse026_top10_top5_selection.md`
- `data/reports/dse026_mvp_product_candidate_rationale.md`
- `data/manifests/mvp_insurer_selection_v1.json`
- `data/manifests/mvp_product_candidates_v1.json`
- `docs/tasks.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/product_b_mvp_gtm_strategy.md`
- `docs/changelog.md`
- `docs/risk_register.md`

## Commands Run

```bash
git status --short
PYTHONPATH=. .venv/bin/python scripts/analyze_dse026_insurer_universe.py
PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py data/manifests/product_source_bundles_v1.draft.json
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
git diff --check
git status --short
```

## Results

- Added a canonical-insurer analysis helper for local corpus readiness.
- Locked the MVP top 5 as HDFC ERGO, Star Health, ICICI Lombard, Care Health, and Niva Bupa.
- Locked the later-wave top 10 additions as Tata AIG, Bajaj Allianz, New India Assurance, Aditya Birla Health, and SBI General.
- Deferred ManipalCigna, United India, Oriental Insurance, Reliance General, and Future Generali from first-wave MVP scope.
- Defined 30 product collection targets for DSE-027, six per MVP insurer.
- Validation passed: source bundle registry validation, gold corpus validation, JSON parsing, full pytest, and `git diff --check`.

## Generated Artifacts

- `data/reports/dse026_insurer_selection_rubric.md`
- `data/reports/dse026_corpus_availability_analysis.json`
- `data/reports/dse026_corpus_availability_analysis.md`
- `data/reports/dse026_market_trust_evidence.md`
- `data/reports/dse026_top10_top5_selection.md`
- `data/reports/dse026_mvp_product_candidate_rationale.md`
- `data/manifests/mvp_insurer_selection_v1.json`
- `data/manifests/mvp_product_candidates_v1.json`

## Decisions Made

- Use a weighted rubric instead of ad hoc insurer picking.
- Separate local corpus strength from external market/source desirability.
- Favor source collectability in tie-breaks because DSE-027 depends on it.
- Start DSE-027 with HDFC ERGO instead of beginning with a lower-volume proof case.

## Issues / Limitations

- Current active manifest still lacks source URLs.
- Local bundle registry is overwhelmingly policy-wording-heavy.
- Some insurer source pages are easier to discover through search than through stable site navigation.
- Several product candidates still need exact current sellability and UIN re-verification during DSE-027.

## Next Step

Run DSE-027 for HDFC ERGO:

- collect wording + CIS + brochure + PBT/table sources for the six selected products;
- hash and classify every document;
- record missing pieces honestly instead of forcing launch readiness.
