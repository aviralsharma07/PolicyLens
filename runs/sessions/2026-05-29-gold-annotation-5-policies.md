# Session: Gold Annotation of 5 Policies

Date: 2026-05-29
Task ID: DSE-003
Project: doc-structure-engine
Branch: gold/annotate-5-policies
AI executor: Codex + GPT-5
Human reviewer: Avi

## Goal

Create a validated 5-policy gold corpus with section, clause, table, and fact annotations for downstream parser and extractor evals.

## Relevant Docs Read

- AGENTS.md
- .gitignore
- IMPLEMENTATION_PLAN.md
- docs/tasks.md
- docs/evaluation.md
- docs/data_contracts.md
- docs/open_questions.md
- runs/sessions/2026-05-29-uin-matcher-v1.md

## Files Changed

- gold_corpus/annotation_guide.md
- gold_corpus/schemas/*.schema.json
- gold_corpus/docling_markdown/*.md
- gold_corpus/policies/*/metadata.json
- gold_corpus/policies/*/sections.json
- gold_corpus/policies/*/clauses.json
- gold_corpus/policies/*/tables.json
- gold_corpus/policies/*/facts.json
- scripts/validate_gold_corpus.py
- tests/test_gold_corpus_validator.py
- docs/tasks.md
- docs/evaluation.md
- docs/changelog.md
- docs/open_questions.md
- docs/glossary.md
- README.md
- .gitignore
- data/reports/gold_corpus_manual_review_11_facts_v1.md
- runs/evals/2026-05-29-gold-corpus-v1.json
- runs/sessions/2026-05-29-gold-annotation-5-policies.md

## Commands Run

```bash
git checkout -b gold/annotate-5-policies
python3 scripts/validate_gold_corpus.py
pytest tests/ --tb=short
python3 -m pip install --target /private/tmp/dse003_pytest pytest
PYTHONPATH=/private/tmp/dse003_pytest:. python3 -m pytest tests/ --tb=short
/Users/aviralsharma/Personal\ Projects/insurance-agent/.venv/bin/docling --from pdf --to md --no-ocr --tables --image-export-mode placeholder --output gold_corpus/docling_markdown '/Users/aviralsharma/Personal Projects/policy_data/02_Star_Health/Star_Health_Medi_Classic_Accident_Care_Individual_Insurance_Policy.pdf' '/Users/aviralsharma/Personal Projects/policy_data/03_Care_Health/Care_Health_Care_Plus.pdf'
python3 scripts/validate_gold_corpus.py
pdftotext -layout <source-pdf> -
git status --short
python3 scripts/validate_gold_corpus.py
PYTHONPATH=/private/tmp/dse003_pytest:. python3 -m pytest tests/ --tb=short
```

## Results

- Policies: 5
- Policy JSON files: 25
- Sections: 445
- Clauses: 453
- Table regions: 26
- Facts: 100
- Initial pass fact statuses: 74 present, 3 explicitly_not_covered, 1 not_applicable, 18 not_found, 4 requires_manual_review
- Validator passed.
- `pytest tests/ --tb=short` could not run because `pytest` was not installed on PATH.
- Temporary pytest install under `/private/tmp/dse003_pytest` succeeded after network approval.
- `PYTHONPATH=/private/tmp/dse003_pytest:. python3 -m pytest tests/ --tb=short` passed: 1 test.
- Pass 2 used available IBM Docling markdown for New India, HDFC, and ICICI.
- Pass 2 enriched table summaries and added Docling cross-check metadata.
- Pass 3 re-reviewed facts with precision-first rules and downgraded weak schedule-dependent labels.
- Final fact statuses after pass 3: 67 present, 3 explicitly_not_covered, 1 not_applicable, 18 not_found, 11 requires_manual_review.
- Pass 4 generated missing IBM Docling markdown for Star and Care using `--no-ocr`, `--tables`, and `--image-export-mode placeholder`.
- Pass 4 re-ran structure, table, and fact provenance cross-checks for Star and Care. Star matched 75/91 annotated sections against generated markdown; Care matched 89/91.
- Validator now requires readable Docling markdown for every gold policy and rejects embedded image/base64 markdown in generated artifacts.
- Manual review report created for all 11 `requires_manual_review` facts using only source-PDF evidence. The report proposes promoting 10 facts to `present` and changing ICICI `room_rent_limit` to `not_applicable`, pending Avi approval.
- Annotation JSON was intentionally not changed during the report-only review pass.
- `.gitignore` now allows Markdown files under `data/reports/` so intentional review reports are visible in branch review.
- Pass 5 applied the approved manual review report to the gold annotations: 10 facts moved to `present`, ICICI `room_rent_limit` moved to `not_applicable`, and Star claim intimation was replaced with scoped timelines.
- Final fact statuses after pass 5: 77 present, 3 explicitly_not_covered, 2 not_applicable, 18 not_found, 0 requires_manual_review.

## Generated Artifacts

- gold_corpus/
- gold_corpus/docling_markdown/Star_Health_Medi_Classic_Accident_Care_Individual_Insurance_Policy.md
- gold_corpus/docling_markdown/Care_Health_Care_Plus.md
- data/reports/gold_corpus_manual_review_11_facts_v1.md
- runs/evals/2026-05-29-gold-corpus-v1.json

## Decisions Made

- Replaced Star POS Accident Care with Star Medi Classic Accident Care because the POS file is in `status_unset_review_v1.csv`, not the active DSE corpus.
- Used Care Health Care Plus instead of Care Health Care because Care Plus is active, verified, long/complex, and has no duplicate flag.
- Resolved OQ-005 with manual JSON annotation plus validator for the first 5 policies.

## Issues / Limitations

- Physical bboxes and table cell coordinates are null because DSE-004 and DSE-009 do not exist yet.
- Eighteen facts remain `not_found`; downstream evals and Product B export must not treat those as `explicitly_not_covered`.
- Docling markdown is a secondary review artifact; pypdf text-layer annotations remain the authoritative gold labels until Avi review.
- Annotations are text-layer gold v1 labels and should be reviewed by Avi before being treated as final human labels.

## Next Step

DSE-004: Physical Layout Extractor v1 using the 5-policy gold corpus as the parser eval target.
