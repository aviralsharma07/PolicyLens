# Session: DSE-024 Phase E3C1 Gold Heading Reproducibility Audit

Date: 2026-06-04
Task ID: DSE-024
Project: doc-structure-engine
Branch: feat/dse-020-full-corpus-scale-triage
AI executor: Codex
Human reviewer: Avi

## Goal

Explain why regenerated 20-policy gold heading eval is 17/20 while older DSE-024 artifacts reported 20/20, before making parser changes.

## Relevant Docs Read
- `docs/tasks.md`
- `data/reports/dse024_heading_miss_safe_candidates_v1.md`
- `runs/sessions/2026-06-04-dse024-phase-e3b-heading-miss-inspection.md`

## Files Changed
- `data/reports/dse024_gold_heading_reproducibility_audit_v1.md`
- `runs/sessions/2026-06-04-dse024-phase-e3c1-gold-heading-repro.md`

## Commands Run

```bash
rg -n "aditya_birla_activ_care|care_health_care_plus|tata_aig_arogya_sanjeevani|20/20 PASS|heading-scorer" runs/evals data/reports runs/sessions docs -g '*.json' -g '*.md'

.venv/bin/python - <<'PY'
# Compared old passing heading eval artifacts with regenerated E3B recovery baseline.
PY

.venv/bin/python - <<'PY'
# Inspected current candidate scores, labels, and feature contributions
# for the three failing policies.
PY
```

## Results

- `aditya_birla_activ_care`: `needs_parser_fix`; real headings are same-font structural headings below threshold/fallback floor.
- `care_health_care_plus`: `gold_label_incompatibility`; current labels all match, but 8 additional compact numbered visual headings are not labeled.
- `tata_aig_arogya_sanjeevani`: `needs_parser_fix`; true section/dictionary headings score below fallback floor while definition-list items are promoted.

## Generated Artifacts
- `data/reports/dse024_gold_heading_reproducibility_audit_v1.md`

## Issues / Limitations
- This packet made no parser behavior changes.
- E3C must restore Aditya/Tata-style structural heading handling and document Care as an eval-label gap unless gold labels are updated in a separate task.

## Next Step

Implement narrow E3C parser fixes for section-alpha, section-number, roman/part, parenthesized letter, and safe short numbered headings. Keep global threshold unchanged and keep fallback zero-heading-only.
