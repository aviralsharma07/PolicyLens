# Changelog

## 2026-06-06 (Project Closeout)

### Added
- `docs/project_closeout.md` — final retrospective and closeout record.
- `runs/sessions/2026-06-06-project-closeout.md` — closeout session log.

### Changed
- `README.md` — now marks the repository as complete as a learning / research / open-source artifact rather than an active product roadmap.
- Public-facing repo naming updated from `doc-structure-engine` to `PolicyLens` across major docs and metadata.
- `IMPLEMENTATION_PLAN.md` — reframed as a historical implementation record; future roadmap items marked deferred.
- `docs/tasks.md` — active sprint removed; deferred future work kept only as historical context.
- `docs/decisions.md` — added project-closeout decision.

### Final Position
- The repo remains public and useful.
- The broad insurance-product roadmap is closed.
- The project is preserved as a reference implementation, engineering artifact, and retrospective.

### Known Issues
- Historical documents still contain milestone-era detail because they are part of the project record, not erased history.
- Product B integration and bundle-aware export remain intentionally unfinished.

## 2026-06-06 (DSE-029 — Open-Source Release Hardening)

### Added
- `LICENSE` — MIT license for public release.
- `CONTRIBUTING.md` — contributor workflow and repo boundaries.
- `CODE_OF_CONDUCT.md` — contributor behavior expectations.
- `SECURITY.md` — security reporting and scope.
- `SUPPORT.md` — support expectations for an open-source side-project repo.
- `CITATION.cff` — citation metadata.
- `.github/ISSUE_TEMPLATE/config.yml` and `.github/pull_request_template.md`.
- `runs/sessions/2026-06-06-dse029-open-source-readiness.md`.

### Changed
- `README.md` — fully rewritten for public open-source release with project purpose, architecture, status, limitations, setup, docs map, and contribution guidance.
- `pyproject.toml` — added license, author, classifiers, keywords, and project URLs.
- `docs/ai_execution_protocol.md` — removed stale `docs/adr/*` and `quality_report.py` references from top-level contributor guidance.
- `docs/development_protocol.md` — updated default validation commands to current repo checks.
- `docs/evaluation.md` — corrected top-level contributor-facing wording away from stale hardcoded 5-policy / `quality_report.py` guidance.
- `docs/architecture.md` — updated high-level export and table-engine wording to match current repo reality.
- `docs/glossary.md` — removed stale “91-field” wording from derived feature definition.
- `docs/decisions.md` — corrected ADR index wording and added ADR-0044 to the active table.
- `docs/tasks.md` — recorded DSE-029 completion.

### Results
- Repository now has the minimum public-facing documentation and metadata expected of a serious open-source engineering repo.
- High-level docs are materially less confusing for first-time readers and contributors.

### Known Issues
- Some lower-level historical docs still preserve early-phase milestone wording because they are part of the project record.
- Public release readiness does not imply hosted-service readiness or live insurer-data freshness guarantees.

## 2026-06-06 (DSE-027 — Curated MVP Source Bundles)

### Added
- `source_bundles/mvp.py` — shared helpers for latest-version verification, curated MVP bundle assembly, and downloaded-source indexing.
- `scripts/verify_mvp_candidates.py` — DSE-027 verified-candidate manifest builder.
- `scripts/build_mvp_source_bundles.py` — curated MVP source-bundle registry builder.
- `scripts/download_mvp_source_documents.py` — current official source downloader with hash/page-count index and explicit failure logging.
- `tests/test_dse027_mvp_source_bundles.py` — focused tests for verified-manifest validation and curated bundle behavior.
- `data/manifests/mvp_product_candidate_verification_manual_v1.json` — tracked current-source verification input for all 30 MVP candidates.
- `data/manifests/mvp_product_candidates_verified_v1.json` — generated verified MVP candidate manifest.
- `data/manifests/product_source_bundle_mvp_manual_overrides_v1.json` — curated MVP bundle adjustments.
- `data/manifests/product_source_bundles_mvp_v1.json` — curated MVP source-bundle registry.
- `data/reports/dse027_mvp_candidate_latest_audit_v1.json` and `.md`.
- `data/reports/dse027_source_download_index_v1.json`.
- `data/reports/dse027_curated_mvp_bundle_closeout_v1.md`.
- `runs/sessions/2026-06-06-dse027-curated-mvp-source-bundles.md`.

### Changed
- `docs/tasks.md` — DSE-027 marked done; DSE-028 promoted as the next active Product A task.
- `IMPLEMENTATION_PLAN.md` — DSE-027 results and current-version drift recorded in the active roadmap.

### Results
- All 30 MVP candidates latest-version reviewed against current official insurer surfaces.
- Verification result: 27 `verified_current`, 3 `verified_current_with_gap`, 30 `live`.
- 45 current official source documents downloaded and hashed.
- Curated bundle quality counts: 18 `acceptable_with_known_gap`, 6 `missing_cis`, 4 `missing_pbt`, 2 `stale_version`.
- Major current-version drift documented across HDFC ERGO, Star Health, ICICI Lombard, and Niva Bupa product lines.

### Known Issues
- Two current-source downloads failed and remain recorded in the source download index:
  - Star Health Family Health Optima brochure: host-resolution failure
  - Star Health Super Surplus brochure: `403 Forbidden`
- The curated MVP corpus is now truthful and reproducible, but not yet fully recommendation-complete; DSE-028 must carry source bundle quality into Product B export semantics.

## 2026-06-06 (DSE-026 — MVP Insurer Universe Selection)

### Added
- `scripts/analyze_dse026_insurer_universe.py` — local-corpus readiness analysis by canonical insurer.
- `data/reports/dse026_insurer_selection_rubric.md` — weighted insurer-selection rubric.
- `data/reports/dse026_corpus_availability_analysis.json` and `.md` — Product A corpus readiness analysis for the insurer universe.
- `data/reports/dse026_market_trust_evidence.md` — external market/source-availability evidence writeup.
- `data/reports/dse026_top10_top5_selection.md` — final top 10 and MVP top 5 decision report.
- `data/reports/dse026_mvp_product_candidate_rationale.md` — first 30-product DSE-027 collection target rationale.
- `data/manifests/mvp_insurer_selection_v1.json` — machine-readable insurer ranking manifest.
- `data/manifests/mvp_product_candidates_v1.json` — machine-readable product candidate manifest.
- `runs/sessions/2026-06-06-mvp-insurer-selection.md`.

### Changed
- `docs/tasks.md` — DSE-026 marked done; DSE-027 promoted as the next active Product A task.
- `IMPLEMENTATION_PLAN.md` — DSE-026 result recorded and HDFC ERGO named as the first source-bundle sprint target.
- `docs/product_b_mvp_gtm_strategy.md` — preliminary shortlist replaced with the finalized DSE-026 insurer universe.

### Results
- MVP top 5 locked: HDFC ERGO, Star Health, ICICI Lombard, Care Health, Niva Bupa.
- Later-wave top 10 additions locked: Tata AIG, Bajaj Allianz, New India Assurance, Aditya Birla Health, SBI General.
- Deferred from first-wave MVP scope: ManipalCigna, United India, Oriental Insurance, Reliance General, Future Generali.
- DSE-027 initial collection set locked at 30 product targets across the MVP top 5.

### Known Issues
- DSE-026 is a build-order decision, not a consumer-facing insurer-quality verdict.
- Some candidate products still need exact current sellability and UIN re-verification during DSE-027.

## 2026-06-05 (DSE-025 — Product Source Bundle Registry v1)

### Added
- `schemas/product_source_bundle.schema.json` — source-bundle registry schema.
- `source_bundles/validator.py` — dependency-free registry validator.
- `source_bundles/builder.py` — draft registry builder from active policy wordings and UIN report.
- `scripts/build_source_bundle_registry.py` and `scripts/validate_source_bundles.py`.
- `tests/test_source_bundles.py` — focused validation and builder tests.
- `data/manifests/product_source_bundles_v1.example.json` — compact example registry.
- `data/manifests/product_source_bundle_manual_overrides_v1.json` — manual source-identified Activ Care bundle override.
- `data/manifests/product_source_bundles_v1.draft.json` — generated 507-bundle draft registry.
- `data/reports/dse025_source_bundle_baseline_audit.md` — current-state source-bundle audit.
- `runs/sessions/2026-06-05-product-source-bundle-registry.md`.

### Changed
- `docs/tasks.md` — DSE-025 marked done and DSE-026 made the next active Product A task.
- `IMPLEMENTATION_PLAN.md` — source-bundle baseline result added to the active roadmap.

### Results
- Draft registry: 507 bundles.
- Source quality: 504 `missing_pbt`, 1 `acceptable_with_known_gap`, 2 `rejected`.
- Document types in registry: 630 policy wordings, 18 brochures, 1 CIS, 1 Product Benefit Table.
- Activ Care source bundle now records official wording, CIS, and PBT URLs as source-identified documents.

### Known Issues
- Source-identified remote documents are not launch-complete until downloaded, hashed, and reviewed.
- Current active manifest still has no `source_url` values.
- DSE-027 must perform actual source collection for selected MVP insurers/products.

## 2026-06-05 (Product Strategy Reset — Source-Bundled MVP)

### Added
- `docs/product_b_mvp_gtm_strategy.md` — GTM and MVP strategy for a curated, citation-backed Product B advisor.
- DSE-025 through DSE-028 roadmap tasks for source bundles, top-insurer selection, source-bundle sprint, and bundle-aware export.
- Product source-bundle contract in `docs/data_contracts.md`.
- ADR-0041, ADR-0042, and ADR-0043 covering curated MVP scope, source-bundle product identity, and variant/condition-scoped facts.
- Risk register entries for missing PBTs, variant flattening, source drift, document conflicts, UIN version drift, incomplete public sources, and overconfident Product B display.
- Session log for the Product A/Product B strategy reset.

### Changed
- `IMPLEMENTATION_PLAN.md` now treats the 647-policy pipeline as scale diagnostics, not the Product B MVP launch universe.
- `docs/tasks.md` now makes DSE-025 Product Source Bundle Registry the next Product A task.
- `docs/export_contract.md` now documents the v1 export limitation: policy-wording-based facts are useful for prototype evidence exploration but not launch-grade recommendations when PBT/CIS/source bundles are missing.

### Known Issues
- Product B export v1 can still display incomplete product truth if downstream UI treats policy-wording facts as final variant-level facts.
- Product source bundles have not yet been collected for the curated MVP insurer universe.

## 2026-06-05 (DSE-023 — Packet 3: Final Handoff Acceptance)

### Added
- `runs/evals/2026-06-05-export-dse023-final.json` — final export eval artifact.
- `data/processed/product_b_export_v1/` — Product B handoff package for the reviewed 20-policy benchmark.

### Changed
- `docs/tasks.md` — DSE-023 marked `done`.
- `docs/evaluation.md` — Derived Export eval marked active with DSE-023 final results.
- `runs/sessions/2026-06-05-product-b-export-v1.md` — final closeout appended.

### Final Metrics
- 20/20 reviewed policies exported.
- 20/20 concept fields per policy.
- Schema validation errors: 0.
- Present facts missing evidence: 0.
- Evidence span IDs missing from DB: 0.
- False present: 0.
- Gold status accuracy: 97.8%.
- Gold value accuracy: 98.2%.
- Full pytest: 480/480 passed.

## 2026-06-05 (DSE-023 — Packet 2: Handoff Package Builder)

### Added
- `scripts/build_product_b_handoff.py` — reproducible Product B handoff package builder.
- `tests/test_export.py` — handoff package tests for reviewed-policy manifest, no raw/interim/SQLite files, checksums, missing `policy_features.json`, and legacy metadata without `label_status`.

### Fixed
- Handoff policy discovery includes the original reviewed gold policies whose metadata predates `label_status: reviewed`; only `label_status: draft` is excluded.

### Validation
- Builder produced `data/processed/product_b_export_v1` with 20 reviewed policies.
- Focused export tests passed.

## 2026-06-05 (DSE-023 — Packet 1: Export Contract Freeze)

### Changed
- `docs/export_contract.md` — DSE-023 v1 scope added: Product B Export v1 is the 20-concept ontology-backed JSON contract, not the future 91-field schema.
- `docs/database_strategy.md` — JSON export description updated from 91-field view to 20-concept v1 package.
- `docs/data_contracts.md` — derived export consumer corrected to `derived/export_builder.py`; handoff package boundary documented.
- `docs/evaluation.md` — Derived Export eval purpose updated to v1 20-concept wording.
- Export test/module docstrings updated away from stale 91-field wording.

### Decision
- Product B consumes compiled JSON only. SQLite, raw parser tables, interim parser outputs, and raw PDFs remain internal to Product A.

## 2026-06-05 (DSE-023 — Packet 0: Export Freeze Audit)

### Added
- `data/reports/dse023_export_freeze_audit.md` — audit of current Product B export shape, ontology mapping, product identity, evidence fields, parse quality, and stale 91-field documentation.
- `runs/sessions/2026-06-05-product-b-export-v1.md` — DSE-023 session log.

### Changed
- `docs/tasks.md` — DSE-023 moved to Active Sprint and marked `in_progress`.

### Findings
- Current export is a 20-policy benchmark package candidate with 20 ontology-backed concept fields per policy.
- Product B should consume compiled JSON only, not SQLite or raw parser/interim outputs.
- Stale “91-field” language remains in active docs/docstrings and must be clarified in Packet 1.

## 2026-06-05 (DSE-022 — Packet 4: Final Closeout)

### Added
- `runs/sessions/2026-06-05-table-eval-expansion.md` — Packet 4 final closeout section.

### Changed
- `docs/tasks.md` — DSE-022 status changed to `done`; moved from Active Sprint to Completed; Packet 4 results added.
- `docs/evaluation.md` — Table Extraction current status updated to "DSE-022 final PASS"; final eval artifact path listed.
- `docs/changelog.md` — Packet 4 entry added.
- `docs/risk_register.md` — R20 updated from Active to Mitigated; remaining empty headers/rows limitation noted.

### Final Metrics
- 20/20 policies accounted for.
- 387/387 labels detected at 100% recall.
- Priority recall 100%.
- Type accuracy 100%.
- Header lineage 100% (required only where gold headers exist).
- Unrecorded missing cell bboxes 0.
- Legacy rows documented 395/395.
- Tata AIG explicitly `no_physical_labels`.

## 2026-06-05 (DSE-022 — Packet 3: Cataract Sublimit Table Type Fix)

### Added
- `table_engine/table_type_classifier.py` — "sum insured" added as schedule_of_benefits keyword; premium-marker disambiguation now checks cell text (not heading context) so heading noise does not block benefit→schedule reclassification.
- `tests/test_table_engine.py` — 5 new tests: cataract as schedule_of_benefits, cataract with premium heading, premium retention not reclassified, premium retention with benefit heading, generic percent not schedule.
- `runs/evals/2026-06-05-table-engine-dse022-final.json` — DSE-022 final eval artifact (generated output consumed by eval, not a committed source artifact).
- `docs/evaluation.md` — DSE-022 Final Result section added.
- `runs/sessions/2026-06-05-table-eval-expansion.md` — Packet 3 section added.
- `docs/changelog.md` — Packet 3 entry added.

### Fixed
- new_india_floater phys_table_002 cataract sublimit table no longer misclassified as `premium`. Type accuracy is now 100% (was 99.74%).

### Audit-only scope
No gold labels, table detection logic, eval thresholds, or physical labels were changed.

## 2026-06-05 (DSE-022 — Packet 2: Physical Table Label Quality Audit)

### Added
- `data/reports/dse022_physical_table_label_audit.json` — per-policy physical table label quality audit for all 20 reviewed policies.
- `data/reports/dse022_physical_table_label_audit.md` — Markdown audit report with classification, findings, and recommendations.

### Changed
- `docs/tasks.md` — removed blank Backlog row between DSE-014 and DSE-023; added DSE-021 to Completed table.
- `docs/evaluation.md` — line 592: fixed "DSE-019 legacy 5-policy gate" → "DSE-009 legacy 5-policy gate".
- `runs/sessions/2026-06-05-table-eval-expansion.md` — Packet 2 next step updated.
- `data/reports/dse009_gold_table_source_review.json` — restored original 5-policy version from HEAD~1.
- `data/reports/dse009_gold_table_source_review.md` — restored original 5-policy version from HEAD~1.

### Fixed
- DSE-009 historical reports restored (overwritten by Packet 1 eval regeneration).
- docs/tasks.md Backlog table broken blank row fixed.
- docs/evaluation.md typo: DSE-019 → DSE-009.

### Audit Results
- 387 physical labels across 20 policies examined; 79 priority labels.
- 14 policies `label_ok`, 1 `needs_extractor_review` (new_india_floater), 1 `reviewed_no_physical_labels` (tata_aig), 4 `nonpriority_diagnostic_only`.
- 0 gold label corrections needed.
- 1 type mismatch found: new_india_floater phys_table_002 (gold: schedule_of_benefits, extractor: premium).
- 370 DSE-012 labels have empty headers/rows — known annotation limitation.
- All bboxes valid; 1 low-severity plausibility flag (bajaj_allianz phys_table_0046).
- 373/395 legacy rows correctly auto-mapped via source_table_id.

### Audit-only scope
This packet is audit-only. No extractor files, table-engine code, gold labels, or PDFs were created or modified. All changes are limited to reports, docs, and session logs. No table extraction behavior changed.

### Known Issues
- new_india_floater phys_table_002 extractor type classification needs fixing (schedule_of_benefits → premium).
- DSE-012 bulk-reviewed labels lack cell-level detail (370/387 labels have empty headers/rows).

## 2026-06-05 (DSE-022 — 20-Policy Table Eval Expansion, Packet 0 + Packet 1)

### Added
- `scripts/eval_table_engine.py` — dynamic reviewed-policy discovery, zero-label policy handling (no_physical_labels), automated legacy disposition for all 395 rows across 20 policies, DSE-022 eval gate replacing hardcoded 5-policy gate.
- `tests/test_table_engine.py` — 10 new tests for discover_reviewed_policies, physical label mapping, legacy dispositions, no undocumented legacy rows.
- `data/reports/dse022_legacy_table_dispositions_v1.json` — all 395 legacy tables.json rows classified.
- `data/reports/dse022_legacy_table_dispositions_v1.md` — Markdown disposition report.
- `runs/evals/2026-06-05-table-engine-dse022-baseline.json` — DSE-022 baseline eval: 20/20 policies evaluated, 19 with labels, 1 zero-label (tata_aig_arogya_sanjeevani), 100% detection recall, 99.74% type accuracy, 100% header lineage.

### Changed
- `docs/tasks.md` — DSE-022 removed from Backlog, detail status `planned` → `in_progress`; "full-corpus eval gates" → "20-policy gold benchmark gates".
- `IMPLEMENTATION_PLAN.md` — "full-corpus eval gates" → "20-policy gold benchmark gates".
- `docs/evaluation.md` — Table Extraction eval section updated: hard gates now reference all reviewed policies (not 5); DSE-022 baseline documented; summary table updated.
- `tests/test_gold_corpus_validator.py` — physical_table_labels assertion from `>= 10` to `== 387`.

### Fixed
- Hardcoded 5-policy table eval gate replaced with dynamic discovery from gold_corpus.
- tata_aig_arogya_sanjeevani (0 physical table labels) is now explicit `no_physical_labels` instead of being silently treated as an evaluation gap.
- All 395 legacy `tables.json` rows receive automated or explicit dispositions; 0 undocumented rows.

### Known Issues
- 196 tables across the 20-policy corpus have recorded missing cell bbox issues (pdfplumber limitation, not a gold gap).
- 7 legacy rows remain `deferred_needs_pdf_review` from the original DSE-009 manual review; all have explicit reasons.

## 2026-06-05 (DSE-021 — Final Full Chain)

### Added
- `runs/evals/2026-06-05-fact-extraction-dse021-final.json` — final 20-concept deterministic extraction eval.
- `runs/evals/2026-06-05-fact-scoring-dse021-final.json` — final SQLite fact scoring eval.
- `runs/evals/2026-06-05-export-dse021-final.json` — final Product B export eval.

### Changed
- DSE-021 marked done after all 20 priority concepts passed the full 20-policy chain: extraction, clause store/source spans, fact scoring, export, gold validation, and full pytest.

### Fixed
- Completed deterministic concept coverage for the 20-policy benchmark without adding LLM, table remediation, Product B code, or raw PDF changes.

### Known Issues
- Some exact limits remain intentionally conservative when the current section-tree evidence cannot safely carry source-PDF percentages; parser/table remediation remains a separate DSE-022 concern.

## 2026-06-05 (DSE-021 — Packet 3B: Coverage Wave Extractors)

### Added
- `RestorationBenefitExtractor`, `ModernTreatmentCoverageExtractor`, and `NewbornCoverageExtractor`.
- Focused regression tests for restoration/recharge, body-part/property restoration rejection, modern-treatment coverage and exclusions, newborn conditional coverage, definitions, and baby-item annexure rejection.
- `runs/evals/2026-06-05-fact-extraction-dse021-coverage-wave.json` passing eval artifact.

### Changed
- `restoration_benefit`, `modern_treatment_coverage`, and `newborn_coverage` are now active deterministic concepts in `TARGET_CONCEPTS` and the ontology registry.
- Coverage-wave gold labels corrected only where Packet 3A source review proved the prior label/value/evidence wrong or too specific for verified section-tree evidence.

### Known Issues
- Star restoration and Tata AIG modern-treatment exact source PDF percentages are not carried safely by the current section-tree clauses; deterministic v1 emits conservative `covered` values for those rows until parser/table remediation improves source context.

## 2026-06-05 (DSE-021 — Packet 3A: Coverage Wave Gold Audit)

### Added
- `data/reports/dse021_coverage_wave_gold_audit.md` — source-backed classification for all 20 `restoration_benefit`, `modern_treatment_coverage`, and `newborn_coverage` gold labels before extractor implementation.

### Changed
- Packet 3B implementation rules are locked: accept only operative coverage clauses, reject reconstruction/property-restoration/baby-item false positives, and use canonical covered/conditional/schedule-dependent value shapes.

### Known Issues
- `restoration_benefit`, `modern_treatment_coverage`, and `newborn_coverage` extractors are not implemented yet.
- Packet 3B must apply only source-backed gold corrections from the audit; no gold label should be changed just to satisfy eval.

## 2026-06-04 (DSE-021 — Packet 2B: Room Rent + ICU Extractors)

### Added
- `RoomRentLimitExtractor` and `IcuLimitExtractor` with conservative handling for operative percentage limits, actuals/no fixed limits, schedule-dependent limits, and conditional component values.
- Regression tests for Arogya-style percentage limits, actuals, schedule-dependent wording, definition-only rejection, paired table-like room/ICU clauses, and IFFCO conditional components.
- `runs/evals/2026-06-04-fact-extraction-dse021-room-icu.json` final passing eval artifact.

### Changed
- `room_rent_limit` and `icu_limit` are now active deterministic concepts in `TARGET_CONCEPTS` and the ontology registry.
- Room/ICU gold labels were corrected only where Packet 2A/2B source review proved the old label/value/evidence wrong or noncanonical.

### Fixed
- Corrected Kotak ICU from `not_found` to schedule-dependent after source review found ICU Charges under the operative What We Will Pay inpatient-treatment clause.
- Corrected Kotak room-rent evidence from a definition-like snippet to the operative Cap on Room Rent clause.

### Known Issues
- These extractors read clauses/table-like text from existing section trees. They do not remediate physical table extraction or header lineage; DSE-022 remains responsible for table-engine quality.

## 2026-06-04 (DSE-021 — Packet 2A: Room Rent + ICU Gold Audit)

### Added
- `data/reports/dse021_room_icu_gold_audit.md` — source-backed classification for all 20 `room_rent_limit` and `icu_limit` gold labels before extractor implementation.

### Changed
- Packet 2B implementation rules are locked: reject definitions, accept only operative room/ICU clauses/tables, represent actuals and schedule-dependent limits explicitly, and preserve conditional components when one scalar would be misleading.

### Known Issues
- `room_rent_limit` and `icu_limit` extractors are not implemented yet.
- Packet 2B must apply several source-backed gold corrections where current labels are table-row bleed, definition-only evidence, missing operative limits, or noncanonical value shapes.

## 2026-06-04 (DSE-021 — Packet 1C: Deductible Extractor)

### Added
- `DeductibleExtractor` for operative deductible clauses.
- Regression tests for schedule-dependent deductible, definition-only rejection, free-look deduction rejection, explicit amount parsing, top-up deductible, and time deductible hours.
- `runs/evals/2026-06-04-fact-extraction-dse021-deductible.json` final passing eval artifact.

### Changed
- `deductible` is now an active deterministic concept in `TARGET_CONCEPTS` and ontology.
- Deductible gold labels corrected only where Packet 1B source audit proved the current label/value wrong or non-canonical.

### Fixed
- Fact extraction eval now passes with 15 active deterministic concepts: 20/20 policies, precision 100.00%, normalized value accuracy 100.00%, evidence accuracy 100.00%, false-present count 0.

### Known Issues
- Exact deductible amount remains schedule-dependent when the source clause points to policy schedule/certificate rather than stating an amount in the wording.

## 2026-06-04 (DSE-021 — Packet 1B: Deductible Gold Audit)

### Added
- `data/reports/dse021_deductible_gold_audit.md` — source-backed classification for all 20 deductible gold labels before extractor implementation.

### Changed
- DSE-021 session log now records Packet 1B audit results and Packet 1C implementation rules.

### Known Issues
- Deductible extractor is not implemented yet.
- Packet 1C must correct three source-backed deductible gold issues before using eval as a hard gate: Future Generali and Kotak should be `not_found`; Reliance should be `present`.

## 2026-06-04 (DSE-021 — Packet 1A: Claim Intimation Timeline Extractor Remediation)

### Added
- `ClaimIntimationTimelineExtractor` for `claim_intimation_timeline`.
- Regression tests for claim-intimation phrasing, adjacent notification bullets, and false-positive document/death submission rows.
- `data/reports/dse021_claim_intimation_mismatch_audit.md` with source-backed gold corrections and extractor remediation notes.
- `runs/evals/2026-06-04-fact-extraction-dse021-claim-intimation.json` final passing eval artifact.

### Changed
- `extractors/models.py` and `ontology/concepts.v1.json` now mark `claim_intimation_timeline` as an active deterministic concept.
- `extractors/deterministic.py` handles notification terms split across adjacent clauses, including Arogya-style `Notification of Claim` headings followed by 24/48-hour bullets.
- Gold `facts.json` labels for `claim_intimation_timeline` were corrected only where source text proved the previous label/value was wrong or non-comparable.

### Fixed
- DSE-021 claim-intimation eval now passes: 20/20 policies, precision 100.00%, recall 99.53%, normalized value accuracy 100.00%, status accuracy 98.57%, evidence accuracy 100.00%, false-present count 0.
- Rejected reimbursement document-submission rows and death-document deadlines that previously looked like claim-intimation timelines.

### Known Issues
- `claim_intimation_timeline` records the primary/earliest claim-notification deadline. Separate document filing timelines remain deferred.

## 2026-06-04 (DSE-021 — Packet 0B: Shared Wave 2 Utilities)

### Added
- `extractors/wave2_utils.py` — shared utility helpers for Wave 2 extractors:
  - `clean_lower` — clean space + ligature fix + lower (wraps `evidence.clean_space`)
  - `has_any` — text substring check against an iterable of terms
  - `evidence_window` — compact source text window around a span
  - `near_terms` — detect signal terms near a span within a configurable radius
  - `reject_if_context` — return rejection reason if reject terms found near a span
  - `find_duration_near_terms` — filter `find_durations` results by nearby signal terms and allowed units
  - `schedule_dependent_value` — standard shape for schedule-dependent concepts
  - `coverage_value` — standard shape for coverage-status concepts (supports `covered` and `conditional`; raises `ValueError` for unsupported statuses)
- `tests/test_wave2_utils.py` — comprehensive unit tests for all 7 utility categories (18 tests).

### Known Issues
- No extractors use these utilities yet; they are tested but not integrated.

## 2026-06-04 (DSE-021 — Wave 2 Baseline Audit + Kickoff)

### Added
- `data/reports/dse021_wave2_baseline_audit.md` — baseline audit for the 7 remaining deterministic extractors, with gold status counts, evidence snippets, DSE-020 not_found pressure, and recommended implementation packets.
- `runs/sessions/2026-06-04-extractor-wave2.md` — DSE-021 kickoff session log.

### Changed
- DSE-021 in `docs/tasks.md` moved from `planned` to `in_progress`.
- Branch created: `feat/dse-021-extractor-wave2`.

### Known Issues
- All 7 planned concepts currently at 566 `not_found` in full corpus; zero extractors exist for any of these.
- Gold coverage varies: restoration_benefit (7/20 present) and newborn_coverage (3/20 present) are the sparsest.

## 2026-06-04 (DSE-024 — E3D Parser-Target Closeout)

### Added
- `data/manifests/parser_target_overrides_v1.json` — explicit parser-target override manifest.
- `tests/test_dse020_triage_report.py` — regression coverage for parser-target exclusions in the DSE-020 triage report.
- `runs/sessions/2026-06-04-dse024-e3d-parser-target-closeout.md` — DSE-024 closeout session log.

### Changed
- `scripts/dse020_triage_report.py` now accepts `--parser-target-overrides`.
- DSE-020 triage separates excluded parser targets from zero-heading / zero-clause parser failures.
- DSE-021 moved from blocked to planned.

### Fixed
- `23_raheja_qbe_raheja_qbe_product_list` is now recorded as a non-policy product-list parser exclusion instead of a parser failure.
- DSE-020 triage now reports **0 zero-heading parser targets**, **0 zero-clause parser targets**, and **1 excluded parser target**.

### Known Issues
- 133 policies still have zero fact candidates; this is now an extractor coverage/input recall issue for DSE-021, not a zero-clause parser blocker.
- Current regenerated gold heading eval remains 17/20; section-tree eval remains 19/20 with the known `oriental_cancer_protect` issue.

## 2026-06-04 (DSE-024 — Phase E3C Safe Heading Fixes)

### Added
- `data/reports/dse024_gold_heading_reproducibility_audit_v1.md` — audit explaining why regenerated 20-policy heading eval is 17/20 instead of the older reported 20/20.
- `data/reports/dse024_phase_e3c_safe_heading_fixes.md` — E3C report with full-corpus parser results and remaining residual policy.
- `runs/evals/2026-06-04-heading-scorer-dse024-e3c-safe-fixes.json` — current regenerated gold heading eval after E3C.
- `runs/evals/2026-06-04-section-tree-dse024-e3c-safe-fixes.json` — current regenerated gold section-tree eval after E3C.
- `runs/sessions/2026-06-04-dse024-phase-e3c1-gold-heading-repro.md` — E3C1 reproducibility audit session.
- `runs/sessions/2026-06-04-dse024-phase-e3c-safe-heading-fixes.md` — E3C safe-fix session.

### Changed
- Heading scorer now has fallback-only structural recognition for section-token headings, part-token headings, parenthesized letter headings, roman policy-section headings, compact lettered headings, short colon labels, and short dictionary headings.
- New structural heading signals have zero global score weight and only affect the zero-heading fallback layer.
- DSE-020 heading candidates, section trees, and scale triage report were regenerated after E3C.

### Fixed
- Full-corpus zero-heading / zero-clause policies dropped from **58** to **1** without lowering the global heading threshold.
- Added fallback guards for known high-risk false positives: percentage rows, serial/table rows, duration-percentage rows, procedure/item rows, and generic `POLICY WORDINGS`.

### Known Issues
- Current regenerated gold heading eval is **17/20 PASS**, failing `aditya_birla_activ_care`, `care_health_care_plus`, and `tata_aig_arogya_sanjeevani`; this is documented as a reproducibility/eval-label issue, not hidden.
- Current regenerated gold section-tree eval is **19/20 PASS**, with only the pre-existing `oriental_cancer_protect` tree-accuracy issue.
- The only remaining full-corpus zero-clause item is `23_raheja_qbe_raheja_qbe_product_list`, a 4-page product-list style document with pending match status; this should be handled by corpus/identity filtering.

## 2026-06-04 (DSE-024 — Phase E3B Recovery + Heading-Miss Inspection)

### Added
- `data/reports/dse024_heading_miss_safe_candidates_v1.json` — inspection-only audit of 33 residual `heading_miss` policies.
- `data/reports/dse024_heading_miss_safe_candidates_v1.md` — Markdown summary with top candidates, false-positive classes, and narrow safe-pattern candidates.
- `runs/evals/2026-06-04-heading-scorer-dse024-e3b-recovery-baseline.json` — regenerated clean heading eval after abandoning the bad E3B attempt.
- `runs/sessions/2026-06-04-dse024-phase-e3b-heading-miss-inspection.md` — recovery and inspection session log.

### Fixed
- Removed the failed uncommitted E3B scorer/test edits that lowered fallback safety and regressed gold heading eval.
- Removed stray failed-report artifacts under `data/reports/reports/` and `data/reports/eval_dse024_phase_e3b_heading.json`.
- Regenerated DSE-020 heading candidates, section trees, and triage report from the restored scorer state.

### Results
- Current DSE-020 triage is back to **58 zero-heading / 58 zero-clause policies**.
- All 33 `heading_miss` policies were audited:
  - **27** classified as `safe_pattern_fix` candidates.
  - **6** classified as `false_top_candidate`.
- Safe candidate patterns were narrowed to structural forms such as numbered short titles, section-token headings, roman policy-section headings, and part headings.
- High-risk top candidates such as percentage rows, table header fragments, procedure rows, bare numbers, and generic document titles were explicitly rejected.

### Known Issues
- Regenerating the 20-policy gold heading candidates from the restored scorer produced **17/20 PASS**, with failures on `aditya_birla_activ_care`, `care_health_care_plus`, and `tata_aig_arogya_sanjeevani`. Earlier 20/20 heading eval artifacts were not reproducible from the current regenerated artifacts and must not be used as a blind acceptance claim for E3C.
- E3C must implement only inspection-backed narrow fixes and must first reconcile or account for the gold heading reproducibility gap.

## 2026-06-04 (DSE-024 — Phase E3A: Classify Remaining 58 Zero-Clause Policies)

### Added
- `scripts/dse024_classify_residual58.py` — classification script for 58 post-E2 zero-clause policies.
- `data/reports/dse024_residual58_classification_v1.json` — per-policy classification into 6 buckets.
- `data/reports/dse024_residual58_classification_v1.md` — Markdown report with top fix candidates.

### Results
- **58 residual zero-clause policies classified (0 unclassified).**
- **33 heading_miss** — plausible near-miss headings (max_score 0.3-0.5); need format-specific heading patterns.
- **8 duplicate_or_superseded** — same-hash duplicates; deduplication removes them.
- **8 physical_text_issue** — max_score ≤ 0 (negative/zero); pdfplumber extraction quality issue.
- **4 non_policy_or_rider** — brochures/prospectuses; document-type filtering.
- **3 unsupported_format** — very short or product-list documents.
- **2 manual_review_required** — unclear without human PDF inspection.
- **0 section_tree_fail** — confirms E2 rebuild resolved all 44.
- **Fix parser:** 41 (heading_miss + physical_text_issue).
- **Filter/defer corpus:** 15 (duplicate + non_policy + unsupported).
- **No stale E1 counts carried forward.**

## 2026-06-04 (DSE-024 — Section Tree Rebuild for 44 section_tree_fail Policies)

### Added
- `data/reports/dse024_section_tree_fail_investigation_v1.md` — investigation report with root cause analysis and edge case verification.
- `runs/evals/2026-06-04-heading-scorer-dse024-e2.json` — gold heading eval (20/20 PASS, no regression).
- `runs/evals/2026-06-04-section-tree-dse024-e2.json` — gold section tree eval (19/20 FAIL, pre-existing `oriental_cancer_protect` unchanged).

### Changed
- `data/interim/dse020/logical/*/section_tree.json` — regenerated for all 647 policies using post-fallback heading candidates.
- `data/interim/dse020/logical/section_tree_run_summary.json` — regenerated summary.
- `data/reports/dse020_scale_triage_report_v1.json` and `.md` — regenerated after section tree rebuild.

### Results
- **All 44 section_tree_fail policies resolved.** Root cause confirmed: section tree was built before fallback heading promotion. No code changes needed — section tree builder already filters by `decision == "heading"`.
- **Zero-clause count: 110 → 58** (52 policies gained clauses).
- **Zero-heading count: 84 → 58** (tied to zero-clause; all remaining are heading_miss/duplicate/needs_review/non-policy/unsupported buckets).
- **Gold heading eval: 20/20 PASS** — no regression.
- **Gold section tree eval: 19/20 FAIL** — pre-existing `oriental_cancer_protect` unchanged.
- **Gold corpus validation: PASS** — 20 policies, 400 facts, 2739 sections, 6251 clauses.
- **Full pytest: 400/400 PASS** — no regressions.
- **647/647 section trees** built successfully, 0 errors.
- **No code changes** — section_tree.py heading filter already handles fallback-promoted headings, compact headings (`10.Renewal`), and alpha headings (`D. BENEFITS:`).
- **58 remaining zero-clause policies** are heading_miss (34), duplicate_or_superseded (14), needs_manual_review (10), non_policy_or_rider (6), unsupported_format (2).

### Known Issues
- 34 heading_miss policies need format-specific heading pattern additions (not section tree fixes).
- Section tree rebuild revealed pre-existing heading scorer quality gap between gold pipeline (`data/interim/logical`) and full-corpus pipeline (`data/interim/dse020/logical`) for some gold policies (aditya_birla_activ_care, tata_aig_arogya_sanjeevani).

## 2026-06-04 (DSE-024 — Residual Zero-Clause Classification)

### Added
- `scripts/dse024_classify_residual_zero_clause.py` — diagnostic-only script to classify 110 zero-clause policies.
- `data/reports/dse024_residual_zero_clause_classification_v1.json` — per-policy classification into 6 buckets.
- `data/reports/dse024_residual_zero_clause_classification_v1.md` — Markdown report with top 20 fix candidates.

### Results
- 110 zero-clause policies classified:
  - **section_tree_fail** (44): fallback headings exist, need section tree rebuild
  - **heading_miss** (34): plausible near-miss headings below t=0.5
  - **duplicate_or_superseded** (14): duplicate-hash policies from same PDF
  - **needs_manual_review** (10): unclear without human inspection
  - **non_policy_or_rider** (6): brochures, riders, prospectuses
  - **unsupported_format** (2): very short or product-list documents
- 0 unclassified, 0 code behavior changes in this packet.
- Top 20 highest-confidence parser-fix candidates listed with per-policy evidence.

### Known Issues
- 44 section_tree_fail policies could be resolved simply by rebuilding section tree after fallback promotion (headings already computed, no scorer changes needed).
- 34 heading_miss policies need format-specific heading pattern additions (not threshold lowering).
- 14 duplicate_or_superseded policies don't need parser fixes — deduplication will remove them.

## 2026-06-04 (DSE-024 — Fallback Heading Promotion Layer)

### Added
- `HeadingScorer` zero-heading fallback promotion layer for low-confidence but structurally plausible headings.
- Fallback audit metadata in `heading_candidates.json`: `promotion_source`, `promotion_reason`, `original_decision`, `original_score`, and `fallback_evaluation`.
- `data/reports/dse024_fallback_heading_promotion_report.json` — machine-readable report comparing D2 to fallback results.
- `data/reports/dse024_fallback_heading_promotion_report.md` — Markdown fallback promotion report.
- `runs/evals/2026-06-04-heading-scorer-dse024-fallback.json` — gold heading eval after fallback.
- `runs/evals/2026-06-04-section-tree-dse024-fallback.json` — gold section tree eval after fallback.
- `runs/sessions/2026-06-04-dse024-fallback-heading-promotion.md` — fallback session log.

### Changed
- `data/interim/dse020/logical/*/heading_candidates.json` and `section_tree.json` — regenerated parser outputs for the 647-policy DSE-020 corpus.
- `data/reports/dse020_scale_triage_report_v1.json` and `.md` — regenerated after fallback promotion.
- `docs/data_contracts.md` — documented optional fallback promotion audit fields in Contract 3A.
- `docs/tasks.md`, `IMPLEMENTATION_PLAN.md`, and `docs/risk_register.md` — updated parser blocker count from 122 to 110.

### Results
- **Zero-clause count improved:** D2 `122` → fallback `110`.
- **Zero-heading count improved:** D2 `122` → fallback `84`.
- **No new zero-clause regressions vs D2:** 12 policies improved, 0 regressed.
- **Gold heading eval:** 20/20 PASS.
- **Gold section tree eval:** 19/20 FAIL, unchanged pre-existing `oriental_cancer_protect` tree-accuracy issue.

### Known Issues
- 110 policies still have zero headings/clauses.
- DSE-021 remains blocked until remaining parser coverage improves or unsupported/non-policy documents are filtered.

## 2026-06-04 (DSE-024 — Phase D2 Regression Recovery)

### Added
- `data/reports/dse024_phase_d2_regression_recovery.json` — machine-readable recovery report comparing DSE-020 baseline, D1 regression, and D2 recovery.
- `data/reports/dse024_phase_d2_regression_recovery.md` — Markdown recovery report with changed features, eval results, and next decision.
- `runs/evals/2026-06-04-heading-scorer-dse024-phase-d2.json` — gold heading eval after recovery.
- `runs/evals/2026-06-04-section-tree-dse024-phase-d2.json` — gold section tree eval after recovery.
- `runs/sessions/2026-06-04-dse024-phase-d2-regression-recovery.md` — D2 recovery session log.

### Changed
- `structure_parser/heading_scorer.py` — reverted harmful Phase C penalties for TOC dot leaders, short all-caps numbered lines, and tab-containing lines.
- `structure_parser/heading_scorer.py` — retained reduced sentence-case penalty for bold numbered headings.
- `structure_parser/heading_patterns.py` — retained letter-numbered heading support while keeping `S. No.` / serial rows excluded.
- `tests/test_heading_scorer.py` — added regression coverage for letter headings, serial-number rows, and bold numbered sentence-case headings.
- `data/interim/dse020/logical/*/heading_candidates.json` and `section_tree.json` — regenerated parser outputs for the 647-policy DSE-020 corpus.
- `data/reports/dse020_scale_triage_report_v1.json` and `.md` — regenerated after D2 recovery.
- `docs/tasks.md` — DSE-024 D2 recovery results recorded.

### Results
- **Zero-clause count recovered:** D1 `156` → D2 `122`, improving beyond the original DSE-020 baseline of `132`.
- **No new baseline regressions:** 10 policies improved from the original 132 zero-clause set; 0 new zero-clause policies appeared.
- **Gold heading eval:** 20/20 PASS.
- **Gold section tree eval:** 19/20 FAIL, unchanged pre-existing `oriental_cancer_protect` tree-accuracy issue.
- **Focused pytest:** 41/41 PASS.

### Known Issues
- 122 policies still have zero headings/clauses and require a new fallback heading promotion strategy.
- Further global threshold lowering remains rejected until false-positive controls are explicit and tested.

## 2026-06-04 (DSE-024 — Phase D1 Zero-Clause Revalidation)

### Added
- `data/reports/dse024_phase_d1_zero_clause_revalidation.json` — D1 revalidation report with pre/post Phase C comparison.
- `data/reports/dse024_phase_d1_zero_clause_revalidation.md` — Markdown report with delta analysis.
- `runs/evals/2026-06-04-heading-scorer-dse024-phase-d1.json` — gold heading eval (20/20 PASS, no regression).
- `runs/evals/2026-06-04-section-tree-dse024-phase-d1.json` — gold section tree eval (19/20 FAIL, pre-existing).
- `runs/sessions/2026-06-04-dse024-phase-d1-revalidation.md` — D1 session log.

### Changed
- `data/interim/dse020/logical/*/section_tree.json` — regenerated 647 section trees to pick up Phase C heading candidates.
- `data/interim/dse020/logical/section_tree_run_summary.json` — new run summary after section tree rebuild.
- `data/reports/dse020_scale_triage_report_v1.json` — regenerated (zero-clause: 132→156, zero-heading: 132→156).
- `data/reports/dse020_scale_triage_report_v1.md` — regenerated.
- `docs/tasks.md` — DSE-024 Phase D1 results recorded.

### Results
- **Zero-clause reduction: NOT achieved** — count increased from 132 to 156 (+24).
- **Root cause:** Phase C stricter penalties (TOC dots, tab character, short all-caps) pushed 24 marginal headings below t=0.5.
- **15/24 regressed are Star Health** — their format relies on numbered headings (score 0.48-0.50).
- **0 policies gained headings** — permissive Phase C additions (letter-numbering, reduced sentence-case) did not help zero-heading policies at t=0.5.
- **Gold heading eval: 20/20 PASS** — no regression.
- **Gold section tree: 19/20 FAIL** — pre-existing `oriental_cancer_protect` unchanged.
- **Full heading+manifest pytest: 37/37 PASS.**

### Known Issues
- Zero-clause count at 156 is worse than original 132 baseline.
- Section tree eval at 19/20 remains pre-existing `oriental_cancer_protect` issue.
- Zero-clause reduction requires new approach: format-specific heading additions or threshold lowering with FP suppression.

## 2026-06-04 (DSE-024 — Phase C Targeted Heading Scorer Fixes)

### Added
- **TOC suppression**: `has_toc_dots` weight changed from +0.10 to -0.30. Lines with dot leaders (TOC entries) now get a -0.30 penalty instead of a +0.10 boost.
- **Short all-caps numbered penalty**: New `short_all_caps_numbered` feature (-0.25) penalizes short (<30 chars) all-caps numbered items that don't match the heading dictionary. Targets medical supply codes ("43 SPLINT") and procedure codes.
- **Tab character penalty**: New `has_tab_char` feature (-0.30) penalizes lines containing tab characters (table data leaked into line text).
- **Letter-numbering pattern**: Added `^[A-Z]\.\s(?!No|no)` pattern to NUMBERING_PATTERNS for single-letter section markers ("A. Definitions", "B. Coverage"). Excludes "S. No." (serial number) false positives.
- **Reduced sentence-case penalty**: Bold+numbered+sentence-case lines now get -0.10 instead of -0.30. Prevents definition headings ("6. Exclusions") from being penalized as body text.
- `data/reports/dse024_threshold_experiment_v3.md` — corrected post-fix threshold experiment report.
- `runs/sessions/2026-06-04-dse024-parser-remediation-phase-c.md` — Phase C session log.

### Changed
- `structure_parser/heading_patterns.py` — added letter-numbering pattern to NUMBERING_PATTERNS.
- `structure_parser/heading_scorer.py` — added WEIGHTS entries for `has_toc_dots` (-0.30), `short_all_caps_numbered` (-0.25), `has_tab_char` (-0.30). Added `short_all_caps_numbered` and `has_tab` to `compute_features()`. Added sentence-case penalty reduction for bold+numbered in `feature_contributions()`. Added letter-numbering to `_numbering_token()` and `_level_hint()`.
- `data/interim/dse020/logical/` — all 647 heading_candidates.json files regenerated with new scorer.

### Results
- **Gold heading eval: 20/20 PASS** (no regression at threshold 0.5)
- **FP ratio improved**: at t=0.45, from 54.2% (pre-fix) to 44.4% (post-fix)
- **List/Item Risk reduced 46%**: 61 → 33
- **TOC Risk reduced 9%**: 55 → 50
- **Real headings minimally affected**: 136 → 134 (-1.5%)
- **Full pytest: 393/393 PASS**

### Known Issues
- 56/132 zero-clause policies gain ≥1 heading at t=0.45, but FP ratio (44.4%) is still above 25% target.
- Aditya Birla and Tata AIG gold policies still have 0 headings at t=0.5 in DSE-020 pipeline (different physical extraction than gold corpus).
- Section tree builder has not been updated to handle the 134 real headings at t=0.45.

## 2026-06-04 (DSE-024 — Phase A Classification Complete)

### Added
- `scripts/dse024_classify_zero_clause_policies.py` — automated classifier for 132 zero-clause policies using conservative heuristics (document_type, slug keywords, heading score, duplicate hash groups).
- `data/reports/dse024_zero_clause_classification_v1.json` — full JSON classification output.
- `data/reports/dse024_zero_clause_classification_v1.md` — Markdown classification summary.

### Changed
- `data/reports/dse024_zero_clause_policy_audit_plan.md` — appended Phase A results and recommended 20-policy sample for Phase B.
- `runs/sessions/2026-06-04-dse024-full-corpus-parser-remediation-plan.md` — updated with Phase A completion.

### Classification Results
- HEADING_MISS: 117 (88.6%) — heading scorer produces candidates but none above 0.5
- NON_POLICY: 9 (6.8%) — brochures, CIS, prospectus, product list
- DUPLICATE: 6 (4.5%) — duplicate-hash entries
- SECTION_FAIL: 0 — no headings above threshold for section tree to fail on
- PHYSICAL_BAD: 0 — all 132 had successful physical extraction
- UNSUPPORTED: 0 — all remaining had usable text
- UNKNOWN: 0 — all classified

Key finding: 53/117 HEADING_MISS policies have max heading score >= 0.45,
meaning a small threshold reduction from 0.50 to ~0.45 would capture nearly half.

## 2026-06-04 (DSE-024 — Phase B Sample Inspection Complete)

### Added
- `scripts/dse024_inspect_zero_clause_sample.py` — deep inspection script for 20 representative zero-clause policies.
- `data/reports/dse024_zero_clause_sample_inspection_v1.json` — full JSON inspection output with per-policy top-20 candidates, classification, root cause, and false-positive risk.
- `data/reports/dse024_zero_clause_sample_inspection_v1.md` — Markdown inspection summary with per-policy deep dives, concrete heading examples, and recommended parser changes.

### Changed
- `data/reports/dse024_zero_clause_policy_audit_plan.md` — appended Phase B results with root cause distribution, key findings, and recommended parser changes ranked by impact.

### Phase B Findings
- **threshold_too_high**: 9/20 policies (real headings at 0.45-0.499 but miss 0.5)
- **needs_manual_review**: 5/20 policies (need human inspection of physical text)
- **missing_feature_spacing**: 2/20 (headings lack gap-based spacing signal)
- **missing_feature_numbered_heading**: 1/20 (letter prefixes A., B. not matched)
- **missing_feature_all_caps**: 1/20 (all-caps headings not bold/not numbered)
- **non_policy/duplicate**: 2/20 (already classified in Phase A)

Highest-leverage fix: lower threshold to 0.45 (helps 12/20 inspected policies).
**Warning:** Do NOT blindly lower — TOC-dominated and procedure-code-dominated documents would admit false positives.

## 2026-06-04 (DSE-024 — Full-Corpus Parser Remediation Planning)

### Added
- DSE-024 planned: classify and fix 132 zero-clause policies from DSE-020 triage. Blocks DSE-021 (extractor wave 2).
- `runs/sessions/2026-06-04-dse024-full-corpus-parser-remediation-plan.md` — planning session log.
- `data/reports/dse024_zero_clause_policy_audit_plan.md` — audit plan for classifying zero-clause failures.

### Changed
- `docs/tasks.md` — DSE-020 moved to Completed; DSE-024 added as active; DSE-021 set to blocked.
- `IMPLEMENTATION_PLAN.md` — roadmap reordered: DSE-024 before DSE-021; rationale documented.
- `docs/risk_register.md` — added R25 for 132 zero-clause policies.

## 2026-06-04 (DSE-020 — Final Acceptance)

### Changed
- DSE-020 accepted and finalized. Status set to `done` in docs/tasks.md.

## 2026-06-04 (DSE-020 — Artifact Hygiene + Final Checks)

### Fixed
- **Generic 20-policy benchmark reports overwritten**: DSE-020 batch DB/export run wrote to generic summary paths (`dse010_sqlite_build_summary.json`, `dse011_fact_scoring_summary.json`, `dse013_export_summary.json`). Restored from git.
- **Stale export dirs**: 2 stale export directories from the pre-fix first attempt remained on disk (bajaj_allianz_silver_health, future_generali_health_elite). Removed.
- **Export count discrepancy**: Triage report counted 568 exports (via glob, included stale dirs). Now correctly shows 566.

### Added
- `data/reports/dse020_sqlite_full_summary.json` — DSE-020-specific clause store summary (591 policies).
- `data/reports/dse020_fact_scoring_full_summary.json` — DSE-020-specific fact scoring summary (591 policies, regenerated).
- `data/reports/dse020_export_full_summary.json` — DSE-020-specific export summary (566 policies).

### Changed
- `docs/tasks.md` — DSE-020 status corrected from `done` to `in_progress`.
- `IMPLEMENTATION_PLAN.md` — updated current state to 2026-06-04; full 647-policy run no longer marked pending.
- `dse-020-tracking` — Phase 5 checklist updated with current completion status.

### Validation
- Gold corpus validator: PASSED (20/20 reviewed, 400 facts).
- Source-span validation: ALL CHECKS PASSED (591 docs, 0 FK violations, 548135 valid spans).
- Full pytest: 393/393 PASSED.
- `git diff --check`: PASSED.

## 2026-06-04 (DSE-020 — Full 647-Policy Pipeline Dry Run + Scale Triage)

### Added
- `data/reports/dse020_scale_triage_report_v1.json` — comprehensive scale triage report with per-stage counts, top not_found concepts, structural warnings, and recommended fixes.
- `data/reports/dse020_scale_triage_report_v1.md` — Markdown version of the scale triage report.

### Changed
- `scripts/run_clause_store.py` — added duplicate-hash skip logic in `main()`. Tracks `seen_document_ids` set; skips slugs whose document_id was already processed; cleans stale resolved facts for skipped slugs via `shutil.rmtree()`; summary now includes `policies_skipped_duplicate_hash`.
- `scripts/validate_source_spans.py` — added diagnostic print showing manifest entry count vs unique document_id count when `--manifest` is used.

### Fixed
- **Duplicate-hash document identity issue**: The DSE-020 manifest has 647 entries but only 591 unique document hashes (56 entries share document_ids). Previously, the clause store ingested ALL 647 slugs, causing doubled sections/clauses for shared-document_id entries. Now, the second (and subsequent) slug per document_id is skipped with a recorded reason in the build summary.

### Results
- Clause store: **591/647 ingested** (56 skipped duplicate hash), DB 1938.17 MB.
- Source-span validation: **ALL CHECKS PASSED** — 591 source_documents, 0 FK violations, count parity exact, 548135 valid source_spans, 3628 resolved facts verified.
- Fact scoring: **598/647 policies** processed, 14792 candidates, 3759 facts, 0 conflicts, 0 FK violations.
- Export: **566/591 policies** exported (25 had 0 resolved facts).
- Triage report key findings:
  - Full 647 per-policy run: 100% stage completion across all 5 stages.
  - 132 policies with zero headings and zero clauses (parser/section-tree gap).
  - 133 policies with zero fact candidates (extractor input coverage gap).
  - Top not_found concepts: claim_intimation_timeline, deductible, icu_limit (568 each).

### Known Issues
- 56 duplicate-hash entries in the manifest share document_ids with other entries. The clause store skips the second occurrence to avoid double-counting sections/clauses. This is a corpus identity issue — the same PDF was obtained from different sources (IRDAI vs website) and appears under two slugs.
- 132 policies have zero clauses and zero headings, indicating fundamental parser/section-tree gaps that need remediation before full production readiness.
- 133 policies have zero fact candidates, likely downstream of the zero-clause issue.

## 2026-06-03 (DSE-020 — Full 647-Policy Scale Triage Infrastructure)

### Added
- `scripts/build_dse020_manifest.py` — builds a collision-safe 647-policy DSE-020 run manifest with reviewed-gold source-path mapping.
- `scripts/run_pipeline_batch_dse020.py` — DSE-020 namespaced per-policy runner for physical, heading, section, table, and fact stages with append-only progress JSONL and atomic summary writes.
- `scripts/dse020_triage_report.py` — generates JSON/Markdown scale triage reports from manifest, progress, SQLite, and export outputs.
- `tests/test_dse020_manifest.py` — tests slug generation, gold mapping, collision suffixing, and manifest validation.
- `data/manifests/dse020_run_manifest_v1.json` — 647-policy manifest with 647 unique slugs, 20 reviewed-gold mappings, 0 missing PDFs, and 9 collision groups.
- DSE-020 smoke reports under `data/reports/dse020_*_smoke*`.

### Changed
- `scripts/run_clause_store.py` — added optional manifest-driven policy discovery, metadata fallback for non-gold policies, `--limit`, `--slug`, and configurable summary output.
- `scripts/run_fact_scoring.py` — added optional manifest-driven policy discovery, configurable physical root, `--limit`, `--slug`, and configurable summary output.
- `scripts/run_export.py` — added configurable summary output.
- `scripts/validate_source_spans.py` — added optional manifest-driven source artifact parity validation for DSE-020 roots.
- `dse-020-tracking` and DSE-020 session log — updated with short-context executor packet protocol and smoke results.
- `docs/tasks.md` — DSE-020 marked `in_progress` with Phase 0/1 progress.

### Results
- Manifest generation: **PASS** — 647 policies, 647 unique slugs, 20 reviewed-gold mappings, 0 missing PDFs.
- Per-policy smoke: **PASS** — 39 policies processed across all five per-policy stages with 0 stage failures.
- Clause-store/source-span smoke: **PASS** — 20 reviewed-gold policies, 0 FK violations, source artifact parity passed against DSE-020 roots.
- Fact scoring smoke: **PASS** — 20/20 policies, 665 candidates, 181 facts, 0 conflicts, 0 FK violations.
- Export smoke: **PASS** — 20/20 policies exported under `data/export/dse020`.

### Known Issues
- Full 647-policy run has not started yet.
- Smoke triage reproduces known parser weaknesses for Tata AIG and Aditya Birla: zero headings, zero clauses, zero fact candidates in DSE-020 generated outputs.

## 2026-06-02 (DSE-019 — Canonical Insurance Concept Ontology Registry v1)

### Added
- `ontology/concepts.v1.json` — canonical registry for the 20 priority Product A concepts, including value shapes, export fields, extractor status, evidence requirements, allowed statuses, and Product B display rules.
- `ontology/loader.py` and `ontology/validator.py` — lightweight registry loading and validation helpers.
- `tests/test_ontology.py` — drift tests between ontology, export mapping, extractor targets, fact statuses, and gold fact labels.

### Changed
- `docs/tasks.md` — reset active roadmap after DSE-018 and added DSE-019 through DSE-023 planning sequence.
- `IMPLEMENTATION_PLAN.md` — updated from early 7-day execution plan to current-state roadmap with ontology as the next control-plane layer.
- `docs/data_contracts.md` — added ontology registry contract.
- `docs/export_contract.md` — clarified that exported concept fields are governed by the ontology registry.
- `docs/decisions.md` — added ADR-0038 for ontology as canonical concept source.

### Known Issues
- Runtime extractor/export modules still use their existing local constants; DSE-019 validates consistency but does not refactor runtime code to read directly from ontology.
- Full 647-policy production-scale quality remains unproven until DSE-020.

## 2026-06-02 (DSE-018 — Deterministic Extractor Expansion Wave 1)

### Added
- Wave 1 deterministic extractors for renewability, claim settlement timeline, AYUSH coverage, ambulance coverage, cumulative bonus/NCB, specific disease waiting periods, maternity waiting, and organ donor coverage.
- Regression tests for claim-settlement false positives, slash-separated specific disease waiting periods, PED-definition leakage, and maternity `not covered until N months` wording.
- `data/reports/dse018_wave1_mismatch_audit.md` — source-backed audit of the final 10 mismatch rows.
- `runs/evals/2026-06-02-fact-extraction-dse018-final.json` — final passing 20-policy fact extraction eval for 13 concepts.

### Changed
- `extractors/deterministic.py` — tightened claim-settlement, specific disease, and maternity extraction for expanded-corpus formats and column-interleaved PDF text.
- `gold_corpus/policies/*/facts.json` — corrected source-proven fact labels for the final DSE-018 mismatch audit.
- `tests/test_fact_extractors.py` — updated registry coverage test from 5 concepts to all 13 active deterministic concepts.
- `docs/evaluation.md` — updated Fact Extraction eval to the DSE-018 13-concept Wave 1 gate and result.

### Results
- Fact extraction eval: **PASS** — 20/20 policies, precision 100.00%, recall 99.49%, normalized value accuracy 100.00%, status accuracy 98.46%, evidence accuracy 100.00%, false-present count 0.
- Clause-store/source-span evals: **PASS** — 20 policies, 56,854 lines, 4,190 sections, 10,330 clauses, 0 FK violations, 0 provisional resolved evidence IDs, DB 82.45 MB.
- Fact scoring eval: **PASS** — 746 candidates, 203 facts, status accuracy 98.5%, normalized value accuracy 97.5%, evidence accuracy 100.0%, false-present count 0.
- Export eval: **PASS** — 20 exports, 20/20 concepts per policy, 0 present facts missing evidence, gold status accuracy 98.5%, gold value accuracy 97.5%, false-present count 0.
- Full pytest: **PASS** — 382/382.

### Known Issues
- Reliance Health Gain claim-settlement primary 30-day source text is present in the PDF but absent from the current section-tree clauses. The extractor emits `not_found` rather than a wrong 45-day investigation value.
- Remaining 7 non-Wave-1 concepts stay explicit `not_found` until later extractor or LLM-refinement tasks.

## 2026-06-02 (DSE-017 — 20-Policy End-to-End Pipeline Rebuild + Fact Regression Remediation)

### Changed
- `scripts/eval_clause_store.py` — removed hardcoded 5-policy count and `_EXPECTED_COUNTS` constant. Policy count derived dynamically from gold_corpus. DB size limit raised 30MB → 120MB (ADR-0035).
- `scripts/eval_fact_scoring.py` — removed hardcoded 5-policy count. Dynamic from gold_corpus.
- `scripts/eval_export.py` — removed hardcoded 5-policy count. Dynamic from gold_corpus.
- `scripts/eval_fact_extractors.py` — removed hardcoded `GOLD_POLICIES` set for gate count. Uses `_discover_reviewed_policies()`.
- `scripts/validate_source_spans.py` — removed hardcoded `_EXPECTED_POLICY_COUNT = 5`. Dynamic from gold_corpus.
- `scripts/run_clause_store.py`, `scripts/run_fact_scoring.py` — updated docstrings from "5 policies" to "all reviewed policies".
- `scripts/eval_fact_extractors.py`, `scripts/eval_fact_scoring.py`, `scripts/eval_export.py` — value comparison now allows predicted metadata supersets only when all gold scalar keys match exactly.
- `structure_parser/section_tree.py` — preserves pre-heading body content when the first detected heading appears very late.
- `extractors/deterministic.py` — tightened 5 existing deterministic extractors for the 20-policy corpus without adding new concepts.
- `normalizers/duration.py` — supports hyphenated durations and adjective-separated durations such as `30-day` and `48 consecutive months`.

### Added
- `data/reports/dse017_fact_regression_audit.md` — source-backed audit of every failed concept-policy pair from the first 20-policy semantic run.

### Results
- Initial DSE-017 rebuild exposed semantic regressions: precision 76.9%, value accuracy 82.2%, 5 false present. This failed run is preserved in the `*-dse017-20-policy.json` eval artifacts.
- Remediation rebuilt SQLite at 20-policy scale: 82.31 MB, 20 source_documents, 56,854 lines, 4,190 sections, 10,330 clauses, 26,405 source_spans.
- 282 fact candidates, 83 extracted facts, 0 conflicts, 0 FK violations.
- 20 policy exports, each with 20 concept fields.
- Structural evals (clause store, source spans): **PASS**.
- Gold-comparison evals after remediation (fact extraction, fact scoring, export): **PASS** — 100% status accuracy, 100% normalized value accuracy, 100% evidence accuracy, 0 false present for the 5 implemented concepts.

### Known Issues
- DSE-017 still validates only the 5 implemented deterministic concepts. The remaining 15 export concepts remain explicit `not_found` until extractor expansion.
- Some fact evidence spans are clause-level degraded because the source text is column-interleaved; source-span validation records these as resolved but not exact substring offsets.
- Diagnostic section-tree regression eval is 19/20; Oriental Cancer Protect still misses the tree-accuracy threshold while section and clause F1 remain 100%.
- Table engine eval (R20) still uses 5-policy assumptions.

---

## 2026-06-01 (DSE-012 — Gold Corpus Expansion, Human Review Complete)

### Added
- `scripts/human_review_dse012_gold.py` — reproducible source-PDF review/promoter for the 15 DSE-012 draft policies.
- `data/reports/dse012_human_review/` — per-policy review reports plus consolidated human-review summary.
- `runs/evals/2026-06-01-gold-corpus-dse012-reviewed.json` — passing 20-policy gold corpus eval artifact.
- Expanded parser regression eval artifacts for heading, section tree, table, and fact extraction against the reviewed corpus.

### Changed
- Promoted all 15 DSE-012 draft policy folders to reviewed gold annotations.
- `scripts/validate_gold_corpus.py` — now treats all 20 policies as reviewed, requires 400 fact annotations, and rejects remaining draft markers.
- `docs/tasks.md` — DSE-012 marked done.
- `docs/evaluation.md` — Gold Corpus eval updated with the 20-policy DSE-012 result.

### Fixed
- Tata AIG and Aditya Birla section/heading/clauses were manually rebuilt from source-PDF/physical-line review after degenerate pipeline trees.
- DSE-012 fact annotations now use manual extraction status, source-document objects, review pass metadata, and evidence text for every present / explicitly-not-covered fact.
- Removed lingering draft status markers from promoted DSE-012 annotation JSON files.

### Known Issues
- Expanded heading scorer eval fails on Tata AIG and Aditya Birla; parser remediation is deferred to a future parser task.
- Expanded section tree eval fails on Tata AIG, Aditya Birla, and Oriental Cancer Protect; these failures are recorded as downstream parser quality findings.
- Table eval still contains 5-policy-era hard-gate wording and needs a follow-up update for 20-policy reporting.

---

## 2026-06-01 (DSE-012 — Gold Corpus Expansion, Phase A-C Infrastructure)

### Added
- `scripts/run_pipeline_batch.py` — full pipeline batch orchestrator (physical→headings→sections→tables→facts).
- `scripts/generate_draft_gold.py` — converts pipeline output to draft gold annotations (7 files per policy, all marked `label_status: draft`).
- `scripts/gold_review_report.py` — per-policy human review report generator with priority triage (CRITICAL/HIGH/NORMAL).
- `data/manifests/dse012_gold_expansion_candidates_v1.json` — 15-policy selection manifest with rationale.
- `data/reports/dse012_policy_selection_rationale.md` — diversity analysis and selection criteria.
- 15 new draft policy directories under `gold_corpus/policies/` — 105 annotation files total (7 per policy).
- `data/reports/dse012_review/review_report.md` — consolidated human review report.

### Changed
- `scripts/validate_gold_corpus.py` — accepts 20 policies (5 reviewed + 15 draft). Structural sanity checks for all 7 draft files (metadata label_status, section_id presence, fact count=20, etc.). Docling/annotation pass checks skipped for drafts.
- `scripts/gold_review_report.py` — elevated priority for policies with < 3 heading labels but > 1 section (catches partial heading detection failures).
- `identity/plan_normalizer.py` — NBSP (`\xa0`) normalization + broad legal entity suffix stripping (`", {INSURER} Company Limited"`). Fixes Tata AIG and SBI General plan names.

### Pipeline Results (15 new policies)
- 15/15 policies processed, 75/75 stages passed.
- 595 pages, 44,139 lines, 6,279 clauses, 600 tables, 75 extracted facts.
- 2 CRITICAL policies (Tata AIG, Aditya Birla — degenerate section trees).
- 2 HIGH policies (Niva Bupa, Royal Sundaram — very few heading labels).
- 11 NORMAL policies.
- Status: **paused at human review (Phase D)**.

### Known Issues
- Tata AIG and Aditya Birla heading detection failures — heading scorer found no visual headings. Parser remediation deferred until after DSE-012 review.
- 15/20 concepts per policy need manual annotation (no extractors implemented).
- Existing 5 reviewed gold policies unchanged.

---

## 2026-06-01 (DSE-015 — Insurer/Plan Normalizer Library)

### Added
- `identity/uin_utils.py` — canonical UIN base extraction via V-delimiter (ADR-0030). Replaces buggy `[:11]` hardcoded slice.
- `identity/insurer_registry.py` — 32-insurer registry with canonical_name, legal_name, display_name, folder_aliases, IRDAI prefix (ADR-0032). Subsumes DSE-002 FOLDER_TO_LIFECYCLE.
- `identity/plan_normalizer.py` — plan name cleanup: strips insurer suffixes, generic boilerplate, produces display_name and short_name (ADR-0031).
- `tests/test_identity.py` — 45 unit tests (UIN parsing, registry, plan normalization, backward compat, regression).
- `runs/evals/2026-06-01-export-dse015-v1.json` — passing export eval with identity gates.

### Changed
- `clause_store/schema.sql` — products table: +display_name, +short_name, +match_confidence, +match_method. product_versions table: +version_number, +approval_date, +financial_year.
- `clause_store/models.py` — Product and ProductVersion dataclasses extended with new fields.
- `clause_store/repository.py` — insert_product() and insert_product_version() updated for new columns.
- `scripts/run_clause_store.py` — uses identity library for UIN parsing, plan cleaning, lifecycle enrichment. Fixes uin_base truncation bug (ADR-0030).
- `derived/export_builder.py` — product_identity block now emits all 9 fields: insurer, plan_name, display_name, uin, uin_base, product_version, effective_date, match_confidence, match_method.
- `derived/schema_validator.py` — validates product_identity completeness: uin_base >= 12 chars, display_name required, plan_name must not contain insurer.
- `tests/test_export.py` — fixture updated with display_name, version_number, approval_date.

### Fixed
- **uin_base truncation**: `run_clause_store.py:157` hardcoded `full_uin[:11]` producing 11-char bases. Now uses V-delimiter via `identity.uin_utils.extract_uin_base()` producing correct 12-char bases for all 5 gold policies.
- **Plan name insurer contamination**: "Arogya Sanjeevani Policy, HDFC ERGO" → "Arogya Sanjeevani". "Medi Classic Accident Care Individual Insurance Policy" → "Medi Classic Accident Care".
- **Missing export fields**: product_version, effective_date, match_confidence, match_method now populated from lifecycle data and UIN match report.

---

## 2026-06-01 (DSE-013 — Derived Export, 20-Concept Skeleton)

### Added
- `derived/__init__.py`, `derived/field_mapping.py` — 20-concept → export field mapping with scalar/compound value extraction.
- `derived/export_builder.py` — builds policy_features.json (20-concept view with evidence provenance), policy_fact_sources.json (full candidate provenance), policy_clauses_minimal.json (lightweight clause context).
- `derived/schema_validator.py` — validates exported JSON against export_contract.md shape.
- `scripts/run_export.py` — batch CLI: reads from SQLite, writes 3 JSON files per policy to data/export/{policy_id}/, persists to derived_policy_features table.
- `scripts/eval_export.py` — 14 hard gates: schema completeness, evidence integrity (including evidence_clause), cross-file page consistency, gold value/status comparison, false-present detection.
- `tests/test_export.py` — 41 unit tests covering field mapping, export builder (including evidence_clause fallback), fact sources, clauses minimal, schema validator, cross-file page consistency, end-to-end.
- `data/reports/dse013_export_summary.json` — committed build summary.
- `runs/evals/2026-06-01-export-dse013-v1.json` — initial eval artifact (pre-evidence_clause and cross-file gates).
- `runs/evals/2026-06-01-export-dse013-v2.json` — final passing eval artifact (14 gates).
- ADR-0027 through ADR-0029 documenting export design decisions.

### Results
- 5/5 policies exported with 20 concepts each (100 feature entries total).
- Fill rate: 25% (5/20 concepts have extractors; 15 are not_found — correct and expected).
- Schema validation: 0 errors across 5 exports.
- Gold status accuracy (5 concepts): 100% (25/25).
- Gold value accuracy (5 concepts): 100% (23/23).
- Evidence integrity: 23/23 source_span_ids exist in SQLite.
- False present: 0.
- derived_policy_features table: 5 rows populated.

### Known Issues
- 15/20 concepts are not_found (no extractors yet).
- evidence_clause shows source-local clause number (e.g., "4.1") not a stable ID.
- policy_clauses_minimal truncates clause text to 500 chars.

---

## 2026-06-01 (DSE-011 — Fact Candidate Scoring + Conflict Resolution)

### Added
- `extractors/scoring.py` — composite scoring: confidence (0.50) + evidence quality (0.30) + pattern specificity (0.15) + source priority (0.05). ADR-0025.
- `extractors/conflict_detector.py` — detects value/status/scope disagreements among accepted candidates for same (document, concept). Resolves via higher_score_wins or manual_review. ADR-0026.
- `scripts/run_fact_scoring.py` — batch ingest: scores 76 candidates, inserts into `extracted_fact_candidates` (76 rows) and `extracted_facts` (23 rows), runs conflict detection (0 conflicts for v1).
- `scripts/eval_fact_scoring.py` — 12 hard gates: parity, FK, precision, status/value/evidence accuracy, false-present, conflict resolution, cross-doc links, accepted candidate min score.
- `tests/test_fact_scoring.py` — 48 unit tests covering scoring, conflict detection (synthetic conflicts), persistence, gold comparison, end-to-end pipeline flow, and accepted-candidate threshold validation.
- `data/reports/dse011_fact_scoring_summary.json` — committed build summary.
- `runs/evals/2026-06-01-fact-scoring-dse011-v1.json` — initial eval artifact (pre-min-score gate).
- `runs/evals/2026-06-01-fact-scoring-dse011-v2.json` — final passing eval artifact (includes accepted_candidate_min_score gate).
- ADR-0023 through ADR-0026 documenting schema refinement, fact storage policy, scoring formula, conflict detection.

### Changed
- `clause_store/schema.sql` — refined deferred DDL for `extracted_fact_candidates` (expanded from 14 to 22 columns), `extracted_facts` (added source_candidate_id, source_clause_id, CHECK constraint on fact_status), `fact_conflicts` (added document_id, concept, pipeline_run_id, CHECK constraints on conflict_type and resolution). Added indexes.
- `clause_store/models.py` — added ExtractedFactCandidate, ExtractedFact, FactConflict dataclasses.
- `clause_store/repository.py` — added insert_fact_candidates(), insert_extracted_facts(), insert_fact_conflicts(), query_facts_for_document(), query_candidates_for_document(), query_conflicts_for_document(), count_facts_by_concept().

### Results
- 76 candidates persisted (parity: 100% per-document)
- 23 extracted facts persisted (parity: 100% per-document)
- Fact status accuracy: 100% (25/25 concept-policy pairs match gold)
- Normalized value accuracy: 100% (23/23 present facts match gold)
- Evidence accuracy: 100% (23/23 evidence_span_ids point to valid source_spans)
- False present: 0
- Conflicts: 0 (expected — single extractor per concept)
- FK violations: 0
- Cross-document fact links: 0

### Known Issues
- 0 production conflicts (proven via synthetic tests only — 1 extractor per concept)
- Only 5 of 20 gold concepts evaluated; remaining 15 need new extractors (future task)
- Composite score weights (0.50/0.30/0.15/0.05) are reasonable defaults, not empirically tuned

---

## 2026-05-31 (DSE-010 — SQLite identity remediation)

### Added
- Source-artifact count parity gates for DSE-010: `document_lines=12,715`, `document_sections=1,156`, `policy_clauses=2,522`.
- Cross-document source span consistency checks.
- Resolved fact span existence/document/clause/text validation.
- ADR-0022 documenting SQLite namespaced IDs for document-local artifacts.
- `runs/evals/2026-05-31-clause-store-dse010-v2.json` — passing DSE-010 v2 eval artifact.
- `runs/sessions/2026-05-31-clause-store-source-spans-v2.md` — remediation session log.

### Changed
- `document_lines`, `document_sections`, and `policy_clauses` now use globally namespaced DB IDs while preserving original local IDs in `source_*` columns.
- `source_spans.clause_id` and `document_tables.parent_clause_id` now point to global clause UIDs.
- Resolved facts now include `evidence_clause_uid`, `evidence_document_id`, and `evidence_line_uids`.
- SQLite runs use rollback journal mode to avoid generated WAL/SHM sidecars in `git status`.
- `docs/database_strategy.md` now documents the 19-table SQLite store and namespaced ID strategy.

### Fixed
- Fixed silent cross-policy overwrites caused by repeated local IDs such as `p1l_1` and `clause_0000`.
- Fixed validators/eval that previously compared the DB to itself instead of checking source JSON row parity.
- Added fallback clause source spans for clauses without resolvable line IDs so clauses are not silently dropped.

### Known Issues
- 16/23 (69.6%) fact evidence spans still have clause-level char offsets because exact DSE-007 evidence snippets do not always align with current clause text boundaries.
- `document_text_spans` remains intentionally unpopulated per ADR-0017.

---

## 2026-05-31 (DSE-010 — Clause Store + Source Spans)

### Added
- `clause_store/` package: `schema.sql` (19-table SQLite DDL), `models.py` (dataclasses), `repository.py` (init_db, insert_*, query_*, backfill_table_parent_clauses), `span_builder.py` (clause/evidence/cell spans), `fact_resolver.py` (provisional ID resolution).
- `scripts/run_clause_store.py` — batch ingest CLI for 5 gold policies.
- `scripts/validate_source_spans.py` — structural integrity validator.
- `scripts/eval_clause_store.py` — hard gate eval with 6 gates.
- `tests/test_clause_store.py` — 59 unit tests (schema, inserts, span builder, fact resolver, table parent clause, bbox IoU).
- `data/reports/dse010_sqlite_build_summary.json` — committed build summary artifact.
- `runs/sessions/2026-05-31-clause-store-source-spans.md` — session log.
- `runs/evals/2026-05-31-clause-store-dse010-v1.json` — passing eval artifact.

### Changed
- `docs/evaluation.md` — Clause Store + Source Spans eval layer added; hard gates table updated.
- `docs/tasks.md` — DSE-010 marked done; detail block added; completed table updated.
- `docs/changelog.md` — DSE-010 entry.
- `docs/decisions.md` — ADR-0017 through ADR-0021 added.
- `docs/open_questions.md` — OQ-001 marked answered (ADR-0021).

### Key results
- 5,915 source_spans across 5 gold policies (2,301 clause_body, 3,591 table_cell, 23 fact_evidence).
- 23/23 accepted present facts resolved to real source_span_ids (0 provisional IDs remaining).
- 192/197 tables (97.5%) parent_clause_id resolved via bbox overlap (avg IoU 0.67).
- DB size: 7.92 MB. FK violations: 0. Clause span coverage: 100%.

### Known Issues
- 16/23 (69.6%) fact evidence spans have clause-level char offsets (char_start=0) because DSE-007 evidence_text boundaries predate current clause segmentation.
- `document_text_spans` DDL exists but not populated (ADR-0017).
- `extracted_facts`, `fact_conflicts`, `derived_policy_features` deferred to DSE-011/DSE-013.

---

## 2026-05-31 (DSE-009 — Table Engine v1 finalization)

### Added
- `gold_corpus/policies/*/physical_table_labels.json` — 18 physical table labels across 5 policies for DSE-009 hard gates.
- `runs/evals/2026-05-31-table-engine-dse009-v3.json` — passing physical table eval artifact.
- `data/reports/dse009_gold_table_source_review.json` and `.md` — disposition report for all 26 legacy DSE-003 `tables.json` rows.
- Header lineage fields on table cells and table records.
- Conservative `pdfplumber_text` extraction path for small, headered borderless grids.

### Changed
- DSE-009 eval now uses physical table labels for hard gates and treats legacy semantic table annotations as audited context.
- Table matching now uses one-to-one matching with bbox IoU plus type/content signatures.
- Gold validator now checks `physical_table_labels.json` for every gold policy.
- DSE-009 task status moved to done after v3 gates passed.

### Fixed
- DSE-009 no longer fails because prose-derived fact summaries are evaluated as physical tables.
- Type classification improved for physical benefit grids that mention sum insured but are not premium tables.
- `pdfplumber_text` output is filtered to avoid large page-body false tables.

### Known Issues
- Parent clause assignment remains provisional until DSE-010 source-span/bbox overlap.
- DSE-012 should expand physical table labels and review additional bboxes across more policies.

---

## 2026-05-31 (DSE-009 — Table Engine v1 remediation)

### Added
- `runs/evals/2026-05-31-table-engine-dse009-v2.json` — strict DSE-009 eval artifact.
- `data/reports/dse009_header_lineage_review.json` — header lineage review report.
- `data/reports/dse009_gold_table_annotation_audit.json` — gold/table mismatch audit.
- Unit tests for strict table eval matching, raw-line preservation, parent-clause specificity, and title-row header detection.

### Changed
- `scripts/eval_table_engine.py` now separates same-page table presence from strict type/content detection and records git commit metadata.
- `scripts/run_table_engine.py` now assigns provisional parent clauses by shortest containing page span plus owning section depth instead of a nonexistent clause level.
- `table_engine/text_alignment_detector.py` now preserves `raw_lines` for ambiguous borderless candidates and keeps `cells=[]`.
- `table_engine/table_detector.py` now clamps heading-context crops to page bounds and records missing cell bboxes as explicit issues.
- `table_engine/cell_extractor.py` now detects header rows across the first 3 rows, allowing title rows above real headers.
- `docs/tasks.md` and `docs/evaluation.md` now mark DSE-009 as `in_progress` because strict v2 gates fail.

### Known Issues
- Strict v2 eval fails: priority content detection recall is 57.1% against the 85% gate; header lineage pass rate is 20% against the 85% gate.
- Some gold table annotations are manual fact summaries over prose rather than physical tables, so they need source-PDF review before DSE-009 can be accepted.

---

## 2026-05-31 (DSE-009 — Table Engine v1 first pass)

### Added
- `table_engine/__init__.py` — package init.
- `table_engine/models.py` — Pydantic models: TableCell, ExtractedTable, TableDocument, ExtractionMethod (pdfplumber_lattice, text_alignment_candidate), TableType (6 types + unknown), ColumnCluster.
- `table_engine/table_detector.py` — primary lattice detection via pdfplumber.find_tables(); stable table IDs; per-cell bbox extraction.
- `table_engine/text_alignment_detector.py` — fallback column x-cluster heuristic for borderless tables; emits cells=[] with "cells_not_reliably_split" issue when column split is ambiguous.
- `table_engine/table_type_classifier.py` — keyword-based type scorer (no ML); 6 types; room_rent vs schedule_of_benefits disambiguation.
- `table_engine/cell_extractor.py` — cell grid → structured TableCell list; header detection by known header terms; None→"" normalization.
- `scripts/run_table_engine.py` — batch CLI; two-tier detection; type classification; parent clause assignment; outputs document_tables.json + document_table_cells.json per policy.
- `scripts/eval_table_engine.py` — gold corpus eval; hard gate checking; per-policy and aggregate metrics; JSON artifact output.
- `tests/test_table_engine.py` — 43 unit tests covering models, classifier, cell extractor, text alignment detector, column clustering.
- `data/reports/dse009_table_bbox_review_candidates.json` — predicted bboxes for manual DSE-012 gold upgrade.
- `runs/evals/2026-05-31-table-engine-dse009-v1.json` — passing DSE-009 eval artifact.
- `runs/sessions/2026-05-31-table-engine-v1.md` — session log.
- `docs/data_contracts.md` — Contract 3C: Table Engine Output.

### Changed
- `docs/evaluation.md` — Table Extraction eval moved to active with DSE-009 commands, results, and hard gate status.
- `docs/tasks.md` — DSE-009 marked done after hard gates passed; task detail block added.
- `docs/decisions.md` — ADR-0014 (pdfplumber-only v1 table extraction), ADR-0015 (keyword classifier for table type).

### Known Issues
- Type accuracy is 54% due to text_alignment_candidates classifying noisy page body text without structured cells.
- care_health_care_plus p4 (waiting_period) and p12 (room_rent) are undetectable as physical tables (definition lists).
- Parent clause ID is provisional page-range lookup; replaced by bbox overlap in DSE-010.

---

## 2026-05-30 (DSE-008 — Normalizers Library v1)

### Added
- `normalizers/indian_number_words.py` — shared number-word parsing, Indian magnitude multipliers, numeric cleanup, and hyphenated word parsing.
- `normalizers/money.py` — INR money parsing for rupee symbols, `Rs.`, `INR`, Indian comma grouping, decimals, lakh/lac/crore, and explicit special values.
- `normalizers/age.py` — age extraction with exact, greater-than, and greater-than-or-equal comparator metadata.
- `normalizers/coverage_status.py` — coverage status normalization with negation precedence.
- `scripts/eval_normalizers.py` — fixed-vector DSE-008 normalizer eval harness.
- `tests/test_normalizers/test_normalizers.py` — unit tests for money, duration, percentage, age, coverage status, and Indian number words.
- `runs/evals/2026-05-30-normalizers-dse008-v1.json` — passing DSE-008 eval artifact.
- `runs/evals/2026-05-30-fact-extraction-dse007-regression-after-dse008.json` — passing DSE-007 regression artifact after normalizer expansion.

### Changed
- `normalizers/duration.py` — preserved DSE-007 APIs while adding `yr/yrs`, hyphenated number words, and shared number parsing.
- `normalizers/percentage.py` — preserved DSE-007 APIs while adding word percentages like `twenty percent`.
- `docs/tasks.md` — DSE-008 marked done after hard gates passed.
- `docs/evaluation.md` — Normalizer Unit Tests eval moved to active with DSE-008 commands and results.
- `docs/data_contracts.md` — added normalizer result contract and allowed special statuses.

### Fixed
- Money special values such as `actuals`, `as charged`, and `subject to limit` now emit explicit symbolic normalized values instead of `0` or `null`.
- Coverage negations such as `not covered` and `not admissible` win over naive positive coverage matching.

### Known Issues
- DSE-008 does not add new extractors or table/source-span/export behavior.
- Money special values require future extractor/export interpretation before Product B display.

## 2026-05-30 (DSE-007 — First 5 Deterministic Extractors)

### Added
- `normalizers/duration.py` — minimal duration parsing for days, months, years, and common number words used by DSE-007.
- `normalizers/percentage.py` — minimal percentage parsing for co-pay extraction.
- `extractors/` package — candidate models, evidence verification, deterministic extractors, and registry/conflict resolution for `free_look_period`, `grace_period`, `ped_waiting_period`, `initial_waiting_period`, and `co_pay`.
- `scripts/run_fact_extractors.py` — batch CLI that reads DSE-006 `section_tree.json` and writes fact candidates, accepted facts, and a run summary.
- `scripts/eval_fact_extractors.py` — DSE-007 eval with precision, recall, normalized value accuracy, status accuracy, evidence accuracy, and false-present gates.
- `tests/test_fact_extractors.py` — unit and integration coverage for normalizers, extractors, registry behavior, and DSE-006 input availability.
- `runs/evals/2026-05-30-fact-extraction-dse007-v1.json` — passing DSE-007 eval over 5 gold policies.

### Changed
- `docs/tasks.md` — DSE-007 marked done after hard gates passed.
- `docs/evaluation.md` — Fact Extraction eval updated from planned to active with DSE-007 commands and results.
- `docs/data_contracts.md` — Contract 5 expanded for candidate and accepted fact schemas.
- `docs/decisions.md` — ADR-0013 added for provisional clause evidence IDs before DSE-010 source spans.
- Care Health gold fact correction: `ped_waiting_period` normalized value changed from 48 months to 36 months because the stored evidence text states 36 months.

### Fixed
- DSE-007 handles fact-bearing section headings from DSE-006 by enriching clause extraction text with the section heading line.
- Evidence text is verified before a deterministic `present` fact can be accepted.
- Co-pay extraction rejects definition-only clauses without a concrete percentage.

### Known Issues
- Evidence IDs are provisional `clause:{clause_id}` links until DSE-010 creates true source spans.
- DSE-007 intentionally does not implement table extraction, SQLite clause storage, source-span DB, LLM refinement, derived export, or Product B integration.
- DSE-008 broader normalizer work remains planned.

## 2026-05-30 (DSE-006 — Section Tree Builder)

### Added
- `structure_parser/section_tree.py` — `SectionTreeBuilder` with stack-based tree builder, level inference, content assignment, compact synthetic body-section detection, and deterministic IDs
- `structure_parser/clause_segmenter.py` — `ClauseSegmenter` with compact numbered-body clause splitting, paragraph-gap detection, and full untruncated text
- `scripts/run_section_tree.py` — CLI entry point to build section trees + clause segments for all gold policies
- `scripts/eval_section_tree.py` — evaluation script with one-to-one page-aware matching, recall-aware tree accuracy, section F1, clause F1 proxy, and missed critical section gates
- `tests/test_section_tree.py` — tests covering compact numbering, Roman subclauses, deterministic IDs, list over-generation guards, no clause truncation, CLI behavior, eval gates, and gold integrations
- `docs/adr/0012-section-tree-builder.md` — ADR: stack-based tree builder with synthetic body-numbered sections
- `docs/data_contracts.md` — Contract 3B (Section Tree Output) with full schema
- `runs/evals/2026-05-30-section-tree-v3.json` — passing DSE-006 eval over 5 gold policies

### Changed
- `docs/tasks.md` — DSE-006 marked done after v3 gates passed
- `docs/evaluation.md` — added active Section Tree / Clause Boundary eval layer with hard gates and v3 results
- `docs/decisions.md` — ADR-0012 added to Active ADRs table

### Fixed
- Compact policy numbering such as `2.1.1Accident`, `5.10RENEWAL`, and top-of-page numbered headings are now parsed.
- Dense numbered lists are no longer promoted to sections unless they align with policy structure or current gold labels.
- Eval no longer reports high tree accuracy when recall is low.

### Known Issues
- Clause boundary F1 uses a section-aligned proxy until gold clauses include physical line/span IDs.
- Section precision accounts for partial DSE-003 labels; revisit during DSE-012 gold expansion.

## 2026-05-30 (DSE-005 — Heading Candidate Scorer v2 remediation)

### Added
- `structure_parser/` package — scored heading detection for logical document structure
- `structure_parser/heading_patterns.py` — numbering regexes (decimal, compact, multi-dot, SECTION/PART prefix, Roman numeral), TOC dot pattern, 40+ heading dictionary terms, ALL CAPS and sentence case detection helpers
- `structure_parser/heading_scorer.py` — `HeadingScorer` class with font, bold, caps, numbering, dictionary, TOC, spacing, sentence-case, length, position, boilerplate, and numbered-definition features. Candidate output includes bbox, span IDs, normalized text, numbering token, level hint, and contribution breakdown.
- `scripts/run_heading_scorer.py` — CLI entry point to score all 5 gold PDFs, write a run summary, and fail loudly on missing physical outputs
- `scripts/eval_heading_scorer.py` — evaluation script with one-to-one page-aware matching against DSE-005 visual-heading labels
- `tests/test_heading_scorer.py` — tests covering numbering patterns, all-caps, sentence case, heading dictionary, TOC dots, text normalization, scorer unit tests, spacing feature, eval matching, CLI behavior, and 3 gold integration tests
- `docs/adr/0004-scored-heading-detection.md` — ADR: scored heading with 6 weighted features + 4 penalties
- `gold_corpus/policies/*/heading_labels.json` — 101 DSE-005 visual-heading labels separate from DSE-003 logical sections
- `data/interim/logical/*/heading_candidates.json` — 5 policies scored with full feature breakdown
- `runs/evals/2026-05-30-heading-scorer-v1.json` — failed first-pass eval retained for history
- `runs/evals/2026-05-30-heading-scorer-v2.json` — passing remediation eval

### Changed
- `docs/tasks.md` — DSE-005 marked done only after v2 acceptance gates passed
- `docs/evaluation.md` — split DSE-005 visual heading candidate gates from DSE-006 section tree / clause boundary gates
- `docs/data_contracts.md` — added Heading Scorer Output contract for DSE-006
- `scripts/validate_gold_corpus.py` — now validates DSE-005 `heading_labels.json` files and reports 30 policy JSON files
- `pyproject.toml` — registered the `slow` pytest marker used by gold integration tests

### Fixed
- `heading_scorer.py` font_size_ratio: changed from continuous ratio (`ratio * 0.25`) to binary (`1.0 * 0.25` if ratio > 1.0 else 0). Fixed bug where every body-sized line got +0.25 for free.
- `scripts/eval_heading_scorer.py` — removed broad substring/word-overlap matching that let one generic heading match many logical section rows
- `heading_scorer.py` — added a boilerplate company-name penalty after Care produced a non-structural company-name candidate

### Known Issues
- DSE-005 evaluates visual headings only. DSE-006 must build section trees and clause boundaries from visual headings plus logical section labels.
- ICICI headings use the same body font size and rely heavily on bold/spacing/numbering signals.

## 2026-05-29 (DSE-004 — review fixes)

### Added
- `pdf_parser/` package — physical layout extraction with pdfplumber
- `pdf_parser/models.py` — Pydantic models for PhysicalDocument, Page, Block, Line, Span, ParserIssue
- `pdf_parser/layout_extractor.py` — CLI entry point: extract PDF → document_physical.json, with gold corpus batch mode
- `pdf_parser/header_footer_detector.py` — region classification (top/body/bottom) + repeated-line tagging (no deletion)
- `pdf_parser/debug_html_generator.py` — per-page text-block overlay HTML with header/footer highlighting
- `scripts/validate_physical_outputs.py` — schema, bbox, page count, font metadata, debug HTML validation
- `scripts/run_physical_eval.py` — hard gate metrics against 5 gold PDFs with evidence coverage computation
- `tests/test_layout_extractor.py` — unit tests for bbox validation, stable IDs, header/footer detection, model roundtrip
- `docs/adr/0011-use-pdfplumber-for-physical-parsing.md` — ADR: pdfplumber over OCR/vision

### Fixed
- `pdf_parser/layout_extractor.py` — span ID linkage: `char_index` (always 0) replaced with `enumerate` counter. 617k line→span refs now resolve correctly.
- `pdf_parser/layout_extractor.py` — hardcoded absolute path replaced with `pathlib`-based relative default
- `scripts/run_physical_eval.py` — added span referential integrity gate (requires 100%). Evidence coverage set to `reported_only`, hard gate deferred to DSE-010.
- `tests/test_layout_extractor.py` — replaced vacuous bbox test with proper assertion; added span integrity tests (resolve + dangling); added 2 gold PDF integration tests (Star, HDFC).

### Changed
- docs/tasks.md — DSE-004 marked done with review-fixed acceptance criteria and actual results
- docs/evaluation.md — Physical Parser eval updated with active status and DSE-004 commands
- docs/decisions.md — ADR-0011 added (pdfplumber physical parsing)

### Added
- `gold_corpus/` — DSE-003 gold corpus with 5 policies, 25 annotation JSON files, schemas, and annotation guide
- `gold_corpus/docling_markdown/` — generated no-OCR IBM Docling markdown for Star Medi Classic Accident Care and Care Plus
- `data/reports/gold_corpus_manual_review_11_facts_v1.md` — source-PDF-only reviewer report for the 11 facts that were still marked `requires_manual_review`
- `scripts/validate_gold_corpus.py` — strict validator for gold policy folders, schemas, page references, fact statuses, and evidence coverage
- `tests/test_gold_corpus_validator.py` — pytest coverage for the gold corpus validator
- `runs/evals/2026-05-29-gold-corpus-v1.json` — Gold Corpus eval result
- `identity/` package with insurer normalizer, plan name normalizer, and UIN matcher orchestrator
- `scripts/uin_match_report.py` — DSE-002 CLI runner
- `data/manifests/uin_match_report_v1.json` — full 647-entry UIN match report
- `data/manifests/unmatched_triage_report_v1.csv` — triage CSV for entries needing review
- `data/manifests/uin_match_summary_v1.json` — summary statistics
- docs/evaluation.md — UIN Match eval layer with hard gates
- Initial project scaffold: IMPLEMENTATION_PLAN.md v2, docs/ directory
- docs/evaluation.md — 7 eval layers with hard gates
- docs/database_strategy.md — SQLite → JSON → Supabase phases
- docs/export_contract.md — Product A → Product B JSON contract
- docs/decisions.md — ADR index
- docs/development_protocol.md — Development workflow
- docs/ai_execution_protocol.md — AI agent guidelines
- docs/architecture.md — Pipeline and layered design overview
- docs/glossary.md — Domain and technical terms
- docs/data_contracts.md — Module-to-module schema contracts
- docs/risk_register.md — 18 identified risks
- docs/adr/0001-use-sqlite-for-engine.md — ADR: SQLite over Supabase for engine
- docs/adr/0002-clauses-before-fields.md — ADR: Clause-store architecture
- runs/sessions/ directory — Session logging
- runs/evals/ directory — Eval result tracking
- runs/experiments/ directory — Experiment tracking
- `scripts/corpus_lockdown.py` — main corpus lockdown script
- `data/manifests/active_policy_wordings_v1.json` — 647 active policy wordings with SHA-256 hashes
- `data/manifests/excluded_documents_v1.json` — 281 excluded documents with reasons
- `data/manifests/status_unset_review_v1.csv` — 139 policy wordings for manual triage

### Changed
- docs/tasks.md — DSE-003 marked done with gold corpus outputs and validation results
- docs/evaluation.md — added active Gold Corpus eval layer and DSE-003 result
- docs/open_questions.md — OQ-005 answered: first 5 annotations use CLI/manual JSON workflow
- README.md — current phase updated to Gold Corpus complete, Physical Parser next
- Gold corpus annotations — second pass cross-checked available IBM Docling markdown and enriched table summaries
- Gold corpus facts — third pass downgraded weak schedule-dependent labels to `requires_manual_review` for precision
- Gold corpus validator — now requires readable Docling markdown for every gold policy and rejects embedded image/base64 markdown for generated artifacts
- Star/Care annotations — fourth pass re-ran structure, table, and fact provenance checks against generated Docling markdown
- Gold corpus manual review — applied source-backed resolutions for all 11 `requires_manual_review` facts
- Gold corpus facts — final status distribution is now 77 `present`, 3 `explicitly_not_covered`, 2 `not_applicable`, 18 `not_found`, and 0 `requires_manual_review`
- Gold corpus validator/tests — now fail if any DSE-003 gold fact remains `requires_manual_review`
- Gold corpus validator — validates optional `additional_evidence` page/text entries for multi-page fact support
- `.gitignore` — allowed Markdown files under `data/reports/` so intentional review reports can be tracked
- docs/tasks.md — DSE-002 marked done with actual results (verified 646/647, 100% verified+special)

### Fixed
- docs/glossary.md — fact status count corrected from 8-value to 7-value enum

### Removed
- None

### Known Issues
- Gold v1 annotations have null bbox and table cell coordinates until DSE-004/DSE-009 generate physical/table parser outputs
- Gold v1 annotations have 18 `not_found` facts; Product B must still avoid displaying these as "not covered"
- ADR files did not follow AGENTS.md bold-field format (fixed same day)
- Run log templates did not match AGENTS.md required fields (fixed same day)

## 2026-05-28

### Added
- None

### Changed
- Approaches A-E experiments completed (see our_experience.md)
- notes3.md + notes4.md: Friend's architectural analysis received
- notes5.md + notes6.md: Friend's detailed review and corrections
- Decision to split Product A and Product B made
- 909 PDFs analyzed, 647 active policy wordings identified
- 1,099 UIN lifecycle records obtained from IRDAI
- 18 table schema designed with notes5 + notes6 corrections

### Fixed
- None

### Removed
- None

### Known Issues
- None
