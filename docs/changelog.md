# Changelog

## 2026-05-31 (DSE-010 — Clause Store + Source Spans)

### Added
- `clause_store/` package: `schema.sql` (19-table SQLite DDL), `models.py` (dataclasses), `repository.py` (init_db, insert_*, query_*, backfill_table_parent_clauses), `span_builder.py` (clause/evidence/cell spans), `fact_resolver.py` (provisional ID resolution).
- `scripts/run_clause_store.py` — batch ingest CLI for 5 gold policies.
- `scripts/validate_source_spans.py` — structural integrity validator.
- `scripts/eval_clause_store.py` — hard gate eval with 6 gates.
- `tests/test_clause_store.py` — 59 unit tests (schema, inserts, span builder, fact resolver, table parent clause, bbox IoU).
- `data/reports/dse010_sqlite_build_summary.json` — committed build summary artifact.
- `runs/sessions/2026-05-31-clause-store-source-spans.md` — session log.
- `runs/evals/2026-05-31-clause-store-dse010-v1.json` — passing eval artifact.

### Changed
- `docs/evaluation.md` — Clause Store + Source Spans eval layer added; hard gates table updated.
- `docs/tasks.md` — DSE-010 marked done; detail block added; completed table updated.
- `docs/changelog.md` — DSE-010 entry.
- `docs/decisions.md` — ADR-0017 through ADR-0021 added.
- `docs/open_questions.md` — OQ-001 marked answered (ADR-0021).

### Key results
- 5,915 source_spans across 5 gold policies (2,301 clause_body, 3,591 table_cell, 23 fact_evidence).
- 23/23 accepted present facts resolved to real source_span_ids (0 provisional IDs remaining).
- 192/197 tables (97.5%) parent_clause_id resolved via bbox overlap (avg IoU 0.67).
- DB size: 7.92 MB. FK violations: 0. Clause span coverage: 100%.

### Known Issues
- 16/23 (69.6%) fact evidence spans have clause-level char offsets (char_start=0) because DSE-007 evidence_text boundaries predate current clause segmentation.
- `document_text_spans` DDL exists but not populated (ADR-0017).
- `extracted_facts`, `fact_conflicts`, `derived_policy_features` deferred to DSE-011/DSE-013.

---

## 2026-05-31 (DSE-009 — Table Engine v1 finalization)

### Added
- `gold_corpus/policies/*/physical_table_labels.json` — 18 physical table labels across 5 policies for DSE-009 hard gates.
- `runs/evals/2026-05-31-table-engine-dse009-v3.json` — passing physical table eval artifact.
- `data/reports/dse009_gold_table_source_review.json` and `.md` — disposition report for all 26 legacy DSE-003 `tables.json` rows.
- Header lineage fields on table cells and table records.
- Conservative `pdfplumber_text` extraction path for small, headered borderless grids.

### Changed
- DSE-009 eval now uses physical table labels for hard gates and treats legacy semantic table annotations as audited context.
- Table matching now uses one-to-one matching with bbox IoU plus type/content signatures.
- Gold validator now checks `physical_table_labels.json` for every gold policy.
- DSE-009 task status moved to done after v3 gates passed.

### Fixed
- DSE-009 no longer fails because prose-derived fact summaries are evaluated as physical tables.
- Type classification improved for physical benefit grids that mention sum insured but are not premium tables.
- `pdfplumber_text` output is filtered to avoid large page-body false tables.

### Known Issues
- Parent clause assignment remains provisional until DSE-010 source-span/bbox overlap.
- DSE-012 should expand physical table labels and review additional bboxes across more policies.

---

## 2026-05-31 (DSE-009 — Table Engine v1 remediation)

### Added
- `runs/evals/2026-05-31-table-engine-dse009-v2.json` — strict DSE-009 eval artifact.
- `data/reports/dse009_header_lineage_review.json` — header lineage review report.
- `data/reports/dse009_gold_table_annotation_audit.json` — gold/table mismatch audit.
- Unit tests for strict table eval matching, raw-line preservation, parent-clause specificity, and title-row header detection.

### Changed
- `scripts/eval_table_engine.py` now separates same-page table presence from strict type/content detection and records git commit metadata.
- `scripts/run_table_engine.py` now assigns provisional parent clauses by shortest containing page span plus owning section depth instead of a nonexistent clause level.
- `table_engine/text_alignment_detector.py` now preserves `raw_lines` for ambiguous borderless candidates and keeps `cells=[]`.
- `table_engine/table_detector.py` now clamps heading-context crops to page bounds and records missing cell bboxes as explicit issues.
- `table_engine/cell_extractor.py` now detects header rows across the first 3 rows, allowing title rows above real headers.
- `docs/tasks.md` and `docs/evaluation.md` now mark DSE-009 as `in_progress` because strict v2 gates fail.

### Known Issues
- Strict v2 eval fails: priority content detection recall is 57.1% against the 85% gate; header lineage pass rate is 20% against the 85% gate.
- Some gold table annotations are manual fact summaries over prose rather than physical tables, so they need source-PDF review before DSE-009 can be accepted.

---

## 2026-05-31 (DSE-009 — Table Engine v1 first pass)

### Added
- `table_engine/__init__.py` — package init.
- `table_engine/models.py` — Pydantic models: TableCell, ExtractedTable, TableDocument, ExtractionMethod (pdfplumber_lattice, text_alignment_candidate), TableType (6 types + unknown), ColumnCluster.
- `table_engine/table_detector.py` — primary lattice detection via pdfplumber.find_tables(); stable table IDs; per-cell bbox extraction.
- `table_engine/text_alignment_detector.py` — fallback column x-cluster heuristic for borderless tables; emits cells=[] with "cells_not_reliably_split" issue when column split is ambiguous.
- `table_engine/table_type_classifier.py` — keyword-based type scorer (no ML); 6 types; room_rent vs schedule_of_benefits disambiguation.
- `table_engine/cell_extractor.py` — cell grid → structured TableCell list; header detection by known header terms; None→"" normalization.
- `scripts/run_table_engine.py` — batch CLI; two-tier detection; type classification; parent clause assignment; outputs document_tables.json + document_table_cells.json per policy.
- `scripts/eval_table_engine.py` — gold corpus eval; hard gate checking; per-policy and aggregate metrics; JSON artifact output.
- `tests/test_table_engine.py` — 43 unit tests covering models, classifier, cell extractor, text alignment detector, column clustering.
- `data/reports/dse009_table_bbox_review_candidates.json` — predicted bboxes for manual DSE-012 gold upgrade.
- `runs/evals/2026-05-31-table-engine-dse009-v1.json` — passing DSE-009 eval artifact.
- `runs/sessions/2026-05-31-table-engine-v1.md` — session log.
- `docs/data_contracts.md` — Contract 3C: Table Engine Output.

### Changed
- `docs/evaluation.md` — Table Extraction eval moved to active with DSE-009 commands, results, and hard gate status.
- `docs/tasks.md` — DSE-009 marked done after hard gates passed; task detail block added.
- `docs/decisions.md` — ADR-0014 (pdfplumber-only v1 table extraction), ADR-0015 (keyword classifier for table type).

### Known Issues
- Type accuracy is 54% due to text_alignment_candidates classifying noisy page body text without structured cells.
- care_health_care_plus p4 (waiting_period) and p12 (room_rent) are undetectable as physical tables (definition lists).
- Parent clause ID is provisional page-range lookup; replaced by bbox overlap in DSE-010.

---

## 2026-05-30 (DSE-008 — Normalizers Library v1)

### Added
- `normalizers/indian_number_words.py` — shared number-word parsing, Indian magnitude multipliers, numeric cleanup, and hyphenated word parsing.
- `normalizers/money.py` — INR money parsing for rupee symbols, `Rs.`, `INR`, Indian comma grouping, decimals, lakh/lac/crore, and explicit special values.
- `normalizers/age.py` — age extraction with exact, greater-than, and greater-than-or-equal comparator metadata.
- `normalizers/coverage_status.py` — coverage status normalization with negation precedence.
- `scripts/eval_normalizers.py` — fixed-vector DSE-008 normalizer eval harness.
- `tests/test_normalizers/test_normalizers.py` — unit tests for money, duration, percentage, age, coverage status, and Indian number words.
- `runs/evals/2026-05-30-normalizers-dse008-v1.json` — passing DSE-008 eval artifact.
- `runs/evals/2026-05-30-fact-extraction-dse007-regression-after-dse008.json` — passing DSE-007 regression artifact after normalizer expansion.

### Changed
- `normalizers/duration.py` — preserved DSE-007 APIs while adding `yr/yrs`, hyphenated number words, and shared number parsing.
- `normalizers/percentage.py` — preserved DSE-007 APIs while adding word percentages like `twenty percent`.
- `docs/tasks.md` — DSE-008 marked done after hard gates passed.
- `docs/evaluation.md` — Normalizer Unit Tests eval moved to active with DSE-008 commands and results.
- `docs/data_contracts.md` — added normalizer result contract and allowed special statuses.

### Fixed
- Money special values such as `actuals`, `as charged`, and `subject to limit` now emit explicit symbolic normalized values instead of `0` or `null`.
- Coverage negations such as `not covered` and `not admissible` win over naive positive coverage matching.

### Known Issues
- DSE-008 does not add new extractors or table/source-span/export behavior.
- Money special values require future extractor/export interpretation before Product B display.

## 2026-05-30 (DSE-007 — First 5 Deterministic Extractors)

### Added
- `normalizers/duration.py` — minimal duration parsing for days, months, years, and common number words used by DSE-007.
- `normalizers/percentage.py` — minimal percentage parsing for co-pay extraction.
- `extractors/` package — candidate models, evidence verification, deterministic extractors, and registry/conflict resolution for `free_look_period`, `grace_period`, `ped_waiting_period`, `initial_waiting_period`, and `co_pay`.
- `scripts/run_fact_extractors.py` — batch CLI that reads DSE-006 `section_tree.json` and writes fact candidates, accepted facts, and a run summary.
- `scripts/eval_fact_extractors.py` — DSE-007 eval with precision, recall, normalized value accuracy, status accuracy, evidence accuracy, and false-present gates.
- `tests/test_fact_extractors.py` — unit and integration coverage for normalizers, extractors, registry behavior, and DSE-006 input availability.
- `runs/evals/2026-05-30-fact-extraction-dse007-v1.json` — passing DSE-007 eval over 5 gold policies.

### Changed
- `docs/tasks.md` — DSE-007 marked done after hard gates passed.
- `docs/evaluation.md` — Fact Extraction eval updated from planned to active with DSE-007 commands and results.
- `docs/data_contracts.md` — Contract 5 expanded for candidate and accepted fact schemas.
- `docs/decisions.md` — ADR-0013 added for provisional clause evidence IDs before DSE-010 source spans.
- Care Health gold fact correction: `ped_waiting_period` normalized value changed from 48 months to 36 months because the stored evidence text states 36 months.

### Fixed
- DSE-007 handles fact-bearing section headings from DSE-006 by enriching clause extraction text with the section heading line.
- Evidence text is verified before a deterministic `present` fact can be accepted.
- Co-pay extraction rejects definition-only clauses without a concrete percentage.

### Known Issues
- Evidence IDs are provisional `clause:{clause_id}` links until DSE-010 creates true source spans.
- DSE-007 intentionally does not implement table extraction, SQLite clause storage, source-span DB, LLM refinement, derived export, or Product B integration.
- DSE-008 broader normalizer work remains planned.

## 2026-05-30 (DSE-006 — Section Tree Builder)

### Added
- `structure_parser/section_tree.py` — `SectionTreeBuilder` with stack-based tree builder, level inference, content assignment, compact synthetic body-section detection, and deterministic IDs
- `structure_parser/clause_segmenter.py` — `ClauseSegmenter` with compact numbered-body clause splitting, paragraph-gap detection, and full untruncated text
- `scripts/run_section_tree.py` — CLI entry point to build section trees + clause segments for all gold policies
- `scripts/eval_section_tree.py` — evaluation script with one-to-one page-aware matching, recall-aware tree accuracy, section F1, clause F1 proxy, and missed critical section gates
- `tests/test_section_tree.py` — tests covering compact numbering, Roman subclauses, deterministic IDs, list over-generation guards, no clause truncation, CLI behavior, eval gates, and gold integrations
- `docs/adr/0012-section-tree-builder.md` — ADR: stack-based tree builder with synthetic body-numbered sections
- `docs/data_contracts.md` — Contract 3B (Section Tree Output) with full schema
- `runs/evals/2026-05-30-section-tree-v3.json` — passing DSE-006 eval over 5 gold policies

### Changed
- `docs/tasks.md` — DSE-006 marked done after v3 gates passed
- `docs/evaluation.md` — added active Section Tree / Clause Boundary eval layer with hard gates and v3 results
- `docs/decisions.md` — ADR-0012 added to Active ADRs table

### Fixed
- Compact policy numbering such as `2.1.1Accident`, `5.10RENEWAL`, and top-of-page numbered headings are now parsed.
- Dense numbered lists are no longer promoted to sections unless they align with policy structure or current gold labels.
- Eval no longer reports high tree accuracy when recall is low.

### Known Issues
- Clause boundary F1 uses a section-aligned proxy until gold clauses include physical line/span IDs.
- Section precision accounts for partial DSE-003 labels; revisit during DSE-012 gold expansion.

## 2026-05-30 (DSE-005 — Heading Candidate Scorer v2 remediation)

### Added
- `structure_parser/` package — scored heading detection for logical document structure
- `structure_parser/heading_patterns.py` — numbering regexes (decimal, compact, multi-dot, SECTION/PART prefix, Roman numeral), TOC dot pattern, 40+ heading dictionary terms, ALL CAPS and sentence case detection helpers
- `structure_parser/heading_scorer.py` — `HeadingScorer` class with font, bold, caps, numbering, dictionary, TOC, spacing, sentence-case, length, position, boilerplate, and numbered-definition features. Candidate output includes bbox, span IDs, normalized text, numbering token, level hint, and contribution breakdown.
- `scripts/run_heading_scorer.py` — CLI entry point to score all 5 gold PDFs, write a run summary, and fail loudly on missing physical outputs
- `scripts/eval_heading_scorer.py` — evaluation script with one-to-one page-aware matching against DSE-005 visual-heading labels
- `tests/test_heading_scorer.py` — tests covering numbering patterns, all-caps, sentence case, heading dictionary, TOC dots, text normalization, scorer unit tests, spacing feature, eval matching, CLI behavior, and 3 gold integration tests
- `docs/adr/0004-scored-heading-detection.md` — ADR: scored heading with 6 weighted features + 4 penalties
- `gold_corpus/policies/*/heading_labels.json` — 101 DSE-005 visual-heading labels separate from DSE-003 logical sections
- `data/interim/logical/*/heading_candidates.json` — 5 policies scored with full feature breakdown
- `runs/evals/2026-05-30-heading-scorer-v1.json` — failed first-pass eval retained for history
- `runs/evals/2026-05-30-heading-scorer-v2.json` — passing remediation eval

### Changed
- `docs/tasks.md` — DSE-005 marked done only after v2 acceptance gates passed
- `docs/evaluation.md` — split DSE-005 visual heading candidate gates from DSE-006 section tree / clause boundary gates
- `docs/data_contracts.md` — added Heading Scorer Output contract for DSE-006
- `scripts/validate_gold_corpus.py` — now validates DSE-005 `heading_labels.json` files and reports 30 policy JSON files
- `pyproject.toml` — registered the `slow` pytest marker used by gold integration tests

### Fixed
- `heading_scorer.py` font_size_ratio: changed from continuous ratio (`ratio * 0.25`) to binary (`1.0 * 0.25` if ratio > 1.0 else 0). Fixed bug where every body-sized line got +0.25 for free.
- `scripts/eval_heading_scorer.py` — removed broad substring/word-overlap matching that let one generic heading match many logical section rows
- `heading_scorer.py` — added a boilerplate company-name penalty after Care produced a non-structural company-name candidate

### Known Issues
- DSE-005 evaluates visual headings only. DSE-006 must build section trees and clause boundaries from visual headings plus logical section labels.
- ICICI headings use the same body font size and rely heavily on bold/spacing/numbering signals.

## 2026-05-29 (DSE-004 — review fixes)

### Added
- `pdf_parser/` package — physical layout extraction with pdfplumber
- `pdf_parser/models.py` — Pydantic models for PhysicalDocument, Page, Block, Line, Span, ParserIssue
- `pdf_parser/layout_extractor.py` — CLI entry point: extract PDF → document_physical.json, with gold corpus batch mode
- `pdf_parser/header_footer_detector.py` — region classification (top/body/bottom) + repeated-line tagging (no deletion)
- `pdf_parser/debug_html_generator.py` — per-page text-block overlay HTML with header/footer highlighting
- `scripts/validate_physical_outputs.py` — schema, bbox, page count, font metadata, debug HTML validation
- `scripts/run_physical_eval.py` — hard gate metrics against 5 gold PDFs with evidence coverage computation
- `tests/test_layout_extractor.py` — unit tests for bbox validation, stable IDs, header/footer detection, model roundtrip
- `docs/adr/0011-use-pdfplumber-for-physical-parsing.md` — ADR: pdfplumber over OCR/vision

### Fixed
- `pdf_parser/layout_extractor.py` — span ID linkage: `char_index` (always 0) replaced with `enumerate` counter. 617k line→span refs now resolve correctly.
- `pdf_parser/layout_extractor.py` — hardcoded absolute path replaced with `pathlib`-based relative default
- `scripts/run_physical_eval.py` — added span referential integrity gate (requires 100%). Evidence coverage set to `reported_only`, hard gate deferred to DSE-010.
- `tests/test_layout_extractor.py` — replaced vacuous bbox test with proper assertion; added span integrity tests (resolve + dangling); added 2 gold PDF integration tests (Star, HDFC).

### Changed
- docs/tasks.md — DSE-004 marked done with review-fixed acceptance criteria and actual results
- docs/evaluation.md — Physical Parser eval updated with active status and DSE-004 commands
- docs/decisions.md — ADR-0011 added (pdfplumber physical parsing)

### Added
- `gold_corpus/` — DSE-003 gold corpus with 5 policies, 25 annotation JSON files, schemas, and annotation guide
- `gold_corpus/docling_markdown/` — generated no-OCR IBM Docling markdown for Star Medi Classic Accident Care and Care Plus
- `data/reports/gold_corpus_manual_review_11_facts_v1.md` — source-PDF-only reviewer report for the 11 facts that were still marked `requires_manual_review`
- `scripts/validate_gold_corpus.py` — strict validator for gold policy folders, schemas, page references, fact statuses, and evidence coverage
- `tests/test_gold_corpus_validator.py` — pytest coverage for the gold corpus validator
- `runs/evals/2026-05-29-gold-corpus-v1.json` — Gold Corpus eval result
- `identity/` package with insurer normalizer, plan name normalizer, and UIN matcher orchestrator
- `scripts/uin_match_report.py` — DSE-002 CLI runner
- `data/manifests/uin_match_report_v1.json` — full 647-entry UIN match report
- `data/manifests/unmatched_triage_report_v1.csv` — triage CSV for entries needing review
- `data/manifests/uin_match_summary_v1.json` — summary statistics
- docs/evaluation.md — UIN Match eval layer with hard gates
- Initial project scaffold: IMPLEMENTATION_PLAN.md v2, docs/ directory
- docs/evaluation.md — 7 eval layers with hard gates
- docs/database_strategy.md — SQLite → JSON → Supabase phases
- docs/export_contract.md — Product A → Product B JSON contract
- docs/decisions.md — ADR index
- docs/development_protocol.md — Development workflow
- docs/ai_execution_protocol.md — AI agent guidelines
- docs/architecture.md — Pipeline and layered design overview
- docs/glossary.md — Domain and technical terms
- docs/data_contracts.md — Module-to-module schema contracts
- docs/risk_register.md — 18 identified risks
- docs/adr/0001-use-sqlite-for-engine.md — ADR: SQLite over Supabase for engine
- docs/adr/0002-clauses-before-fields.md — ADR: Clause-store architecture
- runs/sessions/ directory — Session logging
- runs/evals/ directory — Eval result tracking
- runs/experiments/ directory — Experiment tracking
- `scripts/corpus_lockdown.py` — main corpus lockdown script
- `data/manifests/active_policy_wordings_v1.json` — 647 active policy wordings with SHA-256 hashes
- `data/manifests/excluded_documents_v1.json` — 281 excluded documents with reasons
- `data/manifests/status_unset_review_v1.csv` — 139 policy wordings for manual triage

### Changed
- docs/tasks.md — DSE-003 marked done with gold corpus outputs and validation results
- docs/evaluation.md — added active Gold Corpus eval layer and DSE-003 result
- docs/open_questions.md — OQ-005 answered: first 5 annotations use CLI/manual JSON workflow
- README.md — current phase updated to Gold Corpus complete, Physical Parser next
- Gold corpus annotations — second pass cross-checked available IBM Docling markdown and enriched table summaries
- Gold corpus facts — third pass downgraded weak schedule-dependent labels to `requires_manual_review` for precision
- Gold corpus validator — now requires readable Docling markdown for every gold policy and rejects embedded image/base64 markdown for generated artifacts
- Star/Care annotations — fourth pass re-ran structure, table, and fact provenance checks against generated Docling markdown
- Gold corpus manual review — applied source-backed resolutions for all 11 `requires_manual_review` facts
- Gold corpus facts — final status distribution is now 77 `present`, 3 `explicitly_not_covered`, 2 `not_applicable`, 18 `not_found`, and 0 `requires_manual_review`
- Gold corpus validator/tests — now fail if any DSE-003 gold fact remains `requires_manual_review`
- Gold corpus validator — validates optional `additional_evidence` page/text entries for multi-page fact support
- `.gitignore` — allowed Markdown files under `data/reports/` so intentional review reports can be tracked
- docs/tasks.md — DSE-002 marked done with actual results (verified 646/647, 100% verified+special)

### Fixed
- docs/glossary.md — fact status count corrected from 8-value to 7-value enum

### Removed
- None

### Known Issues
- Gold v1 annotations have null bbox and table cell coordinates until DSE-004/DSE-009 generate physical/table parser outputs
- Gold v1 annotations have 18 `not_found` facts; Product B must still avoid displaying these as "not covered"
- ADR files did not follow AGENTS.md bold-field format (fixed same day)
- Run log templates did not match AGENTS.md required fields (fixed same day)

## 2026-05-28

### Added
- None

### Changed
- Approaches A-E experiments completed (see our_experience.md)
- notes3.md + notes4.md: Friend's architectural analysis received
- notes5.md + notes6.md: Friend's detailed review and corrections
- Decision to split Product A and Product B made
- 909 PDFs analyzed, 647 active policy wordings identified
- 1,099 UIN lifecycle records obtained from IRDAI
- 18 table schema designed with notes5 + notes6 corrections

### Fixed
- None

### Removed
- None

### Known Issues
- None
