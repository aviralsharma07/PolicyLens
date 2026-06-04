# Session: DSE-024 Phase E3A — Classify Remaining 58 Zero-Clause Policies

Date: 2026-06-04
Task ID: DSE-024
Project: doc-structure-engine
Branch: feat/dse-020-full-corpus-scale-triage
AI executor: opencode + deepseek-v4-flash-free
Human reviewer: Avi

## Goal

Produce a fresh classification of the 58 remaining zero-clause policies after Phase E2 section tree rebuild. No stale E1 counts. Clearly separate "fix parser" from "filter/defer corpus item".

## Inputs

- `data/reports/dse020_scale_triage_report_v1.json` — post-E2 triage (58 zero-clause)
- `data/manifests/dse020_run_manifest_v1.json` — policy metadata
- `data/interim/dse020/logical/{slug}/heading_candidates.json` — per-policy heading data
- `data/interim/dse020/logical/{slug}/section_tree.json` — per-policy section data
- `data/interim/dse020/physical/{slug}/document_physical.json` — physical extraction data

## Classification Categories

| Bucket | Description |
|---|---|
| `heading_miss` | Plausible near-miss headings (max_score > 0.3 or multiple > 0.25) |
| `physical_text_issue` | Very low/negative max_score — pdfplumber extraction quality issue |
| `duplicate_or_superseded` | Same file hash as another manifest entry |
| `non_policy_or_rider` | Document type is brochure/prospectus, or slug keyword match |
| `unsupported_format` | Very short document (≤6 pages) or very few candidates (<20) |
| `manual_review_required` | Unclear without human PDF inspection |

## Files Created

- `scripts/dse024_classify_residual58.py` — classification script
- `data/reports/dse024_residual58_classification_v1.json` — JSON report
- `data/reports/dse024_residual58_classification_v1.md` — Markdown report
- `runs/sessions/2026-06-04-dse024-phase-e3a-residual58-classification.md` — this file

## Results

| Classification | Count | Action |
|---|---|---|
| heading_miss | 33 | Parser fix needed — add format-specific heading patterns |
| duplicate_or_superseded | 8 | Corpus filter — deduplicate by file hash |
| physical_text_issue | 8 | Parser fix needed — investigate pdfplumber extraction |
| non_policy_or_rider | 4 | Corpus filter — exclude from extraction pipeline |
| unsupported_format | 3 | Corpus filter — document-level filtering |
| manual_review_required | 2 | Manual review needed |
| **Total** | **58** | |
| section_tree_fail | 0 | (Confirmed resolved by E2) |

### Breakdown

- **Fix parser:** 41 (33 heading_miss + 8 physical_text_issue)
- **Filter/defer corpus:** 15 (8 duplicate + 4 non_policy + 3 unsupported)
- **Manual review:** 2

### Top heading_miss candidates

| # | Insurer | Max Score | >0.3 | Top Candidate |
|---|---|---|---|---|
| 1 | SBI_General | 0.4957 | 24 | "1" |
| 2 | Future_Generali | 0.4802 | 94 | "POLICY WORDINGS" |
| 3 | HDFC_ERGO | 0.4750 | 91 | "Contents" |
| 4 | IFFCO_Tokio | 0.4310 | 9 | "4) Body Mass Index (BMI);" |
| 5 | Star_Health | 0.4233 | 19 | "4    80%" |

### physical_text_issue
8 policies: Aditya Birla (5), Kotak Mahindra (3) — all with max_score ≤ 0 (negative or zero), indicating garbled pdfplumber extraction.

## Commands Run

```bash
PYTHONPATH=. .venv/bin/python scripts/dse024_classify_residual58.py
PYTHONPATH=. .venv/bin/python -m pytest tests/test_dse020_manifest.py tests/test_heading_scorer.py --tb=short
git diff --check
git status --short
```

## Decisions

- No `section_tree_fail` bucket populated (0 occurrences) — confirms E2 rebuild resolved all 44.
- `physical_text_issue` separated from `heading_miss` — policies with max_score ≤ 0 cannot be fixed by heading scorer changes; they need extraction-layer investigation.
- E1 counts are NOT carried forward — this report is self-contained for the 58 post-E2 policies.

## Next Step

Tackle 33 heading_miss policies with format-specific heading pattern additions, or investigate 8 physical_text_issue policies for pdfplumber extraction quality.
