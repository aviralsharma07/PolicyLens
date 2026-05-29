## 2026-05-29 — ADR-0008: 7-Status Fact System (Not Present/Absent Binary)

**Status:** accepted

**Decision:** Use 7 fact status values instead of binary found/not_found: present, explicitly_not_covered, not_applicable, not_found, ambiguous, conflicting, requires_manual_review. Each status has a specific Product B display rule.

**Context:** A binary "found / not found" fact status loses critical information. The difference between "deductible is not applicable" (policy type doesn't have deductibles — show "N/A") and "deductible was not found" (could not locate — show "Not found in policy text") is meaningful. Similarly, ambiguous and conflicting are distinct states requiring different handling.

**Options considered:**
1. Binary found/not_found
2. Numeric confidence score only
3. 7-status fact system (chosen)

**Reasoning:** Binary conflates "not applicable" with "not found", which causes wrong user-facing displays ("No deductible" from a not_found status is a real bug pattern we observed). Confidence scores don't capture the reason a value is missing — a low-confidence conflicting fact needs different handling than a low-confidence not_found fact.

**Consequences:**
- Positive: Product B shows honest states instead of fabricating values.
- Positive: Triage queue is clear — conflicting and ambiguous facts auto-flagged.
- Positive: Improvement drives are targeted (e.g., "reduce not_found rate on Room Rent from 40% to 20%").
- Negative: More complexity in extraction pipeline (must explicitly set status).
- Negative: Product B must handle 7 states in the UI.

**Revisit when:** Product B UX data shows that users are confused by the 7 states. Consider collapsing ambiguous/conflicting/requires_manual_review into a single "needs_review" status for user-facing display while keeping fine-grained status internally.
