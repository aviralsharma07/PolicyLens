# Changelog

## 2026-05-29

### Added
- `identity/` package with insurer normalizer, plan name normalizer, and UIN matcher orchestrator
- `scripts/uin_match_report.py` — DSE-002 CLI runner
- `data/manifests/uin_match_report_v1.json` — full 647-entry UIN match report
- `data/manifests/unmatched_triage_report_v1.csv` — triage CSV for entries needing review
- `data/manifests/uin_match_summary_v1.json` — summary statistics
- docs/evaluation.md — UIN Match eval layer with hard gates
- Initial project scaffold: IMPLEMENTATION_PLAN.md v2, docs/ directory
- docs/evaluation.md — 7 eval layers with hard gates
- docs/database_strategy.md — SQLite → JSON → Supabase phases
- docs/export_contract.md — Product A → Product B JSON contract
- docs/decisions.md — ADR index
- docs/development_protocol.md — Development workflow
- docs/ai_execution_protocol.md — AI agent guidelines
- docs/architecture.md — Pipeline and layered design overview
- docs/glossary.md — Domain and technical terms
- docs/data_contracts.md — Module-to-module schema contracts
- docs/risk_register.md — 18 identified risks
- docs/adr/0001-use-sqlite-for-engine.md — ADR: SQLite over Supabase for engine
- docs/adr/0002-clauses-before-fields.md — ADR: Clause-store architecture
- runs/sessions/ directory — Session logging
- runs/evals/ directory — Eval result tracking
- runs/experiments/ directory — Experiment tracking
- `scripts/corpus_lockdown.py` — main corpus lockdown script
- `data/manifests/active_policy_wordings_v1.json` — 647 active policy wordings with SHA-256 hashes
- `data/manifests/excluded_documents_v1.json` — 281 excluded documents with reasons
- `data/manifests/status_unset_review_v1.csv` — 139 policy wordings for manual triage

### Changed
- docs/tasks.md — DSE-002 marked done with actual results (verified 646/647, 100% verified+special)

### Fixed
- None

### Removed
- None

### Known Issues
- ADR files did not follow AGENTS.md bold-field format (fixed same day)
- Run log templates did not match AGENTS.md required fields (fixed same day)

## 2026-05-28

### Added
- None

### Changed
- Approaches A-E experiments completed (see our_experience.md)
- notes3.md + notes4.md: Friend's architectural analysis received
- notes5.md + notes6.md: Friend's detailed review and corrections
- Decision to split Product A and Product B made
- 909 PDFs analyzed, 647 active policy wordings identified
- 1,099 UIN lifecycle records obtained from IRDAI
- 18 table schema designed with notes5 + notes6 corrections

### Fixed
- None

### Removed
- None

### Known Issues
- None
