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

### Hard Gates
On 5 gold PDFs:
```
95%+ pages produce text blocks
0 catastrophic reading-order failures in critical sections
debug HTML generated for every page
```

### Commands
```bash
python -m pdf_parser.layout_extractor --pdf <path>
python scripts/debug_html_generator.py --doc <doc_id>
```

### Output Artifacts
```
physical/{policy_id}/document_physical.json
debug/{policy_id}/page_*.html
```

### Current Status
planned

---

## Eval: Heading / Section Parser

### Purpose
Ensures the scored heading detector and section tree builder correctly identify document structure. This is the most critical layer — bad structure means bad clause boundaries, which means bad extraction.

### Inputs
- `document_logical_ast.json` per PDF
- Gold section annotations (from gold corpus)

### Metrics
- Heading precision (target: >= 90%)
- Heading recall (target: >= 80%)
- Section tree accuracy (target: >= 85%)
- Clause boundary F1 (target: >= 80%)
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
Do not build many extractors until:
```
heading precision >= 90%
heading recall >= 80%
clause boundary F1 >= 80%
```

### Commands
```bash
python -m pdf_parser.heading_detector --pdf <path>
python -m pdf_parser.section_tree --ast <ast_path>
python scripts/quality_report.py --layer headings
```

### Output Artifacts
```
logical/{policy_id}/heading_candidates.json
logical/{policy_id}/section_tree.json
```

### Current Status
planned

---

## Eval: Table Extraction

### Purpose
Tables are one of the hardest parts of the corpus. This eval ensures tables are detected, classified by type, and their cells extracted with correct header lineage. Tables must NOT be flattened into text soup.

### Inputs
- Raw PDF pages with table regions
- Gold table annotations (cells, headers, type, parent clause)

### Metrics
- Table detection recall (target: >= 85% for benefit/waiting tables)
- Table type classification accuracy (target: >= 80%)
- Cell text accuracy
- Header association accuracy
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
table detection recall >= 85%
header lineage manually acceptable on 5 gold PDFs
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
planned

---

## Eval: Normalizer Unit Tests

### Purpose
Normalizers are used by every extractor. If a normalizer is wrong, every extractor that uses it produces wrong facts. Test normalizers in isolation before any extractor uses them.

### Inputs
- `tests/test_normalizers/` unit test file

### Metrics
- Unit test pass rate (target: 100%)
- Test coverage of edge cases

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
python -m pytest tests/test_normalizers/ -v
```

### Output Artifacts
Test results in console. No persistent artifact file needed.

### Current Status
planned

---

## Eval: Fact Extraction

### Purpose
The primary quality gate for the engine. Ensures extracted facts are correct, evidence is accurate, and scope/conditions are properly captured. This is where we must be ruthless.

### Inputs
- `extracted_facts` from gold policies
- Gold fact annotations

### Metrics
- Fact precision (target: >= 95% deterministic, >= 85% LLM)
- Fact recall (target: >= 50-60% start, improve over time)
- Normalized value accuracy
- Unit accuracy
- Evidence accuracy (target: >= 95% deterministic, >= 85% LLM)
- Scope accuracy
- Condition accuracy
- False positive rate

### Hard Rules
Deterministic extractors:
```
precision >= 95%
evidence accuracy >= 95%
recall can be low initially (50-60% acceptable)
```

LLM-assisted facts:
```
precision >= 85%
evidence string must be verified in source text
confidence lower by default (0.70-0.85)
```

### Commands
```bash
python -m extractors.candidate_registry --policy <policy_id>
python scripts/quality_report.py --layer facts
```

### Output Artifacts
```
runs/evals/<date>-fact-extraction-<version>.json
```

### Current Status
planned

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

## Summary of Hard Gates

| Layer | Gate | Blocks |
|-------|------|--------|
| Corpus Identity | 100% files have file_hash + document_type + insurer + source + match_status | Parsing |
| Physical Parser | >= 95% pages produce text blocks, 0 catastrophic reading-order failures | Section building |
| Headings/Sections | precision >= 90%, recall >= 80%, F1 >= 80% | Building extractors |
| Tables | detection recall >= 85% for benefit/waiting tables | Fact extraction from tables |
| Normalizers | 100% unit tests pass | Extractor development |
| Facts: Deterministic | precision >= 95%, evidence accuracy >= 95% | LLM refinement |
| Facts: LLM | precision >= 85%, evidence verified in source text | Export to Product B |
| Export | Every field has value or fact_status. No silent empties. | Product B consumption |
