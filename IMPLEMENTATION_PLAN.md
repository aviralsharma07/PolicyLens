# Document Structure Engine — Implementation Plan v2

## Project Closeout — 2026-06-06

Active development on `doc-structure-engine` is closed.

This document now serves as a **historical implementation record**, not an active roadmap. The repository is being preserved as an open-source engineering artifact and project retrospective.

Important interpretation rules:

- completed sections below remain part of the project record,
- previously planned work should not be read as committed future execution,
- any “next task” language in older sections is historical unless explicitly reactivated later.

Final strategic conclusion:

- the document compiler work was successful,
- the broad insurance-comparison product thesis was not operationally sane as a solo side-project built on public insurer PDFs,
- the repo should now be read as a reference implementation, learning artifact, and open-source case study.

## Strategic Reset — 2026-06-05

The 647-policy pipeline proved parser, extractor, and export capability, but Product B should **not** launch as a 647-policy comparison product. That would optimize for breadth before trust.

Product B MVP will focus on **5 top insurers** and roughly **30-40 high-value retail products/variants**, each backed by complete official source bundles.

Core truths from Product B prototype review:
- Current engine parses policy wordings well.
- Policy wording alone is insufficient for Product B recommendations.
- Product Benefit Tables (PBTs), CIS documents, brochures/prospectuses, and schedule-like tables often hold variant-specific values missing from the wording.
- Launch-grade recommendations require product bundles, not isolated PDFs.
- Accuracy, source quality, citations, and user education matter more than corpus breadth.
- The 647-policy corpus remains useful as diagnostic infrastructure, not as the MVP launch universe.

The Aditya Birla Activ Care co-pay review is the concrete failure mode: the policy wording supported a conditional 15% non-preferred-provider co-pay, while Standard/Classic/Premier variant-level co-pay values lived in a separate Product Benefit Table. Product B must not flatten those into one generic scalar.

## Current State — 2026-06-06

All 20 priority deterministic concepts are active and passing 20-policy gold benchmark gates. DSE-021 completed the remaining 7 extractors (claim intimation timeline, deductible, room rent limit, ICU limit, restoration benefit, modern treatment coverage, newborn coverage) with precision 100%, evidence accuracy 100%, false-present count 0. DSE-024 resolved all parser-target zero-clause failures, reducing the count from 132 to 0. DSE-022 passed the 20-policy table eval. DSE-023 froze the first Product B handoff package. The full-corpus pipeline runs on 647 policies with 566 unique docs exported.

Product A now has:
- 20 reviewed gold policies.
- 647 active policy wordings identified.
- Physical layout extraction.
- Heading/section/clause parsing.
- Physical table engine v1 with 20-policy eval gate passing.
- SQLite clause store and source spans.
- Fact candidate scoring and conflict infrastructure.
- Product B export v1 handoff package.
- **20/20 priority concepts with active deterministic extractors**.
- DSE-020 full-corpus scale triage completed and passing.
- 0 parser-target zero-clause failures; 1 excluded parser target.
- Product Source Bundle Registry v1 with 507 draft bundles.
- Curated MVP source-bundle registry v1 with 30 latest-reviewed product bundles.

Product A is ready for curated insurer/product selection before launch-grade Product B recommendations. The first Product B handoff package is available at `data/processed/product_b_export_v1` and should be consumed by `insurance-agent` as compiled JSON only, but it should be treated as a prototype/evidence-explorer dataset until PBT/CIS/brochure source bundles are downloaded, hashed, reviewed, and exported.

The next risks are:
- schedule/condition-heavy facts,
- unresolved/ambiguous facts requiring LLM refinement,
- full-corpus semantic QA beyond the 20-policy gold benchmark,
- Product B display semantics validated through the local prototype,
- missing PBT/CIS/brochure documents causing incomplete or misleading product comparisons,
- variant-specific facts flattened into one scalar value.

## Historical Roadmap After Strategic Reset

1. DSE-019 — Canonical Insurance Concept Ontology Registry v1 — done
2. DSE-020 — Full 647-Policy Pipeline Dry Run + Scale Triage — done
3. DSE-024 — Full-Corpus Parser Remediation for Zero-Clause Policies — done
4. DSE-021 — Remaining Deterministic Extractors Wave 2 — done
5. DSE-022 — 20-Policy Table Eval Expansion + Table Remediation — done
6. DSE-023 — Product B Export v1 Freeze + Handoff Dataset — done
7. PB-001 — Local PolicyLens Prototype over Product A Export — active in `insurance-agent`
8. DSE-025 — Product Source Bundle Registry — done
9. DSE-026 — Top 10 Insurer Universe + MVP Top 5 Selection — done
10. DSE-027 — Curated MVP Source Bundle Sprint with Latest-Version Safety Gate — done
11. DSE-028 — Bundle-Aware Product B Export — deferred at project closeout
12. Product B advisor flow over curated source-bundled products — deferred at project closeout
13. DSE-014 — Evidence-Constrained LLM Refinement — deferred at project closeout

The old "full-corpus Product B export refresh" path is deferred. DSE-020 remains a valuable scale diagnostic, but the MVP launch path was never taken to a maintained product state.

## MVP Product Strategy

Product B should behave like a trustworthy advisor, not a directory.

Launch scope:
- Top 5 insurers first.
- Roughly 6-7 important retail products/variants per insurer.
- Total MVP corpus: 30-40 products/variants.
- Every user-facing recommendation should cite official source text.
- The recommendation output should be 1-3 policies max, plus explicit "why not" caveats where useful.

Long-term product universe:
- Top 10 Indian health insurers only, unless traction proves that deeper coverage is worth the QA cost.
- No attempt to cover every old, group, rider, withdrawn, or low-signal product.

Source bundle requirement:
- Policy wording provides legal clauses.
- Product Benefit Table / table of benefits provides variant-specific limits and co-pay/room/ICU/deductible values.
- CIS provides consumer-facing summary and regulatory key terms.
- Brochure/prospectus helps product/variant discovery but must not override wording/PBT without source evidence.
- Policy schedule is customer-specific and usually unavailable publicly; schedule-dependent facts must remain explicitly marked.

Parser remediation, extractor wave 2, table eval expansion, Product B export v1, source-bundle registry v1, DSE-026 insurer/product selection, and DSE-027 curated MVP source-bundle collection are complete. The next priority is DSE-028 bundle-aware export. LLM refinement comes later and should refine evidence-constrained facts, not compensate for missing official product documents.

DSE-025 baseline result: current manifests can generate 507 draft product bundles, but 504 are `missing_pbt`, 1 is `acceptable_with_known_gap` (Aditya Birla Activ Care with official source URLs identified but not downloaded/hash-reviewed), and 2 are `rejected`. This confirms the source-bundle pivot: the old corpus is strong as policy wording infrastructure, not as a complete Product B recommendation corpus.

DSE-026 result: the MVP top 5 are locked as **HDFC ERGO, Star Health, ICICI Lombard, Care Health, and Niva Bupa**. Later-wave top 10 additions are **Tata AIG, Bajaj Allianz, New India Assurance, Aditya Birla Health, and SBI General**.

DSE-027 result: the MVP universe is now pinned to **30 current/live product candidates** across the top 5 insurers. All 30 were latest-version reviewed against current official insurer surfaces. The curated registry at `data/manifests/product_source_bundles_mvp_v1.json` currently contains:

- `acceptable_with_known_gap`: 18
- `missing_cis`: 6
- `missing_pbt`: 4
- `stale_version`: 2

The task also proved substantial version drift between older local corpus files and current live insurer documents. Product B should trust the DSE-027 curated bundle registry over historical wording files whenever the two disagree.

DSE-020 infrastructure and smoke validation were completed. The 647-policy manifest is collision-safe, DSE-020 outputs are namespaced, and 20-policy DB/export smoke passed. The full 647-policy pipeline run completed: per-policy stages passed for all 647 policies, batch DB/export processed 591 unique docs (56 duplicate-hash skipped), 566 exported. Triage report generated and accepted.

## Core Diagnosis

Based on analysis of 909 PDFs (647 active policy wordings) and 1,099 IRDAI UIN records:

> We do **not** have an OCR problem. We do **not** have a PDF extraction problem.
> We have a **document structure + product identity + legal-fact normalization problem**.

**Corpus facts:**
- ~100% text-layer PDFs (no scanned documents)
- 647 clean active policy wordings after filtering
- 73% of files are policy wordings (rest: brochures, circulars, non-health, etc.)
- 1,099 UIN records from IRDAI health products listing
- 78% of files matchable to UIN by insurer + plan name
- 0 PDFs have UIN embedded in filename/metadata (must extract from text)

**Enemies (in order):**
1. UIN reconciliation
2. Policy versioning
3. Clause hierarchy
4. Table normalization
5. Scope / condition handling
6. Fact provenance
7. Avoiding false positives

---

## Core Philosophy

> Clauses are source truth. Fields are derived views.

> Unknown is acceptable. Wrong is fatal.

> Precision > recall. Always.

---

## Architecture

```
PDF Corpus (909 files)
 ↓
[Phase -1] Corpus Lockdown
  → Document type firewall
  → Active/policy_wording filter
  → Excluded docs triage
  → 647 clean files
 ↓
[Phase 0] UIN Reconciliation
  → Insurer/plan normalizer
  → 5-tier match system
  → Unmatched triage
  → Every file has match_status
 ↓
[Phase 1] Physical Layout Extraction
  → pdfplumber: pages, blocks, lines, text_spans
  → Coordinates, font sizes, reading order
  → Header/footer removal
  → Output: document_physical.json
 ↓
[Phase 2] Structure Parser (Logical Layer)
  → Scored heading candidates (not binary)
  → Section tree construction
  → Clause segmentation
  → Cross-reference detection
  → Output: document_logical_ast.json
 ↓
[Phase 3] Table Engine
  → Table type classifier
  → Camelot + pdfplumber
  → Raw cell storage with coordinates
  → Header lineage preservation
  → Output: document_tables.json
 ↓
[Phase 4] Clause Store + Source Spans
  → 15 core tables in SQLite
  → Every clause/fact → source_spans (bbox, char range)
  → Pipeline run versioning
  → Debug HTML exports
 ↓
[Phase 5] Fact Candidate Extraction
  → Generate ALL candidates (not first-match-wins)
  → Score + rank per concept
  → Conflict detection
  → Acceptance with rejection reasons
 ↓
[Phase 6] Deterministic Extractors (15-20 concepts)
  → Normalizers: money, duration, percentage, age, coverage, Indian number words
  → Priority concepts (see below)
  → Every extractor: concept + value_json + scope_json + condition_json + evidence + confidence + status
 ↓
[Phase 7] Gold Corpus (5 → 20)
  → 5 deeply annotated first
  → Expand after stable
 ↓
[Phase 8] Derived 91-Field Export → Product B
  → Every field: value/status, confidence, evidence, source document, method
  → Never export without evidence chain
```

---

## 18 Core Tables

```
products
├── id
├── uin_base
├── normalized_insurer
├── normalized_plan_name
├── product_type
└── insurance_type

product_versions
├── id
├── product_id FK
├── full_uin
├── version_label
├── effective_date
├── withdrawal_date
├── active_status
└── source_priority

source_documents
├── id
├── product_version_id FK
├── document_type          # policy_wording / brochure / circular / prospectus / reference_data
├── source_url
├── source_domain          # irdai / insurer_website
├── filename
├── file_hash              # SHA-256 for dedup
├── page_count
├── canonical_status       # canonical / alternate / withdrawn
└── parser_status          # pending / parsed / failed

document_pages
├── id
├── document_id FK
├── page_number
├── width
├── height
├── rotation
└── is_cover_page

document_blocks
├── id
├── page_id FK
├── bbox_json              # {x0, y0, x1, y1}
├── block_type             # text / image / table / header / footer
└── text

document_lines
├── id
├── block_id FK
├── bbox_json
└── text

document_text_spans
├── id
├── line_id FK
├── bbox_json
├── font_size
├── font_name
├── is_bold
├── is_italic
├── color
└── text

document_sections
├── id
├── document_id FK
├── section_number         # "4", "4.1"
├── title
├── level                  # 0=document, 1=section, 2=clause, 3=subclause
├── parent_id FK → document_sections
├── page_start
├── page_end
└── heading_score          # from scored detector

policy_clauses
├── id
├── section_id FK
├── clause_number          # "4.1"
├── title
├── raw_text               # Full text of the clause
├── page
├── children_json          # Subclause IDs
└── references_json        # Cross-references to other clauses

source_spans
├── id
├── document_id FK
├── page_number
├── block_ids_json
├── table_cell_ids_json
├── bbox_json
├── text
├── char_start
├── char_end
└── source_span_type          # text / table_cell / table_row / heading / clause / page_region

document_tables
├── id
├── document_id FK
├── page
├── bbox_json
├── parent_clause_id FK
├── extraction_method      # camelot_lattice / camelot_stream / pdfplumber / manual
├── table_type             # schedule_of_benefits / waiting_period / room_rent / premium / etc.
└── confidence

document_table_cells
├── id
├── table_id FK
├── row_index
├── col_index
├── text
├── bbox_json
├── row_span
├── col_span
└── is_header

extracted_fact_candidates
├── id
├── clause_id FK
├── concept
├── candidate_value_json
├── evidence_span_id FK → source_spans
├── extractor_name         # "regex_free_look" / "table_waiting_period" / "llm_refinement"
├── extractor_version      # semver of the extractor that produced this candidate
├── pattern_id             # specific regex pattern or heuristic rule ID
├── normalizer_version     # version of the normalizer applied
├── score                  # 0.0 - 1.0
├── accepted
└── rejection_reason

extracted_facts
├── id
├── clause_id FK
├── concept
├── value_json             # typed structure (not flat string)
├── normalized_value_json  # canonical form
├── value_type             # duration / percentage / money / age / coverage_status / text
├── unit
├── numeric_value
├── currency
├── duration_months
├── percentage
├── coverage_status        # covered / not_covered / conditional
├── scope_json             # {cover: "base"/"optional"/"add-on", member_type: ..., network_type: ...}
├── condition_json         # {entry_age_min: 61, sum_insured_band: ...}
├── extraction_method      # regex / table_parser / heuristic / llm / manual
├── confidence
├── evidence_span_id FK → source_spans
├── pipeline_run_id FK → pipeline_runs
├── fact_status            # present / explicitly_not_covered / not_applicable / not_found / ambiguous / conflicting / requires_manual_review
├── validated
└── validator

fact_conflicts
├── id
├── fact_a_id FK → extracted_facts
├── fact_b_id FK → extracted_facts
├── conflict_type          # same_concept_different_value / general_vs_schedule / base_vs_optional / old_vs_new / definition_vs_benefit
├── resolution             # resolved / unresolved
├── resolved_by
└── resolution_notes

pipeline_runs
├── id
├── git_commit
├── parser_version
├── extractor_version
├── ontology_version
├── started_at
├── finished_at
├── status
├── input_count
├── success_count
├── failure_count
└── notes

validation_labels
├── id
├── document_id FK
├── pipeline_run_id FK
├── label_type              # heading / clause / table / fact
├── concept
├── expected_value_json
├── expected_source_span
├── expected_page
├── annotator
├── reviewed_by
├── label_status            # draft / reviewed / final
└── notes

derived_policy_features
├── id
├── product_version_id FK
├── document_id FK
├── pipeline_run_id FK
├── feature_json
├── feature_schema_version
├── created_at
└── export_status

document_issues
├── id
├── document_id FK
├── pipeline_run_id FK
├── issue_type              # missing_text_layer / weird_reading_order / table_parse_failed / heading_conflict / duplicate_section_number / uin_ambiguous / clause_segmentation_low_confidence
├── severity                # error / warning / info
├── page_number
├── description
├── raw_context
└── resolved
```

| Status | Meaning | Display Rule |
|--------|---------|-------------|
| `present` | Found and verified | Show to user |
| `explicitly_not_covered` | Policy says "not covered" | Show as "Not covered" |
| `not_applicable` | Concept doesn't apply to this plan type | Show as "N/A" |
| `not_found` | Looked but couldn't find | Show as "Not found in policy text" |
| `ambiguous` | Found but meaning unclear | Flag for review, don't show |
| `conflicting` | Multiple contradictory values | Flag for review, don't show |
| `requires_manual_review` | Low confidence or unusual pattern | Flag for review |

**Critical rule**: Never show "No deductible" unless `fact_status = explicitly_not_covered`. Otherwise show "Deductible not found in policy text."

---

## Priority Concepts (15-20, grow from data)

| # | Concept | Category | Expected Value Type |
|---|---------|----------|-------------------|
| 1 | PED waiting period | waiting_period | duration (months) |
| 2 | Initial waiting period | waiting_period | duration (months) |
| 3 | Specific disease waiting periods | waiting_period | list of {disease, months} |
| 4 | Room rent limit | room_rent | percentage_of_SI or amount |
| 5 | ICU limit | room_rent | percentage_of_SI or amount |
| 6 | Co-pay | cost | percentage |
| 7 | Deductible | cost | amount or percentage |
| 8 | Cumulative bonus / NCB | benefit | {increase%, max%, base} |
| 9 | Restoration benefit | benefit | coverage_status |
| 10 | AYUSH coverage | benefit | coverage_status |
| 11 | Modern treatment coverage | benefit | coverage_status |
| 12 | Maternity waiting | waiting_period | duration (months) |
| 13 | Newborn coverage | benefit | coverage_status |
| 14 | Organ donor coverage | benefit | coverage_status |
| 15 | Ambulance coverage | benefit | amount |
| 16 | Free look period | regulatory | duration (days) |
| 17 | Grace period | regulatory | duration (days) |
| 18 | Renewability | regulatory | coverage_status |
| 19 | Claim intimation timeline | claim | duration |
| 20 | Claim settlement timeline | claim | duration |

---

## Canonical Ontology Registry

The ontology registry is the canonical source for Product A concept identity, value shapes, export mapping, evidence requirements, and Product B display semantics.

Registry location:

```text
ontology/
├── concepts.v1.json
├── loader.py
└── validator.py
```

The registry must define all 20 priority concepts. Existing extractor target concepts, export field mappings, and gold corpus fact labels must agree with the registry. Product B display rules must come from ontology-backed fact status semantics, especially the distinction between `not_found` and `explicitly_not_covered`.

The registry does not replace extractors, normalizers, source spans, or evals. It prevents drift between them.

---

## Normalizers Library

```text
normalizers/
├── money.py               # "₹5 lakh" → 500000, "Rs. 5,00,000" → 500000, "1 crore" → 10000000
├── duration.py            # "36 months" → 36, "2 years" → 24, "1 yr" → 12
├── percentage.py          # "20%" → 20, "20 per cent" → 20
├── age.py                 # "60 years" → 60, "18 yrs" → 18
├── coverage_status.py     # "covered" → covered, "not covered" → not_covered, "covered after waiting" → conditional
└── indian_number_words.py # "lakh" → 100000, "crore" → 10000000, "lac" → 100000
```

Every extractor pipeline: candidate detection → normalization → validation → fact creation (not regex match → fact).

---

## Scored Heading Detection

Not binary heading detection. Score-based:

```python
heading_score =
    numbering_score         # matches "4.", "4.1", "SECTION 4" patterns
  + font_score              # font size significantly above body text
  + bold_score              # is_bold or is_italic
  + spacing_score           # extra space before/after
  + insurance_heading_score # matches known heading dictionary
  + toc_match_score         # matches table of contents entry
  - sentence_like_penalty   # starts with lowercase, ends with period
  - too_long_penalty        # > 100 chars
  - footer_header_penalty   # in bottom/top 10% of page
  - all_caps_false_positive # "THE COMPANY SHALL NOT BE LIABLE"
```

Only headings above configurable threshold become sections.

---

## Extractor Pipeline

```
clause or table
  ↓
candidate generation (ALL extractors run)
  ↓
candidate scoring (confidence, evidence quality)
  ↓
conflict detection (multiple values for same concept)
  ↓
candidate acceptance or rejection
  ↓
fact emission with full metadata
```

Not first-match-wins. Store rejected candidates too during debugging.

---

## Evidence-Constrained LLM (Phase 6+)

Rules:
1. Only send relevant clause context (not entire PDF)
2. LLM must quote exact supporting snippet from the clause
3. Verify evidence string exists in clause text
4. If evidence not found → reject the fact
5. LLM facts get lower default confidence than deterministic

Output format:
```json
{
  "facts": [
    {
      "concept": "ROOM_RENT_LIMIT",
      "value": {"type": "no_limit"},
      "evidence": "There is no restriction on room rent...",
      "confidence": 0.78
    }
  ]
}
```

---

## Visual Debugging

Generate debug HTML from the start. Not product UI — engineering instrumentation.

```text
debug/
  {policy_id}/
    page_01.html       # Headings highlighted blue, clauses green, tables orange
    page_02.html
    ...
    ast.json           # Full AST visualization
    tables.json        # Table cell structure
    facts.html         # Extracted facts with source highlights
```

pdfplumber has built-in visual debugging utilities.

---

## Historical Initial Sprint Plan

This section records the original build plan. The current active roadmap is listed near the top of this document.

### Day 1: Corpus Lockdown

**Files:**
- `scripts/corpus_lockdown.py`
- `data/active_policy_wordings.json` — 647 files with metadata
- `data/excluded_documents.json` — why each was excluded
- `data/uin_match_report.json` — initial match assessment

**Logic:**
- Read `classification_report.json` and `policy_index.csv`
- Filter: `document_type == policy_wording && status == active && category != non_health`
- Compute file_hash per PDF
- Initial UIN match attempt via filename/insurer patterns
- Output triage reports

**Success:**
- 647 active policy wordings listed
- Each has: file_hash, document_type, insurer, source, match_status
- 0 silent assumptions

### Day 2: UIN Matcher v1

**Files:**
- `identity/uin_matcher.py`
- `identity/insurer_normalizer.py`
- `identity/plan_name_normalizer.py`
- `identity/unmatched_triage_report.csv`

**Match Tiers:**
1. Tier 1: Exact UIN found in PDF text (scan full text for UIN patterns)
2. Tier 2: Exact insurer + normalized plan name match
3. Tier 3: Fuzzy insurer + fuzzy plan name (levenshtein)
4. Tier 4: Source URL domain + plan name
5. Tier 5: Unmatched → manual review

**Output per file:**
```json
{
  "file_id": "...",
  "matched_uin": "...",
  "uin_base": "...",
  "match_confidence": 0.91,
  "match_method": "fuzzy_insurer_plan",
  "candidate_matches": [...],
  "requires_review": false
}
```

**Target:** >=90% matched or explicitly classified as unmatched/legacy.

### Day 3: Pick 5 Gold PDFs + Annotate

**Selection (from existing 5 test PDFs + analysis):**
1. New India Assurance — Floater MediClaim (public sector, standard)
2. Star Health — POS Accident Care Individual (private, accident-focused)
3. HDFC ERGO — Arogya Sanjeevani (standardized product, clean structure)
4. ICICI Lombard — Family Shield (comprehensive, table-heavy)
5. Care Health — Care Health Care (complex, long policy)

**Annotation format:**
```text
gold/{policy_id}/
  source.pdf
  metadata.json         # insurer, plan, UIN if found, pages, source
  sections.json         # manually identified section tree
  clauses.json          # clause boundaries with page refs
  tables.json           # table regions and cell content
  facts.json            # gold-extracted facts with status
```

**Manual work:** 2-4 hours per PDF for first few.
**Goal:** Reproducible by a second person using same guidelines.

### Day 4: Physical Parser v1

**Files:**
- `pdf_parser/layout_extractor.py` (pdfplumber primary)
- `pdf_parser/header_footer_detector.py`
- `scripts/debug_html_generator.py`

**Output per PDF:** `physical/{policy_id}/document_physical.json`
- Pages with dimensions
- Blocks with bbox + text + type
- Lines with font metadata
- Text spans with coordinates

**Debug HTML:** Pages rendered with structure overlaid.
**Validation:** Run against first gold PDF, check reading order.

### Day 5: Heading Candidate Scorer

**Files:**
- `pdf_parser/heading_detector.py` (scored, not binary)
- `tests/test_heading_scorer.py`

**Output per PDF:**
```json
{
  "candidates": [
    {
      "text": "4. Waiting Period",
      "page": 24,
      "bbox": [100, 200, 400, 220],
      "score": 0.94,
      "features": {
        "numbered": true,
        "bold": true,
        "font_above_body": true,
        "font_size": 14.0,
        "is_all_caps": false
      }
    }
  ]
}
```

**Validation:** Heading precision/recall vs gold sections.

### Day 6: Section Tree Builder

**Files:**
- `pdf_parser/section_tree.py`
- `pdf_parser/clause_segmenter.py`

**Logic:**
- Accept heading candidates above threshold
- Build hierarchy from numbering patterns
- Assign text blocks to parent headings
- Detect clause boundaries

**Validation:** Clause boundary F1 vs gold policies.

### Day 7: First 5 Extractors

**Files:**
- `normalizers/money.py`, `duration.py`, `percentage.py`, `age.py`, `coverage_status.py`, `indian_number_words.py`
- `extractors/free_look.py`
- `extractors/grace_period.py`
- `extractors/ped_waiting.py`
- `extractors/initial_waiting.py`
- `extractors/copay.py`

**Each extractor:**
- Regex patterns for candidate detection
- Normalizer for value standardization
- Scope/condition extraction
- Evidence span linking
- Confidence scoring

**Validation:** Precision >= 95% on gold policies. Recall can be 50-60%.

---

## Milestone Plan (Beyond 7 Days)

| Milestone | Goal | Success Criterion | Approx Timeline |
|-----------|------|-------------------|-----------------|
| M1: Structure Debugger | Parse 3 PDFs with visual debug output | Heading precision >= 90%, F1 >= 80% | Day 4-6 |
| M2: Gold Annotation | 5 PDFs manually labeled | Reproducible by second person | Day 3 + ongoing |
| M3: Clause Store + Provenance | 15 tables, pipeline_runs, source_spans | Every fact links to page + span | Day 8-10 |
| M4: Deterministic Extractors (15) | High precision fact extraction | Precision >= 95%, recall 50-60% | Day 7-14 |
| M5: Table Intelligence | Table type classifier, cell storage | Structured rows with source cells | Day 10-14 |
| M6: LLM Refinement | Evidence-constrained LLM on ambiguous | Precision >= 85%, evidence required | Day 12-16 |
| M7: Gold Corpus (20) | Expand 5 → 20 policies | Stable across diverse insurers | Day 15-25 |
| M8: 91-Field Export | Derived view for Product B | Every field has status + evidence | Day 20-30 |

---

## What We Do NOT Build (Yet)

- **OCR** — 100% text-layer corpus, not needed
- **Vision/image parsing** — not needed
- **Embeddings/Vector search** — downstream Product B
- **Agents/Orchestration** — not needed for extraction engine
- **Frontend** — Product A is CLI pipeline. Debug HTML is engineering instrumentation, not product UI
- **LLM fallback chains** — one model, one clean interface
- **Regulatory compliance engine** — design data model with hooks, but build comparison first
- **Marketing-vs-policy detector** — deferred (could be killer feature later)
- **50+ ontology concepts** — start with 15-20, grow from data

---

## Success Metrics

### Structure
- Heading precision >= 90%
- Heading recall >= 80%
- Clause boundary F1 >= 80%
- Table detection recall >= 85% for benefit/waiting-period tables

### Deterministic facts
- Precision >= 95%
- Recall can start at 50-60%
- Evidence accuracy >= 95%

### LLM-assisted facts
- Precision >= 85%
- Evidence required (verified in source text)
- Lower confidence by default, flagged for review

### Product B export
- No field exported without: value/status, confidence, evidence, source document, extraction method
- Fact status must be `present` or `explicitly_not_covered` for user-facing display
- "Unknown" → acceptable and honestly communicated
- "Wrong" → fatal, never allowed

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| False positives in deterministic extraction | High | Very high | Score + evidence before emission; precision over recall |
| Clause segmentation silently wrong | High | High | Source spans + visual debug + structure metrics |
| UIN matching fails on 22% unmatched | High | Medium | Triage reports + manual decisions per file |
| Policy Schedule overrides body clauses | High | Very high | Precedence rules (Schedule > Benefit grid > Clause > Definition) + conflict table |
| Optional covers pollute base policy facts | High | High | `scope_json: {cover: "base"/"optional"/"add-on"/"variant"}` on every fact |
| Brochures misclassified as policy wordings | Medium | High | Document type firewall + manual audit of classification_report.json |
| Table headers misassociated | High | High | Cell-level coordinate storage + header lineage tracking |
| "Not found" confused with "not applicable" | High | High | 7-status fact system (present / explicitly_not_covered / not_applicable / not_found / ambiguous / conflicting / requires_manual_review) |
| Regex improvements regress old PDFs | High | Medium | Regression test suite against gold corpus; pipeline_runs track version |
| Regulatory defaults change | Medium | High | Versioned ontology with circular source + effective_date |
| Insurer name variations cause duplicate products | High | Medium | Insurer normalizer with alias table; merged during UIN reconciliation |

---

## Directory Structure

```
doc-structure-engine/
├── README.md
├── pyproject.toml
├── docs/                         # Design docs (write before coding)
│   ├── evaluation.md             # Eval layers, metrics, hard gates
│   ├── database_strategy.md      # SQLite → JSON → Supabase phases
│   └── export_contract.md        # Product A → Product B JSON contract
├── pipeline/
│   ├── __init__.py
│   └── run.py                  # CLI orchestrator
├── identity/                    # Phase -1, 0: Product identity
│   ├── __init__.py
│   ├── corpus_lockdown.py
│   ├── uin_matcher.py
│   ├── insurer_normalizer.py
│   ├── plan_name_normalizer.py
│   └── match_tiers.py
├── pdf_parser/                  # Phase 1, 2: Structure
│   ├── __init__.py
│   ├── layout_extractor.py      # pdfplumber primary
│   ├── header_footer_detector.py
│   ├── heading_detector.py      # scored, not binary
│   ├── section_tree.py
│   ├── clause_segmenter.py
│   └── document_ast.py
├── table_engine/                # Phase 3: Table intelligence
│   ├── __init__.py
│   ├── table_detector.py
│   ├── table_type_classifier.py
│   ├── camelot_extractor.py
│   ├── pdfplumber_table_extractor.py
│   └── cell_normalizer.py
├── clause_store/                # Phase 4: Storage
│   ├── __init__.py
│   ├── models.py                # Pydantic models for all 18 tables
│   ├── schema.sql
│   └── repository.py
├── extractors/                  # Phase 5, 6: Fact extraction
│   ├── __init__.py
│   ├── base.py                  # Abstract extractor
│   ├── candidate_registry.py    # Run all, score, resolve
│   ├── normalizers/
│   │   ├── __init__.py
│   │   ├── money.py
│   │   ├── duration.py
│   │   ├── percentage.py
│   │   ├── age.py
│   │   ├── coverage_status.py
│   │   └── indian_number_words.py
│   ├── free_look.py
│   ├── grace_period.py
│   ├── ped_waiting.py
│   ├── initial_waiting.py
│   ├── specific_disease_waiting.py
│   ├── copay.py
│   ├── deductible.py
│   ├── room_rent.py
│   ├── icu_limit.py
│   ├── cumulative_bonus.py
│   ├── restoration.py
│   ├── ayush.py
│   ├── maternity.py
│   ├── newborn.py
│   ├── organ_donor.py
│   ├── ambulance.py
│   └── ... (grow from data)
├── llm_refinement/              # Phase 6+: LLM on ambiguous only
│   ├── __init__.py
│   ├── client.py                # One clean interface (Ollama Qwen2.5)
│   ├── prompts.py               # Clause-context prompts, not full PDF
│   └── evidence_verifier.py     # Check LLM quotes against source
├── provenance/                  # Phase 4+: Provenance tracking
│   ├── __init__.py
│   ├── tracker.py
│   └── pipeline_runs.py
├── ontology/                    # Phase 6+: Canonical concepts
│   ├── __init__.py
│   ├── concepts.json            # 15-20 concept specs with aliases, expected units, likely sections
│   └── mapper.py                # Raw term → canonical concept
├── gold_corpus/                 # Phase 7: Gold standard
│   ├── policies/
│   │   ├── new_india_floater/
│   │   ├── star_health_pos/
│   │   ├── hdfc_arogya/
│   │   ├── icici_family_shield/
│   │   └── care_health_care/
│   └── annotation_guide.md
├── derived/                     # Phase 8: 91-field export
│   ├── __init__.py
│   ├── field_mapping.yaml       # Maps concepts → 91-field schema slots
│   └── policy_feature_builder.py
├── scripts/
│   ├── corpus_lockdown.py
│   ├── batch_run.py
│   ├── debug_html_generator.py
│   ├── quality_report.py        # JSON + HTML output
│   └── triage_report.py
├── tests/
│   ├── test_identity/
│   ├── test_parser/
│   ├── test_table_engine/
│   ├── test_extractors/
│   ├── test_normalizers/
│   └── test_ontology/
└── data/
    ├── active_policy_wordings.json
    ├── excluded_documents.json
    ├── uin_match_report.json
    └── unmatched_triage_report.csv
```

---

## Dependencies

```
pdfplumber          # Primary: page geometry, font metadata, text extraction
PyMuPDF (fitz)      # Secondary: fast text extraction
camelot-py          # Table extraction (lattice, stream, network)
pydantic            # Data models
SQLite3             # Storage (stdlib; PostgreSQL later)
ollama + requests   # LLM refinement (Qwen2.5 7B local)
```

No OCR tools. No vector DB. No orchestration frameworks.

---

## What Product B (insurance-agent) Receives

After Phase 8, `doc-structure-engine` exports per-policy:

```json
{
  "policy_id": "hdfc_ergo_arogya_sanjeevani",
  "insurer": "HDFC ERGO",
  "plan": "Arogya Sanjeevani Policy",
  "uin": "HDFHLIP...",
  "extracted_at": "2026-06-01T12:00:00Z",
  "pipeline_run_id": "run_abc123",
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
      "condition": null
    },
    "copay_percentage": {
      "value": null,
      "fact_status": "not_found",
      "confidence": null,
      "method": null,
      "evidence": null,
      "scope": null,
      "condition": null
    }
  }
}
```

Product B's job: pure UX. Comparison, explanation, querying. No extraction logic.

---

## The Compiler Analogy

```
PDF            = source code
layout parser  = lexer
section parser = parser
AST            = syntax tree
ontology       = type system
extractors     = semantic analyzer
derived fields = compiled output
provenance     = debug symbols
gold corpus    = test suite
pipeline runs  = compiler versions
```
