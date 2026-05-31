# Open Questions

This file tracks unresolved design/product questions. Do not let major unresolved questions live only in chat history.

---

## OQ-001 — Should the heading scorer output be stored as a separate table or as JSON in document_sections?

**Status:** answered

**Question:** The heading detector produces candidates with scores and feature breakdowns. Should these be stored in a separate `heading_candidates` table (which then gets resolved into accepted/rejected) or embedded as JSON in `document_sections`?

**Current thinking:** Separate table seems cleaner because rejection reasons and feature breakdowns are useful during debugging but not needed in the section tree. However, a separate table adds more JOINs for the common case (just get accepted sections).

**Options:**
1. Separate `heading_candidates` table → `document_sections` is clean (only accepted). Extra JOIN.
2. JSON field in `document_sections` → simpler queries. Harder to query rejected candidates.

**Decision needed by:** Phase 2 implementation (heading_detector.py + section_tree.py)
**Resolution:** Answered by ADR-0021 (2026-05-31, DSE-010). Heading score and heading_type are stored as fields on `document_sections`. No separate `heading_candidates` SQLite table.

---

## OQ-002 — How to handle multi-version PDFs (same UIN, different effective dates)?

**Status:** open

**Question:** An insurer may have multiple versions of the same product. We have IRDAI UIN data showing version history. But some PDFs in our corpus may not match any specific UIN version. How do we decide which PDF is the "canonical" version?

**Current thinking:** The `canonical_status` field in `source_documents` handles this. But we need rules: preferred source (IRDAI > insurer website), preferred date (newer > older), and preferred status (active > withdrawn). This also affects the gold corpus — which version do we annotate?

**Options:**
1. Always pick the latest active version as canonical
2. Allow multiple versions to coexist with different `canonical_status` values
3. Pick IRDAI-sourced copy over insurer-sourced copy

**Decision needed by:** Phase 0 UIN reconciliation completion
**Resolution:** 

---

## OQ-003 — Should LLM refinement run automatically or only on explicit request?

**Status:** open

**Question:** The deterministic extractors will miss some concepts (estimated 20-30%). The LLM can fill some of these gaps, but with lower precision (>= 85%). Should the LLM refinement step run automatically after deterministic extraction, or should it wait for human review?

**Current thinking:** Auto-run seems better for coverage. Mark LLM-produced facts with lower confidence and flag them for review if the concept is a "critical field" (e.g., PED waiting, co-pay, room rent). Non-critical LLM facts can be accepted at lower confidence.

**Options:**
1. Auto-run LLM on ALL unresolved concepts, flag critical ones for review
2. Auto-run LLM but require manual approval for every LLM fact
3. Manual-only — user triggers LLM refinement per-concept

**Decision needed by:** Phase 6 LLM refinement implementation
**Resolution:** 

---

## OQ-004 — Table type classification: rule-based or ML-based?

**Status:** open

**Question:** Tables need to be classified by type (waiting_period, room_rent, premium, schedule_of_benefits, etc.). Should we use rule-based classification (column headers, section context) or train a lightweight classifier?

**Current thinking:** Start rule-based. The section context is usually informative (a table under "Waiting Period" is likely a waiting period table). Column headers also give strong signals ("Disease", "Waiting Period"). If rule-based fails on >10% of tables, consider ML.

**Options:**
1. Rule-based (section context + column header matching) — simpler, faster to build
2. ML classifier (logistic regression over header tokens + section features) — more robust
3. Hybrid — rule-based with ML fallback

**Decision needed by:** Phase 3 table engine implementation
**Resolution:** 

---

## OQ-005 — Should the gold corpus annotation interface be CLI or a web tool?

**Status:** answered

**Question:** Annotating 5 policy PDFs requires: marking section boundaries, clause boundaries, table regions, and fact values. The annotation format is JSON files. Should we use a CLI workflow (edit JSON manually with text editor) or build a lightweight web annotation UI?

**Current thinking:** CLI for the first 5 policies (direct JSON editing + debug HTML for visual reference). If the annotation process becomes painful, build a minimal Streamlit app. The friend's plan says we should start annotating immediately, not build tooling first.

**Options:**
1. CLI-only — edit JSON by hand, use debug HTML for visual reference
2. Streamlit annotation UI — minimal web tool for structured annotation
3. LabelStudio — existing open-source annotation platform (overkill for now)

**Decision needed by:** Gold corpus annotation start (Day 3 of 7-day sprint)
**Resolution:** Use CLI/manual JSON annotation for the first 5 policies. DSE-003 created `gold_corpus/annotation_guide.md`, JSON schema files, and `scripts/validate_gold_corpus.py`. Revisit a Streamlit or LabelStudio interface only if expanding from 5 to 20 policies becomes too slow or review quality drops.
