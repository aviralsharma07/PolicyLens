# Architectural Decisions

This file records key architectural decisions. Each ADR has a unique ID and links to the detailed record in `docs/adr/`.

---

## Active ADRs

| ID | Title | Date | Status |
|----|-------|------|--------|
| 0001 | Use SQLite for engine storage (not Supabase) | 2026-05-29 | Accepted |
| 0002 | Clauses before fields (clause-store architecture) | 2026-05-29 | Accepted |
| 0003 | Separated Product A (doc-structure-engine) from Product B (insurance-agent) | 2026-05-29 | Accepted |
| 0004 | Scored heading detection over binary classification | 2026-05-29 | Accepted |
| 0005 | Candidate-first fact extraction (not first-match-wins) | 2026-05-29 | Accepted |
| 0006 | Evidence-constrained LLM (quote or reject) | 2026-05-29 | Accepted |
| 0007 | Precision over recall for fact extraction | 2026-05-29 | Accepted |
| 0008 | 7-status fact system (not present/absent binary) | 2026-05-29 | Accepted |
| 0011 | Use pdfplumber for physical layout extraction | 2026-05-29 | Accepted |
| 0012 | Stack-based section tree builder with synthetic body-numbered sections | 2026-05-30 | Accepted |
| 0013 | Provisional clause evidence IDs for DSE-007 | 2026-05-30 | Accepted |
| 0014 | pdfplumber-only table extraction for DSE-009 v1 (no camelot) | 2026-05-31 | Accepted |
| 0015 | Keyword-based table type classifier (no ML) with two-tier detection | 2026-05-31 | Accepted |
| 0016 | Split physical table labels from semantic table summaries | 2026-05-31 | Accepted |

---

## Proposed ADRs

| ID | Title | Date | Status |
|----|-------|------|--------|
| 0009 | Separate Supabase project for engine in production | TBD | Proposed |
| 0010 | Regulatory compliance engine deferred | TBD | Proposed |

---

## Rejected ADRs

| ID | Title | Date | Status |
|----|-------|------|--------|
| — | Use OCR/vision PDF extraction | 2026-05-28 | Rejected — 100% text-layer corpus confirmed |

---

## Decision Records

### 2026-05-29 — ADR-0001: Use SQLite for Engine Storage (Not Supabase)

**Status:** accepted

**Decision:** Use SQLite for Phase 1 development. Compiled output (policy_features.json) is exported as JSON files and pushed to the existing insurance-agent Supabase project only when stable.

**Context:** The engine produces heavy intermediate data (pages, blocks, lines, text spans, table cells — millions of rows per policy). The existing insurance-agent project uses Supabase, but storing raw engine data there would pollute the app schema, hit Free Plan storage limits, and couple the engine to the app's deployment cycle.

**Options considered:**
1. Supabase (same project) — Add all 18 tables to existing insurance-agent Supabase
2. Supabase (separate project) — Create a new Supabase project for engine data
3. Local SQLite — Store everything in a local engine.sqlite file
4. PostgreSQL directly — Self-hosted or cloud PostgreSQL

**Reasoning:** SQLite has zero infrastructure (stdlib, no network, no auth), allows fast iteration without schema migrations, has no quota limits, enables file-level portability, and simplifies debugging. Raw data stays local; only clean compiled data enters Supabase.

**Consequences:**
- Positive: Fast iteration. No cloud dependency for core engine.
- Positive: Only clean compiled data enters Supabase.
- Negative: Cannot share engine data across machines without file transfer.
- Negative: SQLite concurrent write limited (not an issue for single-user dev).

**Revisit when:** Engine needs to run remotely, multi-developer access required, or data exceeds 10GB. Migrate to Supabase/PostgreSQL at that point.

### 2026-05-29 — ADR-0002: Clauses Before Fields (Clause-Store Architecture)

**Status:** accepted

**Decision:** Store clauses as atomic legal units. Derive fields from clauses. Never flatten first.

**Context:** The initial approach attempted to extract 91 flat fields directly from PDF text using LLM prompts. This failed because the LLM saw unstructured text soup, flat fields lose relationship context, there was no provenance to trace fields back to source, and different policies express the same concept in different sections.

**Options considered:**
1. Flat extraction with provenance tracking
2. Document-level key-value extraction
3. Hybrid (store both clauses and flat fields)
4. Clause-store architecture (chosen)

**Reasoning:** The clause-store approach ensures every fact traces back to a specific clause, page, and coordinate. It supports inheritance and override, naturally attaches scope/conditions to clauses, and allows adding new field types without re-extraction.

**Consequences:**
- Positive: Facts are debuggable with full provenance.
- Positive: Supports schedule overrides with conflict records.
- Positive: Scope/conditions attach naturally to clauses.
- Negative: More storage (clauses + spans + candidates + conflicts).
- Negative: Requires reliable clause segmentation.

**Revisit when:** Clause segmentation quality (F1 >= 80%) cannot be achieved on the 647-file corpus.

### 2026-05-29 — ADR-0003: Separated Products (Engine vs Application)

**Status:** accepted

**Decision:** Split into two products with a JSON contract boundary. doc-structure-engine (Product A) owns PDF parsing, extraction, gold corpus, provenance. insurance-agent (Product B) owns UI, comparisons, explanations, conversations.

**Context:** The old single-codebase approach had extraction code tangled with API routes, different iteration speeds, testing extraction required running the full app, and raw parsing data mixed with user data in Supabase.

**Options considered:**
1. Single repo with modules
2. Monorepo with clear boundaries
3. Two products with JSON contract (chosen)

**Reasoning:** Separation ensures independent iteration, extraction testing without the app, and clean API design through the JSON contract boundary.

**Consequences:**
- Positive: Independent iteration speeds.
- Positive: Raw engine data stays separate from user data.
- Negative: Two repos to manage.
- Negative: Contract changes require coordinated updates.

**Revisit when:** JSON contract becomes a bottleneck and both products stabilize.

### 2026-05-29 — ADR-0004: Scored Heading Detection Over Binary Classification

**Status:** accepted

**Decision:** Use scored heading detection instead of binary. Score based on: numbering, font size, bold/italic, spacing, heading dictionary, TOC match. Penalties for sentence-like text, too-long, footer/header position, all-caps false positives. Default threshold 0.5.

**Context:** Insurance PDFs use 6+ distinct heading styles. Binary detection fails on styles it wasn't configured for.

**Options considered:**
1. Binary regex-only heading detection
2. ML classifier for heading detection
3. Scored heading detection with heuristics (chosen)

**Reasoning:** Scored detection works across different heading styles without per-insurer configuration. ML is overkill — scored heuristics + small gold corpus will match or beat ML with far less complexity.

**Consequences:**
- Positive: Works across heading styles without per-insurer config.
- Positive: Score threshold tunable per phase.
- Negative: Requires font-size distribution calculation per document.

**Revisit when:** Heading precision < 90% or recall < 80% on gold corpus after tuning.

### 2026-05-29 — ADR-0005: Candidate-First Fact Extraction (Not First-Match-Wins)

**Status:** accepted

**Decision:** Generate all candidates, score them, then resolve conflicts. Precedence rules: Schedule > Benefit grid > Clause > Definition.

**Context:** Insurance policies express the same concept in multiple places. First-match-wins misses schedule overrides, misses scope dependencies, and creates silent false positives.

**Options considered:**
1. First-match-wins
2. Weighted average across candidates
3. Candidate-first with scoring + conflict resolution (chosen)

**Reasoning:** Candidate-first catches schedule-overrides-body-clause patterns. First-match-wins misses schedule overrides. Averaging is wrong for insurance (1% vs 2% should not average to 1.5%).

**Consequences:**
- Positive: Catches schedule-overrides-body-clause patterns.
- Positive: Rejected candidates stored for debugging.
- Negative: More storage and complex scoring logic.

**Revisit when:** Scoring logic becomes unmanageable (> 20 concepts with custom precedence rules).

### 2026-05-29 — ADR-0006: Evidence-Constrained LLM

**Status:** accepted

**Decision:** LLM facts must quote their evidence, and the evidence must be verified in the source text. LLM-assisted facts get lower default confidence (0.70-0.85) vs deterministic (0.90-0.98).

**Context:** LLMs hallucinate. 30%+ of LLM extraction failures included convincing-but-wrong hallucinated values. A single hallucinated insurance value causes real financial harm.

**Options considered:**
1. Pure regex extraction (no LLM)
2. LLM with confidence threshold but no evidence check
3. Evidence-constrained LLM (chosen)

**Reasoning:** Evidence constraints dramatically reduce hallucinated values. Pure regex misses concepts requiring reasoning. Confidence thresholds alone are insufficient because LLMs produce confident-sounding wrong answers.

**Consequences:**
- Positive: Dramatically reduces hallucinated values.
- Positive: Every LLM fact is auditable.
- Negative: Rejects valid extractions where LLM paraphrased correctly.

**Revisit when:** Evidence verification rejects > 10% of otherwise correct LLM extractions.

### 2026-05-29 — ADR-0007: Precision Over Recall for Fact Extraction

**Status:** accepted

**Decision:** Precision >= 95% for deterministic facts. Recall can be lower. "Not found" is an acceptable answer.

**Context:** A wrong answer damages trust more than an absent answer. "No deductible" (wrong) → claim denial → lost trust. "Deductible not found" (unknown) → manual check → still trusted.

**Options considered:**
1. Maximize fill rate
2. Recall-first with confidence threshold
3. Precision-first with evidence verification (chosen)

**Reasoning:** Experiments showed fill rate approach produced 30%+ hallucination rate. No safe confidence threshold exists for LLM — evidence verification is more reliable.

**Consequences:**
- Positive: Users trust the platform — answers are rarely wrong.
- Negative: Early versions show many "not found" values.
- Negative: Product B must handle null/unknown values gracefully.

**Revisit when:** Product B UX feedback indicates "not found" rates cause user abandonment.

### 2026-05-29 — ADR-0008: 7-Status Fact System (Not Present/Absent Binary)

**Status:** accepted

**Decision:** Use 7 fact status values: present, explicitly_not_covered, not_applicable, not_found, ambiguous, conflicting, requires_manual_review.

**Context:** Binary "found/not_found" loses critical information. "Not applicable" and "not found" require different user-facing displays. Conflating them caused the real bug of showing "No deductible" when the value was simply not found.

**Options considered:**
1. Binary found/not_found
2. Numeric confidence score only
3. 7-status fact system (chosen)

**Reasoning:** Binary conflates distinct states causing wrong user displays. Confidence scores don't capture why a value is missing.

**Consequences:**
- Positive: Product B shows honest states instead of fabricating values.
- Positive: Triage queue is clear (conflicting/ambiguous auto-flagged).
- Negative: More complexity in extraction pipeline.
- Negative: Product B must handle 7 states in UI.

**Revisit when:** Product B UX data shows users confused by 7 states.

## 2026-05-30 — Separate Visual Heading Labels From Logical Sections

**Status:** accepted

**Decision:** DSE-005 evaluates heading candidates against dedicated visual-heading labels in `heading_labels.json`, not against every logical section row in `sections.json`.

**Context:** The first DSE-005 eval used DSE-003 `sections.json` as the heading gold source. That mixed visual headings with logical clause/list/definition entries, producing low recall and inconsistent TP/FN counts. Heading detection and section-tree construction are adjacent but separate layers.

**Options considered:**
1. Keep using all `sections.json` rows for DSE-005
2. Mutate `sections.json` to remove logical entries
3. Add DSE-005 visual-heading labels while preserving DSE-003 logical sections

**Reasoning:** Dedicated visual labels let DSE-005 test the exact behavior it owns: identifying visible heading lines from physical layout. Preserving `sections.json` keeps DSE-003 logical structure intact for DSE-006.

**Consequences:**
- Positive: Heading candidate precision/recall is measured against the right target.
- Positive: DSE-006 can still evaluate logical section tree and clause boundaries against `sections.json`.
- Negative: Gold corpus now has another label file per policy to maintain.

**Revisit when:** DSE-006 defines a richer unified logical/visual annotation schema.

## 2026-05-30 — Stack-Based Section Tree Builder With Synthetic Body-Numbered Sections

**Status:** accepted

**Decision:** Build the DSE-006 section tree using a stack-based algorithm over DSE-005 heading candidates sorted by reading order. Detect additional sub-sections from numbered body lines inside leaf sections as synthetic nodes.

**Context:** DSE-005 produces visual heading candidates (e.g., "3. Definitions") but correctly rejects long definition entries (e.g., "3.1. Accident means...") as body text. DSE-006 must build a complete section hierarchy that includes these sub-entries for extractor granularity.

**Options considered:**
1. Recursive descent parser over numbering patterns.
2. ML classifier for section boundaries.
3. Stack-based tree builder + body-numbered detection (chosen).

**Reasoning:** Insurance policy numbering is not always well-formed. Stack-based handles irregular hierarchies. Body-numbered detection recovers definition entries without weakening DSE-005 heading precision.

**Consequences:**
- Positive: Handles irregular hierarchies (gaps, mixed styles).
- Positive: Recovers definition sub-entries without weakening DSE-005 heading precision.
- Positive: Synthetic nodes carry `heading_type` for downstream awareness.
- Negative: TOC duplicates must be deduplicated manually.
- Negative: Synthetic detection may introduce false sub-sections in dense policies.

**Revisit when:** Synthetic body-numbered detection produces >20% false positives on 20-policy gold corpus.

## 2026-05-30 — DSE-006 Eval Uses Gold-Window Matching Until Gold Expansion

**Status:** accepted

**Decision:** Evaluate DSE-006 against the current gold section labels using the annotated gold page window and do not precision-penalize predicted numeric sections that are outside the current gold section-number set.

**Context:** DSE-003 gold labels are deep but not equally exhaustive across all policies. New India, Care, Star, and HDFC contain valid numbered policy sections beyond the manually labeled subset. Penalizing every additional predicted section as a false positive made the eval reject structurally correct output for unlabeled sections.

**Options considered:**
1. Treat every extra predicted section as a false positive.
2. Rewrite DSE-003 gold labels during DSE-006.
3. Use gold-window matching now and revisit precision after DSE-012 expands the corpus.

**Reasoning:** The DSE-006 hard gate must protect recall, hierarchy, and critical-section coverage without pretending partial gold is exhaustive. Rewriting gold labels in a parser task would violate the gold-corpus boundary.

**Consequences:**
- Positive: DSE-006 gates now fail on missed gold structure instead of unlabeled valid structure.
- Positive: Gold annotations remain untouched.
- Negative: Section precision is less strict until DSE-012 expands gold coverage.

**Revisit when:** DSE-012 expands the gold corpus or adds exhaustive physical line/span labels for section and clause boundaries.

## 2026-05-30 — Provisional Clause Evidence IDs for DSE-007

**Status:** accepted

**Decision:** Accepted DSE-007 deterministic facts use provisional evidence IDs in the form `clause:{clause_id}` until DSE-010 creates true source spans.

**Context:** DSE-007 needs evidence-constrained deterministic facts now, but DSE-010 source spans and SQLite clause storage are not implemented yet. DSE-006 section trees provide clause IDs, page ranges, line IDs, and clause text.

**Options considered:**
1. Block all fact extraction until DSE-010.
2. Emit facts without evidence IDs.
3. Use provisional clause evidence IDs with verified evidence text.

**Reasoning:** Provisional clause IDs preserve the evidence rule while keeping DSE-007 independently testable. Every accepted `present` fact still verifies its `evidence_text` against DSE-006 extraction text.

**Consequences:**
- Positive: Deterministic facts are auditable before the source-span DB exists.
- Positive: DSE-010 can replace provisional IDs with true spans.
- Negative: Clause-level evidence is coarser than final source spans.
- Negative: Fact-bearing heading lines are represented through the owning clause until DSE-010.

**Revisit when:** DSE-010 builds `source_spans` and the local SQLite clause store.

---

## 2026-05-31 — pdfplumber-only table extraction for DSE-009 v1

**Status:** accepted

**Decision:** Use pdfplumber as the sole table extraction tool for DSE-009. Do not add camelot-py.

**Context:** IMPLEMENTATION_PLAN.md lists camelot-py as a potential tool. DSE-009 needed to choose whether to add camelot (lattice + stream modes) or stay with pdfplumber.

**Options considered:**
1. pdfplumber only (find_tables + text alignment fallback)
2. pdfplumber primary + camelot fallback
3. camelot primary

**Reasoning:** pdfplumber is already a dependency with working `find_tables()`. Adding camelot adds a significant dependency (requires Ghostscript, image libraries). The 5-policy gold corpus shows that most misses are text-formatted lists (no physical table structure), not tables that camelot would find better. Precision-first: camelot's stream mode risks false positives on definition lists.

**Consequences:**
- Positive: No new dependencies. Keeps pipeline simple and fast.
- Positive: Known infrastructure; pdfplumber already imports Table API.
- Negative: Borderless tables with no column structure are detected only as `text_alignment_candidate` with cells=[].
- Negative: Type accuracy is limited for text_alignment_candidates.

**Revisit when:** Gold corpus expands to 20 policies (DSE-012) and there is evidence that camelot would improve recall without hurting precision.

---

## 2026-05-31 — Keyword-based table type classifier with two-tier detection

**Status:** accepted

**Decision:** Use a keyword-based type classifier (no ML) and a two-tier detection strategy (pdfplumber lattice + text alignment fallback).

**Context:** Need to classify tables into 6 types (waiting_period, schedule_of_benefits, room_rent, premium, claims_documents, network_list) without a training dataset.

**Options considered:**
1. No classification — emit all tables as unknown
2. Keyword-based scorer with normalized hit count
3. ML classifier trained on gold corpus
4. Rule-based classifier using structural signals (row/column count, header patterns)

**Reasoning:** Gold corpus has 26 tables across 6 types — insufficient for ML training. Keyword matching is transparent, debuggable, and precise for lattice tables with actual cell content. The two-tier approach (lattice + text alignment fallback) ensures no silent failure for borderless tables; the fallback marks cells as unreliable rather than fabricating structure.

**Text alignment fallback design:** Detect column x-clusters from body line x0 positions. If a run of 3+ lines shares 2+ stable cluster positions, emit as `text_alignment_candidate`. Cells=[] when column split is ambiguous (i.e., row-to-cell assignment is unreliable). Always logs `cells_not_reliably_split` issue when cells are omitted.

**Consequences:**
- Positive: No training data needed. Transparent and auditable.
- Positive: Clear distinction between structured (lattice) and candidate (fallback) tables.
- Negative: Type accuracy is 54% overall — text_alignment_candidates classify from noisy page body text.
- Negative: Premium/SOB disambiguation requires careful keyword tuning.

**Revisit when:** DSE-012 expands gold corpus to 20 policies. At that scale, a simple rule-based classifier with structural features (header content, row count, column count patterns) may outperform pure keyword matching.

---

## 2026-05-31 — Strict table eval separates page presence from content detection

**Status:** accepted

**Decision:** DSE-009 table evaluation must not count a gold table as detected merely because any extracted table exists on the same page. The strict gate uses type/content matching for detection and reports same-page table presence only as a diagnostic `page_region_recall` metric.

**Context:** The first DSE-009 eval passed by matching any table on the gold page. Review showed this inflated priority detection recall even when the extracted table type and header/cell content did not match the gold annotation.

**Options considered:**
1. Keep same-page matching as the hard gate.
2. Use strict type/content matching as the hard gate and page-region matching as a diagnostic.
3. Remove DSE-009 hard gates until DSE-012 adds bboxes.

**Reasoning:** Same-page matching hides real parser gaps and would let bad table evidence flow into downstream fact extraction. Strict matching is noisier against current gold annotations, but it protects the pipeline from false confidence.

**Consequences:**
- Positive: Eval now catches wrong-type matches, conceptual gold summaries, and missing header lineage.
- Positive: DSE-009 remains aligned with the Product A table rule that tables must preserve cells, coordinates, and headers.
- Negative: Current DSE-003 table annotations are not sufficient for full DSE-009 acceptance because some rows summarize prose rather than physical tables.

**Revisit when:** Gold `tables.json` entries have reviewed bboxes/header rows, or the project explicitly splits physical table extraction from prose-derived table-like fact summaries.

---

## 2026-05-31 — Split physical table labels from semantic table summaries

**Status:** accepted

**Decision:** DSE-009 hard gates evaluate `physical_table_labels.json`, not DSE-003 `tables.json`. Legacy `tables.json` remains semantic/manual annotation history for prose-derived table-like facts and high-level summaries.

**Context:** DSE-009 v2 failed because several DSE-003 table annotations summarized facts from prose or definitions rather than physical PDF tables with cells, headers, and bboxes. A physical table parser should not fabricate cells for those annotations.

**Options considered:**
1. Loosen DSE-009 eval back to same-page matching.
2. Rewrite DSE-003 `tables.json` to make the table engine pass.
3. Split physical-table labels from semantic/manual summaries and audit every legacy table row.

**Reasoning:** The implementation plan defines Phase 3 as physical table intelligence: raw cells, coordinates, and header lineage. Keeping semantic summaries in the hard gate would punish the correct parser behavior and reward fake structure.

**Consequences:**
- Positive: DSE-009 now measures the correct layer: physical table extraction.
- Positive: Prose-derived facts remain available to deterministic clause/fact extractors.
- Positive: Every legacy table row has an explicit disposition in `data/reports/dse009_gold_table_source_review.md`.
- Negative: DSE-012 must expand/review physical table labels, not just semantic summaries.

**Revisit when:** DSE-012 expands the gold corpus to 20 policies or introduces a dedicated prose-summary/table-like-fact annotation layer.

---

## 2026-05-31 — Defer document_text_spans population (character-level spans)

**Status:** accepted

**Decision:** `document_text_spans` DDL exists in `clause_store/schema.sql` but is not populated by DSE-010. Character-level spans (617K rows across 5 gold policies) stay in `document_physical.json`. SQLite source_spans are built from line-level data only.

**Context:** The physical parser produces one span per character. Loading 617K character-level rows into SQLite would make `engine.sqlite` very large and slow, with no current consumer of that granularity.

**Options considered:**
1. Load all character-level spans as-is → 617K rows, ~100MB+ DB, no consumer
2. Group consecutive chars with same font into word/run-level spans → significant complexity
3. Skip population, use physical JSON for char-level on demand → simple, bounded DB

**Reasoning:** Source spans need to answer "where in the PDF did this fact come from?" Line-level bboxes are sufficient for that. Character-level detail is a debugging/inspection concern available from physical JSON.

**Consequences:**
- Positive: DB stays bounded (7.92 MB for 5 policies).
- Positive: After ADR-0022 fixed ID collision and preserved all source rows, DB remains bounded (18.42 MB for 5 policies).
- Positive: No complex char-grouping logic needed.
- Negative: Character-level font signals (bold, italic) not queryable from SQLite directly.

**Revisit when:** A downstream consumer (fact refinement, layout ML) requires font-level signals at query time.

---

## 2026-05-31 — source_spans uses page_regions_json (ADR-0018)

**Status:** accepted

**Decision:** `source_spans.page_regions_json` stores a JSON array of `{page, bbox, line_ids}` objects, replacing the flat `page_number + bbox_json` fields in the IMPLEMENTATION_PLAN.md v1 schema.

**Context:** 37/554 (7%) of care_health clauses span multiple pages. A single `page_number + bbox_json` cannot represent cross-page location accurately.

**Options considered:**
1. Flat `page_number + bbox_json` → simple, breaks for cross-page clauses
2. `page_regions_json` array → handles any number of pages, slightly more complex to query
3. One row per (clause, page) → cleaner query, more rows

**Reasoning:** Option 2 gives one row per span with complete multi-page location. Querying a specific page requires `json_extract` in SQLite, which is acceptable since cross-page clauses are a minority.

**Consequences:**
- Positive: Cross-page clauses correctly represented.
- Positive: Single span_id per clause.
- Negative: Page-specific bbox requires JSON parsing in queries.

**Revisit when:** Performance profiling shows `json_extract` on `page_regions_json` is a bottleneck.

---

## 2026-05-31 — char_start/char_end are clause-text offsets, not PDF character stream offsets (ADR-0019)

**Status:** accepted

**Decision:** `source_spans.char_start` and `char_end` measure the offset of evidence_text within `clause.text` (after `clean_space()` normalization), not within the PDF character stream.

**Context:** The physical parser's `Span.char_start` was never populated (always `None`). PDF character offsets from pdfplumber are page-relative and not globally stable.

**Reasoning:** Clause-text offsets are stable, verifiable, and don't require character-level span data. Any verifier can reconstruct the evidence location by: open `policy_clauses.raw_text`, index at `[char_start:char_end]`.

**Consequences:**
- Positive: No dependency on pdfplumber character index.
- Positive: Verification is simple string comparison.
- Negative: Cannot map directly to a PDF character index for rendering.
- Negative: 16/23 accepted facts (69.6%) have degraded clause-level offsets (char_start=0, char_end=len(clause_text)) because DSE-007 evidence_text boundaries shifted with clause re-segmentation.

**Revisit when:** A PDF rendering use case requires pixel-level evidence highlighting.

---

## 2026-05-31 — Resolved facts as separate artifact, DSE-007 output immutable (ADR-0020)

**Status:** accepted

**Decision:** `data/interim/facts/{slug}/accepted_facts.json` (DSE-007 output) is never overwritten. DSE-010 writes `data/interim/facts_resolved/{slug}/accepted_facts.json` with real source_span_ids. DSE-011+ and Product B consume resolved facts only.

**Context:** DSE-007 facts have provisional `evidence_span_id = "clause:{id}"`. DSE-010 must replace these with real span IDs but must not mutate the extractor's output.

**Reasoning:** Immutable extractor outputs are essential for debugging and re-running. Separation of raw extractor output from resolved/enriched output follows the pipeline's overall immutability principle.

**Consequences:**
- Positive: DSE-007 output can always be re-resolved by re-running DSE-010.
- Positive: Audit trail preserved (provisional_evidence_span_id field in resolved facts).
- Negative: Two fact JSON files per policy (raw + resolved).

**Revisit when:** DSE-011 redesigns fact candidate management.

---

## 2026-05-31 — OQ-001 resolved: heading score embedded in document_sections (ADR-0021)

**Status:** accepted

**Decision:** `document_sections.heading_score` and `document_sections.heading_type` store the heading scorer output. No separate `heading_candidates` table is created.

**Context:** OQ-001 asked whether heading candidates should be a separate table or embedded in sections.

**Reasoning:** Only accepted headings become sections. Rejected candidates are logged in `heading_candidates.json` but don't need SQLite persistence — no current query needs rejected candidates. Embedding heading score avoids an extra JOIN for the common case.

**Consequences:**
- Positive: Simpler schema — one table for sections (no candidates table).
- Negative: Rejected candidate details not queryable from SQLite.

**Revisit when:** A heading quality analysis query needs rejected candidates from the DB.

---

## 2026-05-31 — Namespace document-local IDs in SQLite (ADR-0022)

**Status:** accepted

**Decision:** DSE-010 stores globally unique SQLite IDs for document-local artifacts by prefixing the source-local ID with `document_id`, e.g. `{document_id}:p1l_1`, `{document_id}:sec_0001`, and `{document_id}:clause_0001`. The original local IDs are preserved in `source_line_id`, `source_section_id`, `source_clause_id`, and `source_line_ids_json`.

**Context:** DSE-006/DSE-007 artifacts intentionally use policy-local IDs. During DSE-010 review, `document_lines.line_id` and `policy_clauses.clause_id` were discovered as global primary keys even though values like `p1l_1` and `clause_0000` repeat across all five policies. This caused silent row replacement and made DB self-consistency checks pass while source rows were missing.

**Options considered:**
1. Rewrite upstream DSE-006/DSE-007 artifacts to use global IDs.
2. Use composite primary keys such as `(document_id, clause_id)` everywhere.
3. Namespace local IDs during DSE-010 ingestion and preserve source-local IDs in explicit columns.

**Reasoning:** Option 3 keeps upstream artifacts stable, minimizes downstream query complexity, and makes every SQLite FK unambiguous. It also preserves source-local IDs for audit/debug compatibility.

**Consequences:**
- Positive: SQLite now preserves all 12,715 lines, 1,156 sections, and 2,522 clauses across the five gold policies.
- Positive: Source spans and resolved facts cannot accidentally link across documents.
- Negative: DSE-010 consumers must distinguish DB UIDs from source-local IDs.

**Revisit when:** A future schema migration introduces composite keys throughout the local engine store.

---

## 2026-06-01 — Refine deferred DDL for fact tables (ADR-0023)

**Status:** accepted

**Decision:** DSE-011 expands the IMPLEMENTATION_PLAN.md placeholder DDL for `extracted_fact_candidates` (14 → 22 columns), `extracted_facts` (added source_candidate_id, source_clause_id, CHECK on fact_status), and `fact_conflicts` (added document_id, concept, pipeline_run_id, CHECK constraints). These tables were empty (never populated), so no migration is needed.

**Context:** DSE-007 fact candidates carry 21 fields; the v1 DDL only had 14 columns, missing fields needed for scoring, evidence tracking, and gold evaluation.

**Reasoning:** DSE-011 is the first consumer of these tables. Refining the DDL now (while tables are empty) is zero-risk and avoids lossy data insertion.

**Consequences:**
- Positive: Full candidate data persisted for debugging and eval.
- Positive: CHECK constraints enforce valid fact_status and conflict_type values.

**Revisit when:** DSE-012+ adds new fact statuses or conflict types.

---

## 2026-06-01 — extracted_facts stores only present/explicitly_not_covered facts (ADR-0024)

**Status:** accepted

**Decision:** `extracted_facts` stores only facts with affirmative evidence (fact_status IN ('present', 'explicitly_not_covered')). `not_found` status is derived at query time: if a concept has no row in `extracted_facts` for a document, it's not_found.

**Context:** `extracted_facts.clause_id` is NOT NULL, but not_found facts have no clause reference.

**Reasoning:** Architecturally cleaner — the table stores findings with provenance, not absences. The concept list is known (TARGET_CONCEPTS), so deriving not_found is trivial.

**Consequences:**
- Positive: No dummy clause references for not_found facts.
- Positive: UNIQUE INDEX on (document_id, concept) guarantees one fact per concept per document.
- Negative: Consumers must derive not_found by checking absence.

**Revisit when:** A consumer needs to store explicit not_found records with metadata (e.g., "searched 554 clauses, none matched").

---

## 2026-06-01 — Composite scoring formula (ADR-0025)

**Status:** accepted

**Decision:** composite_score = 0.50 × confidence + 0.30 × evidence_quality + 0.15 × pattern_specificity + 0.05 × source_priority. Acceptance threshold: 0.85.

**Context:** DSE-007 extractors assign confidence per candidate. DSE-011 needs a multi-dimensional score for ranking and future multi-extractor conflict resolution.

**Reasoning:** Confidence alone is insufficient when multiple extractors with different calibration produce candidates for the same concept. Adding evidence quality and pattern specificity prevents high-confidence garbage from winning over low-confidence quality.

**Consequences:**
- Positive: Extensible — future dimensions (LLM confidence, cross-reference, etc.) can be added.
- Negative: Weights are not empirically tuned (no training data for weight optimization).

**Revisit when:** DSE-012+ has 20 concepts with diverse extractor patterns and enough data to tune weights empirically.

---

## 2026-06-01 — Conflict detection logic (ADR-0026)

**Status:** accepted

**Decision:** A conflict is two or more accepted candidates for the same (document, concept) with different normalized values, different statuses, or different scopes. Resolution strategies: higher_score_wins, manual_review_required, merged.

**Context:** Current pipeline has 1 extractor per concept → 0 conflicts. But the infrastructure must be proven correct for future multi-extractor scenarios.

**Reasoning:** Building the conflict machinery now (with synthetic test coverage) means future extractors plug in safely. The conflict_detector finds disagreements; the resolver applies a strategy; both are tested with synthetic conflicting candidates.

**Consequences:**
- Positive: Infrastructure ready for 15+ extractors.
- Positive: Proven correct via 10 synthetic conflict tests.
- Negative: 0 production conflicts — the machinery is exercised only in tests until DSE-012+.

**Revisit when:** Adding a second extractor for any concept (e.g., LLM + deterministic for room_rent).

---

## 2026-06-01 — All 20 concepts emitted in every export (ADR-0027)

**Status:** accepted

**Decision:** Every policy export contains exactly 20 feature keys in `features`. Concepts without extractors are emitted with `fact_status = "not_found"` and `value = null`. No concept key is ever omitted.

**Context:** Only 5/20 concepts have extractors. Product B needs a stable schema shape.

**Reasoning:** A stable shape means Product B never encounters a missing key. "Not found" is explicit and honest — Product B can display "Not found in policy text" rather than silently omitting a comparison field.

**Consequences:**
- Positive: Product B always sees 20 fields, regardless of extractor coverage.
- Positive: Fill rate is measurable (concepts_resolved / 20).
- Negative: 75% of fields are currently not_found.

**Revisit when:** Concept list grows beyond 20.

---

## 2026-06-01 — Scalar extraction for simple types, full JSON for compound types (ADR-0028)

**Status:** accepted

**Decision:** For concepts with a single scalar value key (e.g., `free_look_period` → `days`), the export `value` field is the scalar number. For compound concepts (co-pay components, room rent structures), the export `value` is the full normalized_value_json dict.

**Context:** Product B needs both simple numbers for display ("15 days") and structured objects for complex benefits.

**Reasoning:** A uniform approach (always dict) would complicate display. A uniform approach (always scalar) would lose compound structure. This hybrid maps naturally to how Product B will render each concept.

**Consequences:**
- Positive: Simple values are easy to display ("15 days").
- Positive: Compound values carry full structure for rich rendering.
- Negative: Product B must handle both types per concept.

**Revisit when:** Product B requests a different value format.

---

## 2026-06-01 — Export is gitignored; build summary committed (ADR-0029)

**Status:** accepted

**Decision:** `data/export/` is generated output (gitignored). `data/reports/dse013_export_summary.json` and `runs/evals/` artifacts are committed. Engineers regenerate exports by running `run_export.py`.

**Context:** Export JSON files change every pipeline run (timestamps, run IDs). Committing them would create noise.

**Reasoning:** Same pattern as `data/engine.sqlite` (gitignored, reproducible). The eval artifact captures the quality metrics for review.

**Consequences:**
- Positive: No binary/JSON churn in git history.
- Negative: Engineers must run `run_export.py` locally to inspect exports.

**Revisit when:** A CI/CD pipeline needs committed export artifacts for deployment.
