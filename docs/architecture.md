# Architecture

## Overview

doc-structure-engine is a deterministic document compiler for Indian health insurance policy PDFs. It converts policy wordings into structured, provenance-tracked facts.

It does NOT:
- Chat with users (that's Product B)
- Search or retrieve (that's Product B)
- Render UIs (that's Product B)
- Use OCR or vision (corpus is 100% text-layer)
- Use embeddings or vector search (not needed for extraction)

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
  20-concept Product B export v1 → evidence chain → downstream product consumes
```

---

## Layered Design

```
┌──────────────────────────────────────────┐
│           Product B (insurance-agent)     │
│  Consumes compiled policy_features.json   │
└──────────────────────────────────────────┘
                     ▲
                     │ export contract
                     │
┌──────────────────────────────────────────┐
│  Phase 8: Derived Product B Export v1     │
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
│  Phase 2-4: Document Structure Engine    │
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
                    → exported as policy_features.json
```

---

## Boundaries

```
doc-structure-engine (Product A)
  ├── Owns: all parsing, extraction, storage, gold corpus
  ├── Outputs: policy_features.json + evidence chains
  └── Not responsible: UI, search, conversations, users

insurance-agent (Product B)
  ├── Owns: user-facing features, comparisons, explanations
  ├── Inputs: policy_features.json from Product A
  └── Not responsible: PDF extraction, fact verification
```
