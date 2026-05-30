# ADR-0013: Provisional Clause Evidence IDs for DSE-007

**Date:** 2026-05-30
**Status:** accepted
**Task:** DSE-007

## Context

DSE-007 extracts deterministic facts before DSE-010 builds the SQLite clause store and true source spans. The extractors still need evidence-constrained output now, and every accepted `present` fact must point to source text.

DSE-006 already provides clause IDs, page ranges, line IDs, and full clause text. Some facts are carried in section heading lines, so DSE-007 uses clause text enriched with the owning section heading during extraction.

## Decision

Use provisional evidence IDs in the form:

```text
clause:{clause_id}
```

Every accepted deterministic fact must also store:

- `evidence_clause_id`
- `evidence_line_ids`
- `evidence_page`
- `evidence_text`

The evidence text must verify as an exact normalized substring of the DSE-006 clause extraction text used by the extractor.

## Options Considered

1. Wait for DSE-010 source spans before any fact extraction.
2. Emit facts without evidence IDs until DSE-010.
3. Use provisional clause evidence IDs and replace them with true source spans in DSE-010.

## Reasoning

Option 3 keeps DSE-007 useful and testable without weakening the evidence rule. It also avoids designing the DSE-010 span store prematurely.

## Consequences

- Positive: DSE-007 can enforce evidence verification now.
- Positive: Accepted facts are auditable back to DSE-006 clauses and lines.
- Positive: DSE-010 can migrate deterministic facts from provisional clause IDs to true source spans.
- Negative: Clause IDs are coarser than true source spans.
- Negative: Heading-line evidence must be represented through the owning clause until source spans exist.

## Revisit When

DSE-010 creates `source_spans` and the local SQLite clause store.

