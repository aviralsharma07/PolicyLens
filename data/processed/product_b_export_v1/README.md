# Product B Export v1 Handoff

This package is produced by Product A (`doc-structure-engine`) for Product B (`insurance-agent`).

Scope:
- reviewed 20-policy benchmark
- 20 ontology-backed priority concepts
- compiled JSON only

Do not treat `not_found` as `not covered`. Product B may display "not covered" only when `fact_status` is `explicitly_not_covered`.

Files:
- `manifest.json` — policy identity, export path, fill rate, and status counts
- `export_contract.md` — Product A → Product B schema contract
- `ontology_concepts.v1.json` — canonical concept registry
- `benchmark_20_reviewed/{policy_id}/` — per-policy compiled exports
- `quality/coverage_summary.json` — aggregate concept/status coverage
- `quality/export_eval.json` — final export eval, when provided
- `checksums.sha256` — package integrity checksums
