# Tasks

Lightweight local issue tracker. All IDs are `DSE-XXX` (Document Structure Engine).

## Active Sprint

| ID | Title | Status | Priority | Phase |
|----|-------|--------|----------|-------|
| DSE-002 | UIN Matcher v1 | done | P0 | Phase 0 |
| DSE-003 | Gold annotation of 5 policies | done | P0 | Phase 7 |
| DSE-004 | Physical Layout Extractor v1 | done | P1 | Phase 1 |
| DSE-005 | Heading Candidate Scorer | done | P1 | Phase 2 |
| DSE-006 | Section Tree Builder | done | P1 | Phase 2 |
| DSE-007 | First 5 Extractors (free look, grace, PED, initial wait, co-pay) | done | P1 | Phase 6 |
| DSE-008 | Normalizers Library (money, duration, percentage, age, coverage) | done | P1 | Phase 6 |

---

## Backlog

| ID | Title | Status | Priority | Phase |
|----|-------|--------|----------|-------|
| DSE-010 | Clause Store + Source Spans | done | P2 | Phase 4 |
| DSE-011 | Fact Candidate Scoring + Conflict Resolution | done | P2 | Phase 5 |
| DSE-012 | Expand gold corpus 5 → 20 | done | P2 | Phase 7 |
| DSE-013 | Derived Export (20-Concept Skeleton) | done | P2 | Phase 8 |
| DSE-014 | LLM Refinement Integration | planned | P3 | Phase 6 |
| DSE-015 | Insurer/Plan Normalizer Library | done | P1 | Phase 0 |
| DSE-017 | 20-Policy Pipeline Rebuild + Scale Validation | done | P1 | Scale |

---

## Completed

| ID | Title | Completed | Phase |
|----|-------|-----------|-------|
| DSE-000 | Project scaffold + documentation setup | 2026-05-29 | Infrastructure |
| DSE-001 | Corpus Lockdown | 2026-05-29 | Phase -1 |
| DSE-002 | UIN Matcher v1 | 2026-05-29 | Phase 0 |
| DSE-003 | Gold annotation of 5 policies | 2026-05-29 | Phase 7 |
| DSE-004 | Physical Layout Extractor v1 | 2026-05-29 | Phase 1 |
| DSE-005 | Heading Candidate Scorer | 2026-05-30 | Phase 2 |
| DSE-006 | Section Tree Builder | 2026-05-30 | Phase 2 |
| DSE-007 | First 5 Extractors (free look, grace, PED, initial wait, co-pay) | 2026-05-30 | Phase 6 |
| DSE-008 | Normalizers Library v1 | 2026-05-30 | Phase 6 |
| DSE-009 | Table Engine v1 | 2026-05-31 | Phase 3 |
| DSE-010 | Clause Store + Source Spans | 2026-05-31 | Phase 4 |
| DSE-011 | Fact Candidate Scoring + Conflict Resolution | 2026-06-01 | Phase 5 |
| DSE-012 | Expand gold corpus 5 → 20 | 2026-06-01 | Phase 7 |
| DSE-013 | Derived Export (20-Concept Skeleton) | 2026-06-01 | Phase 8 |
| DSE-015 | Insurer/Plan Normalizer Library | 2026-06-01 | Phase 0 |
| DSE-017 | 20-Policy Pipeline Rebuild + Scale Validation | 2026-06-02 | Scale |

---

## Task Detail

### DSE-001 — Corpus Lockdown

**Status:** in_progress
**Priority:** P0
**Phase:** Phase -1
**Goal:** Filter 1067 indexed PDFs into 647 active, 139 needs_review, 281 excluded, with SHA-256 hashes and triage flags.
**Acceptance criteria:**
- `scripts/corpus_lockdown.py` reads `policy_index.json` + `classification_report.json`
- Output: `data/manifests/active_policy_wordings_v1.json`, `data/manifests/excluded_documents_v1.json`, `data/manifests/status_unset_review_v1.csv`
- 647 active entries all have: file_hash, document_type, corpus_status, insurer, source_domain, match_status
- 281 excluded entries all have exclusion_reason
- No file silently dropped: 647 + 139 + 281 = 1067
- 70 non-canonical duplicates flagged with `possible_duplicate` triage flag
- 18 brochures in active set flagged with `document_type_brochure` triage flag
**Branch:** feat/corpus-lockdown
**Related docs:** evaluation.md (Layer 1 gates), database_strategy.md

### DSE-002 — UIN Matcher v1

**Status:** done
**Priority:** P0
**Phase:** Phase 0
**Goal:** Verify UIN-insurer-plan assignments for all 647 active policy wordings against uin_lifecycle.json.
**Approach:** All 647 entries pre-assigned UINs in policy_index.json. Work was verification (not discovery): insurer normalizer (folder→lifecycle name mapping), plan name normalizer (filename→product name extraction), tiered confidence scoring.
**Results:**
- Verified: 646 (99.8%)
- Plan name matched: 584 (high confidence)
- Insurer match only: 62 (medium confidence)
- Special case: 1 (non_policy_wordings brochure)
- Conflicts: 0
- Unmatched: 0
- Verified + special: 100.0%
**Outputs:**
- `data/manifests/uin_match_report_v1.json` — full 647-entry report
- `data/manifests/unmatched_triage_report_v1.csv` — triage entries
- `data/manifests/uin_match_summary_v1.json` — summary stats
**Files created:**
- `identity/__init__.py`
- `identity/insurer_normalizer.py` — 23 folder→lifecycle mappings
- `identity/plan_name_normalizer.py` — filename extraction + fuzzy matching
- `identity/uin_matcher.py` — orchestrator with 3-tier confidence
- `scripts/uin_match_report.py` — CLI runner
**Branch:** feat/uin-matcher-v1
**Related docs:** evaluation.md (UIN Match layer)

### DSE-003 — Gold Annotation of 5 Policies

**Status:** done
**Priority:** P0
**Phase:** Phase 7
**Goal:** Manually annotate 5 diverse policy PDFs with section trees, clause boundaries, tables, and critical facts.
**Policies:**
1. New India Assurance — Floater MediClaim
2. Star Health — Medi Classic Accident Care Individual
3. HDFC ERGO — Arogya Sanjeevani
4. ICICI Lombard — Family Shield
5. Care Health — Care Plus
**Acceptance criteria:**
- Each policy has: metadata.json, sections.json, clauses.json, tables.json, facts.json
- Every annotation has source page reference
- Annotations are reproducible by a second person (annotation guide)
- `scripts/validate_gold_corpus.py` passes
- 100 fact annotations exist across the 20 priority concepts
- Raw PDFs remain external read-only references under `policy_data/`
**Branch:** gold/annotate-5-policies
**Results:**
- Policies: 5
- Policy JSON files: 25
- Sections: 445
- Clauses: 453
- Table regions: 26
- Facts: 100
- Fact statuses: 77 present, 3 explicitly_not_covered, 2 not_applicable, 18 not_found, 0 requires_manual_review
- Docling coverage: all 5 policies now have readable markdown cross-check artifacts; Star and Care markdown was generated with OCR disabled and placeholder image export
- Second pass: cross-checked New India, HDFC, and ICICI against available IBM Docling markdown and enriched table summaries
- Third pass: precision review downgraded weak schedule-dependent facts to `requires_manual_review`
- Fourth pass: re-ran structure/table/fact provenance checks for Star and Care using the generated Docling markdown
- Fifth pass: applied source-PDF-only manual review patch for the 11 previously unresolved facts
**Outputs:**
- `gold_corpus/annotation_guide.md`
- `gold_corpus/schemas/*.schema.json`
- `gold_corpus/policies/*/{metadata,sections,clauses,tables,facts}.json`
- `gold_corpus/docling_markdown/*.md`
- `data/reports/gold_corpus_manual_review_11_facts_v1.md`
- `scripts/validate_gold_corpus.py`
**Related docs:** evaluation.md (Gold Corpus eval), open_questions.md (OQ-005)

### DSE-004 — Physical Layout Extractor v1

**Status:** done
**Priority:** P1
**Phase:** Phase 1
**Goal:** Extract page/block/line/span physical layout from PDFs using pdfplumber (no OCR/vision). Produce `document_physical.json` and debug HTML per page. Tag header/footer candidates without deleting text.
**Acceptance criteria:**
- `pdf_parser/layout_extractor.py` — core extraction (pages → blocks → lines → spans)
- `pdf_parser/models.py` — Pydantic models for PhysicalDocument, Page, Block, Line, Span
- `pdf_parser/header_footer_detector.py` — region classification + repeated-line tagging
- `pdf_parser/debug_html_generator.py` — per-page text-block overlay HTML
- `scripts/validate_physical_outputs.py` — schema, bbox, page count, font metadata validation
- `scripts/run_physical_eval.py` — hard gate metrics against 5 gold PDFs
- `tests/test_layout_extractor.py` — unit tests (bbox, IDs, header/footer, roundtrip)
- Hard gates: all pages extracted, file hash/page count match, text coverage >= 95%, font metadata >= 90%, 0 catastrophic failures, debug HTML for every page, span referential integrity = 100%, no hardcoded absolute paths, session log and eval artifact present
- Evidence coverage: reported metric only; hard gate deferred to DSE-010
- Runs on 5 gold PDFs (218 pages total), produces eval report
**Files created:**
- `pdf_parser/__init__.py`
- `pdf_parser/models.py`
- `pdf_parser/layout_extractor.py`
- `pdf_parser/header_footer_detector.py`
- `pdf_parser/debug_html_generator.py`
- `scripts/validate_physical_outputs.py`
- `scripts/run_physical_eval.py`
- `tests/test_layout_extractor.py`
**Results:**
- 5/5 gold PDFs processed (218 pages)
- 5/5 file hashes match gold metadata
- 5/5 page counts match gold metadata
- Text coverage: 100% all policies
- Font metadata: 100% all policies
- Catastrophic failures: 0
- Debug HTML: 218/218 pages
- Span referential integrity: 100.0% all policies (617,060/617,060 refs valid)
- Tests: 21/21 passed
- Gold corpus validator: passed
**Branch:** feat/physical-layout-extractor-v1
**Related docs:** evaluation.md (Physical Parser eval), data_contracts.md (Contract 3), decisions.md (ADR-0011), runs/sessions/2026-05-29-physical-layout-extractor-v1.md

### DSE-005 — Heading Candidate Scorer

**Status:** done
**Priority:** P1
**Phase:** Phase 2
**Goal:** Implement scored heading detection using weighted feature signals (font size, bold, numbering, heading dictionary, TOC dots) to identify visual headings from physical layout lines. Penalize non-headings (sentence-case body text, footer/header regions, all-caps false positives).
**ADR:** 0004-scored-heading-detection.md — weights: numbering +0.3, font above body +0.25, bold/italic +0.15, spacing +0.1, heading dict +0.1, TOC +0.1; penalties: sentence-like -0.3, too long -0.2, footer/header -0.3, all-caps FP -0.2; threshold 0.5
**Files created:**
- `structure_parser/__init__.py` — package init
- `structure_parser/heading_patterns.py` — numbering regexes (decimal, compact, SECTION, PART, Roman), TOC dots, 40+ heading dictionary terms, ALL CAPS/sentence case detection, normalize_heading_text
- `structure_parser/heading_scorer.py` — `HeadingScorer` class with scored features, spacing signal, candidate metadata, and contribution breakdown
- `scripts/run_heading_scorer.py` — entry point: loads physical JSON, runs scorer, saves candidates, writes run summary, exits non-zero on missing inputs
- `scripts/eval_heading_scorer.py` — eval against DSE-005 visual heading labels with one-to-one page-aware matching
- `tests/test_heading_scorer.py` — 32 tests (unit, eval matching, CLI behavior, 3 gold integration)
- `gold_corpus/policies/*/heading_labels.json` — DSE-005 visual-heading gold labels separate from DSE-003 logical sections
**Results:**
- v1 eval failed: 0/5 policies passed because visual heading candidates were evaluated against all logical section entries in `sections.json`, and the matcher allowed generic headings to overmatch many rows.
- v2 eval passed: 5/5 policies passed against 101 visual-heading labels.
- Precision/recall/F1: 100.00% on all 5 gold policies with one-to-one page-aware matching.
- Tests: 54/54 pass in full suite.
- Gold corpus validator: passed with 30 policy JSON files and 101 heading labels.
**Outputs:**
- `data/interim/logical/*/heading_candidates.json` — 5 policies scored
- `data/interim/logical/heading_run_summary.json` — heading scoring run summary
- `runs/evals/2026-05-30-heading-scorer-v1.json` — failed first-pass eval retained for history
- `runs/evals/2026-05-30-heading-scorer-v2.json` — passing remediation eval
**Known limitations:**
- DSE-005 evaluates visual heading candidates only; DSE-006 must build section trees and clause boundaries from visual headings plus logical labels.
- ICICI family_shield: headings same font size as body (11.04pt), relies solely on bold
- All-caps and boilerplate penalties may need more tuning after expansion to 20-policy gold corpus.
**Branch:** fix/dse-005-heading-scorer-gates
**Related docs:** docs/adr/0004-scored-heading-detection.md, evaluation.md (Heading Candidate Scorer), runs/sessions/2026-05-30-heading-scorer-v1.md

### DSE-006 — Section Tree Builder

**Status:** done
**Priority:** P1
**Phase:** Phase 2
**Goal:** Build hierarchical section trees and clause boundaries from DSE-005 visual heading candidates plus DSE-004 physical lines.
**ADR:** 0012-section-tree-builder.md — stack-based visual-heading tree with iterative synthetic body-numbered detection.
**Files created:**
- `structure_parser/section_tree.py` — stack-based tree builder, compact body-number parser, synthetic section detection, stable section IDs
- `structure_parser/clause_segmenter.py` — clause segmentation from compact numbered prefixes and paragraph gaps
- `scripts/run_section_tree.py` — batch CLI for section tree generation
- `scripts/eval_section_tree.py` — DSE-006 eval against logical gold sections/clauses
- `tests/test_section_tree.py` — unit, eval, CLI, and gold integration coverage
- `docs/adr/0012-section-tree-builder.md` — section tree ADR
**Results:**
- First remediation eval failed because compact no-space headings were missed and dense numbered lists were over-generated.
- Final v3 eval passed: 5/5 gold policies passed.
- Final metrics: Care 97.75% section F1 / 96.67% tree accuracy; HDFC 97.44% / 95.00%; ICICI 92.47% / 92.13%; New India 100.00% / 100.00%; Star 90.51% / 88.41%.
- Gold corpus validator: passed.
- Full pytest suite: passed.
**Outputs:**
- `data/interim/logical/*/section_tree.json` — 5 policy section trees and clauses
- `data/interim/logical/section_tree_run_summary.json` — DSE-006 run summary
- `runs/evals/2026-05-30-section-tree-v3.json` — passing DSE-006 eval
**Known limitations:**
- Clause boundary F1 is a section-aligned proxy until gold clauses carry physical line/span IDs.
- Section precision excludes predicted numeric sections outside the current gold labels because DSE-003 gold is partial in some policies; this should be revisited when DSE-012 expands the corpus.
- Dense item lists are kept as clauses/list content unless they align with gold-labeled structure.
**Branch:** feat/section-tree-builder-v1
**Related docs:** evaluation.md (Section Tree / Clause Boundary), data_contracts.md (Contract 3B), decisions.md, runs/sessions/2026-05-30-section-tree-builder-v1.md

### DSE-007 — First 5 Deterministic Extractors

**Status:** done
**Priority:** P1
**Phase:** Phase 6
**Goal:** Extract the first five deterministic policy facts from DSE-006 section trees using a candidate-first, evidence-verified pipeline.
**Concepts:**
- `free_look_period`
- `grace_period`
- `ped_waiting_period`
- `initial_waiting_period`
- `co_pay`
**Files created:**
- `normalizers/duration.py` — minimal day/month/year duration parsing for DSE-007 concepts
- `normalizers/percentage.py` — minimal percentage parsing for co-pay values
- `extractors/models.py` — candidate and accepted fact models with AGENTS §14 fields
- `extractors/evidence.py` — evidence text verification helpers
- `extractors/deterministic.py` — first five deterministic concept extractors
- `extractors/registry.py` — candidate-first registry and conflict resolution
- `scripts/run_fact_extractors.py` — batch extractor CLI
- `scripts/eval_fact_extractors.py` — DSE-007 gold eval
- `tests/test_fact_extractors.py` — normalizer, extractor, registry, and integration tests
**Results:**
- 5/5 gold policies processed.
- 25/25 target concepts attempted.
- Gold corpus validator passed.
- DSE-007 eval passed: deterministic present precision 100%, present recall 100%, normalized value accuracy 100%, status accuracy 100%, evidence accuracy 100%, false present for gold `not_found`: 0.
- Full pytest suite passed.
**Outputs:**
- `data/interim/facts/*/fact_candidates.json`
- `data/interim/facts/*/accepted_facts.json`
- `data/interim/facts/fact_extraction_run_summary.json`
- `runs/evals/2026-05-30-fact-extraction-dse007-v1.json`
**Known limitations:**
- Evidence spans are provisional `clause:{clause_id}` IDs until DSE-010 creates true source spans.
- DSE-007 only implements duration and percentage normalization needed by the five concepts; broader money, age, and coverage-status normalization remains DSE-008.
- Tables, SQLite clause store, source-span DB, LLM refinement, derived export, and Product B integration remain untouched.
**Branch:** feat/dse-007-first-extractors-v1
**Related docs:** evaluation.md (Fact Extraction), data_contracts.md (Contract 5), decisions.md, runs/sessions/2026-05-30-first-five-extractors-v1.md

### DSE-008 — Normalizers Library v1

**Status:** done
**Priority:** P1
**Phase:** Phase 6
**Goal:** Expand the minimal DSE-007 duration/percentage helpers into reusable normalizers for future deterministic extractors.
**Files created/changed:**
- `normalizers/indian_number_words.py` — shared number-word parsing, Indian magnitudes, numeric cleanup
- `normalizers/money.py` — INR amount and special money-value normalization
- `normalizers/duration.py` — backward-compatible duration parsing with `yr/yrs` and hyphenated words
- `normalizers/percentage.py` — backward-compatible percentage parsing with word percentages
- `normalizers/age.py` — age and age-comparator normalization
- `normalizers/coverage_status.py` — coverage status normalization with negation precedence
- `scripts/eval_normalizers.py` — fixed-vector normalizer eval
- `tests/test_normalizers/test_normalizers.py` — normalizer unit tests
**Results:**
- Normalizer eval passed: 35/35 vectors, 100% pass rate.
- Full pytest suite passed: 110 tests.
- DSE-007 fact extraction regression eval passed with no metric regression.
- Gold corpus validator passed.
**Outputs:**
- `runs/evals/2026-05-30-normalizers-dse008-v1.json`
- `runs/evals/2026-05-30-fact-extraction-dse007-regression-after-dse008.json`
**Known limitations:**
- DSE-008 normalizes scalar values and simple statuses only; it does not implement table extraction, source spans, SQLite storage, new fact extractors, LLM refinement, derived export, or Product B integration.
- Money special values are explicit symbolic statuses (`actuals`, `as_charged`, `subject_to_limit`) and must be interpreted by future extractors/export code.
**Branch:** feat/dse-008-normalizers-v1
**Related docs:** evaluation.md (Normalizer Unit Tests), data_contracts.md (Contract 4A), runs/sessions/2026-05-30-normalizers-library-v1.md

### DSE-009 — Table Engine v1

**Status:** done
**Priority:** P2
**Phase:** Phase 3
**Goal:** Build a two-tier table detection and extraction engine for 5 gold policies.
**Approach:**
- Primary: pdfplumber lattice extraction for tables with visible grid lines (`pdfplumber_lattice`).
- Fallback: text alignment heuristic for borderless tables (`text_alignment_candidate`).
- Secondary: conservative `pdfplumber_text` strategy, retained only for small headered grids.
- Keyword-based type classifier (no ML): 6 types + unknown.
- Header row detection across the first 3 table rows with per-cell column/row header lineage.
- Parent clause assignment by shortest containing clause page span plus owning section depth (provisional).
- DSE-009-specific physical table labels split from DSE-003 semantic `tables.json`.
**Files created:**
- `table_engine/__init__.py`
- `table_engine/models.py` — Pydantic models (TableCell, ExtractedTable, TableDocument, ExtractionMethod, TableType, ColumnCluster)
- `table_engine/table_detector.py` — pdfplumber lattice extraction
- `table_engine/text_alignment_detector.py` — column x-cluster fallback
- `table_engine/table_type_classifier.py` — keyword scorer
- `table_engine/cell_extractor.py` — cell grid → TableCell list
- `scripts/run_table_engine.py` — batch CLI
- `scripts/eval_table_engine.py` — eval against gold corpus
- `tests/test_table_engine.py` — 49 focused non-slow unit tests
- `data/reports/dse009_table_bbox_review_candidates.json` — bbox review for DSE-012
- `data/reports/dse009_header_lineage_review.json` — header lineage review
- `data/reports/dse009_gold_table_annotation_audit.json` — gold/table mismatch audit
- `data/reports/dse009_gold_table_source_review.md` — legacy table disposition report
**Results:**
- 5/5 gold policies processed.
- Strict v3 eval passed against 18 physical table labels.
- Physical table detection recall: 100%.
- Priority physical table detection recall: 100%.
- Header lineage pass rate: 100%.
- Type accuracy on matched physical labels: 94.44%.
- 42 tables with missing cell bboxes now record explicit `cell_bbox_missing:<count>` issues.
- Unrecorded missing cell bbox count: 0.
- Focused non-slow table tests passed: 57/57.
**Outputs:**
- `data/interim/tables/*/document_tables.json` — 5 policies
- `data/interim/tables/*/document_table_cells.json` — 5 policies
- `data/interim/tables/table_run_summary.json`
- `runs/evals/2026-05-31-table-engine-dse009-v1.json`
- `runs/evals/2026-05-31-table-engine-dse009-v2.json`
- `runs/evals/2026-05-31-table-engine-dse009-v3.json`
- `data/reports/dse009_table_bbox_review_candidates.json`
- `data/reports/dse009_header_lineage_review.json`
- `data/reports/dse009_gold_table_annotation_audit.json`
- `data/reports/dse009_gold_table_source_review.json`
- `data/reports/dse009_gold_table_source_review.md`
**Known limitations:**
- DSE-003 `tables.json` remains semantic/manual annotation history. DSE-009 hard gates now use `physical_table_labels.json`.
- `text_alignment_candidate` preserves raw lines but intentionally emits `cells=[]` when borderless column splitting is unreliable.
- Legacy gold table source dispositions are documented, including prose summaries that should be handled by clause/fact extraction rather than physical table parsing.
- Parent clause ID is provisional (page-range lookup); replaced by bbox overlap in DSE-010.
**Branch:** fix/dse-009-table-engine-gates
**Related docs:** evaluation.md (Table Extraction), data_contracts.md (Contract 3C), decisions.md (ADR-0014, ADR-0015), runs/sessions/2026-05-31-table-engine-v1.md

### DSE-010 — Clause Store + Source Spans

**Status:** done
**Priority:** P2
**Phase:** Phase 4
**Goal:** Persist all 5 gold-policy interim JSON into SQLite (`data/engine.sqlite`), build real `source_spans` records (clause → lines → bbox coordinates), replace provisional `"clause:{id}"` evidence IDs with real span IDs, and resolve table parent clause assignment via bbox spatial overlap.
**Acceptance criteria:**
- 5/5 gold policies ingested into SQLite — PASS
- 0 dangling FK references — PASS
- Source artifact count parity — PASS (`document_lines=12,715`, `document_sections=1,156`, `policy_clauses=2,522`)
- 0 cross-document source span mismatches — PASS
- 0 resolved fact span mismatches — PASS
- 0 unresolved present facts — PASS
- Clause span coverage >= 95% — PASS (100%)
- 0 provisional IDs in resolved facts — PASS
- DB size < 30 MB — PASS (18.42 MB)
- 232/232 tests (new + prior) — PASS
- Gold corpus validator — PASS
**Files created:**
- `clause_store/__init__.py`
- `clause_store/schema.sql` — 19-table SQLite DDL (15 populated, 4 deferred)
- `clause_store/models.py` — Python dataclasses for SQLite row types
- `clause_store/repository.py` — init_db(), insert_*, query_*, backfill_table_parent_clauses()
- `clause_store/span_builder.py` — clause spans, fact evidence spans, table cell spans
- `clause_store/fact_resolver.py` — provisional → real evidence ID resolution
- `scripts/run_clause_store.py` — batch ingest CLI
- `scripts/validate_source_spans.py` — structural integrity validator
- `scripts/eval_clause_store.py` — hard gate eval with source-count parity and cross-document checks
- `tests/test_clause_store.py` — 60 unit tests
**Results:**
- 6,136 total source_spans (2,522 clause_body, 3,591 table_cell, 23 fact_evidence)
- 192/197 tables (97.5%) parent_clause_id resolved via bbox overlap (avg IoU: 0.48)
- 23/23 accepted present facts resolved to real span IDs
- 113 cross-page clause spans across 5 policies
- DB size: 18.42 MB
**Key design decisions (ADRs):**
- ADR-0017: `document_text_spans` deferred (char-level spans stay in physical JSON)
- ADR-0018: `page_regions_json` handles cross-page clauses
- ADR-0019: `char_start`/`char_end` are clause-text offsets
- ADR-0020: resolved facts are a separate artifact; DSE-007 output is immutable
- ADR-0021: heading score in `document_sections`; OQ-001 closed
- ADR-0022: document-local IDs are namespaced in SQLite and original IDs are preserved in source_* columns
**Known limitations:**
- 16/23 (69.6%) fact evidence spans have clause-level char offsets (not subspan-level) because DSE-007 evidence_text boundaries shifted slightly with clause re-segmentation
- `document_text_spans` DDL exists but is not populated (ADR-0017)
- One block per page (physical parser limitation)
- `extracted_facts`, `fact_conflicts`, `derived_policy_features` not populated (DSE-011/013)
**Branch:** fix/dse-010-global-sqlite-ids
**Related docs:** evaluation.md (Clause Store + Source Spans), decisions.md (ADR-0017 through ADR-0022), docs/open_questions.md (OQ-001 closed), runs/sessions/2026-05-31-clause-store-source-spans-v2.md

### DSE-012 — Expand Gold Corpus 5 → 20

**Status:** done
**Priority:** P2
**Phase:** Phase 7
**Goal:** Expand the reviewed gold corpus from 5 to 20 policy wordings with 7 annotation files per policy.
**Approach:**
- Selected 15 additional policies for insurer/product diversity.
- Ran the existing pipeline to generate draft annotations.
- Performed source-PDF human review using `pdftotext`, physical JSON, pipeline drafts, and targeted page checks.
- Promoted all 15 new policies from draft to reviewed gold.
**Results:**
- 20/20 policies reviewed.
- 140 annotation JSON files present (20 policies × 7 files).
- 400 reviewed fact labels present (20 policies × 20 concepts).
- Status distribution: 257 `present`, 11 `explicitly_not_covered`, 5 `not_applicable`, 127 `not_found`.
- Tata AIG and Aditya Birla degenerate section trees manually rebuilt from source-PDF/physical-line review.
- Gold corpus validator passed with 20 reviewed policies and 0 draft policies.
- Full pytest suite passed.
**Outputs:**
- `data/manifests/dse012_gold_expansion_candidates_v1.json`
- `data/reports/dse012_human_review/human_review_summary.md`
- `runs/evals/2026-06-01-gold-corpus-dse012-reviewed.json`
- `runs/evals/2026-06-01-heading-scorer-dse012-reviewed.json`
- `runs/evals/2026-06-01-section-tree-dse012-reviewed.json`
- `runs/evals/2026-06-01-table-engine-dse012-reviewed.json`
- `runs/evals/2026-06-01-fact-extraction-dse012-reviewed.json`
**Known limitations:**
- Expanded heading/section evals now fail on Tata AIG and Aditya Birla, exposing parser gaps discovered by the larger gold corpus.
- Table eval script still has 5-policy-era hard-gate wording and reports DSE-012 run failure despite strong detection metrics on the expanded labels.
- DSE-012 is annotation completion only; parser remediation is deferred.
**Branch:** feat/dse-012-gold-corpus-expansion
**Related docs:** evaluation.md (Gold Corpus / expanded parser regression), risk_register.md, runs/sessions/2026-06-01-gold-corpus-human-review.md
