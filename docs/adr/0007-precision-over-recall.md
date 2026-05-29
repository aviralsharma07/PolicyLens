## 2026-05-29 — ADR-0007: Precision Over Recall for Fact Extraction

**Status:** accepted

**Decision:** Precision >= 95% for deterministic facts. Recall can be lower. Accept only facts with high evidence quality. "Not found" is an acceptable answer. Never emit a value with insufficient evidence. The export contract distinguishes not_found, not_applicable, ambiguous, and conflicting — all valid states. LLM-assisted facts can have lower precision (>= 85%) but must have evidence verification.

**Context:** For insurance comparison products, a wrong answer damages trust more than an absent answer. "No deductible" (wrong) leads to claim denial and lost trust. "Deductible not found" (unknown) leads to manual check — mildly annoying but still trusted.

**Options considered:**
1. Maximize fill rate (original approach)
2. Recall-first with confidence threshold
3. Precision-first with evidence verification (chosen)

**Reasoning:** Experiments showed fill rate approach produced 30%+ hallucination rate. There is no safe confidence threshold for an LLM — an answer at 0.9 confidence can still be wrong. Evidence verification is more reliable than confidence scoring alone.

**Consequences:**
- Positive: Users trust the platform — answers are rarely wrong.
- Positive: "Not found" signals drive extractor improvement priorities.
- Negative: Early versions show many "not found" values.
- Negative: Harder to demo (fewer filled fields).
- Negative: Product B must handle null/unknown values gracefully.

**Revisit when:** Product B UX feedback indicates that "not found" rates above X% cause user abandonment. May need to relax precision threshold for non-critical concepts at that point.
