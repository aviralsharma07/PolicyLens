# DSE-023 Export Freeze Audit

Date: 2026-06-05  
Task: DSE-023 — Product B Export v1 Freeze + Handoff Dataset  
Scope: audit only; no exporter behavior changes

## Summary

The current Product A export is a working 20-policy, 20-concept Product B handoff candidate. It is not a full 91-field export. The DSE-023 freeze should explicitly define v1 as the ontology-backed 20-concept JSON package and leave any larger 91-field expansion as a future schema version.

Current export reality:

- `data/export/{policy_id}/policy_features.json`
- `data/export/{policy_id}/policy_fact_sources.json`
- `data/export/{policy_id}/policy_clauses_minimal.json`
- 20 reviewed policies currently have `policy_features.json`.
- Each `policy_features.json` has 20 feature fields.
- `export_schema_version` is `1.0`.
- `product_identity` includes insurer, plan name, display name, UIN, UIN base, product version, effective date, match confidence, and match method.
- Product B should consume compiled JSON files only, not SQLite or raw parser tables.

## Files Audited

- `docs/export_contract.md`
- `docs/data_contracts.md`
- `docs/database_strategy.md`
- `ontology/concepts.v1.json`
- `derived/field_mapping.py`
- `derived/export_builder.py`
- `derived/schema_validator.py`
- `scripts/run_export.py`
- `scripts/eval_export.py`
- sample `data/export/*/policy_features.json`

## Actual JSON Shape

The actual `policy_features.json` shape matches the core export contract:

- top-level keys: `policy_id`, `export_schema_version`, `exported_at`, `pipeline_run_id`, `source_document`, `product_identity`, `features`, `unresolved_concepts`, `parse_quality`
- feature keys: `value`, `unit`, `fact_status`, `confidence`, `method`, `evidence`, `evidence_page`, `evidence_clause`, `scope`, `condition`, `source_span_id`
- every policy emits all 20 Product A priority concept fields through `derived/field_mapping.py`

Sample inspection found policy exports such as:

- `aditya_birla_activ_care`: 20 features, fill rate 0.80
- `bajaj_allianz_silver_health`: 20 features, fill rate 0.85
- `care_health_care_plus`: 20 features, fill rate 1.00
- `cholamandalam_flexi_max_protect`: 20 features, fill rate 0.25

Low fill rate is not a schema failure. It is represented with explicit `not_found` statuses.

## Ontology And Field Mapping

`ontology/concepts.v1.json` is the canonical 20-concept registry. `derived/field_mapping.py` maps the same 20 concepts to Product B-facing field names.

Important freeze requirement:

- DSE-023 should state that ontology concept identity and `derived/field_mapping.py` must agree before a handoff package is accepted.
- Product B should use the exported field names from the package, while Product A keeps concept IDs as the source-of-truth identity.

## Product Identity

The export builder emits all required Product B identity keys:

- `insurer`
- `plan_name`
- `display_name`
- `uin`
- `uin_base`
- `product_version`
- `effective_date`
- `match_confidence`
- `match_method`

Observed note: `match_confidence` is currently a string quality label in the fixture/tests and current data model, while older docs show a numeric example. DSE-023 Packet 1 should freeze the v1 contract to accept the actual exported representation or explicitly introduce a non-breaking companion field later. Do not silently change the export type in Packet 0.

## Feature Status, Value, And Evidence

The current validator enforces:

- all 20 feature fields are present
- valid fact statuses only
- `present` facts have evidence, evidence page, evidence clause, and source span ID
- `not_found` facts have null values
- product identity core fields are non-null

Critical Product B display rule remains valid:

- `not_found` means not found in policy text.
- Product B must not display “not covered” unless `fact_status = explicitly_not_covered`.

## Parse Quality

`parse_quality` is useful for Product B v1 because it exposes:

- total concepts attempted
- resolved count
- not found count
- not applicable count
- overall fill rate
- average confidence

Recommended freeze: keep this block in v1 and treat it as policy-level quality metadata, not as a user-facing score by itself.

## Benchmark Vs Full Corpus

DSE-023 v1 should package the reviewed 20-policy benchmark first.

Reason:

- DSE-021 proved 20 concepts end to end on reviewed gold.
- DSE-022 proved 20-policy table eval is clean.
- DSE-020 produced full-corpus scale diagnostics, but the full 647-policy export refresh is a scale package, not the v1 contract freeze.

Full-corpus Product B package should be a follow-up after v1 package mechanics are stable.

## Stale Or Ambiguous Documentation

The following should be fixed in Packet 1:

- `docs/database_strategy.md` still describes `policy_features.json` as a “91-field derived view.”
- `docs/evaluation.md` says the derived export eval ensures the “91-field export contract.”
- `tests/test_export.py` and `derived/__init__.py` docstrings still say “91-field export.”
- `IMPLEMENTATION_PLAN.md`, `docs/architecture.md`, and ADR history contain 91-field language. Historical references can remain when clearly historical, but current-roadmap sections should call DSE-023 v1 the 20-concept ontology-backed export.

## Packet 1 Decisions Needed

Packet 1 should freeze these points:

- `export_schema_version = "1.0"` remains unchanged.
- Product B consumes compiled JSON only.
- V1 export is 20-concept ontology-backed JSON, not the future 91-field export.
- Every feature has value/status/evidence fields.
- `not_found` is not “not covered.”
- `explicitly_not_covered` is required before Product B displays “not covered.”

## Audit Verdict

Proceed to DSE-023 Packet 1.

The export is structurally ready for a Product B v1 handoff package, but the docs must be made precise before building the package. No exporter behavior change is required from Packet 0.
