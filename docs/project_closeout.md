# Project Closeout

Date: 2026-06-06
Status: closed

## Summary

`doc-structure-engine` is complete as a learning, research, and open-source project.

The repository should not be read as an actively advancing product roadmap. It should be read as:

- a document-intelligence engine built against a real regulated-document problem,
- a case study in evaluation-driven extraction,
- a record of what worked,
- and a record of where the product thesis broke.

## Original Goal

The original ambition was to help build an agentic alternative to noisy insurance aggregators by turning insurer PDFs into structured, explainable policy data.

The product expectation was:

- user fills in profile information,
- system narrows the field,
- system recommends 1-3 policies with citations,
- user avoids spam-call-led insurance discovery.

## What Was Built

The project successfully built:

- corpus lockdown and document-type filtering,
- UIN reconciliation,
- physical layout extraction,
- heading scoring and section-tree construction,
- clause segmentation,
- table extraction,
- source spans and clause store,
- deterministic extraction for 20 priority insurance concepts,
- evaluated 20-policy gold corpus,
- full-corpus scale pipeline over 647 active policy wordings,
- source-bundle registry,
- curated 30-product MVP insurer/product bundle registry,
- Product B handoff export package.

## What Worked

### Engineering

- The document compiler approach was materially better than naïvely sending PDFs to a general LLM.
- Precision-first extraction with evidence requirements worked.
- Evaluation gates and gold-corpus discipline prevented a lot of silent self-deception.
- The parser/extractor stack became strong enough to generate credible structured outputs from complex policy documents.

### Learning

- The project surfaced where LLMs fail on long legal/product documents.
- It showed that clause structure, provenance, and normalization matter more than generic “RAG”.
- It created a substantial public engineering artifact worth preserving.

## What Broke

The consumer-product thesis did not fail because parsing was impossible. It failed because **product truth is an operational data problem, not only a parsing problem**.

Key problems:

1. Policy wording PDFs alone are not enough.
2. Variant truth often lives in PBTs, CIS documents, brochures, and schedules.
3. Product names, UIN versions, and live sellability drift over time.
4. Public insurer documents are fragmented and not maintained as one canonical open dataset.
5. A stale recommendation system in insurance is trust-destroying.

The project’s turning point was the realization that a policy can be “correctly parsed” and still be **misleading as a product recommendation** if variant-level truth lives elsewhere.

## Final Strategic Decision

The broad product ambition is closed.

This repository will **not** continue as:

- a solo-maintained national insurance comparison engine,
- a fully current insurer-data platform,
- or a direct PolicyBazaar replacement.

The repository remains valuable as:

- an open-source engine,
- a portfolio-grade system,
- a teaching artifact,
- and a base for technical writing or future narrower tools.

## What This Repo Should Be Used For Now

Reasonable uses:

- learning how to build evaluated document pipelines,
- studying evidence-linked extraction,
- adapting the compiler approach to another regulated domain,
- open-source reference work,
- technical writing / project retrospective material.

Unreasonable uses:

- treating it as live market-complete insurance truth,
- plugging it into a production recommendation flow without fresh document operations,
- assuming missing facts mean missing coverage,
- assuming policy wording alone fully defines product comparison truth.

## Final State

At closeout, the repo has:

- 20 reviewed gold policies,
- 20 active deterministic concepts,
- full parser / table / extraction pipeline,
- full test suite passing,
- source-bundle registry,
- curated MVP insurer/product bundle set,
- public open-source hygiene and governance docs.

## Future Directions

These are possibilities, not commitments:

1. write technical articles from the project,
2. open-source the repo and keep it stable,
3. adapt the engine into a more general document-compiler / provenance system,
4. build a much narrower curated advisor only if manual source governance is acceptable.

No future direction in this document should be read as an active project plan.
