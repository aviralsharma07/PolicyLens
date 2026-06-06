# PolicyLens

Deterministic, evidence-linked document intelligence for Indian health insurance policy documents.

`PolicyLens` is a standalone document compiler for Indian health insurance policy PDFs. It compiles policy documents into structured, provenance-backed data with explicit evidence and status fields. It was built to answer a hard document-intelligence problem: legal and product PDFs are not useful unless extracted facts stay tied to source text, structure, and context.

This repository is currently optimized for:

- Indian health insurance policy wordings and adjacent official product documents
- structured extraction with explicit evidence
- evaluation-driven development on a reviewed gold corpus
- cautious, precision-first structured outputs

It is **not** a chat app, a generic RAG wrapper, or a universal “extract anything from any PDF” product.

---

## What this project does

The engine turns policy documents into a layered representation:

1. **Identity**
   - corpus lockdown
   - document-type filtering
   - insurer / plan normalization
   - UIN reconciliation

2. **Physical parsing**
   - page / block / line extraction
   - coordinates and layout metadata

3. **Logical parsing**
   - heading scoring
   - section tree construction
   - clause segmentation

4. **Table handling**
   - table detection and extraction
   - header lineage
   - source linkage

5. **Fact extraction**
   - deterministic extractors for 20 priority concepts
   - evidence-backed fact candidates
   - conflict handling

6. **Compiled export**
   - JSON export package for inspection, analysis, or downstream use
   - explicit `fact_status`, confidence, and evidence

---

## Why it exists

This project started from a real document and product-truth frustration:

- policy aggregators were noisy and opaque
- important products were hidden or inconsistently surfaced
- sales flows were stronger than explanation flows
- “compare plans” UX often lacked source-backed truth

The first idea was to let a general LLM read PDFs directly. That failed for three reasons:

1. cost and scaling pressure,
2. weak structure fidelity on long legal documents,
3. no reliable typed output layer for comparison-grade data.

So this project became a document compiler instead of a generic RAG demo.

---

## Repository status

This project is **complete as a learning / research / open-source artifact**.

Active feature development is closed. The repository is being preserved because the underlying work is real and useful:

- deterministic document parsing for complex regulated PDFs
- evidence-linked structured extraction
- evaluation-driven engineering discipline
- source-bundle modeling for product-truth problems

It is **not** being actively continued as a live insurance-comparison product roadmap.

If you are reading this as a builder:

- use the repo as a case study, reference implementation, or starting point
- do not assume the insurer corpus will stay current without ongoing document operations
- do not treat the exported facts as a production insurance recommendation service

---

## How to try it

There are three useful ways to try `PolicyLens`.

### 1. Verify the repository state

This is the fastest way to confirm the project is healthy locally:

```bash
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py data/manifests/product_source_bundles_v1.draft.json
PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py data/manifests/product_source_bundles_mvp_v1.json
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
```

### 2. Inspect the included artifacts

If you want to understand what the engine produces, start with:

```text
gold_corpus/policies/
data/reports/
data/manifests/product_source_bundles_v1.draft.json
data/manifests/product_source_bundles_mvp_v1.json
data/processed/product_b_export_v1/   # historical path name for the compiled export package
```

Recommended reading order:

1. `gold_corpus/policies/*/facts.json`
2. `data/reports/dse025_source_bundle_baseline_audit.md`
3. `data/reports/dse026_top10_top5_selection.md`
4. `data/reports/dse027_curated_mvp_bundle_closeout_v1.md`

### 3. Reuse the engine on your own text-layer PDFs

If you want to adapt the project, the main reusable entry points are:

```text
scripts/corpus_lockdown.py
scripts/uin_match_report.py
scripts/run_heading_scorer.py
scripts/run_section_tree.py
scripts/run_table_engine.py
scripts/run_fact_extractors.py
scripts/run_clause_store.py
scripts/run_export.py
```

The project is most suitable when your documents are:

- text-layer PDFs,
- structurally repetitive within a domain,
- high-stakes enough to require evidence,
- and better served by precision-first extraction than broad fuzzy retrieval.

---

## Current status

As of the final documented state:

- 20 reviewed gold-corpus policies
- full parser and extractor pipeline implemented
- 20/20 priority deterministic concepts active
- full test suite passing
- curated MVP insurer universe selected
- curated 30-product MVP source-bundle registry built
- current-version drift against live insurer sources explicitly tracked
- public open-source release hardening completed
- project closeout documented

The most important strategic lesson so far:

> Policy wording PDFs alone are not enough for launch-grade insurance comparison.

Many comparison-critical values live in:

- Product Benefit Tables (PBTs)
- Customer Information Sheets (CIS)
- brochures / prospectuses
- variant-specific tables

That is why the repository now includes a **source-bundle registry** and a curated MVP bundle set.

---

## Current capabilities

### Parser / structure

- active-policy corpus filtering
- UIN lifecycle matching
- physical layout extraction from text-layer PDFs
- heading scorer and section tree builder
- clause segmentation
- table extraction and evaluation
- source span generation

### Semantic extraction

Deterministic extractors are active for 20 priority concepts, including:

- pre-existing disease waiting period
- initial waiting period
- co-pay
- deductible
- room rent limit
- ICU limit
- claim intimation timeline
- restoration benefit
- modern treatment coverage
- newborn coverage

Every exported concept uses explicit status values such as:

- `present`
- `explicitly_not_covered`
- `not_applicable`
- `not_found`
- `ambiguous`
- `conflicting`
- `requires_manual_review`

### Product identity / source bundles

- draft full-corpus source-bundle registry
- curated MVP source-bundle registry for 30 current/live products
- source-quality tracking:
  - `complete`
  - `acceptable_with_known_gap`
  - `missing_pbt`
  - `missing_cis`
  - `stale_version`
  - others

---

## What this project does not do

- no user-facing UI
- no consumer chat product
- no embeddings/vector-search layer for end-user retrieval
- no OCR-first pipeline
- no “extract anything from any document” promise

This repository is intentionally narrower:

> structured, evidence-aware compilation of regulated insurance documents

---

## Repo layout

```text
PolicyLens/
├── README.md
├── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── docs/
│   ├── architecture.md
│   ├── evaluation.md
│   ├── export_contract.md
│   ├── data_contracts.md
│   ├── database_strategy.md
│   ├── development_protocol.md
│   ├── ai_execution_protocol.md
│   ├── decisions.md
│   ├── changelog.md
│   ├── risk_register.md
│   ├── tasks.md
│   ├── glossary.md
│   └── product_b_mvp_gtm_strategy.md
├── identity/
├── pdf_parser/
├── structure_parser/
├── table_engine/
├── clause_store/
├── extractors/
├── ontology/
├── derived/
├── source_bundles/
├── scripts/
├── tests/
├── data/
│   ├── manifests/
│   ├── interim/
│   ├── processed/
│   ├── reports/
│   └── tmp/
└── runs/
    ├── sessions/
    ├── experiments/
    └── evals/
```

---

## Quick start

### Requirements

- Python 3.9+
- macOS/Linux shell
- text-layer PDFs for the main parser path

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Basic validation

```bash
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
```

### Source bundle validation

```bash
PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py data/manifests/product_source_bundles_v1.draft.json
PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py data/manifests/product_source_bundles_mvp_v1.json
```

---

## Key artifacts

### Gold corpus

Reviewed benchmark corpus:

```text
gold_corpus/policies/
```

### Full-corpus scale identity

```text
data/manifests/active_policy_wordings_v1.json
data/manifests/uin_match_report_v1.json
```

### Source-bundle registries

```text
data/manifests/product_source_bundles_v1.draft.json
data/manifests/product_source_bundles_mvp_v1.json
```

### MVP insurer/product selection

```text
data/manifests/mvp_insurer_selection_v1.json
data/manifests/mvp_product_candidates_v1.json
data/manifests/mvp_product_candidates_verified_v1.json
```

### Compiled export package

```text
data/processed/product_b_export_v1/
```

---

## Documentation map

If you are new to the repo, read in this order:

1. [README.md](./README.md)
2. [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)
3. [docs/architecture.md](./docs/architecture.md)
4. [docs/evaluation.md](./docs/evaluation.md)
5. [docs/data_contracts.md](./docs/data_contracts.md)
6. [docs/export_contract.md](./docs/export_contract.md)
7. [docs/project_closeout.md](./docs/project_closeout.md)
8. [docs/tasks.md](./docs/tasks.md)
9. [docs/decisions.md](./docs/decisions.md)
10. latest file in [runs/sessions/](./runs/sessions/)

Most important public docs:

- [architecture](./docs/architecture.md)
- [evaluation](./docs/evaluation.md)
- [data contracts](./docs/data_contracts.md)
- [export contract](./docs/export_contract.md)
- [database strategy](./docs/database_strategy.md)
- [project closeout / retrospective](./docs/project_closeout.md)

---

## Open-source scope

This repo is being published primarily as:

- a working document-intelligence system
- a learning artifact in evaluation-driven AI engineering
- a case study in structured extraction from regulated documents
- a truthful record of where a consumer-AI product idea stopped being operationally sane

It is **not** being presented as:

- a complete insurance comparison business
- a fully self-updating national insurance database
- a legal/commercial source of truth for all live products

The curated MVP source-bundle work exists precisely because “parse old PDFs once and trust them forever” is not good enough.

---

## Important limitations

1. **This is a domain-shaped engine, not a universal document extractor.**
2. **Current insurer product truth can drift over time.**
3. **Some product bundles are still incomplete even after latest-version verification.**
4. **The downstream recommendation product must respect source quality.**
5. **`not_found` must never be treated as `not covered`.**
6. **The repo is optimized for text-layer PDFs, not scanned-image corpora.**

---

## Design principles

- Clauses are source truth. Fields are derived views.
- Unknown is acceptable. Wrong is fatal.
- Precision over recall.
- No extracted fact without evidence.
- Compiled outputs are safer to consume than raw parser internals.

---

## Contributing

Please read:

- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- [SECURITY.md](./SECURITY.md)

For substantial changes, keep the project’s operating rules:

- small verified steps
- tests/evals before claims
- session logs for meaningful work
- no silent failures

---

## License

This project is licensed under the [MIT License](./LICENSE).
