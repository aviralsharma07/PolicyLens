# AI Execution Protocol

This document defines how AI agents (including the current session) should operate within this project.

## Required Reading

When starting a new session, the AI must read in order:

1. `docs/development_protocol.md` — workflow, branching, definitions of done
2. `docs/architecture.md` — pipeline overview, layered design
3. `docs/evaluation.md` — active eval gates and metrics (check which layer you're working on)
4. `docs/decisions.md` + `docs/adr/*` — architectural decisions made
5. `docs/data_contracts.md` — module-to-module contracts
6. Most recent `runs/sessions/*` — what happened last session
7. `docs/tasks.md` — active task list with DSE-XXX IDs

For domain-specific work, also read:
- `docs/glossary.md` — insurance terminology
- `docs/export_contract.md` — what Product B expects

---

## Before Editing

Before making any changes, state:

```text
- Goal
- Files to read
- Files likely to modify
- Tests/evals to run
- Expected outputs/artifacts
```

Do not edit until the task scope is clear. If the task involves both doc-structure-engine and insurance-agent code (forbidden), stop and ask.

---

## Allowed Scope

This AI is permitted to:

- Read all files in `doc-structure-engine/`
- Modify files in `doc-structure-engine/`
- Run bash commands for building, testing, data analysis
- Create session logs, eval reports, experiment logs
- Add new ADRs when making meaningful decisions
- Read files in `insurance-agent/docs/` and `insurance-agent/data/` for reference data
- Read `/Users/aviralsharma/Personal Projects/notes*.md` for user/friend guidance
- Read raw PDFs in `policy_data/` for analysis (read-only)
- Read `insurance-agent/` schemas for reference (do not modify)

---

## Forbidden Actions

The AI must NOT:

1. **Edit files in `insurance-agent/`** — this is Product B. Does not belong to this repo.
2. **Mutate raw PDFs** — read-only access to `policy_data/`.
3. **Delete raw data** — excluded files are logged, not deleted.
4. **Create Supabase tables for engine data** — use local SQLite (see ADR-0001).
5. **Skip eval gates** — do not proceed to the next layer before the current layer passes its hard gates.
6. **Emit facts without provenance** — every fact must have evidence text, page, clause, method, confidence.
7. **Use OCR or vision models** — the corpus is 100% text-layer. Use pdfplumber/PyMuPDF.
8. **Build LLM fallback chains** — one clean LLM interface. No multi-model orchestration.
9. **Mix document types** — brochures/circulars/non-health are excluded from extraction.
10. **Deploy to production without human review** — all exports validated against gold corpus first.
11. **Commit without session log** — every session must update `runs/sessions/`.
12. **Silently swallow exceptions** — see No Silent Failure Policy in `development_protocol.md`.
13. **Add cross-project imports** — do not import raw extraction logic into Product B or vice versa.
14. **Write files outside `doc-structure-engine/`** without explicit instruction.

---

## Required Tests / Evals

After every non-trivial change, run:

```bash
pytest tests/ --tb=short  # if tests exist
python scripts/quality_report.py --layer <affected_layer>
```

If tests cannot run because files are not implemented yet, note it in the session log.

---

## Completion Summary Format

At the end of every task, respond with:

```text
## Completion Summary

### Files Changed
- ...

### Commands Run
```bash
...
```

### Tests / Evals
- ...

### Generated Artifacts
- ...

### Docs Updated
- ...

### Known Limitations
- ...

### Next Recommended Step
- ...
```

If nothing was changed, say so clearly.

---

## When To Ask The User

Ask the user for input when:

1. **Task scope is unclear** — "should I implement A or B?"
2. **Ambiguous between projects** — "is this doc-structure-engine or insurance-agent work?"
3. **Schema change affects Product B** — "should I add this field to the export contract?"
4. **Gold corpus annotation needs domain judgment** — "is this waiting period 24 months or 36?"
5. **Manual decisions on unmatched UINs** — "this PDF can't be matched to any UIN. Should I flag it as legacy_product or ignore_for_now?"
6. **New decision that should be an ADR** — "I need to decide between options X and Y. Which way?"
7. **Before deploying to production** — confirm readiness
8. **When eval gates fail without clear fix** — "I'm stuck. Precision is 82% and I can't find a pattern."

---

## Error Handling

If an operation fails:

1. Log the error in `document_issues` (the DB table, not a file)
2. Note the issue in the session log
3. Do not silently retry — investigate root cause first
4. If the issue is a new pattern not handled by current code, decide: add to current task or create a new ticket

---

## Session Boundaries

Each AI session should:

1. Start by reading the most recent session log
2. State the goal for this session explicitly
3. Do one thing well (one layer, one module, one fix)
4. Reference the active task ID (DSE-XXX) in commits and sessions
5. End with a completed session log entry
6. List unresolved issues for the next session
