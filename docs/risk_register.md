# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|----|------|-----------|--------|------------|-------|--------|
| R01 | False positives in deterministic extraction | High | Very high | Score + evidence before emission; precision over recall; candidate scoring not first-match-wins | — | Active |
| R02 | Clause segmentation silently wrong | High | High | Source spans + visual debug + structure metrics (precision/recall/F1) | — | Active |
| R03 | UIN matching fails on 22% unmatched | High | Medium | Triage reports + manual decisions per file. Match tiers with confidence scores | — | Active |
| R04 | Policy Schedule overrides body clauses | High | Very high | Precedence rules (Schedule > Benefit grid > Clause > Definition) + conflict table + source_span_type | — | Active |
| R05 | Optional covers pollute base policy facts | High | High | `scope_json: {cover: "base"/"optional"/"add-on"/"variant"}` on every fact | — | Active |
| R06 | Brochures misclassified as policy wordings | Medium | High | Document type firewall + manual audit of classification_report.json | — | Active |
| R07 | Table headers misassociated with values | High | High | Cell-level coordinate storage + header lineage tracking + type-specific table extractors | — | Active |
| R08 | "Not found" confused with "not applicable" | High | High | 7-status fact system (no binary found/not_found). Strict export rules for Product B | — | Active |
| R09 | Regex improvements regress old PDFs | High | Medium | Regression test suite against gold corpus; pipeline_runs track version; versioned extractors | — | Active |
| R10 | Regulatory defaults change over time | Medium | High | Versioned ontology with circular source + effective_date on product_versions | — | Active |
| R11 | Insurer name variations cause duplicate products | High | Medium | Insurer normalizer with alias table; merged during UIN reconciliation | — | Active |
| R12 | IRDAI updates UIN database breaking matches | Medium | Medium | uin_lifecycle.json has generated_at timestamp; re-run matcher on updates | — | Active |
| R13 | pdfplumber version changes break layout | Low | High | Pin pdfplumber version in pyproject.toml; lock CI | — | Active |
| R14 | Gold corpus annotations drift from actual policy | Low | High | Periodic re-validation; annotator + reviewer fields in validation_labels | — | Active |
| R15 | LLM produces convincing but wrong evidence | Medium | High | Evidence must be verified in source text. Reject if not found. LLM facts get lower confidence | — | Active |
| R16 | SQLite reaches file size limits (millions of spans) | Low | Medium | Monitor sqlite file size; migrate to PostgreSQL when > 10GB expected | — | Active |
| R17 | Team members unfamiliar with insurance terminology | High | Medium | docs/glossary.md; gold annotation guide; pair annotation sessions | — | Active |
| R18 | AI agent fails to follow execution protocol | Medium | Medium | docs/ai_execution_protocol.md; session logs are reviewed; hard gates prevent unchecked progress | — | Active |
| R19 | Heading scorer under-detects flattened/all-caps policy formats | High | High | DSE-012 expanded gold now includes Tata AIG and Aditya Birla failures; future parser task must add format-aware heading features and rerun 20-policy evals | — | Active |
| R20 | Expanded table eval still uses 5-policy-era hard-gate assumptions | Medium | Medium | Keep DSE-012 table eval artifact as diagnostic; update table eval to report 20-policy gates before using it as an expansion hard gate | — | Active |
| R21 | Expanded-corpus semantic drift in deterministic extractors | High | High | DSE-017 and DSE-018 add source-backed disagreement audits, gold fixes only with evidence, narrow extractor fixes, and 20-policy fact/scoring/export regression gates | — | Mitigated |
| R22 | Clause fragmentation can hide source values from deterministic extractors | Medium | High | Precision-first extractors emit `not_found` rather than infer values missing from clause text; parser follow-up needed for fragmented settlement/table-like clauses | — | Active |
| R23 | Full-corpus scale run can silently process only reviewed gold outputs | Medium | High | DSE-020 adds collision-safe 647-policy manifest, DSE-020 output roots, manifest-driven clause-store/fact-scoring hooks, and smoke validation before the full run | — | Active |
| R24 | Duplicate-hash entries cause doubled sections/clauses in SQLite | High | Medium | Clause store skips duplicate-hash slugs at ingestion time; build summary records skipped count | — | Mitigated |
| R25 | 110 zero-clause policies block full-corpus extraction coverage | High | Very high | DSE-024 classified the original 132 failures and fallback heading promotion reduced active failures to 110; next mitigation is remaining-format remediation or corpus filtering, not global threshold lowering | — | Active |
