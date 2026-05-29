# Tasks

Lightweight local issue tracker. All IDs are `DSE-XXX` (Document Structure Engine).

## Active Sprint

| ID | Title | Status | Priority | Phase |
|----|-------|--------|----------|-------|
| DSE-002 | UIN Matcher v1 | done | P0 | Phase 0 |
| DSE-003 | Gold annotation of 5 policies | done | P0 | Phase 7 |
| DSE-004 | Physical Layout Extractor v1 | done | P1 | Phase 1 |
| DSE-005 | Heading Candidate Scorer | done | P1 | Phase 2 |
| DSE-006 | Section Tree Builder | planned | P1 | Phase 2 |
| DSE-007 | First 5 Extractors (free look, grace, PED, initial wait, co-pay) | planned | P1 | Phase 6 |
| DSE-008 | Normalizers Library (money, duration, percentage) | planned | P1 | Phase 6 |

---

## Backlog

| ID | Title | Status | Priority | Phase |
|----|-------|--------|----------|-------|
| DSE-009 | Table Engine v1 | planned | P2 | Phase 3 |
| DSE-010 | Clause Store + Source Spans | planned | P2 | Phase 4 |
| DSE-011 | Fact Candidate Scoring + Conflict Resolution | planned | P2 | Phase 5 |
| DSE-012 | Expand gold corpus 5 → 20 | planned | P2 | Phase 7 |
| DSE-013 | Derived 91-Field Export | planned | P2 | Phase 8 |
| DSE-014 | LLM Refinement Integration | planned | P3 | Phase 6 |
| DSE-015 | Insurer/Plan Normalizer Library | planned | P1 | Phase 0 |

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

---

## Task Detail

### DSE-001 — Corpus Lockdown

**Status:** done
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
