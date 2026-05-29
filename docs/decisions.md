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

---

## Proposed ADRs

| ID | Title | Date | Status |
|----|-------|------|--------|
| 0009 | Separate Supabase project for engine in production | TBD | Proposed |
| 0010 | Regulatory compliance engine deferred | TBD | Proposed |
| 0011 | Use pdfplumber for physical layout extraction | 2026-05-29 | Accepted |

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
