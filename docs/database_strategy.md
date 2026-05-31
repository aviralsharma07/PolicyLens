# Database Strategy

## Current Strategy

**Local SQLite for development, JSON export for Product B, Supabase only for compiled data.**

Product A (doc-structure-engine) and Product B (insurance-agent) have different database needs:
- Product A = heavy write, schema evolves fast, raw parsing data, local-first
- Product B = read-heavy, stable schema, compiled outputs, user-facing

**Do not put raw engine tables in Supabase. Use local SQLite first.**

---

## Why This Strategy

1. **Iteration speed** — SQLite has zero configuration. No migrations, no network, no auth.
2. **Data isolation** — raw engine data (text spans, cell coordinates, candidates) is internal. Product B should never query it directly.
3. **Supabase Free Plan limits** — raw text spans and table cells can grow to millions of rows. Free Plan has database-size quotas. Official Supabase docs say Free projects include disk space but read-only mode is triggered by the database-size quota.
4. **Schema volatility** — the engine schema will change frequently during development. SQLite handles this trivially. Supabase migrations are more costly.
5. **Portability** — `engine.sqlite` is a single file. Zip it, share it, backup it. No cloud dependency during development.

---

## Local SQLite

### Storage location

```
doc-structure-engine/data/engine.sqlite
```

### Tables

All 19 tables live here in a single SQLite file:
- source_documents, document_pages, document_blocks, document_lines, document_text_spans
- document_sections, policy_clauses
- document_tables, document_table_cells
- source_spans
- extracted_fact_candidates, extracted_facts, fact_conflicts
- validation_labels
- derived_policy_features
- document_issues
- pipeline_runs
- products, product_versions

### Schema

`clause_store/schema.sql` contains DDL for all 19 tables. Run once at init.

### ID strategy

Source artifacts may use document-local IDs such as `p1l_1`, `sec_0001`, and
`clause_0001`. SQLite primary keys must be globally unique, so DSE-010 stores
namespaced IDs:

```text
{document_id}:{source_line_id}
{document_id}:{source_section_id}
{document_id}:{source_clause_id}
```

The original artifact IDs remain available in `source_line_id`,
`source_section_id`, `source_clause_id`, and `source_line_ids_json`.

### Debugging

```bash
sqlite3 data/engine.sqlite "SELECT issue_type, COUNT(*) FROM document_issues GROUP BY issue_type;"
sqlite3 data/engine.sqlite "SELECT concept, fact_status, COUNT(*) FROM extracted_facts GROUP BY concept, fact_status;"
```

---

## JSON Export

### What gets exported

After a pipeline run completes, the engine exports compiled JSON:

```
data/export/{policy_id}/
  policy_features.json       # 91-field derived view per policy
  policy_fact_sources.json   # evidence chain per fact
  policy_clauses_minimal.json # clauses without spans (lighter)
```

### Why JSON

JSON is the API boundary between Product A and Product B. It is:
- Language-agnostic (Product B can be Python, JS, or anything else)
- Self-documenting (every field has status, evidence, confidence)
- Versioned (schema version in every file)
- Git-trackable (JSON files in version control)
- Non-breaking (old versions of the contract remain valid)

---

## Supabase Integration

### What goes into Supabase

Only compiled, product-facing data goes into the **existing** insurance-agent Supabase project.

```
Product A: doc-structure-engine          Product B: insurance-agent
┌─────────────────────────────┐          ┌──────────────────────┐
│ Local SQLite                │          │ Supabase Project     │
│  (all 19 raw tables)        │ ──JSON──►│  public schema:      │
│                             │          │  policy_features     │
│ Exports:                    │          │  product_versions    │
│  policy_features.json ──────┘          │  (compiled only)     │
│  policy_fact_sources.json              │  conversations       │
│  policy_clauses_minimal.json           │  users               │
└─────────────────────────────┘          └──────────────────────┘
```

---

## What Must Not Go To Supabase Yet

The following tables must NOT be created in the insurance-agent Supabase project:

- `document_pages`, `document_blocks`, `document_lines`, `document_text_spans`
- `document_tables`, `document_table_cells`
- `source_spans`
- `extracted_fact_candidates`, `fact_conflicts`
- `document_issues`
- `validation_labels`

These contain raw engine data. They are large (millions of rows), schema-volatile, and irrelevant to Product B.

If you must test Supabase integration early, use a separate custom schema:

```sql
CREATE SCHEMA intelligence_engine;
```

Do NOT expose the raw engine schema to the frontend. Product B queries only `public.policy_features`.

---

## Migration / Revisit Criteria

Revisit this strategy when:

1. **Engine needs to run remotely** — multiple developers need access to the same engine data. Migrate to PostgreSQL (self-hosted or Supabase).
2. **Pipeline runs in CI/CD** — SQLite works in CI but shared storage becomes a problem. Move to a network-accessible DB.
3. **Engine data exceeds 10GB** — SQLite handles this but performance degrades. PostgreSQL is better at scale.
4. **Gold corpus needs multi-user annotation** — shared annotations require a DB with concurrency.
5. **Product B needs real-time extraction** — if Product B needs to trigger extraction on-demand and query results immediately, the JSON export boundary may need to become a direct DB connection.

---

## Open Questions

1. Should old pipeline runs be pruned from SQLite to save space? (OQ: create a retention policy)
2. When should we switch from "export JSON then import" to "direct DB connection" between Products A and B?
3. If we use a custom schema in Supabase, should it be in the same project or a separate project?
