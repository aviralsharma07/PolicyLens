"""
clause_store — DSE-010: Clause Store + Source Spans

Persistence and provenance layer for the document structure engine.
Bridges clause → lines → bbox coordinates (source_spans).
Replaces provisional evidence IDs with real span references.

Key modules:
  schema.sql      — SQLite DDL (19 tables; 15 populated, 4 deferred)
  models.py       — Python dataclasses for SQLite row types
  repository.py   — init_db(), insert_*, query_*, backfill_*
  span_builder.py — clause spans, fact evidence spans, table cell spans
  fact_resolver.py — provisional → real evidence ID resolution
"""
