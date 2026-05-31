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
**Consumer:** `structure_parser/heading_scorer.py`, `structure_parser/section_tree.py` (DSE-006)

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

## Contract 3A: Heading Scorer Output

**Producer:** `structure_parser/heading_scorer.py`
**Consumer:** DSE-006 section tree builder

```json
{
  "document_id": "sha256:abc123",
  "policy_id": "HDFHLIP23024V072223",
  "total_lines_scored": 1392,
  "total_headings": 15,
  "config": {
    "threshold": 0.5,
    "body_font_mode": 11.04,
    "pipeline_run_id": "physical_v1_fixed"
  },
  "candidates": [
    {
      "candidate_id": "policy_candidate_00001",
      "line_id": "p2l_12",
      "text": "1. Preamble",
      "page_number": 2,
      "bbox": [50.0, 120.0, 130.0, 134.0],
      "span_ids": ["p2s_101", "p2s_102"],
      "normalized_text": "1. preamble",
      "numbering_token": "1.",
      "level_hint": 1,
      "score": 0.865,
      "features": {},
      "feature_contributions": {},
      "decision": "heading",
      "threshold_applied": 0.5
    }
  ]
}
```

Rules:
- DSE-005 candidates are visual-heading candidates only.
- DSE-006 must not treat all candidates as final sections without applying tree logic.
- `heading_labels.json` is the DSE-005 visual-heading eval target; `sections.json` remains the logical structure eval target.

---

## Contract 3B: Section Tree Output

**Producer:** `structure_parser/section_tree.py` (DSE-006)
**Consumer:** DSE-007 extractors, DSE-010 clause store

```json
{
  "schema_version": "section_tree.v1",
  "parser_version": "section_tree_builder.v2",
  "document_id": "sha256:abc123",
  "policy_id": "hdfc_arogya_sanjeevani",
  "pipeline_run_id": "physical_v1_fixed",
  "config": {
    "heading_threshold": 0.5,
    "synthetic_detection": "compact_numbered_iterative_v2",
    "clause_segmentation": "numbered_prefix_and_paragraph_gap_v2"
  },
  "source_paths": {
    "physical": "data/interim/physical/hdfc_arogya_sanjeevani/document_physical.json",
    "heading_candidates": "data/interim/logical/hdfc_arogya_sanjeevani/heading_candidates.json"
  },
  "issues": [],
  "total_sections": 67,
  "total_clauses": 67,
  "total_visual_headings": 15,
  "total_synthetic_sections": 52,
  "sections": [
    {
      "section_id": "hdfc_arogya_sanjeevani_sec_0001",
      "heading_candidate_id": "policy_candidate_00001",
      "heading_line_id": "p2l_12",
      "number": "1",
      "title": "1. Preamble",
      "normalized_title": "1. preamble",
      "level": 1,
      "heading_type": "visual",
      "heading_score": 0.865,
      "parent_id": "hdfc_arogya_sanjeevani_root_0000",
      "children": [],
      "page_start": 2,
      "page_end": 2,
      "line_ids": ["p2l_12", "p2l_13", "p2l_14"],
      "content_line_ids": ["p2l_13", "p2l_14"],
      "text": "This Policy is a contract of insurance issued by..."
    },
    {
      "section_id": "hdfc_arogya_sanjeevani_sec_0016",
      "heading_candidate_id": null,
      "heading_line_id": "p2l_45",
      "number": "3.1",
      "title": "3.1. Accident means a sudden unforeseen and involuntary event",
      "normalized_title": "3.1. accident means a sudden unforeseen and involuntary event",
      "level": 2,
      "heading_type": "synthetic_body_numbered",
      "heading_score": null,
      "parent_id": "sec_abc789",
      "children": [],
      "page_start": 2,
      "page_end": 2,
      "line_ids": ["p2l_45", "p2l_46"],
      "content_line_ids": ["p2l_46"],
      "text": "caused by external visible means..."
    }
  ],
  "section_tree": {
    "section_id": "hdfc_arogya_sanjeevani_root_0000",
    "level": 0,
    "children": [
      {
        "section_id": "sec_abc123",
        "level": 1,
        "children": []
      }
    ]
  },
  "clauses": [
    {
      "clause_id": "clause_0001",
      "section_id": "sec_abc123",
      "clause_number": "1",
      "title": "Preamble",
      "page_start": 2,
      "page_end": 2,
      "line_ids": ["p2l_13", "p2l_14"],
      "text": "This Policy is a contract...",
      "segmentation_method": "default",
      "confidence": 0.5
    }
  ]
}
```

Rules:
- Sections with `heading_type = "visual"` come from DSE-005 heading candidates.
- Sections with `heading_type = "synthetic_body_numbered"` are detected from body-numbered lines inside leaf visual sections.
- Sections with `heading_type = "synthetic_body_heading"` are detected from structural all-caps body headings missed by DSE-005.
- Section and clause IDs are deterministic within the policy output.
- Every section has `line_ids` (all lines owned by this section including children) and `content_line_ids` (this section's body lines excluding children).
- Every clause has `segmentation_method` (numbered_body, paragraph_gap, default) and `confidence`.
- TOC headings may appear in the tree; evaluators exclude TOC/CIS/cover rows from hard gates.
- Clause `text` must not be truncated.

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

**Producer:** `extractors/` and `scripts/run_fact_extractors.py`
**Consumer:** Internal evals, later DSE-010 clause/source-span store and DSE-013 derived export.

DSE-007 writes candidate-first extraction output under:

```text
data/interim/facts/{policy_slug}/fact_candidates.json
data/interim/facts/{policy_slug}/accepted_facts.json
data/interim/facts/fact_extraction_run_summary.json
```

Every candidate is retained, including rejected candidates, so error analysis can inspect why a match was rejected or lost conflict resolution.

```json
{
  "candidate_id": "ped_waiting_period_0000",
  "concept": "ped_waiting_period",
  "value_json": {"months": 36},
  "normalized_value_json": {"months": 36},
  "fact_status": "present",
  "scope_json": {"cover": "base_policy"},
  "condition_json": null,
  "extraction_method": "deterministic",
  "confidence": 0.96,
  "evidence_span_id": "clause:clause_0064",
  "pipeline_run_id": "physical_v1_fixed",
  "evidence_page": 28,
  "evidence_text": "Expenses related to the treatment of a pre-existing Disease (PED) ... expiry of 36 months ...",
  "evidence_clause_id": "clause_0064",
  "evidence_line_ids": ["p28l_41", "p28l_42"],
  "extractor_name": "ped_waiting_period",
  "extractor_version": "1.0.0",
  "pattern_id": "ped_waiting_duration",
  "source": "section_tree_clause",
  "accepted": true,
  "rejection_reason": null,
  "debug": {}
}
```

Accepted facts use the same AGENTS §14 fields as candidates. If no safe candidate exists for a concept, emit one accepted `not_found` fact:

```json
{
  "concept": "co_pay",
  "value_json": null,
  "normalized_value_json": null,
  "fact_status": "not_found",
  "scope_json": null,
  "condition_json": null,
  "extraction_method": "deterministic",
  "confidence": 0.0,
  "evidence_span_id": null,
  "pipeline_run_id": "physical_v1_fixed",
  "evidence_page": null,
  "evidence_text": null,
  "evidence_clause_id": null,
  "evidence_line_ids": [],
  "extractor_name": "co_pay",
  "extractor_version": "1.0.0"
}
```

Provisional evidence rule:
- Until DSE-010 builds true source spans, deterministic facts use `evidence_span_id = "clause:{clause_id}"`.
- `evidence_clause_id` and `evidence_line_ids` must also be stored.
- Evidence text must be an exact normalized substring of the DSE-006 clause extraction text.
- DSE-007 may enrich clause extraction text with the section heading line because some policies put fact-bearing values in the heading itself.

---

## Contract 4A: Normalizer Result Shape

**Producer:** `normalizers/`
**Consumer:** deterministic extractors and eval scripts

DSE-008 normalizers return dictionaries with a shared minimum shape:

```json
{
  "value": 500000,
  "normalized": {"amount": 500000, "currency": "INR"},
  "span": [0, 7],
  "text": "₹5 lakh"
}
```

Type-specific normalized payloads:

```json
{"amount": 500000, "currency": "INR"}
{"special_value": "actuals", "currency": "INR"}
{"days": 30}
{"months": 48}
{"percentage": 20}
{"age_years": 61, "comparator": "gte"}
{"coverage_status": "conditional"}
```

Allowed money `special_value` statuses:
- `actuals`
- `as_charged`
- `subject_to_limit`

Allowed coverage statuses:
- `covered`
- `not_covered`
- `conditional`
- `covered_with_actuals`
- `unknown`

Compatibility rule:
- DSE-007 APIs `find_durations`, `normalize_duration`, `find_percentages`, and `normalize_percentage` remain available.
- Special money values must not be emitted as `0` or `null`.
- Negated coverage phrases such as `not covered` and `not admissible` must normalize to `not_covered`, not `covered`.

---

## Contract 3C: Table Engine Output

**Producer:** `table_engine/table_detector.py`, `table_engine/text_alignment_detector.py`
**Consumer:** DSE-010 Clause Store, DSE-011 Fact Candidate Scoring (table-origin facts)
**Task:** DSE-009
**Date:** 2026-05-31

### Output files per policy

```
data/interim/tables/{policy_slug}/document_tables.json
data/interim/tables/{policy_slug}/document_table_cells.json
```

### Extraction method enum

| Value | Meaning |
|---|---|
| `pdfplumber_lattice` | Table has visible grid lines; cells reliably extracted via pdfplumber |
| `pdfplumber_text` | Conservative pdfplumber text-strategy candidate retained only for small headered grids |
| `text_alignment_candidate` | Borderless table detected by column x-cluster heuristics; cells may be partial |

### Table type enum

| Value | Description |
|---|---|
| `waiting_period` | Waiting period durations by type (PED, initial, specific disease) |
| `schedule_of_benefits` | Benefit schedule with limits (room rent, ICU, ambulance, NCB) |
| `room_rent` | Room rent sub-limits by room category or variant |
| `premium` | Premium rate tables by age/sum-insured band |
| `claims_documents` | Document checklist for claim submission |
| `network_list` | List of network hospitals |
| `unknown` | Could not classify with confidence |

### `ExtractedTable` shape

```json
{
  "table_id": "care_health_care_plus_p4_t1",
  "document_id": "sha256:...",
  "policy_id": "care_health_care_plus",
  "page": 4,
  "bbox": [72.0, 234.5, 480.0, 310.2],
  "table_type": "waiting_period",
  "table_type_confidence": 0.91,
  "extraction_method": "pdfplumber_lattice",
  "row_count": 5,
  "col_count": 2,
  "has_header_row": true,
  "header_row_index": 0,
  "header_rows": [0],
  "column_headers": ["Waiting period type", "Duration"],
  "cells": [...],
  "raw_lines": [],
  "column_clusters": null,
  "parent_clause_id": "care_health_care_plus_s4_c2",
  "parent_clause_confidence": 0.75,
  "issues": []
}
```

### `TableCell` shape

```json
{
  "cell_id": "care_health_care_plus_p4_t1_r0_c0",
  "table_id": "care_health_care_plus_p4_t1",
  "row_index": 0,
  "col_index": 0,
  "text": "Waiting period type",
  "bbox": [72.0, 234.5, 280.0, 248.0],
  "is_header": true,
  "column_header_text": null,
  "row_header_text": null,
  "row_span": 1,
  "col_span": 1
}
```

### `ColumnCluster` shape (text_alignment_candidate only)

```json
{
  "col_index": 0,
  "x_center": 90.5,
  "x_min": 72.0,
  "x_max": 110.0
}
```

### `raw_lines` shape (text_alignment_candidate only)

When borderless table structure is detected but cells cannot be safely split,
`cells` must remain `[]` and the source physical lines must be preserved:

```json
{
  "line_id": "p8l_59",
  "text": "3.52. Waiting Period means a period from the inception...",
  "bbox": [75.144, 735.12528, 523.07432, 746.16528]
}
```

### `TableDocument` shape (document_tables.json)

```json
{
  "schema_version": "1.0.0",
  "pipeline_run_id": "table_v1_...",
  "document_id": "sha256:...",
  "policy_id": "care_health_care_plus",
  "source_pdf_path": "...",
  "page_count": 57,
  "tables_found": 5,
  "structured_tables": 3,
  "candidate_tables": 2,
  "tables": [...],
  "issues": []
}
```

### Rules

1. `bbox` may be `null` for text_alignment_candidate tables where line bounds are insufficient.
2. `cells` may be `[]` for text_alignment_candidate tables where column split is ambiguous; in this case `issues` must contain `"cells_not_reliably_split"` and `raw_lines` must preserve the source lines.
3. `None` cell values from pdfplumber are normalized to `""` before storage.
4. `pdfplumber_text` tables are retained only when they have a reliable header row, 2-8 columns, 2-30 rows, and a bounded table area.
5. Missing pdfplumber cell coordinates must be recorded as `cell_bbox_missing:<count>` in the table `issues` array.
6. `parent_clause_id` is provisional (shortest containing clause page span plus owning section depth); will be replaced by bbox overlap in DSE-010.
7. All table IDs are stable: `{policy_id}_p{page}_t{n}` where n is 1-based per page.
8. `document_table_cells.json` is the flat list of all cells from `document_tables.json` for easier downstream lookup.

### `physical_table_labels.json` shape

DSE-009 evaluates physical tables against a separate label file per policy. Legacy
`tables.json` remains semantic/manual annotation history and is not the hard-gate
target for physical table extraction.

```json
{
  "label_id": "new_india_floater_phys_table_003",
  "source_table_id": "dse009_physical_review_added",
  "page": 16,
  "bbox": [53.88, 210.5, 561.22, 571.03],
  "table_type": "schedule_of_benefits",
  "headers": ["S No", "Treatment or Procedure", "Limit (Per Policy Period)"],
  "rows": [["3.15.1", "Uterine Artery Embolization and HIFU", "Upto 20% of Sum Insured"]],
  "header_rows": [0],
  "column_count": 3,
  "row_count": 13,
  "priority": true,
  "reviewer_note": "Physical modern-treatment limit table."
}
```

### Bbox note

All gold `tables.json` entries have `bbox = null` until DSE-012 manual review. DSE-009 produces machine-suggested bboxes in `document_tables.json`. A review report at `data/reports/dse009_table_bbox_review_candidates.json` lists predicted bboxes for manual verification before gold commit.

### DSE-009 v3 gate note

The strict DSE-009 eval treats same-page table presence as diagnostic only. A physical label is detected only when the extracted table has matching bbox/type/content signature. DSE-003 `tables.json` rows that summarize prose are documented in `data/reports/dse009_gold_table_source_review.md` and excluded from DSE-009 hard gates.

---

## Contract 6: Accepted Facts → Derived Export

**Producer:** `extractors/` (after conflict resolution)
**Consumer:** `derived/policy_feature_builder.py`

See `docs/export_contract.md` for the full export contract. This is the Product A → Product B boundary.
