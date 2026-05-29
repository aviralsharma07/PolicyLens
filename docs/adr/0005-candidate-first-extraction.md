## 2026-05-29 — ADR-0005: Candidate-First Fact Extraction (Not First-Match-Wins)

**Status:** accepted

**Decision:** Generate all candidates, score them, then resolve conflicts. ALL extractors run against ALL clauses/tables for a given concept. Every candidate is scored (confidence + evidence quality + source precedence). Conflicts are detected (same concept, different values). Accepted with rejection reasons for losers. Precedence rules: Schedule > Benefit grid > Clause > Definition.

**Context:** Insurance policies express the same concept in multiple places (e.g., "room rent limit" in Schedule of Benefits, body clause, definition section, exclusion clause). A first-match-wins approach misses schedule overrides, misses scope dependencies, and creates silent false positives.

**Options considered:**
1. First-match-wins
2. Weighted average across candidates
3. Candidate-first with scoring + conflict resolution (chosen)

**Reasoning:** Candidate-first catches schedule-overrides-body-clause patterns, stores rejected candidates for debugging, and conflict records help identify parsing errors or real policy contradictions. First-match-wins misses schedule overrides and creates silent wrong values. Averaging is wrong for insurance (1% vs 2% should not average to 1.5%).

**Consequences:**
- Positive: Catches schedule-overrides-body-clause patterns.
- Positive: Rejected candidates stored for debugging.
- Positive: Conflict records identify parsing errors or real contradictions.
- Negative: More storage (candidates table per fact).
- Negative: More complex scoring logic.
- Negative: Need precedence rules per concept type.

**Revisit when:** Scoring logic becomes unmanageable (> 20 concepts with custom precedence rules). Consider rule engine or ML-based conflict resolution at that point.
