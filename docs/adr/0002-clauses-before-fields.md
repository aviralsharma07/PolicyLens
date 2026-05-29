## 2026-05-29 — ADR-0002: Clauses Before Fields (Clause-Store Architecture)

**Status:** accepted

**Decision:** Store clauses as atomic legal units. Derive fields from clauses. Never flatten first. The pipeline stores document sections (hierarchy tree), policy clauses (atomic legal units with raw text/page/references), source spans (coordinates + char ranges), extracted facts (typed values linked to clauses via evidence_span_id), and derived policy features (91-field view compiled from facts).

**Context:** The initial approach attempted to extract 91 flat fields directly from PDF text using LLM prompts. This failed because the LLM saw unstructured text soup, flat fields lose relationship context, there was no provenance to trace fields back to source, and different policies express the same concept in different sections. The friend's analysis proposed: "Clauses are source truth. Fields are derived views."

**Options considered:**
1. Flat extraction with provenance tracking
2. Document-level key-value extraction
3. Hybrid (store both clauses and flat fields)
4. Clause-store architecture (chosen)

**Reasoning:** The clause-store approach ensures every fact traces back to a specific clause, page, and coordinate. It supports inheritance and override (Policy Schedule vs body clause), naturally attaches scope/conditions to clauses, and allows adding new field types without re-extraction. Alternatives were rejected because they lose clause hierarchy, cannot express scope/exceptions, or duplicate data without clear authority.

**Consequences:**
- Positive: Facts are debuggable with full provenance.
- Positive: Supports schedule overrides with conflict records.
- Positive: Scope/conditions attach naturally to clauses.
- Positive: New fields derivable without re-extraction.
- Negative: More storage (clauses + spans + candidates + conflicts).
- Negative: More complex querying for flat view.
- Negative: Requires reliable clause segmentation.

**Revisit when:** Clause segmentation quality (F1 >= 80%) cannot be achieved on the 647-file corpus. In that case, consider a hybrid approach with fallback to document-level extraction.
