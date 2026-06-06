# Contributing

Thanks for taking interest in `doc-structure-engine`.

This repository is a document-intelligence system with a fairly opinionated workflow. Please read this file before opening a PR.

## Before you start

Read these first:

1. [README.md](./README.md)
2. [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)
3. [docs/architecture.md](./docs/architecture.md)
4. [docs/evaluation.md](./docs/evaluation.md)
5. [docs/tasks.md](./docs/tasks.md)
6. [docs/development_protocol.md](./docs/development_protocol.md)

## Project boundaries

This repo is **Product A** only.

Please do not:

- add frontend or chat features here
- add Product B logic here
- move extraction logic into `insurance-agent`
- mutate raw PDFs
- treat brochures as legal source truth without explicit precedence rules

## Development principles

- small, verified steps
- evidence over guesswork
- precision over recall
- no silent failures
- docs updated with behavior changes

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Validation

Run the relevant checks for your change. At minimum:

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/ --tb=short
```

Common repo checks:

```bash
PYTHONPATH=. .venv/bin/python scripts/validate_gold_corpus.py
PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py data/manifests/product_source_bundles_v1.draft.json
git diff --check
```

If your change touches curated MVP source bundles, also run:

```bash
PYTHONPATH=. .venv/bin/python scripts/validate_source_bundles.py data/manifests/product_source_bundles_mvp_v1.json
```

## What a good contribution looks like

A complete contribution usually includes:

- code change
- test or eval update
- session log update in `runs/sessions/`
- changelog update in `docs/changelog.md`
- task or decision doc update if behavior or scope changed

## Session logs

Meaningful work should leave a session log:

```text
runs/sessions/YYYY-MM-DD-<task-slug>.md
```

Use the existing logs as examples.

## Commit style

Use conventional commits when possible, for example:

```text
feat(parser): improve heading fallback detection
fix(export): preserve explicit not covered status
docs(readme): expand public repo overview
```

## Pull requests

When opening a PR, please include:

- what changed
- why it changed
- what tests/evals were run
- known limitations
- whether docs were updated

## Data safety

Non-negotiable:

- do not mutate raw PDFs
- do not delete raw data
- do not invent missing facts
- do not change gold labels casually to make tests pass

## Good first contribution areas

- documentation clarity
- test coverage
- source-bundle validation/reporting
- eval/report tooling
- parser or extractor bug fixes with clear reproductions

## Questions

If a change has architectural implications, open an issue or PR discussion before making a large implementation move.
