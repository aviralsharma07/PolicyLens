# Evaluation — Gates and Metrics

## Principle

> Unknown is acceptable. Wrong is fatal.

Every layer has hard gates. Do not proceed to the next layer until the current layer passes its gates on 5 gold PDFs.

---

## Eval: Corpus Identity

### Purpose
Prevents corrupt, misclassified, or duplicate documents from entering the pipeline. Ensures every file that enters extraction has known identity.

### Inputs
- `active_policy_wordings.json`
- `excluded_documents.json`
- `classification_report.json`
- `policy_index.csv`

### Metrics
- Active policy count = expected 647
- Excluded count + active count = total classified count
- High-confidence UIN match rate
- Ambiguous UIN count
- Unmatched UIN count
- Manual review count

### Tests
1. Every PDF gets a stable file_hash (SHA-256)
2. No duplicate file_hash appears as two canonical documents
3. Every file has document_type
4. Every active policy wording has match_status
5. UIN matching returns top 5 candidates, not just one
6. No file is silently dropped

### Hard Gates
Do not proceed to parsing until:
```
100% of candidate files have:
  - file_hash
  - document_type
  - insurer
  - source
  - match_status
```

### Commands
```bash
python scripts/corpus_lockdown.py
python scripts/quality_report.py --layer identity
```

### Output Artifacts
```
data/active_policy_wordings.json
data/excluded_documents.json
data/uin_match_report.json
data/unmatched_triage_report.csv
```

### Current Status
active

### 2026-05-29 Result

```json
{
  "eval_name": "corpus-identity-v1",
  "date": "2026-05-29",
  "task_id": "DSE-001",
  "git_commit": "24a6320",
  "input_manifest": "policy_index.json (1067 records)",
  "metrics": {
    "active_count": 647,
    "needs_review_count": 139,
    "excluded_count": 281,
    "total_classified": 1067,
    "duplicate_flagged": 70,
    "brochure_flagged": 18,
    "missing_hash": 0,
    "missing_metadata": 0
  },
  "passed": true,
  "failures": [],
  "notes": "53 duplicate content groups found. 70 non-canonical entries flagged possible_duplicate. All PDFs exist on disk."
}
```

---

## Eval: UIN Match

### Purpose
Ensures every active policy wording's UIN assignment is verified against the IRDAI lifecycle registry. Prevents incorrect insurer-product-UIN associations from propagating into extraction.

### Inputs
- `data/manifests/active_policy_wordings_v1.json` (647 entries)
- `insurance-agent/data/uin_lifecycle.json` (1,099 records, 1,082 UIN bases)
- `identity/insurer_normalizer.py` (23 folder→lifecycle mappings)

### Metrics
- Verified entries (insurer match confirmed)
- High confidence (insurer + plan name match)
- Medium confidence (insurer match, plan name fuzzy)
- Conflict (folder insurer ≠ lifecycle insurer)
- Unmatched (UIN not found in lifecycle)
- Special case (non-policy-wordings folder)

### Eval Logic
1. Extract uin_base from full UIN (strip version suffix)
2. Look up uin_base in lifecycle products
3. Normalize folder insurer to lifecycle name via mapping table
4. Compare normalized folder insurer vs lifecycle insurer
5. Extract plan name from filename; fuzzy-match vs lifecycle product_name
6. Assign confidence: high (insurer+plan), medium (insurer only), low (mismatch)

### Hard Gates
```
verified_or_special >= 95%
(verified + special_case) / total >= 0.95
```

### Commands
```bash
python scripts/uin_match_report.py
```

### Output Artifacts
```
data/manifests/uin_match_report_v1.json
data/manifests/unmatched_triage_report_v1.csv
data/manifests/uin_match_summary_v1.json
```

### Current Status
active

### 2026-05-29 Result

```json
{
  "eval_name": "uin-match-v1",
  "date": "2026-05-29",
  "task_id": "DSE-002",
  "input_manifest": "active_policy_wordings_v1.json (647 entries) + uin_lifecycle.json",
  "metrics": {
    "total_entries": 647,
    "verified": 646,
    "high_confidence": 584,
    "medium_confidence": 62,
    "special_case": 1,
    "conflict": 0,
    "unmatched": 0,
    "verified_or_special_pct": 100.0
  },
  "passed": true,
  "failures": [],
  "notes": "All 647 entries verified. 1 special case (NivaBupa brochure in _non_policy_wordings). Insurer mapping complete (23/23). Plan name matching: 584 high (>=0.5 similarity), 62 medium (<0.5 or no extractable plan name)."
}
```

---

## Eval: Gold Corpus

### Purpose
Creates the first manually reviewed ground-truth corpus used by downstream parser, table, and fact extraction evals. Prevents parser work from optimizing against unverified examples or chat-only assumptions.

### Inputs
- `gold_corpus/policies/*/metadata.json`
- `gold_corpus/policies/*/sections.json`
- `gold_corpus/policies/*/clauses.json`
- `gold_corpus/policies/*/tables.json`
- `gold_corpus/policies/*/facts.json`
- Raw PDFs referenced by `source_pdf_path` under `policy_data/` (read-only)

### Metrics
- Policy folders
- Required JSON files
- Section annotations
- Clause annotations
- Table region annotations
- Fact annotations
- Fact status distribution
- Evidence coverage for `present` and `explicitly_not_covered`
- Docling markdown coverage

### Hard Gates
Do not proceed to DSE-004 physical parser eval work until:
```
5 policy folders exist
25 policy JSON files exist
100 fact annotations exist
all page references are valid
all present/explicitly_not_covered facts have evidence_text and evidence_page
0 facts remain in requires_manual_review for the 5-policy gold v1 corpus
all 5 policies have readable Docling markdown cross-check artifacts
python3 scripts/validate_gold_corpus.py passes
```

### Commands
```bash
python3 scripts/validate_gold_corpus.py
pytest tests/ --tb=short
```

### Output Artifacts
```
gold_corpus/
runs/evals/2026-05-29-gold-corpus-v1.json
```

### Current Status
active

### 2026-05-29 Result

```json
{
  "eval_name": "gold-corpus-v1",
  "date": "2026-05-29",
  "task_id": "DSE-003",
  "input_manifest": "active_policy_wordings_v1.json + uin_match_report_v1.json",
  "metrics": {
    "policies": 5,
    "json_files": 25,
    "sections": 445,
    "clauses": 453,
    "tables": 26,
    "facts": 100,
    "docling_markdown_files": 5,
    "generated_docling_markdown_files": 2,
    "status_counts": {
      "present": 77,
      "explicitly_not_covered": 3,
      "not_applicable": 2,
      "not_found": 18
    }
  },
  "passed": true,
  "failures": [],
  "notes": "Gold v1 uses text-layer review, Docling markdown cross-checks for all 5 policies, generated no-OCR Docling markdown for Star and Care, third-pass precision review, and source-PDF-only manual review patch for the 11 previously unresolved facts. Bbox and table cell coordinates remain null until DSE-004/DSE-009."
}
```

---

## Eval: Physical Parser

### Purpose
Ensures the physical layout extraction produces complete, well-structured output before logical parsing begins. Catches PDF reading-order issues, missing pages, or font-size extraction failures.

### Inputs
- `document_physical.json` per PDF (from layout extractor)
- Gold PDF source files
- Debug HTML output

### Metrics
- % of pages producing text blocks (target: >= 95%)
- Catastrophic reading-order failures in critical sections (target: 0)

### Tests
1. Page count matches PDF metadata
2. Extracted text length is non-zero for non-cover pages
3. Lines are in plausible reading order (top→bottom, left→right)
4. Headers/footers are tagged, not deleted blindly
5. Bbox values are within page bounds (0,0,width,height)
6. Font-size distribution is captured per page
7. Debug HTML renders correctly for every page
8. All line.span_ids reference valid span_ids on the same page
9. No hardcoded absolute path defaults in CLI arguments

### Hard Gates
On 5 gold PDFs:
```
95%+ pages produce text blocks
0 catastrophic reading-order failures in critical sections
debug HTML generated for every page
span referential integrity = 100%
no hardcoded absolute path defaults
session log and eval artifact present
```

Evidence coverage: reported metric only. Hard gate deferred to DSE-010 (source spans).

### Commands
```bash
python -m pdf_parser.layout_extractor --gold-corpus gold_corpus --output-root data/interim/physical --debug-root data/reports/physical_debug
python scripts/validate_physical_outputs.py --gold-corpus gold_corpus --physical-root data/interim/physical --debug-root data/reports/physical_debug
python scripts/run_physical_eval.py --gold-corpus gold_corpus --physical-root data/interim/physical --debug-root data/reports/physical_debug --output runs/evals/2026-05-29-physical-parser-v1.json
```

### Output Artifacts
```
data/interim/physical/{policy_slug}/document_physical.json
data/interim/physical/{policy_slug}/issues.json
data/reports/physical_debug/{policy_slug}/page_*.html
runs/evals/2026-05-29-physical-parser-v1.json
```

### Current Status
active

### 2026-05-29 Result

```json
{
  "eval_name": "physical-parser-v1",
  "date": "2026-05-29",
  "task_id": "DSE-004",
  "input_manifest": "gold_corpus (5 policies, 218 pages)",
  "metrics": {
    "policies_processed": 5,
    "passed": 5,
    "failed": 0
  },
  "passed": true,
  "failures": [],
  "notes": "Physical parser v1 processed all 5 gold PDFs. Hard gates: page count match, text coverage >= 95%, font metadata >= 90%, zero catastrophic failures, debug HTML for all pages, span referential integrity = 100%. Evidence coverage is reported_only; hard gate deferred to DSE-010."
}
```

---

## Eval: Heading Candidate Scorer

### Purpose
Ensures the scored heading detector identifies visual heading lines from DSE-004 physical layout before DSE-006 builds the section tree. This protects the logical parser from false structural anchors and missed major headings.

### Inputs
- `document_physical.json` per PDF (from DSE-004 Physical Layout Extractor)
- Gold visual heading labels (`gold_corpus/policies/{policy_slug}/heading_labels.json`)

### Metrics
- Heading precision (target: >= 90%)
- Heading recall (target: >= 80%)
- One-to-one page-aware label matching
- `true_positives + false_negatives == total_gold_visual_headings`
- Duplicate heading false positives
- Missed critical heading count

### Critical Sections to Test (must detect all)
```
Schedule of Benefits
Definitions
Waiting Period
Specific Waiting Period
Exclusions
Claims Procedure
Free Look Period
Renewability
Portability / Migration
```

### Hard Gates
Do not proceed to DSE-006 until:
```
heading precision >= 90%
heading recall >= 80%
all 5 gold policies pass
one-to-one match count invariant passes
```

DSE-006 adds separate hard gates for section tree accuracy and clause boundary F1.

### Commands
```bash
# Score headings for all gold policies
PYTHONPATH=. .venv/bin/python scripts/run_heading_scorer.py \
  --physical-root data/interim/physical \
  --output-root data/interim/logical \
  --threshold 0.5

# Run eval against gold corpus
PYTHONPATH=. .venv/bin/python scripts/eval_heading_scorer.py \
  --candidates-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-05-30-heading-scorer-v2.json

# Run tests
PYTHONPATH=. .venv/bin/python -m pytest tests/test_heading_scorer.py -v
```

### Output Artifacts
```
data/interim/logical/{policy_id}/heading_candidates.json
runs/evals/2026-05-30-heading-scorer-v2.json
gold_corpus/policies/{policy_slug}/heading_labels.json
```

### Current Status
active (DSE-005 done, DSE-006 pending)

### DSE-005 v1 Result (failed)
```
Eval file: runs/evals/2026-05-30-heading-scorer-v1.json
Passed: false
Reason: v1 evaluated visual heading candidates against all logical section entries in sections.json.
The matcher also allowed one generic candidate to match many gold rows, producing inconsistent TP/FN counts.
```

### DSE-005 v2 Result (threshold=0.5, visual-heading labels)
```
Policy                 Gold visual headings  Precision  Recall  F1
Care Health Plus        49                    100.00%   100.00% 100.00%
HDFC Arogya             15                    100.00%   100.00% 100.00%
ICICI Family Shield     15                    100.00%   100.00% 100.00%
New India Floater       11                    100.00%   100.00% 100.00%
Star Medi Classic       11                    100.00%   100.00% 100.00%
```

### Notes
- DSE-005 now evaluates visual headings only. Existing `sections.json` remains the logical structure gold source for DSE-006.
- The scorer output includes bbox, span IDs, normalized text, numbering token, level hint, raw features, and feature contribution breakdown.
- DSE-006 must convert visual heading candidates plus logical section labels into a section tree and clause boundaries.

---

## Eval: Section Tree / Clause Boundary

### Purpose
Ensures the DSE-006 section tree builder correctly constructs hierarchical section trees from DSE-005 heading candidates, detects synthetic body-numbered sub-sections (definition entries and policy clauses), and produces clause boundaries aligned with gold annotations.

### Inputs
- `data/interim/logical/{policy_id}/section_tree.json` — DSE-006 output (sections + clauses)
- `gold_corpus/policies/{policy_slug}/sections.json` — gold section tree
- `gold_corpus/policies/{policy_slug}/clauses.json` — gold clause boundaries

### Metrics
- Section tree accuracy (target: >= 85%; missed gold sections count as incorrect)
- Section recall (target: >= 80%)
- Section F1 (target: >= 80%)
- Clause boundary F1 (target: >= 80%)
- Section boundary (page) accuracy
- Missed critical sections (target: 0)

### Matching Strategy
- Gold sections matched to predicted sections using one-to-one page-aware section number + compact text alignment.
- Page-aware matching: section page_start must align for boundary accuracy.
- TOC/CIS/cover rows are excluded from hard gates.
- Predicted sections beyond the current gold page window are excluded because the DSE-003 labels are partial for some policies.
- Predicted numeric sections not present in current gold labels are reported but not precision-penalized until DSE-012 expands the gold corpus.
- Clause boundary F1 is a section-aligned proxy until gold clauses include physical line/span IDs.

### Hard Gates
Do not proceed to DSE-007 (extractors) until:
```
section_tree_accuracy >= 85%
section_f1 >= 80%
section_recall >= 80%
clause_f1 >= 80%
missed_critical_sections == 0
all 5 gold policies evaluated
no catastrophic failures
```

### Commands
```bash
# Build section tree for all gold policies
PYTHONPATH=. .venv/bin/python scripts/run_section_tree.py \
  --physical-root data/interim/physical \
  --logical-root data/interim/logical \
  --output-root data/interim/logical

# Run eval against gold corpus
PYTHONPATH=. .venv/bin/python scripts/eval_section_tree.py \
  --output-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-05-30-section-tree-v3.json

# Run tests
PYTHONPATH=. .venv/bin/python -m pytest tests/test_section_tree.py -v
```

### Output Artifacts
```
data/interim/logical/{policy_id}/section_tree.json
runs/evals/2026-05-30-section-tree-v1.json
runs/evals/2026-05-30-section-tree-v2.json
runs/evals/2026-05-30-section-tree-v3.json
```

### Current Status
active (DSE-006 passed v3 on 2026-05-30)

### Current Result
- `runs/evals/2026-05-30-section-tree-v3.json`
- 5/5 gold policies passed.
- Policy metrics:
  - Care: section tree accuracy 96.67%, section F1 97.75%, clause F1 97.75%
  - HDFC: section tree accuracy 95.00%, section F1 97.44%, clause F1 97.44%
  - ICICI: section tree accuracy 92.13%, section F1 92.47%, clause F1 92.47%
  - New India: section tree accuracy 100.00%, section F1 100.00%, clause F1 100.00%
  - Star: section tree accuracy 88.41%, section F1 90.51%, clause F1 90.51%

---

## Eval: Table Extraction

### Purpose
Tables are one of the hardest parts of the corpus. This eval ensures tables are detected, classified by type, and their cells extracted with correct header lineage. Tables must NOT be flattened into text soup.

### Inputs
- Raw PDF pages with table regions
- DSE-009 physical table labels: `gold_corpus/policies/*/physical_table_labels.json`
- Legacy DSE-003 `tables.json` rows are audited but excluded from DSE-009 hard gates when they are prose-derived summaries.

### Metrics
- Physical table detection recall
- Priority physical table detection recall (target: >= 85% for benefit/waiting or benefit-schedule tables)
- Table type classification accuracy (target: >= 80%)
- Cell text accuracy
- Header association accuracy
- Bbox IoU match rate
- Row/column alignment accuracy
- Table parent clause assignment accuracy

### Tests
Separately test for:
1. Table detection (did we find the table?)
2. Table type classification (is it waiting_period or premium?)
3. Cell extraction (is every cell value correct?)
4. Header lineage (is each value associated with its column header?)
5. Multi-page continuation (are split tables merged?)
6. Parent clause assignment (which section/clause does the table belong to?)

### Hard Gates
For waiting-period and benefit-schedule tables:
```
all 5 policies evaluated
priority physical table detection recall >= 85%
header lineage accuracy >= 85%
table type accuracy on matched physical tables >= 80%
unrecorded missing cell bbox count = 0
every skipped legacy tables.json row has a documented disposition
```

### Commands
```bash
python -m table_engine.table_detector --pdf <path>
python -m table_engine.table_type_classifier --tables <tables_path>
python scripts/quality_report.py --layer tables
```

### Output Artifacts
```
tables/{policy_id}/document_tables.json
tables/{policy_id}/document_table_cells.json
```

### Current Status
active, passing strict physical-table gate (DSE-009 v3 on 2026-05-31)

### DSE-009 v3 Result

```json
{
  "eval_name": "table-engine-dse009-v3",
  "date": "2026-05-31",
  "task_id": "DSE-009",
  "git_commit": "captured in eval artifact",
  "input_manifest": "gold_corpus physical_table_labels.json (5 policies)",
  "hard_gates": {
    "priority_physical_detection_recall_target": 0.85,
    "priority_physical_detection_recall_actual": 1.0,
    "header_lineage_pass_rate_target": 0.85,
    "header_lineage_pass_rate_actual": 1.0,
    "type_accuracy_target": 0.8,
    "type_accuracy_actual": 0.9444,
    "unrecorded_missing_cell_bboxes_actual": 0
  },
  "metrics": {
    "total_physical_table_labels": 18,
    "physical_table_detection_recall_all": 1.0,
    "type_accuracy_on_content_detected": 0.9444,
    "priority_physical_tables_total": 9,
    "priority_physical_detection_recall": 1.0,
    "priority_type_accuracy": 0.8889,
    "header_lineage_pass_rate": 1.0,
    "tables_with_missing_cell_bboxes_recorded": 42,
    "unrecorded_missing_cell_bboxes": 0,
    "legacy_gold_rows_documented": 26
  },
  "passed": true
}
```

Notes:
- v3 uses `physical_table_labels.json` as the hard-gate target. Legacy `tables.json` rows remain semantic/manual annotation history.
- v1 same-page matching and v2 legacy semantic matching are retained as history but superseded for DSE-009 acceptance.
- Missing pdfplumber cell coordinates are explicit table issues (`cell_bbox_missing:<count>`); no missing cell bbox is unrecorded.
- Legacy semantic table dispositions are documented in `data/reports/dse009_gold_table_source_review.md`.

### Commands

```bash
# Extract tables from gold corpus
PYTHONPATH=. python scripts/run_table_engine.py \
  --gold-corpus gold_corpus \
  --policy-data-root ../policy_data \
  --physical-root data/interim/physical \
  --section-root data/interim/logical \
  --output-root data/interim/tables

# Run eval
PYTHONPATH=. python scripts/eval_table_engine.py \
  --gold-corpus gold_corpus \
  --tables-root data/interim/tables \
  --output runs/evals/2026-05-31-table-engine-dse009-v3.json

# Run unit tests
PYTHONPATH=. python -m pytest tests/test_table_engine.py -v -m "not slow"
```

---

## Eval: Normalizer Unit Tests

### Purpose
Normalizers are used by every extractor. If a normalizer is wrong, every extractor that uses it produces wrong facts. Test normalizers in isolation before any extractor uses them.

### Inputs
- `tests/test_normalizers/` unit tests
- `scripts/eval_normalizers.py` fixed-vector eval harness

### Metrics
- Unit test pass rate (target: 100%)
- Fixed-vector pass rate (target: 100%)
- Coverage of money, duration, percentage, age, coverage status, and Indian magnitudes

### Money Tests
```
"₹5 lakh"             → 500000
"Rs. 5,00,000"        → 500000
"INR 5 lakhs"         → 500000
"1 crore"             → 10000000
"50 lacs"             → 5000000
"₹ 1,00,000"          → 100000
"Rs. 2.5 lakhs"       → 250000
"actuals"             → special value (not zero/none)
"as charged"          → special value
"subject to limit"    → special value
```

### Duration Tests
```
"36 months"           → 36
"2 years"             → 24
"90 days"             → 90
"thirty days"         → 30
"one year"            → 12
"1 yr"                → 12
```

### Percentage Tests
```
"20%"                  → 20
"20 per cent"          → 20
"twenty percent"       → 20
"1% of SI"             → 1
"20% of claim"         → 20
```

### Coverage Status Tests
```
"covered"                    → covered
"not covered"                → not_covered
"covered after waiting period" → conditional
"up to actuals"              → covered_with_actuals
"not admissible"             → not_covered
```

### Indian Number Words Tests
```
"lakh"      → 100000
"lac"       → 100000
"crore"     → 10000000
"thousand"  → 1000
```

### Hard Gates
```
100% of normalizer unit tests pass
```

### Commands
```bash
PYTHONPATH=. .venv/bin/python scripts/eval_normalizers.py --output runs/evals/2026-05-30-normalizers-dse008-v1.json
PYTHONPATH=. .venv/bin/python -m pytest tests/test_normalizers/ -v
```

### Output Artifacts
```
runs/evals/2026-05-30-normalizers-dse008-v1.json
```

### Current Status
active (DSE-008 passed v1 on 2026-05-30)

### Current DSE-008 Result

```json
{
  "total_vectors": 35,
  "passed_vectors": 35,
  "pass_rate": 1.0
}
```

DSE-008 also requires the DSE-007 fact extraction regression eval to pass with no metric regression.

---

## Eval: Fact Extraction

### Purpose
The primary quality gate for the engine. Ensures extracted facts are correct, evidence is verified against source clause text, and scope/conditions are captured before Product B can consume any derived facts.

### Inputs
- `data/interim/logical/{policy_slug}/section_tree.json`
- `data/interim/facts/{policy_slug}/fact_candidates.json`
- `data/interim/facts/{policy_slug}/accepted_facts.json`
- `gold_corpus/policies/{policy_slug}/facts.json`

For DSE-007, the active target concepts are:
- `free_look_period`
- `grace_period`
- `ped_waiting_period`
- `initial_waiting_period`
- `co_pay`

### Metrics
- Deterministic present precision
- Deterministic present recall
- Normalized value accuracy
- Status accuracy
- Evidence accuracy
- False-present count for gold `not_found`
- Per-policy and per-concept breakdown

### Hard Rules
Deterministic extractors:
- all 5 gold policies evaluated
- all 5 DSE-007 concepts attempted for every policy
- no `present` fact without verified evidence text
- no false present for gold `not_found` concepts
- deterministic present precision >= 95%
- evidence accuracy >= 95%
- normalized value accuracy >= 95% for matched present facts
- present recall >= 60%

LLM-assisted facts:
- precision >= 85%
- evidence string must be verified in source text
- confidence lower by default (0.70-0.85)
- not active in DSE-007

### Commands
```bash
PYTHONPATH=. python3 scripts/run_fact_extractors.py --section-root data/interim/logical --output-root data/interim/facts
PYTHONPATH=. python3 scripts/eval_fact_extractors.py --facts-root data/interim/facts --gold-corpus gold_corpus --section-root data/interim/logical --output runs/evals/2026-05-30-fact-extraction-dse007-v1.json
```

### Output Artifacts
```
data/interim/facts/{policy_slug}/fact_candidates.json
data/interim/facts/{policy_slug}/accepted_facts.json
data/interim/facts/fact_extraction_run_summary.json
runs/evals/2026-05-30-fact-extraction-dse007-v1.json
```

### Current Status
active (DSE-007 passed v1 on 2026-05-30)

### Current DSE-007 Result

```json
{
  "policies_passed": 5,
  "deterministic_present_precision": 1.0,
  "deterministic_present_recall": 1.0,
  "normalized_value_accuracy": 1.0,
  "status_accuracy": 1.0,
  "evidence_accuracy": 1.0,
  "false_present_for_gold_not_found": 0
}
```

Notes:
- DSE-007 uses provisional evidence IDs in the form `clause:{clause_id}` because DSE-010 source spans are not built yet.
- DSE-007 extraction text enriches each clause with its section heading because DSE-006 can carry fact-bearing text in heading lines. Evidence line IDs include the heading line when used.
- During DSE-007 eval, the Care Health PED gold normalized value was corrected from 48 months to 36 months because the stored gold evidence text itself states 36 months.

---

## Eval: Derived Export

### Purpose
Ensures the 91-field export contract is complete and no field is silently empty. This is the final gate before Product B consumes the data.

### Inputs
- `derived_policy_features` (compiled view)
- `policy_features.json` export files

### Metrics
- Export completeness (every field has value or fact_status)
- Evidence coverage (% of present facts with evidence)
- Schema version compliance

### Tests
For every exported field, verify:
```
field_name
value or null
fact_status
confidence
method
evidence or null
source document
pipeline_run_id
scope
condition
```

### Hard Gate
```
No exported field may be silently empty.
Allowed: value=null, fact_status=not_found
Not allowed: field missing with no reason
```

### Commands
```bash
python scripts/quality_report.py --layer export
```

### Output Artifacts
```
runs/evals/<date>-export-<version>.json
```

### Current Status
planned

---

## Eval: Clause Store + Source Spans (DSE-010)

### Purpose
Ensures the provenance layer is correct: every clause has a physical location (bbox + page), every accepted fact has a real source_span_id, and the SQLite store has referential integrity.

### Inputs
- `data/engine.sqlite` — clause store database
- `data/interim/facts_resolved/{slug}/accepted_facts.json` — resolved facts (5 policies)

### Metrics
- `policies_ingested` — source_documents count
- `dangling_fk_count` — FK violation count
- `clause_span_coverage` — % of policy_clauses with >= 1 clause_body source_span
- `unresolved_present_facts` — present facts with no real evidence_span_id
- `provisional_ids_in_resolved` — count of "clause:{id}" remaining in resolved facts
- `db_size_bytes` — SQLite file size
- `tables_with_bbox_resolved_parent_pct` — % of tables with bbox-resolved parent clause
- `avg_iou_resolved_parents` — spatial accuracy of parent clause assignments
- `evidence_degradation` — % of fact evidence spans with clause-level vs exact char offsets

### Hard Gates
- `policies_ingested == 5` — all gold policies ingested
- `dangling_fk_count == 0` — referential integrity
- `unresolved_present_facts == 0` — all present facts have real span IDs
- `clause_span_coverage >= 95%` — near-complete clause location
- `provisional_ids_in_resolved == 0` — no provisional IDs in resolved facts
- `db_size_bytes < 30MB` — DB stays bounded

### Commands

```bash
# Ingest all 5 gold policies
PYTHONPATH=. python scripts/run_clause_store.py \
  --gold-corpus gold_corpus \
  --physical-root data/interim/physical \
  --logical-root data/interim/logical \
  --tables-root data/interim/tables \
  --facts-root data/interim/facts \
  --output-db data/engine.sqlite \
  --output-facts-resolved data/interim/facts_resolved

# Structural integrity validation
PYTHONPATH=. python scripts/validate_source_spans.py \
  --db data/engine.sqlite \
  --facts-root data/interim/facts_resolved

# Hard gate eval
PYTHONPATH=. python scripts/eval_clause_store.py \
  --db data/engine.sqlite \
  --facts-root data/interim/facts_resolved \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-05-31-clause-store-dse010-v1.json
```

### Output Artifacts
- `data/engine.sqlite` (gitignored — reproduced by run_clause_store.py)
- `data/interim/facts_resolved/{slug}/accepted_facts.json` (gitignored — reproduced)
- `runs/evals/2026-05-31-clause-store-dse010-v1.json` (committed)
- `data/reports/dse010_sqlite_build_summary.json` (committed)

### DSE-010 v1 Result

```json
{
  "eval_name": "clause-store-dse010-v1",
  "date": "2026-05-31",
  "passed": true,
  "hard_gates": {
    "policies_ingested": 5,
    "dangling_fk_count": 0,
    "unresolved_present_facts": 0,
    "clause_span_coverage": 1.0,
    "provisional_ids_in_resolved": 0,
    "db_size_mb": 7.92
  },
  "metrics": {
    "total_source_spans": 5915,
    "clause_body_spans": 2301,
    "table_cell_spans": 3591,
    "fact_evidence_spans": 23,
    "tables_with_bbox_resolved_parent": 192,
    "tables_bbox_resolved_pct": 97.5,
    "avg_iou_resolved_parents": 0.6659,
    "cross_page_clause_spans": 113,
    "evidence_exact_match": 7,
    "evidence_clause_level_precision": 16
  }
}
```

### Current Status
active (DSE-010 v1 PASS on 2026-05-31)

---

## Summary of Hard Gates

| Layer | Gate | Blocks |
|-------|------|--------|
| Corpus Identity | 100% files have file_hash + document_type + insurer + source + match_status | Parsing |
| Physical Parser | >= 95% pages produce text blocks, 0 catastrophic reading-order failures | Section building |
| Heading Candidates | precision >= 90%, recall >= 80% on visual-heading labels | Section tree building |
| Sections/Clauses | section tree accuracy >= 85%, clause boundary F1 >= 80% | Building extractors |
| Tables | priority physical table recall >= 85%, header lineage >= 85%, type accuracy >= 80% | Fact extraction from tables | active (DSE-009 v3 PASS) |
| Clause Store + Source Spans | 5/5 policies, 0 FK violations, 0 unresolved facts, span coverage >= 95%, DB < 30MB | DSE-011 (fact scoring, conflict resolution) | active (DSE-010 v1 PASS) |
| Normalizers | 100% unit tests pass | Extractor development |
| Facts: Deterministic | precision >= 95%, evidence accuracy >= 95% | LLM refinement |
| Facts: LLM | precision >= 85%, evidence verified in source text | Export to Product B |
| Export | Every field has value or fact_status. No silent empties. | Product B consumption |
