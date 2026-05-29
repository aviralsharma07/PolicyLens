# Session: DSE-002 UIN Matcher v1

Date: 2026-05-29
Task ID: DSE-002
Project: doc-structure-engine
Branch: feat/uin-matcher-v1
AI executor: opencode
Human reviewer: Avi

## Goal
Verify UIN-insurer-plan assignments for all 647 active policy wordings against uin_lifecycle.json (1,099 records). Produce match report with confidence scoring and triage CSV.

## Relevant Docs Read
- docs/tasks.md (DSE-002 criteria)
- docs/evaluation.md (existing eval layers)
- docs/changelog.md (existing entries)
- IMPLEMENTATION_PLAN.md (architecture context)
- AGENTS.md (documentation format rules)

## Data Explored
- `active_policy_wordings_v1.json`: 647 entries, 23 unique folder insurers, 506 unique UINs
- `uin_lifecycle.json`: 1,082 UIN bases across 32 insurers
- Discovered: 0 UINs missing from lifecycle, only 1 mismatch (non_policy_wordings brochure → Niva Bupa)

## Files Created
- `identity/__init__.py` — package init
- `identity/insurer_normalizer.py` — 23 folder→lifecycle mappings, normalize/reverse/validate functions, insurer abbreviation map for filename prefix stripping
- `identity/plan_name_normalizer.py` — filename plan extraction, plan name normalization, fuzzy scoring via difflib.SequenceMatcher
- `identity/uin_matcher.py` — orchestrator: extract uin_base, lookup lifecycle, match insurer, fuzzy-match plan name, assign 3-tier confidence (high/medium/low), write report + triage CSV
- `scripts/uin_match_report.py` — CLI entry point

## Commands Run
```bash
python3 scripts/uin_match_report.py
```

## Results
- Verified: 646 (99.8%)
- High confidence: 584 (insurer + plan name match)
- Medium confidence: 62 (insurer match, plan name fuzzy)
- Conflict: 0
- Special case: 1 (NivaBupa brochure in _non_policy_wordings)
- Unmatched: 0
- Verified + special: 100.0% (exceeds >=95% hard gate)

## Generated Artifacts
- `data/manifests/uin_match_report_v1.json` — full 647-entry report
- `data/manifests/unmatched_triage_report_v1.csv` — triage entries with flags
- `data/manifests/uin_match_summary_v1.json` — summary statistics

## Decisions Made
- Changed DSE-002 approach from "5-tier UIN discovery" to "UIN verification" since UINs were pre-assigned in policy_index.json
- Confidence model: high (insurer+plan≥0.5), medium (insurer match only), low (mismatch), special_case (non_policy_wordings folder)
- Plan name matching is secondary signal — insurer match is primary. Plan name scores are informative, not blocking.
- non_policy_wordings folder entry classified as special_case (not conflict) since the folder is explicitly non-standard

## Issues / Limitations
- 62 medium-confidence entries have fuzzy plan name matches (<0.5 similarity). These are mostly Care Health promotional brochures with long descriptive filenames (e.g., `care-plus-(health-insurance-product)---brochure.pdf`). The UIN insurer match is correct, but filenames don't cleanly map to lifecycle product names.
- Plan name normalizer may over-strip common words (e.g., "Policy" suffix removal might strip part of a plan name in edge cases). Not blocking since insurer match is the primary signal.

## Next Step
Proceed to DSE-003: Gold annotation of 5 policies.
