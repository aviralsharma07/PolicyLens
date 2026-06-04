# Session: DSE-024 Phase C QA Cleanup

Date: 2026-06-04
Task ID: DSE-024
Project: doc-structure-engine
Branch: feat/dse-024-parser-remediation
AI executor: opencode + deepseek-v4-flash-free
Human reviewer: Avi

## Goal

Resolve report/eval inconsistencies from Phase C without implementing new parser fixes or running DSE-020 full pipeline.

## Bugs Found & Fixed

### 1. FP Risk key name mismatch in `write_md_report()`

**Location:** `scripts/dse024_threshold_experiment.py`, FP risk section (~line 496)

**Root cause:** The FP risk assessment section called `_s(t, "toc_risk")` and `_s(t, "list_item_risk")`, but the summary dict stores these as `total_toc_risk` and `total_list_item_risk`. The wrong keys silently returned 0, causing the report to display "0 TOC candidates (0.0%), 0 list/item candidates (0.0%)" even though the classification table showed 31 `numbered_item` candidates and the summary table showed TOC Risk=50, List/Item Risk=33.

**Fix:** Changed `_s(t, "toc_risk")` to `_s(t, "total_toc_risk")` and `_s(t, "list_item_risk")` to `_s(t, "total_list_item_risk")`.

### 2. Hardcoded str key `"0.50"` mismatch with JSON key `"0.5"`

**Location:** `scripts/dse024_threshold_experiment.py`, gold eval comparison section (~line 647)

**Root cause:** The gold eval comparison section hardcoded `results.get("0.50", ...)`, but Python's `str(0.50)` yields `"0.5"`. The JSON was written with `str(threshold)` keys, so the key is `"0.5"`. The lookup silently returned an empty dict, causing the gold eval comparison (TP/FP/FN) to be omitted from the recommendation section.

**Fix:** Changed to use `results.get(str(thresholds[-1]), ...)` and `results.get(str(thresholds[0]), ...)`.

### 3. Same hardcoded key in `current` variable assignment

**Location:** `scripts/dse024_threshold_experiment.py`, line ~624

**Root cause:** `current = s45 if str(thresholds[-1]) == "0.50" else results.get("0.50", ...)`. Both branches were wrong: the condition `str(0.50) == "0.50"` is always False (since `str(0.50) == "0.5"`), and `results.get("0.50")` doesn't match `"0.5"` key.

**Fix:** Simplified to `current = results.get(str(thresholds[-1]), {}).get("summary", {})`.

### 4. Gold heading eval used wrong candidates root

**Root cause (v3 experiment data, not a code bug):** The v3 threshold experiment was run with `--logical-root data/interim/dse020/logical/`, which has different physical extraction for some gold policies (notably `aditya_birla_activ_care` — 0 candidates at t=0.5 vs 71 in gold corpus). This caused the gold heading eval to show 15/20 PASS at t=0.5 instead of 20/20.

**Fix:** Added `--gold-logical-root` argument to the script. The experiment was re-run with `--logical-root data/interim/dse020/logical/` (for correct zero-clause analysis of 647 policies) and `--gold-logical-root data/interim/logical/` (for correct gold heading eval). The report header now clearly states both roots.

## Files Changed

- `scripts/dse024_threshold_experiment.py` — Added `--gold-logical-root` argument, fixed FP risk key names, fixed `"0.50"` → `str(thresholds[-1])` key, added logical root paths to report header and JSON output
- `data/reports/dse024_threshold_experiment_v3.json` — Regenerated with correct gold logical root and fix bugs
- `data/reports/dse024_threshold_experiment_v3.md` — Regenerated with correct data
- `runs/evals/2026-06-04-heading-scorer-dse024-phase-c-check.json` — New direct heading eval
- `runs/evals/2026-06-04-section-tree-dse024-phase-c-check.json` — New direct section tree eval

## Commands Run

```bash
# Re-run threshold experiment with both logical roots
PYTHONPATH=. .venv/bin/python scripts/dse024_threshold_experiment.py \
  --classification data/reports/dse024_zero_clause_classification_v1.json \
  --sample-inspection data/reports/dse024_zero_clause_sample_inspection_v1.json \
  --physical-root data/interim/dse020/physical \
  --logical-root data/interim/dse020/logical \
  --gold-logical-root data/interim/logical \
  --output-root data/interim/dse024 \
  --json-output data/reports/dse024_threshold_experiment_v3.json \
  --md-output data/reports/dse024_threshold_experiment_v3.md

# Direct gold heading eval
PYTHONPATH=. .venv/bin/python scripts/eval_heading_scorer.py \
  --candidates-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-04-heading-scorer-dse024-phase-c-check.json

# Direct section tree eval
PYTHONPATH=. .venv/bin/python scripts/eval_section_tree.py \
  --output-root data/interim/logical \
  --gold-corpus gold_corpus \
  --output runs/evals/2026-06-04-section-tree-dse024-phase-c-check.json

# Tests
PYTHONPATH=. .venv/bin/python -m pytest tests/test_heading_scorer.py tests/test_dse020_manifest.py --tb=short
git diff --check
git status --short
```

## Results

### Threshold Experiment v3 (corrected)
- **Gold heading eval at t=0.5: 20/20 PASS** (P=99.7%, R=96.3%, F1=98.0, 1 FP, 12 FN)
- **Gold heading eval at t=0.45: 5/20 PASS** (P=65.4%, R=96.3%, F1=77.9, 164 FP, 12 FN) — expected, lower threshold admits fewer FPs
- **FP risk now correct**: t=0.45 shows 50 TOC (26.7%) + 33 list/item (17.6%) — matches classification table
- **Both logical roots clearly documented** in report header

### Direct Gold Heading Eval: 20/20 PASS
- All 20 gold policies pass at t=0.5 with precision ≥90% and recall ≥80%

### Direct Section Tree Eval: 19/20 FAIL
- Only `oriental_cancer_protect` fails: TreeAcc=83.33%, SectionF1=100.0%, ClauseF1=100.0%
- **Not a Phase C regression**: TreeAcc=83.33% is identical across all 3 baseline checkpoints (Jun 1, Jun 2, Jun 4)
- Pre-existing baseline failure caused by section-tree-level logic, not heading scorer

### Tests: 37/37 PASS
- `test_heading_scorer.py` — 33/33 PASS
- `test_dse020_manifest.py` — 4/4 PASS
- `git diff --check` — clean (no whitespace issues)

## Generated Artifacts

- `data/reports/dse024_threshold_experiment_v3.json` — corrected experiment data (schema v2 with logical_root fields)
- `data/reports/dse024_threshold_experiment_v3.md` — corrected report with accurate gold eval and FP risk
- `runs/evals/2026-06-04-heading-scorer-dse024-phase-c-check.json` — heading scorer eval artifact
- `runs/evals/2026-06-04-section-tree-dse024-phase-c-check.json` — section tree eval artifact

## Decisions Made

- **oriental_cancer_protect section tree failure is pre-existing, not a Phase C regression** — confirmed identical TreeAcc=83.33% across three checkpoints. Does not block DSE-024 Phase D because the heading scorer changes did not cause it. Phase D may address it as a separate concern.
- **Gold heading eval for threshold experiments must use `data/interim/logical/` root**, not `data/interim/dse020/logical/`, because gold-policy physical extraction differs between DSE-020 and the gold corpus.

## Known Limitations

- oriental_cancer_protect section tree eval remains at TreeAcc=83.33% — pre-existing, unrelated to Phase C
- Section tree eval at 19/20 means DSE-024 acceptance is incomplete (per acceptance criteria)
- DSE-020 triage report not yet regenerated (Phase D)
- 56/132 zero-clause policies gain ≥1 heading at t=0.45, but FP ratio (44.4%) remains above 25% target

## Next Step

Proceed with DSE-024 Phase D: DSE-020 re-validation. Run section tree builder, regenerate triage report, and measure actual zero-clause reduction. The `oriental_cancer_protect` section tree failure is a pre-existing separate issue.
