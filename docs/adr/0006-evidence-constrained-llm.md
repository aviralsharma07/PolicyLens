## 2026-05-29 — ADR-0006: Evidence-Constrained LLM

**Status:** accepted

**Decision:** LLM facts must quote their evidence, and the evidence must be verified in the source. Rules: (1) only send relevant clause context (not entire PDF), (2) LLM must return evidence string — exact text from the clause supporting the value, (3) system verifies the evidence string exists in source clause text (substring check), (4) if evidence not found → reject the fact, (5) LLM-assisted facts get lower default confidence (0.70-0.85) vs deterministic (0.90-0.98), (6) concept-level precision must be >= 85%.

**Context:** LLMs hallucinate. In insurance, a single hallucinated value (e.g., "no room rent limit" when there is one) causes real harm. Early experiments showed 30%+ of LLM extraction failures included convincing-but-wrong hallucinated values.

**Options considered:**
1. Pure regex extraction (no LLM)
2. LLM with confidence threshold but no evidence check
3. Evidence-constrained LLM (chosen)

**Reasoning:** Evidence constraints dramatically reduce hallucinated values, make every LLM fact auditable, and force the LLM to point to real text. Pure regex misses concepts requiring reasoning (e.g., "Does this policy cover AYUSH?" — the answer may be in a clause that doesn't use the word "AYUSH"). Confidence thresholds alone are insufficient because LLMs produce confident-sounding wrong answers.

**Consequences:**
- Positive: Dramatically reduces hallucinated values.
- Positive: Every LLM fact is auditable.
- Positive: Forces LLM to point to real text.
- Negative: Rejects valid extractions where LLM paraphrased correctly but didn't quote exactly.
- Negative: Evidence verification adds a validation step after LLM call.

**Revisit when:** Evidence verification rejects > 10% of otherwise correct LLM extractions. Consider adding fuzzy/near-match evidence verification at that point.
