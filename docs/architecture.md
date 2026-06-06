# Architecture

## Overview

PolicyLens is a deterministic document compiler for Indian health insurance policy PDFs. It converts policy wordings into structured, provenance-tracked facts.

It does NOT:
- chat with users
- render application UIs
- solve generic retrieval/search problems
- use OCR or vision (corpus is 100% text-layer)
- use embeddings or vector search (not needed for extraction)

---

## Pipeline

```
PDF Corpus (647 active policy wordings)
  │
  ▼
Phase -1: CORPUS LOCKDOWN
  Document type firewall → active/policy_wording filter → excluded triage
  │
  ▼
Phase 0: UIN RECONCILIATION
  Insurer/plan normalizer → 5-tier matching → unmatched triage
  │
  ▼
Phase 1: PHYSICAL LAYER
  pdfplumber → pages, blocks, lines, text_spans, coordinates, fonts
  │
  ▼
Phase 2: LOGICAL STRUCTURE
  Scored heading candidates → section tree → clause segmentation → cross-references
  │
  ▼
Phase 3: TABLE ENGINE
  Table detection → type classification → cell extraction → header lineage
  │
  ▼
Phase 4: CLAUSE STORE
  All data persisted with source_spans → pipeline versioning
  │
  ▼
Phase 5: FACT CANDIDATES
  All extractors run → candidates scored → conflicts detected → accepted/rejected
  │
  ▼
Phase 6: DETERMINISTIC EXTRACTION
  15-20 high-value concepts → normalizers → typed value_json → scope/condition
  │
  ▼
Phase 7: GOLD CORPUS
  5 → 20 policies manually annotated → iteration loop
  │
  ▼
Phase 8: DERIVED EXPORT
  20-concept compiled export package → evidence chain → downstream analysis/consumption
```

---

## Layered Design

```
┌──────────────────────────────────────────┐
│  Phase 8: Derived Export Package          │
│  Compiled ontology-backed JSON over facts │
└──────────────────────────────────────────┘
                     ▲
┌──────────────────────────────────────────┐
│  Phase 5-6: Fact Extraction Engine       │
│  Candidates → scoring → conflict res.    │
│  Deterministic + LLM refinement          │
└──────────────────────────────────────────┘
                     ▲
┌──────────────────────────────────────────┐
│  Phase 2-4: PolicyLens                   │
│  Physical → Logical → Clause AST         │
│  Tables + Source Spans + Provenance      │
└──────────────────────────────────────────┘
                     ▲
┌──────────────────────────────────────────┐
│  Phase -1, 0: Identity Layer             │
│  Corpus lockdown + UIN reconciliation    │
└──────────────────────────────────────────┘
                     ▲
                     │
              PDF Corpus (647 files)
```

---

## Data Flow

```
Raw PDF
  → physical text (pdfplumber)
    → logical AST (heading scorer + section tree)
      → clause boundaries (segmenter)
        → tables (type classifier + extraction engine)
          → source spans (bbox + char range)
            → fact candidates (all extractors run)
              → scored + ranked per concept
                → accepted as extracted_facts
                    → compiled into derived_policy_features
                    → exported as structured JSON package
```

---

## Repository Boundaries

```
PolicyLens
  ├── Owns: parsing, extraction, storage, gold corpus, provenance
  ├── Outputs: structured JSON exports + evidence chains
  └── Not responsible: UI, chat, or live application workflows
```
