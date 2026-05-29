# Document Structure Engine

Document intelligence engine for Indian health insurance policy wordings.

Product A: the data/context engineering layer behind the insurance assistant. Converts text-layer PDF policy wordings into structured, evidence-backed facts.

## Core Philosophy

- Clauses are source truth. Fields are derived views.
- Unknown is acceptable. Wrong is fatal.
- Precision > recall.
- No extracted fact without evidence.

## Current Phase

Gold Corpus v1 complete. Next: Phase 1 Physical Layout Extractor.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Tracked vs Ignored

Tracked:

- `data/manifests/*.json` — stable corpus manifests
- `data/reports/*.md` — intentional human-review reports
- `runs/sessions/*.md` — session logs
- `runs/experiments/*.md` — experiment records
- `runs/evals/*.json` — eval summaries

Ignored:

- Raw PDFs, SQLite DBs, debug HTML, interim parser JSON, processed outputs, large reports

## Product Boundary

This project exports compiled, evidence-backed policy features. Product B (`insurance-agent`) consumes those exports.
