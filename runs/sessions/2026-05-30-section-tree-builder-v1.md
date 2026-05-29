# Session: Section Tree Builder v1

Date: 2026-05-30
Task ID: DSE-006
Project: doc-structure-engine
Branch: feat/section-tree-builder-v1
AI executor: Codex + GPT-5
Human reviewer: Avi

## Goal
Build hierarchical section trees and clause boundaries from DSE-005 heading candidates and DSE-004 physical layout for the 5-policy gold corpus.

## Relevant Docs Read
- AGENTS.md
- IMPLEMENTATION_PLAN.md
- docs/evaluation.md
- docs/data_contracts.md
- docs/tasks.md
- docs/adr/0012-section-tree-builder.md

## Files Changed
- structure_parser/section_tree.py
- structure_parser/clause_segmenter.py
- scripts/run_section_tree.py
- scripts/eval_section_tree.py
- tests/test_section_tree.py
- docs/tasks.md
- docs/evaluation.md
- docs/data_contracts.md
- docs/changelog.md
- docs/decisions.md
- docs/adr/0012-section-tree-builder.md
- runs/evals/2026-05-30-section-tree-v3.json
- data/interim/logical/*/section_tree.json
- data/interim/logical/section_tree_run_summary.json

## Commands Run
```bash
PYTHONPATH=/private/tmp/dse004_deps:. python3 -m pytest tests/test_section_tree.py --tb=short
PYTHONPATH=/private/tmp/dse004_deps:. python3 scripts/run_section_tree.py --physical-root data/interim/physical --heading-root data/interim/logical --output-root data/interim/logical
PYTHONPATH=/private/tmp/dse004_deps:. python3 scripts/eval_section_tree.py --output-root data/interim/logical --gold-corpus gold_corpus --output runs/evals/2026-05-30-section-tree-v3.json
```

## Results
- Focused tests passed: 37/37.
- Section tree eval passed: 5/5 gold policies.
- Final per-policy section F1: Care 97.75%, HDFC 97.44%, ICICI 92.47%, New India 100.00%, Star 90.51%.

## Generated Artifacts
- data/interim/logical/care_health_care_plus/section_tree.json
- data/interim/logical/hdfc_arogya_sanjeevani/section_tree.json
- data/interim/logical/icici_family_shield/section_tree.json
- data/interim/logical/new_india_floater/section_tree.json
- data/interim/logical/star_medi_classic_accident/section_tree.json
- data/interim/logical/section_tree_run_summary.json
- runs/evals/2026-05-30-section-tree-v3.json

## Decisions Made
- Use iterative compact-numbered synthetic detection for `2.1.1Accident`-style policy lines.
- Treat top-region numbered lines as body when they parse as policy numbering.
- Use deterministic section and clause IDs.
- Keep clause boundary F1 as a section-aligned proxy until gold clauses carry line/span IDs.
- Avoid precision-penalizing predicted numeric sections outside the current partial gold labels.

## Issues / Limitations
- Gold clause files do not yet have physical line IDs, so DSE-006 cannot compute true line-overlap clause F1.
- Some policies have partial section labels; strict extra-section precision should be revisited during DSE-012.

## Next Step
DSE-007 can consume `section_tree.json` to build the first deterministic extractors.
