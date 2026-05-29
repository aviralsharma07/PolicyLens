## 2026-05-29 — ADR-0003: Separated Products (Engine vs Application)

**Status:** accepted

**Decision:** Split into two products with a JSON contract boundary. doc-structure-engine (Product A) owns PDF parsing, extraction, gold corpus, provenance, and outputs policy_features.json. insurance-agent (Product B) owns UI, comparisons, explanations, conversations, and consumes policy_features.json from Product A.

**Context:** The old single-codebase approach had extraction code tangled with API routes and UI state, different iteration speeds (extraction needs experimentation, UI needs stability), testing extraction required running the full app, and the Supabase schema mixed raw parsing data with user data.

**Options considered:**
1. Single repo with modules
2. Monorepo with clear boundaries
3. Two products with JSON contract (chosen)

**Reasoning:** Separation ensures each product iterates at its own speed, extraction work doesn't require running the app, raw engine data stays out of the app database, and the JSON contract forces clean API design. Previous experience showed extraction code leaking into API routes.

**Consequences:**
- Positive: Independent iteration speeds.
- Positive: Extraction testing without running the app.
- Positive: Raw engine data stays separate from user data.
- Positive: Either product can be replaced independently.
- Positive: JSON contract forces clean API design.
- Negative: Two repos to manage.
- Negative: Contract changes require coordinated updates.
- Negative: Domain model overlap (insurer, plan names appear in both).

**Revisit when:** JSON contract becomes a bottleneck and both products stabilize. Consider monorepo consolidation at that point.
