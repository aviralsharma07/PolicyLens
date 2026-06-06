# Development Protocol

## Development Loop

```
1. Identify the layer to work on
   ↓
2. Define eval gates and success criteria (update docs/evaluation.md if needed)
   ↓
3. Write tests that match the eval gates
   ↓
4. Implement the module
   ↓
5. Run tests against gold corpus
   ↓
6. Pass/fail? If fail → iterate steps 4-5
   ↓
7. Update gold corpus if new patterns discovered
   ↓
8. Update run log (runs/sessions/)
   ↓
9. Commit
```

---

## Branch Naming

```
main                  — Stable, production-ready
  ├── feature/*       — New modules or extractors (e.g. feat/corpus-lockdown)
  ├── fix/*           — Bug fixes (e.g. fix/ped-regex-false-positive)
  ├── gold/*          — Gold annotation updates (e.g. gold/annotate-star-health)
  └── experiment/*    — Short-lived experiments (run, eval, delete)
```

Feature branches merge to main only when:
- All eval gates for that layer pass
- No regressions on existing gold corpus
- Relevant docs updated
- Session log written

---

## Commit Message Format

Use conventional commits with task IDs:

```text
feat(identity): implement corpus lockdown filter

- Filter 909 PDFs to 647 active policy wordings
- Generate file_hash, document_type, insurer, source, match_status per file
- Excluded docs triage with reasons

Closes DSE-001
```

Allowed prefixes: `feat`, `fix`, `test`, `eval`, `docs`, `refactor`, `chore`.

---

## Definition of Done

Before marking any task complete, verify:

```text
- Code implemented
- Relevant tests added/updated
- Relevant evals run
- Eval gates pass (no regression on gold corpus)
- Output artifact generated if applicable
- Session log updated
- Changelog updated
- Known limitations documented
```

---

## Review Checklist

Apply to every AI-generated change:

```text
- Did it edit only allowed files?
- Did it avoid cross-project changes? (never touch insurance-agent/)
- Did it add tests or explain why not?
- Did it run relevant commands?
- Did it update session logs?
- Did it update changelog?
- Did it update decisions if a decision changed?
- Did it avoid silent exceptions?
- Did it avoid hardcoded absolute paths?
- Did it avoid mutating raw data?
- Did it produce the expected artifacts?
- Did it document known limitations?
```

---

## No Silent Failure Policy

Never swallow exceptions silently.

```python
# FORBIDDEN
try:
    extract_value(clause)
except:
    pass

# REQUIRED
try:
    extract_value(clause)
except Exception as e:
    logger.exception("Failed to extract value", extra={"clause_id": clause.id})
    record_issue(clause.document_id, issue_type="extraction_failed", description=str(e))
```

If continuing after a failure, the failure must be recorded in `document_issues`, a report, or a session log.

---

## Data Safety Policy

1. **Never mutate raw PDFs.** Scripts may read them, never write.
2. **Never delete raw data.** If a file is excluded, record the exclusion reason. Do not delete.
3. **Never rename raw data unless explicitly instructed.**
4. **Every input PDF should be tracked by SHA-256 hash.** This enables dedup and version tracking.
5. **Every skipped file needs a reason.** The exclusion report must explain why.
6. **Every unmatched UIN needs a triage row.** Manual decisions are logged.
7. **Every parse failure needs a recorded issue.** `document_issues` table captures these.
8. **Every exported null field needs a fact_status.** No silent empties.

---

## Testing Rules

Run relevant tests after every implementation task.

Preferred commands:

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py data/manifests/product_source_bundles_v1.draft.json
```

If a command fails, report:
- command run
- error summary
- likely cause
- whether it blocks completion

If tests cannot be run because files/scripts are not implemented yet, say so clearly in the session log.

---

## Session Logging

Every coding session creates or updates a markdown log in `runs/sessions/YYYY-MM-DD-description.md`.

Required template:

```markdown
# Session: YYYY-MM-DD — <title>

Date: YYYY-MM-DD
Task ID: DSE-XXX
Project: doc-structure-engine
Branch: <branch>
AI executor: opencode + <model>
Human reviewer: Avi

## Goal
...

## Relevant Docs Read
- ...

## Files Changed
- ...

## Commands Run
```bash
...
```

## Results
...

## Generated Artifacts
- ...

## Decisions Made
- ...

## Issues / Limitations
- ...

## Next Step
...
```
