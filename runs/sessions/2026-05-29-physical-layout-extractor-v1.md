# Session: DSE-004 Physical Layout Extractor v1

Date: 2026-05-29
Task ID: DSE-004
Project: doc-structure-engine
Branch: feat/physical-layout-extractor-v1
AI executor: opencode
Human reviewer: Avi

## Goal
Build Phase 1 physical parsing: extract page/block/line/span layout from PDFs using pdfplumber (no OCR/vision). Produce `document_physical.json` + debug HTML per page. Tag header/footer candidates without deleting text. Validate against 5 gold PDFs (218 pages).

## Relevant Docs Read
- docs/tasks.md (DSE-004 criteria)
- docs/evaluation.md (Physical Parser eval layer)
- docs/data_contracts.md (Contract 3 schema)
- docs/changelog.md (existing entries)
- IMPLEMENTATION_PLAN.md (architecture context)
- AGENTS.md (documentation format rules)
- DSE-004 plan from conversation summary

## Files Created
- `pdf_parser/__init__.py` — package init
- `pdf_parser/models.py` — Pydantic models: PhysicalDocument, Page, Block, Line, Span, ParserIssue, BlockType, Region
- `pdf_parser/layout_extractor.py` — core extraction pipeline + CLI (single PDF + gold corpus batch mode)
- `pdf_parser/header_footer_detector.py` — region classification (top/body/bottom) + repeated-line frequency tagging, no deletion
- `pdf_parser/debug_html_generator.py` — per-page text-block overlay HTML with positioned divs
- `scripts/validate_physical_outputs.py` — schema validation, bbox bounds, page count, font metadata, debug HTML presence, span references
- `scripts/run_physical_eval.py` — hard gate metrics + reported-only evidence coverage with DSE-010 deferral
- `tests/test_layout_extractor.py` — 14 unit tests + 2 integration tests (bbox, stable IDs, header/footer, span integrity, gold PDF roundtrip)
- `docs/adr/0011-use-pdfplumber-for-physical-parsing.md` — ADR: pdfplumber over OCR/vision

## Review Fixes Applied (post-initial build)
1. **Span ID linkage fixed**: `char_index` was always 0, causing 617k broken line→span refs. Changed to `enumerate(chars)` with `ch_idx + 1`.
2. **Hardcoded path removed**: Replaced Avi's absolute path with `pathlib.Path(__file__).resolve().parent.parent.parent / "policy_data"`.
3. **Span integrity gate added**: 100% integrity required in `gates_passed`. Evidence coverage is `reported_only`, hard gate deferred to DSE-010.
4. **Tests strengthened**: Replaced vacuous bbox test with proper assertion; added span integrity tests (resolve + dangling); added 2 gold PDF integration tests (Star, HDFC).

## Commands Run
```bash
.venv/bin/python -m pytest tests/ -v
.venv/bin/python -m pdf_parser.layout_extractor --gold-corpus gold_corpus --output-root data/interim/physical --debug-root data/reports/physical_debug
PYTHONPATH=. .venv/bin/python scripts/validate_physical_outputs.py --gold-corpus gold_corpus --physical-root data/interim/physical --debug-root data/reports/physical_debug
PYTHONPATH=. .venv/bin/python scripts/run_physical_eval.py --gold-corpus gold_corpus --physical-root data/interim/physical --debug-root data/reports/physical_debug --output runs/evals/2026-05-29-physical-parser-v1.json
```

## Results
- 5/5 gold PDFs processed (218 pages)
- 5/5 file hashes match gold metadata
- 5/5 page counts match gold metadata
- Text coverage: 100% all policies
- Font metadata: 100% all policies
- Catastrophic failures: 0
- Debug HTML: 218/218 pages
- Span referential integrity: 100.0% all policies (617,060/617,060 refs valid)
- Tests: 21/21 passed
- Gold corpus validator: passed

## Generated Artifacts
- `data/interim/physical/{slug}/document_physical.json` — 5 files (38-80MB each)
- `data/interim/physical/{slug}/issues.json` — 5 files
- `data/reports/physical_debug/{slug}/page_*.html` — 218 files
- `runs/evals/2026-05-29-physical-parser-v1.json` — eval result
- `data/interim/physical/gold_run_summary.json` — run summary

## Decisions Made
- **pdfplumber primary parser**: Confirmed no OCR needed. Per-policy extraction in 2-8 seconds.
- **Multi-column block**: All lines on a page grouped into one block. Acceptable for Phase 1; DSE-005 heading scoring will need better grouping.
- **Evidence coverage deferred to DSE-010**: Physical layer produces raw spans, not clause text. Evidence matching is a semantic/source-span concern.
- **Single block per page**: Acceptable for Phase 1. DSE-005 will provide better line grouping via heading detection.

## Issues / Limitations
- Single block per page groups multi-column text together. DSE-005 heading scorer should break pages into logical blocks.
- Evidence coverage low (10.5-75%) across policies due to abstraction layer mismatch. Gate deferred to DSE-010.
- Debug HTML is text-block-outline only — no images, no exact page replica, no font rendering.
- pdfplumber may have edge cases with highly compressed/encrypted PDFs (handled via error logging).

## Next Step
DSE-005: Heading Candidate Scorer.
