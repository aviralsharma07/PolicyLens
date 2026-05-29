## 2026-05-29 — ADR-0001: Use SQLite for Engine Storage (Not Supabase)

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
