# Export Contract — Product A → Product B

## Contract Version

**Version:** 1.0
**Last updated:** 2026-06-05
**Status:** active (DSE-023 Product B Export v1 freeze)

---

## Producer

**Name:** doc-structure-engine (Product A)
**Role:** Document intelligence pipeline. Owns PDF parsing, structure extraction, fact extraction, provenance tracking.
**Output format:** JSON files per policy
**Output location:** `data/export/{policy_id}/`
**Handoff package:** `data/processed/product_b_export_v1/`

---

## Consumer

**Name:** insurance-agent (Product B)
**Role:** User-facing insurance assistant. Owns UI, comparisons, explanations, conversations.
**Input format:** JSON files (never queries raw engine tables directly)

---

## Export File Location

```
data/export/{policy_id}/
  policy_features.json         # 20-concept ontology-backed v1 derived view
  policy_fact_sources.json     # Evidence mapping for every field
  policy_clauses_minimal.json  # Clauses for context (lighter, no spans)

data/export/batch_{run_id}.json  # Deferred — not produced by DSE-013 v1. Per-policy files are the primary export.
```

## V1 Scope

DSE-023 freezes Product B Export v1 as the ontology-backed 20-concept JSON contract. It is the first Product B-consumable package and is intentionally narrower than the earlier planned 91-field comparison schema.

The 91-field view remains a future Product B schema expansion. It must not be assumed present in `export_schema_version = "1.0"`.

---

## Top-Level JSON Shape

```json
{
  "policy_id": "hdfc_ergo_arogya_sanjeevani",
  "export_schema_version": "1.0",
  "exported_at": "2026-06-01T12:00:00Z",
  "pipeline_run_id": "run_abc123",
  "source_document": { ... },
  "product_identity": { ... },
  "features": { ... },
  "unresolved_concepts": [],
  "parse_quality": { ... }
}
```

---

## Feature Object Shape

The exported feature set is governed by `ontology/concepts.v1.json`. The ontology defines the canonical concept ID, Product B export field name, value shape, unit, evidence requirements, and display semantics for every priority concept.

Every feature in the `features` map follows this structure:

```json
"<concept_slug>": {
  "value": <typed_value_or_null>,
  "unit": "<string_or_null>",
  "fact_status": "<status>",
  "confidence": <float_or_null>,
  "method": "<string_or_null>",
  "evidence": "<string_or_null>",
  "evidence_page": <int_or_null>,
  "evidence_clause": "<string_or_null>",
  "scope": <json_or_null>,
  "condition": <json_or_null>,
  "source_span_id": "<string_or_null>"
}
```

---

## Fact Status Values

| Status | Meaning | Display Rule |
|--------|---------|-------------|
| `present` | Found and verified | Show to user |
| `explicitly_not_covered` | Policy says not covered | Show as "Not covered" |
| `not_applicable` | Concept doesn't apply | Show as "N/A" |
| `not_found` | Looked but couldn't find | Show as "Not found in policy text" |
| `ambiguous` | Found but meaning unclear | Flag for review, don't show |
| `conflicting` | Multiple contradictory values | Flag for review, don't show |
| `requires_manual_review` | Low confidence or unusual value | Flag for review |

### Critical Display Rule

Never show "No deductible" unless `fact_status = explicitly_not_covered`. Otherwise show "Deductible not found in policy text."

---

## Evidence Requirements

Every fact with `fact_status = present` must have:

| Field | Required | Example |
|-------|----------|---------|
| `evidence` | Yes | "Pre-existing diseases are covered after 36 consecutive months" |
| `evidence_page` | Yes | 32 |
| `evidence_clause` | Yes | "4.1" |
| `source_span_id` | Yes | "span_abc456" |

Facts with `fact_status = not_found` may optionally have an evidence-like note explaining what was searched.

---

## Backward Compatibility Rules

1. **Version field is mandatory** — `export_schema_version` must be checked by Product B before processing.
2. **Adding new features is non-breaking** — Product B must handle unknown feature keys gracefully.
3. **Removing features is breaking** — increment the schema version when removing fields.
4. **Changing the structure of `value` is breaking** — increment the schema version.
5. **Adding new fields inside `value` is non-breaking** — Product B should ignore unknown sub-fields.
6. **Old exports remain valid** — never delete old export files when the schema changes. Keep them with their schema version.
7. **Product B reads compiled JSON only** — Product B must not query Product A SQLite, raw parser tables, physical/logical/table interim files, or raw PDFs.

---

## Example Export

### policy_features.json

```json
{
  "policy_id": "hdfc_ergo_arogya_sanjeevani",
  "export_schema_version": "1.0",
  "exported_at": "2026-06-01T12:00:00Z",
  "pipeline_run_id": "run_abc123",
  "source_document": {
    "filename": "HDFC_ERGO_Arogya_Sanjeevani_Policy_HDFC_ERGO.pdf",
    "file_hash": "sha256:abc123...",
    "source_domain": "website_policy_wording",
    "page_count": 31
  },
  "product_identity": {
    "insurer": "HDFC ERGO",
    "plan_name": "Arogya Sanjeevani Policy",
    "uin": "HDFHLIP...",
    "uin_base": "HDFHLIP...",
    "product_version": 1,
    "effective_date": "2024-04-01",
    "match_confidence": "high",
    "match_method": "uin_insurer_plan_verified"
  },
  "features": {
    "ped_waiting_months": {
      "value": 36,
      "unit": "months",
      "fact_status": "present",
      "confidence": 0.96,
      "method": "regex",
      "evidence": "Pre-existing diseases are covered after 36 consecutive months",
      "evidence_page": 32,
      "evidence_clause": "4.1",
      "scope": {"cover": "base_policy"},
      "condition": null,
      "source_span_id": "span_abc456"
    },
    "copay_percentage": {
      "value": null,
      "fact_status": "not_found",
      "confidence": null,
      "method": null,
      "evidence": null,
      "evidence_page": null,
      "evidence_clause": null,
      "scope": null,
      "condition": null,
      "source_span_id": null
    },
    "maternity_waiting_months": {
      "value": null,
      "fact_status": "not_applicable",
      "confidence": null,
      "method": null,
      "evidence": "Policy is individual mediclaim without maternity cover",
      "evidence_page": null,
      "evidence_clause": null,
      "scope": null,
      "condition": null,
      "source_span_id": null
    },
    "room_rent_limit": {
      "value": {"type": "percentage_of_si", "percentage": 1, "max_amount": null},
      "fact_status": "present",
      "confidence": 0.92,
      "method": "regex",
      "evidence": "Room rent is limited to 1% of Sum Insured",
      "evidence_page": 18,
      "evidence_clause": "2.5",
      "scope": {"cover": "base_policy"},
      "condition": null,
      "source_span_id": "span_abc459"
    }
  },
  "unresolved_concepts": ["newborn_cover"],
  "parse_quality": {
    "total_concepts_attempted": 20,
    "concepts_resolved": 16,
    "concepts_not_found": 3,
    "concepts_not_applicable": 1,
    "overall_fill_rate": 0.80,
    "average_confidence": 0.91
  }
}
```

### policy_fact_sources.json

```json
{
  "policy_id": "hdfc_ergo_arogya_sanjeevani",
  "pipeline_run_id": "run_abc123",
  "sources": {
    "ped_waiting_months": {
      "provenance": [
        {
          "clause_number": "4.1",
          "clause_title": "Pre-existing Disease",
          "clause_text": "Pre-existing diseases are covered after 36 consecutive months from policy inception",
          "page": 32,
          "source_span_type": "clause",
          "extraction_method": "regex",
          "extractor_name": "ped_waiting",
          "candidate_score": 0.96,
          "pipeline_run_id": "run_abc123"
        }
      ],
      "accepted_candidate_id": "candidate_abc001"
    }
  },
  "conflicts_resolved": [],
  "unresolved_conflicts": []
}
```

### policy_clauses_minimal.json

```json
{
  "policy_id": "hdfc_ergo_arogya_sanjeevani",
  "sections": [
    {
      "number": "4",
      "title": "Waiting Period",
      "clauses": [
        {
          "number": "4.1",
          "title": "Pre-existing Disease",
          "text": "Pre-existing diseases are covered after 36 consecutive months from policy inception",
          "page": 32
        }
      ]
    }
  ]
}
```

---

## Confidence Guidelines

| Method | Default confidence |
|--------|-------------------|
| regex (simple) | 0.90-0.98 |
| regex (complex) | 0.80-0.90 |
| table_parser | 0.80-0.95 |
| heuristic | 0.70-0.85 |
| llm (evidence verified) | 0.70-0.85 |
| llm (no evidence) | reject |
| manual | 1.0 |

---

## Export Schema History

| Version | Changes | Date | Status |
|---------|---------|------|--------|
| 1.0 | Initial contract | 2026-05-29 | Superseded by DSE-023 wording |
| 1.0 | DSE-013 implements 20-concept export skeleton | 2026-06-01 | Historical — 5/20 concepts populated |
| 1.0 | DSE-023 freezes 20-concept ontology-backed Product B handoff contract | 2026-06-05 | Current |
