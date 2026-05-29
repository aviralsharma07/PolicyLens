# Session: 2026-05-29 — Corpus Lockdown

Date: 2026-05-29
Task ID: DSE-001
Project: doc-structure-engine
Branch: feat/corpus-lockdown
AI executor: opencode
Human reviewer: Avi

## Goal

Filter 1067 indexed PDFs into three buckets (active/needs_review/excluded) with SHA-256 hashes, exclusion reasons, and triage flags. Generate the corpus manifest for Phase 0 (UIN matching) to consume.

## Relevant Docs Read

- docs/tasks.md (DSE-001 requirements)
- docs/evaluation.md (Corpus Identity eval gates)
- docs/data_contracts.md (Contract 1: Corpus Lockdown → UIN Reconciliation)
- IMPLEMENTATION_PLAN.md (Day 1: Corpus Lockdown)
- AGENTS.md (data safety, logging, no-silent-failure rules)

## Files Changed

- `scripts/corpus_lockdown.py` — created (main corpus lockdown script)
- `data/manifests/active_policy_wordings_v1.json` — created (647 entries)
- `data/manifests/excluded_documents_v1.json` — created (281 entries)
- `data/manifests/status_unset_review_v1.csv` — created (139 rows)
- `docs/tasks.md` — DSE-001: planned → done
- `docs/evaluation.md` — Corpus Identity eval: planned → active, added Result block
- `docs/changelog.md` — added corpus lockdown entries under 2026-05-29
- `runs/sessions/2026-05-29-corpus-lockdown.md` — created (this file)
- `pyproject.toml` — requires-python >=3.9 (was >=3.11, incompatible with system Python)

## Commands Run

```bash
git checkout -b feat/corpus-lockdown
python3 scripts/corpus_lockdown.py
```

## Results

- **Active**: 647 entries (629 policy wordings, 18 brochures)
  - SHA-256 hashes computed for all PDFs on disk
  - 0 missing PDFs, 0 hash failures
  - 70 entries flagged `possible_duplicate` (53 duplicate content groups)
  - 18 brochures flagged `document_type_brochure`
  - All required fields present: file_hash, document_type, corpus_status, insurer, source_domain, match_status
- **Needs Review**: 139 entries (policy wordings with no active/superseded status)
  - CSV generated with columns: document_id, filename, insurer, plan_name, source_url, uin_match, confidence, review_status, notes
- **Excluded**: 281 entries
  - 264 category_not_policy_wording, 13 policy_superseded, 4 file_corrupt
- **Invariants**: 647 + 139 + 281 = 1067 ✓, no duplicate hashes without canonical flagging ✓

## Generated Artifacts

- `data/manifests/active_policy_wordings_v1.json` — 647 active entries
- `data/manifests/excluded_documents_v1.json` — 281 excluded entries
- `data/manifests/status_unset_review_v1.csv` — 139 entries for manual triage

## Decisions Made

- **Three-bucket model**: active (647), needs_review (139), excluded (281). The 139 status_unset files are NOT excluded — they're set aside for manual review per user instruction.
- **Duplicate handling**: Non-canonical copies get `triage_flag: possible_duplicate` instead of hard-removal. The `is_canonical` field from `policy_index.json` determines which copy is primary.
- **`triage_flags` field**: Added as a per-entry array for flexible reporting (future flags: uin_ambiguous, possible_duplicate, low_confidence_match, legacy_product, etc.)
- **Output paths**: Changed from `data/*.json` (gitignored) to `data/manifests/*.json` (tracked) per gitignore configuration.
- **Python 3.9**: pyproject.toml requires-python lowered from >=3.11 to >=3.9 to match system environment.

## Issues / Limitations

- **Corpus discrepancy**: Original plan assumed 647 active policy wordings. Actual data: 629 active policy wordings + 18 active brochures = 647 active total. The plan's 647 count was correct but included brochures.
- **53 duplicate content groups**: Same PDF stored under different filenames (IRDAI copy vs website copy). 70 non-canonical entries flagged — these need dedup resolution in DSE-002.
- **139 status_unset**: These are website-sourced policy wordings never assigned active/superseded. Manual review needed.
- **No UIN matching yet**: match_status = "pending" for all active entries. DSE-002 will handle this.

## Next Step

DSE-002: UIN Matcher v1 — Match 647 active files against 1,099 UIN records from uin_lifecycle.json using 5-tier matching.
