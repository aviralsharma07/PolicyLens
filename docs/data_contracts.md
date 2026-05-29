# Data Contracts

This document defines the schema contracts between modules within the engine.

---

## Module Boundaries

```
identity module  →  pdf_parser module  →  clause_store module  →  extractors module  →  derived module
```

Each step produces files/tables consumed by the next. These are the contracts between them.

---

## Contract 1: Corpus Lockdown → UIN Reconciliation

**Producer:** `identity/corpus_lockdown.py`
**Consumer:** `identity/uin_matcher.py`

```json
{
  "file_id": "sha256:abc123",
  "filename": "HDFC_ERGO_Arogya_Sanjeevani_Policy_HDFC_ERGO.pdf",
  "file_path": "/path/to/policy_data/09_HDFC_ERGO/...",
  "file_hash": "sha256:abc123...",
  "size_bytes": 730900,
  "page_count": 31,
  "document_type": "policy_wording",
  "status": "active",
  "insurer_raw": "HDFC ERGO",
  "plan_name_raw": "Arogya Sanjeevani Policy",
  "source_domain": "website_policy_wording",
  "source_url": null,
  "classified_insurer": "HDFC ERGO",
  "classified_plan": "Arogya Sanjeevani",
  "initial_match_status": "pending"
}
```

---

## Contract 2: UIN Reconciliation → Physical Parser

**Producer:** `identity/uin_matcher.py`
**Consumer:** `pdf_parser/layout_extractor.py`

```json
{
  "file_id": "sha256:abc123",
  "file_path": "...",
  "file_hash": "sha256:abc123...",
  "matched_uin": "HDFHLIP23024V072223",
  "uin_base": "HDFHLIP23024",
  "product_version": 7,
  "match_confidence": 0.94,
  "match_method": "fuzzy_insurer_plan",
  "match_status": "auto_high_confidence",
  "normalized_insurer": "HDFC_ERGO",
  "normalized_plan": "AROGYA_SANJEEVANI",
  "candidate_matches": [
    {"uin": "HDFHLIP23024V072223", "score": 0.94},
    {"uin": "HDFHLIP23024V062223", "score": 0.72}
  ]
}
```

---

## Contract 3: Physical Parser → Structure Parser

**Producer:** `pdf_parser/layout_extractor.py`
**Consumer:** `pdf_parser/heading_detector.py`, `pdf_parser/section_tree.py`

```json
{
  "document_id": "sha256:abc123",
  "pages": [
    {
      "page_number": 1,
      "width": 612,
      "height": 792,
      "blocks": [
        {
          "block_id": 1,
          "block_type": "text",
          "bbox": [50, 100, 562, 120],
          "lines": [
            {
              "line_id": 1,
              "bbox": [50, 100, 562, 115],
              "spans": [
                {
                  "text": "4. Waiting Period",
                  "font_size": 14.0,
                  "font_name": "Helvetica-Bold",
                  "is_bold": true,
                  "bbox": [50, 100, 200, 115]
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "page_count": 31,
  "parser_version": "1.0.0"
}
```

---

## Contract 4: Clause Store → Extractor Candidates

**Producer:** `clause_store/repository.py` (after Phase 2-3)
**Consumer:** `extractors/candidate_registry.py`

```json
{
  "document_id": "sha256:abc123",
  "sections": [
    {
      "section_id": "uuid-1",
      "number": "4",
      "title": "Waiting Period",
      "clauses": [
        {
          "clause_id": "uuid-2",
          "number": "4.1",
          "title": "Pre-existing Disease",
          "text": "Pre-existing diseases are covered after 36 consecutive months from policy inception",
          "page": 32,
          "source_spans": [{"span_id": "uuid-3", "page": 32, "bbox": [50, 200, 562, 220], "text": "...", "char_start": 100, "char_end": 200}],
          "tables": []
        }
      ]
    }
  ]
}
```

---

## Contract 5: Fact Candidates → Accepted Facts

**Producer:** `extractors/candidate_registry.py`
**Consumer:** Internal (scoring + conflict resolution within extractors module)

```json
{
  "candidates": [
    {
      "candidate_id": "uuid-4",
      "clause_id": "uuid-2",
      "concept": "PED_WAITING_MONTHS",
      "value_json": {"months": 36},
      "evidence_span_id": "uuid-3",
      "extractor_name": "ped_waiting",
      "extractor_version": "1.0.0",
      "pattern_id": "ped_waiting_v1",
      "score": 0.96,
      "normalizer_version": "1.0.0"
    }
  ]
}
```

---

## Contract 6: Accepted Facts → Derived Export

**Producer:** `extractors/` (after conflict resolution)
**Consumer:** `derived/policy_feature_builder.py`

See `docs/export_contract.md` for the full export contract. This is the Product A → Product B boundary.
