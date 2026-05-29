# Changelog

## 2026-05-29

### Added
- `gold_corpus/` — DSE-003 gold corpus with 5 policies, 25 annotation JSON files, schemas, and annotation guide
- `gold_corpus/docling_markdown/` — generated no-OCR IBM Docling markdown for Star Medi Classic Accident Care and Care Plus
- `data/reports/gold_corpus_manual_review_11_facts_v1.md` — source-PDF-only reviewer report for the 11 facts that were still marked `requires_manual_review`
- `scripts/validate_gold_corpus.py` — strict validator for gold policy folders, schemas, page references, fact statuses, and evidence coverage
- `tests/test_gold_corpus_validator.py` — pytest coverage for the gold corpus validator
- `runs/evals/2026-05-29-gold-corpus-v1.json` — Gold Corpus eval result
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
- docs/tasks.md — DSE-003 marked done with gold corpus outputs and validation results
- docs/evaluation.md — added active Gold Corpus eval layer and DSE-003 result
- docs/open_questions.md — OQ-005 answered: first 5 annotations use CLI/manual JSON workflow
- README.md — current phase updated to Gold Corpus complete, Physical Parser next
- Gold corpus annotations — second pass cross-checked available IBM Docling markdown and enriched table summaries
- Gold corpus facts — third pass downgraded weak schedule-dependent labels to `requires_manual_review` for precision
- Gold corpus validator — now requires readable Docling markdown for every gold policy and rejects embedded image/base64 markdown for generated artifacts
- Star/Care annotations — fourth pass re-ran structure, table, and fact provenance checks against generated Docling markdown
- Gold corpus manual review — applied source-backed resolutions for all 11 `requires_manual_review` facts
- Gold corpus facts — final status distribution is now 77 `present`, 3 `explicitly_not_covered`, 2 `not_applicable`, 18 `not_found`, and 0 `requires_manual_review`
- Gold corpus validator/tests — now fail if any DSE-003 gold fact remains `requires_manual_review`
- Gold corpus validator — validates optional `additional_evidence` page/text entries for multi-page fact support
- `.gitignore` — allowed Markdown files under `data/reports/` so intentional review reports can be tracked
- docs/tasks.md — DSE-002 marked done with actual results (verified 646/647, 100% verified+special)

### Fixed
- docs/glossary.md — fact status count corrected from 8-value to 7-value enum

### Removed
- None

### Known Issues
- Gold v1 annotations have null bbox and table cell coordinates until DSE-004/DSE-009 generate physical/table parser outputs
- Gold v1 annotations have 18 `not_found` facts; Product B must still avoid displaying these as "not covered"
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
