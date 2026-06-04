# Session: DSE-024 Phase C — Targeted Heading Scorer Fixes

Date: 2026-06-04
Task ID: DSE-024
Project: doc-structure-engine
Branch: feat/dse-024-parser-remediation
AI executor: opencode + deepseek-v4-flash-free
Human reviewer: Avi

## Goal

Implement Phase C of DSE-024: targeted heading scorer fixes based on the Phase C0 threshold experiment findings. The experiment showed that a pure threshold change is unsafe (FP ratio 54.2%), so feature-level fixes must precede any threshold reduction.

## Relevant Docs Read

- AGENTS.md (workspace rules)
- docs/tasks.md (DSE-024 detail section)
- docs/changelog.md
- data/reports/dse024_threshold_experiment_v1.md (Phase C0 findings)
- structure_parser/heading_scorer.py
- structure_parser/heading_patterns.py
- tests/test_heading_scorer.py
- scripts/eval_heading_scorer.py
- scripts/dse024_threshold_experiment.py
- scripts/run_heading_scorer.py

## Files Changed

### structure_parser/heading_patterns.py
- Added letter-numbering pattern `re.compile(r"^[A-Z]\.\s+(?!No\b|no\b)[^\t]")` to NUMBERING_PATTERNS. Matches "A. Definitions" but excludes "S. No." (serial number) and tab-containing lines.

### structure_parser/heading_scorer.py
- **TOC suppression**: Changed `has_toc_dots` weight from +0.10 to -0.30. Lines with dot leaders now penalized instead of promoted.
- **Short all-caps numbered penalty**: Added `short_all_caps_numbered` weight -0.25. Fires when line is all-caps, numbered, <30 chars, and NOT matching heading dictionary. Targets medical supply codes and procedure-code false positives.
- **Tab character penalty**: Added `has_tab_char` feature with weight -0.30. Fires on any line containing tab characters (table data leakage).
- **Reduced sentence-case penalty**: In `feature_contributions()`, lines that are bold AND numbered AND sentence-case now get -0.10 instead of -0.30. Prevents definition headings ("6. Exclusions") from being overly penalized.
- **Letter-numbering token**: Updated `_numbering_token()` regex to match `[A-Z]\.` pattern.
- **Letter-numbering level hint**: Updated `_level_hint()` to return level 1 for single-letter tokens.

### data/reports/dse024_threshold_experiment_v3.md
- Corrected and expanded post-fix experiment report with improvement comparison and accurate recommendation.

### docs/changelog.md
- Added Phase C entry documenting all 5 fixes with results.

### docs/tasks.md
- Updated DSE-024 Phase C detail with completed items.
- Updated acceptance criteria checkbox status.

## Commands Run

```bash
python -m pytest tests/test_heading_scorer.py -v        # 33/33 PASS
python -m pytest -x                                     # 393/393 PASS
python scripts/eval_heading_scorer.py --candidates-root data/interim/logical --gold-corpus gold_corpus   # 20/20 PASS
python scripts/run_heading_scorer.py --physical-root data/interim/dse020/physical --output-root data/interim/dse020/logical  # rescored 647 policies
python scripts/dse024_threshold_experiment.py ...        # threshold experiment v3
```

## Results

### Gold Heading Scorer Eval: 20/20 PASS (no regression)
All 20 gold policies pass heading scorer eval at threshold 0.5. Aditya Birla (P=98.59%, R=87.5%) and Tata AIG (P=100%, R=92%) now correctly detected thanks to letter-numbering pattern.

### Zero-Clause Policy Impact (at t=0.45)

| Metric | Pre-Fix | Post-Fix | Delta |
|--------|---------|----------|-------|
| List/Item Risk | 61 | 33 | -46% |
| TOC Risk | 55 | 50 | -9% |
| Total Accepted | 214 | 187 | -13% |
| numbered_item | 59 | 31 | -47% |
| real_heading | 136 | 134 | -1.5% |
| FP Ratio | 54.2% | 44.4% | -9.8pp |

### Full Pytest: 393/393 PASS

## Generated Artifacts

- `data/reports/dse024_threshold_experiment_v3.md` — post-fix threshold experiment report
- `data/reports/dse024_threshold_experiment_v3.json` — raw experiment data
- `data/interim/dse020/logical/heading_run_summary.json` — updated heading scorer run summary (all 647 policies rescored)

## Decisions Made

- **Keep threshold at 0.50**: FP ratio remains 44.4% at t=0.45, above the 25% target. Threshold change without further feature improvement is unsafe.
- **Tab penalty added mid-session**: The "S. No." and "O.\tBenefits\tPayment\tBasis" false positives at t=0.5 required additional filtering. Tab penalty is a general-purpose fix for table data leakage.
- **Restore gold logical root after DSE-020 overwrite**: The initial full re-score of DSE-020 logical outputs overwrote gold-policy heading_candidates.json with non-gold physical extraction versions, causing false gold eval regression. Corrected by using original `data/interim/logical/` for gold eval.

## Known Limitations

- 56/132 zero-clause policies gain ≥1 heading at t=0.45, but FP ratio (44.4%) is still high.
- Section tree builder not yet updated to handle 134 real headings at t=0.45.
- Aditya Birla and Tata AIG gold policies still show 0 headings at t=0.5 in DSE-020 pipeline (different physical extraction vs gold corpus).
- DSE-020 triage report not yet regenerated (Phase D).

## Next Step

Run Phase D: DSE-020 re-validation. Re-run section tree builder for affected policies, regenerate DSE-020 triage report, and measure actual zero-clause reduction.
