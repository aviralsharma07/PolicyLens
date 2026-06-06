# Architectural Decisions

This file records key architectural decisions. Earlier work used separate `docs/adr/` files for some decisions; the current source of truth is this append-only document.

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
| 0035 | Scale eval gates derive reviewed policy count dynamically | 2026-06-02 | Accepted |
| 0036 | Fact value comparison allows metadata supersets only | 2026-06-02 | Accepted |
| 0037 | Wave 1 deterministic fact value shapes | 2026-06-02 | Accepted |
| 0038 | Ontology registry is canonical concept source | 2026-06-02 | Accepted |
| 0039 | Duplicate-hash entries skipped at clause store ingestion | 2026-06-04 | Accepted |
| 0040 | Product B Export v1 is compiled 20-concept JSON | 2026-06-05 | Accepted |
| 0041 | Curated top-insurer MVP over 647-policy launch | 2026-06-05 | Accepted |
| 0042 | Product identity is a source bundle, not one PDF | 2026-06-05 | Accepted |
| 0043 | Product B recommendations require variant/condition-scoped facts | 2026-06-05 | Accepted |
| 0044 | Latest-version gate overrides older corpus wording files for MVP truth | 2026-06-06 | Accepted |
| 0045 | Project transitions from active roadmap to open-source closeout state | 2026-06-06 | Accepted |

---

## Proposed ADRs

| ID | Title | Date | Status |
|----|-------|------|--------|
| 0009 | Separate Supabase project for engine in production | TBD | Proposed |
| 0010 | Regulatory compliance engine deferred | TBD | Proposed |

---

## 2026-06-05 — ADR-0040: Product B Export v1 is compiled 20-concept JSON

**Status:** accepted

**Decision:** DSE-023 freezes Product B Export v1 as compiled JSON files containing the 20 ontology-backed priority concepts. Product B consumes `policy_features.json`, `policy_fact_sources.json`, and `policy_clauses_minimal.json` from a handoff package. Product B must not query Product A SQLite, raw parser tables, physical/logical/table interim outputs, or raw PDFs.

**Context:** Product A now has 20 reviewed gold policies, all 20 priority deterministic concepts active, source spans, fact scoring, table eval, and a working export. Older planning docs referred to a 91-field export, but the actual stable v1 export is the 20-concept ontology-backed schema. Product B needs a stable handoff boundary before broader schema expansion or LLM refinement.

**Options considered:**
1. Freeze the current 20-concept JSON export as Product B v1.
2. Wait until a full 91-field schema exists.
3. Let Product B read Product A SQLite directly.

**Reasoning:** Option 1 gives Product B a truthful, evidence-backed dataset now while preserving explicit statuses for missing or non-applicable facts. Option 2 delays integration without improving the current contract. Option 3 violates the Product A/Product B boundary and would expose raw, volatile parser internals to a user-facing app.

**Consequences:**
- Positive: Product B gets a stable, versioned, evidence-backed JSON boundary.
- Positive: Product A can keep evolving SQLite/parser schemas without breaking Product B.
- Positive: The 91-field idea remains available as a future schema expansion.
- Negative: Product B v1 comparison coverage is limited to the 20 priority concepts.

**Revisit when:** Product B requires additional comparison fields beyond the 20 priority concepts, or a later ontology version defines the broader 91-field schema.

---

## 2026-06-05 — ADR-0041: Curated Top-Insurer MVP Over 647-Policy Launch

**Status:** accepted

**Decision:** Product B MVP will not launch as a 647-policy comparison product. The launch corpus will be curated around top Indian health insurers, starting with roughly 5 insurers and 30-40 high-value retail products/variants. The 647-policy corpus remains a Product A scale diagnostic and source of future candidates, not the launch promise.

**Context:** DSE-020 proved Product A can run across 647 active policy wordings, and DSE-023 produced a 20-policy Product B handoff package. Product B prototype review then exposed a sharper product truth: buyers do not need hundreds of choices. They need a trusted shortlist with citations and caveats. Broad coverage without complete PBT/CIS/source bundles risks misleading comparisons and trust loss.

**Options considered:**
1. Launch with every exported full-corpus policy.
2. Launch with the 20-policy gold benchmark only.
3. Launch with a curated top-insurer, source-bundled MVP corpus.

**Reasoning:** Option 1 optimizes for breadth before accuracy and would include duplicates, old products, group/custom products, and policies without complete source documents. Option 2 is too small and gold-corpus-shaped rather than user-market-shaped. Option 3 matches the product thesis: fewer trustworthy recommendations with official evidence.

**Consequences:**
- Positive: Product B can focus on trust, clarity, and user fit.
- Positive: QA effort goes into products users are likely to consider.
- Positive: The product can recommend 1-3 policies instead of becoming another noisy aggregator.
- Negative: Launch coverage is intentionally narrow and may miss long-tail insurers.
- Negative: Product selection becomes a product/editorial responsibility that must be documented.

**Revisit when:** User traction shows demand for broader insurer coverage, or source-bundle collection becomes reliable enough to expand without reducing trust.

---

## 2026-06-05 — ADR-0042: Product Identity Is a Source Bundle, Not One PDF

**Status:** accepted

**Decision:** Product A will model launch-grade products as source bundles, not single policy wording PDFs. A source bundle may include policy wording, Product Benefit Table / table of benefits, CIS, brochure/prospectus, rider/add-on documents, source URLs, hashes, UIN/version evidence, and variant names.

**Context:** Policy wordings often state that numeric benefits, co-pay, room rent, ICU, deductible, and variant-specific terms are "as specified in the Product Benefit Table" or "as specified in the Policy Schedule." The Aditya Birla Activ Care review showed this concretely: the local wording supported a conditional 15% non-preferred-provider co-pay, while variant-level Standard/Classic/Premier co-pay values lived outside the wording in a PBT.

**Options considered:**
1. Keep one PDF = one product.
2. Add PBT/CIS documents as unstructured notes.
3. Create an explicit source-bundle registry.

**Reasoning:** Option 1 is incomplete for recommendation-grade comparison. Option 2 helps humans but does not give Product B reliable source quality or variant semantics. Option 3 makes document completeness and source authority first-class.

**Consequences:**
- Positive: Product B can know whether a product is recommendation-ready.
- Positive: Missing PBT/CIS becomes visible instead of silently weakening facts.
- Positive: UIN/version and source conflicts can be handled before user display.
- Negative: Source collection becomes a dedicated workflow, not a side effect of policy-wording scraping.

**Revisit when:** Insurer APIs or regulatory datasets expose complete product bundles directly.

---

## 2026-06-05 — ADR-0043: Product B Recommendations Require Variant/Condition-Scoped Facts

**Status:** accepted

**Decision:** Product B recommendation facts must distinguish base policy facts, variant-specific facts, schedule-dependent facts, conditional facts, and unknown facts. Product B must not flatten condition-heavy or variant-heavy values into one scalar display.

**Context:** The Product B prototype displayed Aditya Birla Activ Care co-pay as a single 15% present value with high confidence. Source review showed that 15% was conditional on non-preferred-provider-network treatment, while other base/variant co-pay values come from PBT/schedule context. The value was extracted with evidence, but the display semantics were misleading.

**Options considered:**
1. Keep scalar feature fields and rely on evidence text for nuance.
2. Add display warnings manually in Product B.
3. Carry scope, condition, source document type, and source quality through Product A export.

**Reasoning:** Option 1 creates overconfident UX. Option 2 is brittle and duplicates Product A semantics in Product B. Option 3 keeps structured truth with the evidence-producing system and allows Product B to display uncertainty honestly.

**Consequences:**
- Positive: Product B can show accurate caveats and variant context.
- Positive: `not_found`, `schedule_dependent`, and `explicitly_not_covered` remain distinct.
- Positive: Conditional clauses can be useful without becoming misleading recommendations.
- Negative: Export and UI complexity increase.

**Revisit when:** Bundle-aware export is implemented and Product B has enough user feedback to refine display semantics.

---

## 2026-06-04 — ADR-0039: Duplicate-hash entries are skipped at clause store ingestion

**Status:** accepted

**Decision:** When the DSE-020 manifest has multiple slugs sharing the same `document_id` (same SHA-256 file hash), the clause store ingests only the first slug encountered. Subsequent slugs are skipped with a "duplicate document_id" result recorded in the build summary and their stale resolved facts directories are removed.

**Context:** The DSE-020 manifest (647 entries) has 591 unique document hashes. 56 entries share an SHA-256 hash with another entry because the same PDF file was obtained from different sources (e.g., IRDAI filing vs insurer website download) and appears under two different slugs. Without deduplication, `document_sections`, `policy_clauses`, and `document_lines` accumulated 2× the correct row count for shared-document_id policies because `INSERT OR REPLACE` on the primary key preserves the first row in `source_documents` but the downstream tables use UIDs that include the slug-specific clause/section IDs and thus both sets of rows persist.

**Options considered:**
1. Skip duplicate-hash entries entirely at clause store ingestion.
2. Filter duplicate-hash entries at validation time only.
3. Add a `manifest_policy_id` layer so each slug is tracked independently from `source_document` identity.

**Reasoning:** Option 1 is simplest and safest. The downstream validator already deduplicates expected counts by `document_id` (via dict key overwrite in `collect_source_counts_from_manifest`), so skipping at ingestion makes the validator's deduplicated expectation match the DB state exactly. Option 2 would leave the DB bloated with doubled data. Option 3 adds schema complexity that is not needed because the duplicate slugs represent the same underlying document with no additional content value.

**Consequences:**
- Positive: DB contains exactly one set of sections/clauses per unique document.
- Positive: Source-span validation passes without special-casing the count parity check.
- Positive: 56 entries recorded in the build summary as intentional skips.
- Negative: The per-policy run still processes all 647 slugs through the 5 per-policy stages (physical, heading, section, tables, facts), so some CPU/storage is "wasted" on duplicate entries at the JSON-output layer.
- Negative: Export count (566/591) is based on unique documents, not manifest entries.

**Revisit when:** The corpus identity system is enhanced to detect and merge duplicate-source entries at the manifest level instead of the clause store level.

---

## 2026-06-06 — ADR-0045: Project Transitions From Active Roadmap To Open-Source Closeout State

**Status:** accepted

**Decision:** `doc-structure-engine` is no longer an active feature roadmap. The repository is preserved as a completed engineering artifact, open-source reference implementation, and project retrospective. Deferred items such as bundle-aware Product B export or LLM refinement remain historical future work, not active commitments.

**Context:** The project successfully built a substantial document compiler for insurance PDFs, but the broader product thesis depended on continuously current insurer product truth assembled from fragmented public documents. That creates an ongoing operational data burden that is not reasonable for this side-project scope.

**Options considered:**
1. Continue the Product A roadmap into bundle-aware export and deeper Product B integration.
2. Freeze the broad product ambition, preserve the engine, and close the roadmap honestly.
3. Rewrite the repo history to present the work as if it were still a live product effort.

**Reasoning:** Option 2 is the truthful choice. The technical work is real and worth preserving, but continuing to imply an active roadmap would overstate the practicality of the product path. Option 1 would continue a product direction already judged operationally unsound for the project context. Option 3 would make the public repository less honest, not more useful.

**Consequences:**
- Positive: the repository becomes a credible public artifact with a clear scope.
- Positive: future readers can learn from both the technical achievements and the stopping point.
- Positive: articles, talks, or future pivots can build on a clean and truthful record.
- Negative: some planned work remains intentionally unfinished.

**Revisit when:** Only if the project is deliberately reactivated with a narrower scope, explicit maintenance plan, and a fresh product/data strategy.

---

## Rejected ADRs

| ID | Title | Date | Status |
|----|-------|------|--------|
| — | Use OCR/vision PDF extraction | 2026-05-28 | Rejected — 100% text-layer corpus confirmed |

---

## Decision Records

### 2026-06-02 — ADR-0038: Ontology Registry Is Canonical Concept Source

**Status:** accepted

**Decision:** Product A concept identity, value shape, export field mapping, active deterministic status, evidence requirements, allowed fact statuses, and Product B display semantics are governed by `ontology/concepts.v1.json`.

**Context:** By DSE-018, ontology knowledge existed across extractor target lists, export mapping, gold facts, fact schemas, decisions, and docs. That was workable while concept shapes were still being discovered, but it risks drift before full-corpus scale runs and Product B handoff.

**Options considered:**
1. Keep concept definitions distributed across extractors and export mapping.
2. Make the export mapping the canonical ontology.
3. Create a dedicated ontology registry and validate existing mappings against it.

**Reasoning:** The export mapping is Product B-facing but too narrow to express evidence requirements, display semantics, extractor status, and future LLM/table responsibilities. A dedicated registry gives Product A one concept control plane while allowing conservative wiring through tests before larger refactors.

**Consequences:**
- Positive: Drift between gold facts, extractor targets, and export fields becomes test-detectable.
- Positive: Product B display semantics can be tied to fact status and concept definition.
- Negative: Future concept additions must update ontology first, then code/docs.

**Revisit when:** Product B requires fields beyond the 20 priority concepts or the 91-field export needs a richer nested ontology.

### 2026-06-02 — ADR-0037: Wave 1 Deterministic Fact Value Shapes

**Status:** accepted

**Decision:** DSE-018 defines canonical normalized value shapes for the Wave 1 deterministic concepts. Claim settlement uses primary settlement/rejection days as `{"days": N}` and may include `{"investigation_days": M}` only when the same accepted evidence safely supports the extension. Specific disease waiting periods use `{"months_options": [...]}`. Maternity language such as "not covered until 36 months" is treated as `present` waiting-period evidence, not an absolute exclusion.

**Context:** The 20-policy corpus exposed inconsistent gold labels and extractor outputs for claim settlement, specific disease waiting periods, and maternity waiting. Some policies contain normal settlement plus investigation extension clauses; some split those clauses across section-tree fragments. Some waiting period clauses use compact slash notation such as `24/48 months`.

**Options considered:**
1. Store only the maximum duration.
2. Store all durations found near a concept keyword.
3. Store concept-specific canonical shapes with precision-first evidence requirements.

**Reasoning:** Maximum-duration extraction hides the primary policy rule. Collecting every nearby duration creates false positives from claim intimation, premium, PED definitions, and unrelated benefit wording. Concept-specific shapes preserve useful values while keeping evidence requirements strict.

**Consequences:**
- Positive: Product B receives stable Wave 1 shapes for comparison.
- Positive: Extractors can reject unsafe values instead of forcing a misleading present fact.
- Negative: If a source PDF value is lost by section-tree clause segmentation, the fact may remain `not_found` until the parser is improved.

**Revisit when:** DSE-014 LLM refinement or a later parser task can safely merge adjacent evidence spans into one accepted fact.

### 2026-06-02 — ADR-0035: Scale Eval Gates Derive Reviewed Policy Count Dynamically

**Status:** accepted

**Decision:** DSE-017 eval scripts derive the expected policy count from reviewed policies in `gold_corpus/` instead of hardcoding 5. The SQLite size gate is raised from 30 MB to 120 MB for the reviewed 20-policy corpus.

**Context:** After DSE-012, the authoritative gold corpus grew from 5 to 20 reviewed policies. DSE-010 through DSE-013 evals still contained 5-policy assumptions, which made the structural pipeline look smaller than the current acceptance target.

**Options considered:**
1. Keep 5-policy evals and treat 20-policy runs as diagnostic.
2. Add separate 20-policy eval scripts.
3. Make existing evals corpus-driven.

**Reasoning:** Corpus-driven gates keep one source of truth and prevent future expansion from leaving stale constants behind. Separate scripts would duplicate gate logic.

**Consequences:**
- Positive: Clause-store, fact-scoring, extraction, source-span, and export gates now scale with reviewed gold.
- Positive: Future gold expansion should not require changing count constants.
- Negative: Generated SQLite size grows with corpus size and must remain monitored.

**Revisit when:** The gold corpus exceeds 100 reviewed policies or SQLite size exceeds the documented gate.

### 2026-06-02 — ADR-0036: Fact Value Comparison Allows Metadata Supersets Only

**Status:** accepted

**Decision:** A predicted normalized fact value may match gold when it includes harmless extra metadata, but only if every scalar key in the gold value matches exactly. Different durations, units, percentages, schedule-dependent markers, or statuses remain mismatches.

**Context:** DSE-017 found values such as extracted `{"percentage": 5, "basis": "admissible_claim_amount"}` versus gold `{"percentage": 5}`. Treating those as mismatches punished useful extractor provenance without improving correctness.

**Options considered:**
1. Require exact JSON equality.
2. Allow loose semantic matching for many shapes.
3. Allow metadata supersets only when gold scalar keys match exactly.

**Reasoning:** Exact equality is too brittle for richer extractor output. Broad semantic matching risks hiding real insurance-value errors. Scalar-key subset matching is narrow and auditable.

**Consequences:**
- Positive: Extractors can carry basis/scope metadata without failing gold value accuracy.
- Positive: Value differences that matter to Product B still fail.
- Negative: Eval code must preserve concept-specific caution when future nested values are introduced.

**Revisit when:** New extractors emit nested compound values that need concept-specific comparison rules.

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

---

## 2026-06-01 — UIN base extraction uses V-delimiter (ADR-0030)

**Status:** accepted

**Decision:** `extract_uin_base(full_uin)` splits at the first `V` followed by digits, not at a fixed character position. DSE-010's `full_uin[:11]` was a bug producing truncated 11-char bases.

**Context:** IRDAI UINs have format `{INSURER_CODE}{PRODUCT_CODE}V{VERSION}{FISCAL_YEAR}`. The base is everything before `V`. Most bases are 12 chars but the format doesn't guarantee a fixed length.

**Consequences:**
- Positive: Correct uin_base for all 5 gold policies (12 chars each).
- Positive: No hardcoded length assumption — future UINs with different base lengths will work.

**Revisit when:** IRDAI changes UIN format.

---

## 2026-06-01 — Plan name normalization strips insurer suffix and boilerplate (ADR-0031)

**Status:** accepted

**Decision:** `clean_plan_name()` strips insurer name suffixes (`, HDFC ERGO`), insurer prefixes (`New India `), and generic boilerplate (`Insurance Policy`, `Policy`, `Individual`).

**Context:** Lifecycle product names include insurer names and generic suffixes that are redundant when displayed alongside the insurer field. Product B needs clean plan names for comparison UI.

**Consequences:**
- Positive: "Arogya Sanjeevani Policy, HDFC ERGO" → "Arogya Sanjeevani" — clean and display-ready.
- Negative: Rule-based — unusual product names may need manual override.

**Revisit when:** Expanding to 647 corpus reveals plan names the rules can't handle.

---

## 2026-06-01 — Insurer registry is canonical source of truth (ADR-0032)

**Status:** accepted

**Decision:** `identity/insurer_registry.py` contains 32 `InsurerRecord` entries covering all lifecycle insurers. It subsumes DSE-002's `FOLDER_TO_LIFECYCLE` mapping. Old `insurer_normalizer.py` API is preserved for backward compatibility.

**Context:** DSE-002 had 23 folder→lifecycle mappings. 9 lifecycle insurers had no mapping (no corpus files). The registry adds them and provides display_name, legal_name, and IRDAI prefix.

**Consequences:**
- Positive: Single source of truth for insurer identity across the pipeline.
- Positive: Backward compatible — `normalize("HDFC_ERGO")` still returns `"HDFC ERGO"`.

**Revisit when:** A new insurer appears in the corpus.

---

## 2026-06-04 — Zero-heading fallback promotion over global threshold lowering (ADR-0033)

**Status:** accepted

**Decision:** Add a conservative fallback heading promotion layer that activates only when normal heading scoring finds zero headings for a document. Do not lower the global heading threshold.

**Context:** DSE-024 Phase D2 recovered the Phase C regression and reduced zero-clause policies to 122, but many remaining failures had plausible structural headings just below the 0.5 threshold. Threshold experiments showed global lowering creates too much false-positive risk.

**Options considered:**
1. Lower global threshold from 0.5 to 0.45.
2. Add insurer-specific hardcoded heading rules.
3. Add a zero-heading-only fallback promotion layer with explicit false-positive guards.

**Reasoning:** Option 3 improves full-corpus parser coverage while preserving the 20-policy gold heading gate. It is auditable because promoted candidates store `promotion_source`, `promotion_reason`, original score, and guard evaluation details.

**Consequences:**
- Positive: Zero-clause policies reduced from 122 to 110 without new zero-clause regressions versus D2.
- Positive: Gold heading eval remained 20/20 PASS.
- Negative: 110 policies still need parser remediation or corpus filtering.

**Revisit when:** False-positive review of promoted headings shows unsafe promotions, or remaining zero-clause policies require format-specific logic beyond this fallback.

---

## 2026-06-04 — Claim intimation stores primary notification deadline (ADR-0034)

**Status:** accepted

**Decision:** `claim_intimation_timeline` stores the primary or earliest claim-notification deadline as `{"hours": N}` or `{"days": N}`. Claim document filing/submission timelines are not included in this concept.

**Context:** DSE-021 Packet 1A found that reviewed gold labels mixed claim notification, claim filing, and truncated `timeline_text` values. Several policies contain multiple deadlines in the same claims procedure section, but Product A needs a stable comparable value for the claim-intimation concept.

**Options considered:**
1. Store the entire claims procedure as `timeline_text`.
2. Store a multi-component object for every scenario.
3. Store the primary/earliest notification deadline and defer filing timelines to a separate concept.

**Reasoning:** Option 3 is deterministic, comparable, and aligned with the concept name. It avoids conflating intimation with document submission while preserving evidence for the selected deadline.

**Consequences:**
- Positive: DSE-021 Packet 1A fact extraction eval passes with 20/20 policies, 100% precision, 100% value accuracy, and 0 false-present facts.
- Positive: Product B gets a stable field instead of opaque text snippets.
- Negative: Rich scenario-specific filing schedules are not represented yet.

**Revisit when:** Product B needs scenario-specific claim filing/display timelines or a separate `claim_document_submission_timeline` concept is added.

---

## 2026-06-04 — Deductible requires operative policy language (ADR-0035)

**Status:** accepted

**Decision:** `deductible` is `present` only when policy wording contains operative language showing a deductible applies. Standard definitions such as `Deductible means...` are not enough.

**Context:** DSE-021 Packet 1B found that several gold labels marked definition-only deductible text as present. This creates a false user-facing impression that the policy has a deductible when the wording only defines the term.

**Options considered:**
1. Treat any `Deductible means...` definition as present.
2. Emit `present` only from operative language and schedule/certificate dependency clauses.
3. Defer deductible until table/schedule parsing improves.

**Reasoning:** Option 2 preserves precision and still captures true schedule-dependent deductibles. It also follows the Product B display rule that `not_found` must not be shown as `No deductible`.

**Consequences:**
- Positive: DSE-021 Packet 1C eval passes with 100% precision, 100% value accuracy, and 0 false-present facts.
- Positive: Definition-only clauses no longer create misleading deductible facts.
- Negative: Exact deductible amounts remain unavailable when the wording points only to the policy schedule/certificate.

**Revisit when:** DSE-022/DSE-023 can reliably parse policy schedules or Product B needs exact deductible amounts beyond schedule-dependent status.

---

## 2026-06-04 — Room and ICU limits use explicit status/value shapes (ADR-0036)

**Status:** accepted

**Decision:** `room_rent_limit` and `icu_limit` use distinct value shapes for explicit percentage limits, actuals/no fixed limit, schedule-dependent limits, and conditional components. Definition-only text is not enough to emit `present`.

**Context:** DSE-021 Packet 2A/2B found that reviewed gold labels mixed table-row bleed, definition clauses, policy-schedule dependencies, actuals/no-limit rows, and conditional sum-insured/city-specific limits. Collapsing these into one scalar would mislead Product B comparisons.

**Options considered:**
1. Store only one scalar percentage/amount when any room/ICU text is found.
2. Store broad text snippets and defer normalization.
3. Use explicit normalized shapes: percentage + unit, `coverage_status: actuals`, `schedule_dependent` with basis, or `components` for conditional limits.

**Reasoning:** Option 3 preserves comparable values without inventing missing schedule data. It also supports policies like IFFCO and Oriental where multiple conditional limits are materially different.

**Consequences:**
- Positive: DSE-021 Packet 2B eval passes with 20/20 policies, 100% precision, 100% value accuracy, and 0 false-present facts.
- Positive: Product B can distinguish actuals/no fixed limit from schedule-dependent unknowns.
- Negative: Exact schedule amounts still require table/schedule remediation where the policy wording references external schedules.

**Revisit when:** DSE-022 table remediation or Product B export freeze needs richer display semantics for component-shaped room/ICU limits.

---

## 2026-06-05 — Coverage-wave extractors must not invent missing exact limits (ADR-0037)

**Status:** accepted

**Decision:** `restoration_benefit`, `modern_treatment_coverage`, and `newborn_coverage` may emit conservative covered/conditional values when exact source PDF percentages or sub-limits are not carried in verified section-tree evidence.

**Context:** DSE-021 Packet 3B found source PDF percentages for Star restoration and Tata AIG modern treatment, but the current section-tree clauses do not safely preserve those exact values. Product B needs evidence-backed facts, not values inferred from inaccessible context.

**Options considered:**
1. Hardcode exact values from source-PDF manual review.
2. Emit `not_found` whenever exact limits are missing from section-tree clauses.
3. Emit evidence-backed covered/conditional status and defer exact limits to parser/table remediation.

**Reasoning:** Option 3 preserves truthful coverage presence without inventing unsupported exact limits. It keeps deterministic precision high while exposing parser/table remediation as the correct layer for exact value recovery.

**Consequences:**
- Positive: DSE-021 Packet 3B passes with 20/20 policies, 100% precision, 100% value accuracy, and 0 false-present facts.
- Positive: Product B can display safe covered/conditional status without overstating exact limits.
- Negative: Some exact limits remain absent until section-tree/table extraction carries the needed evidence.

**Revisit when:** DSE-022 or later parser/table remediation recovers the missing exact source context for these rows.

---

## 2026-06-06 — Curated insurer universe for Product B MVP (ADR-0038)

**Status:** accepted

**Decision:** Product B MVP will launch against a curated insurer universe rather than the full 647-document corpus. The locked MVP top 5 are HDFC ERGO, Star Health, ICICI Lombard, Care Health, and Niva Bupa. Later-wave top-10 additions are Tata AIG, Bajaj Allianz, New India Assurance, Aditya Birla Health, and SBI General.

**Context:** DSE-025 proved that the current corpus is excellent for policy-wording parsing but weak for launch-grade product truth because 504/507 draft bundles are still `missing_pbt`. DSE-026 therefore had to optimize for user-facing trust and source-bundle collectability, not document count.

**Options considered:**
1. Keep Product B open to the full 647-document universe.
2. Launch with a curated top-10 / top-5 insurer universe and a 30-product first collection set.
3. Launch with only a few hand-picked policies without a formal insurer-selection system.

**Reasoning:** Option 2 preserves rigor without over-scaling. It gives Product B enough coverage to be useful while keeping DSE-027 source-bundle collection and QA tractable. It also keeps the selection reproducible through a weighted rubric and explicit evidence artifacts.

**Consequences:**
- Positive: Product A now has a stable insurer/product target list for DSE-027 instead of a vague "collect everything" mandate.
- Positive: Product B can focus on trust, citations, and recommendation quality instead of breadth theater.
- Negative: Some credible insurers are deferred even though they remain reasonable later-wave candidates.

**Revisit when:** DSE-027 source-bundle collection completes for the MVP top 5 or when user traction justifies expanding beyond the locked top 10.

---

## 2026-06-06 — Latest-version gate overrides older corpus wording files for MVP truth (ADR-0044)

**Status:** accepted

**Decision:** For the curated MVP corpus, current official insurer product pages and current official PDFs override older local corpus wording files whenever the two disagree on product naming or UIN/version. Older local files may still be retained as reviewed evidence, but the bundle must be marked `stale_version` or otherwise downgraded until the current official source is downloaded and reviewed.

**Context:** DSE-027 latest-version verification found repeated version drift across the MVP top-5 insurers. Examples included HDFC ERGO Optima Secure/Restore, multiple Star Health products, ICICI Lombard Complete Health, and multiple Niva Bupa products. Treating older local wording files as current would have made Product B recommendations look precise while being wrong on live product identity.

**Options considered:**
1. Trust the older local corpus unless a product disappears completely.
2. Trust current official insurer sources first and treat older local corpus files as fallback/legacy evidence.
3. Avoid current-version judgments and leave Product B to infer freshness at display time.

**Reasoning:** Option 2 is the only approach compatible with a citation-first recommendation product. The local corpus remains valuable for parsing and evidence development, but it cannot be the final authority on live sellable product identity when current official insurer docs disagree.

**Consequences:**
- Positive: Product A now has a reproducible latest-version gate for the curated MVP corpus.
- Positive: Product B can surface `stale_version`, `missing_cis`, and `missing_pbt` honestly instead of flattening old wording files into fake certainty.
- Negative: Source-bundle collection becomes more operationally expensive because live public links must be re-verified and downloaded.

**Revisit when:** DSE-028 bundle-aware export is complete and the MVP corpus reaches a stable review cadence for current official source refreshes.
