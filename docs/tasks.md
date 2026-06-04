# Tasks

Lightweight local issue tracker. All IDs are `DSE-XXX` (Document Structure Engine).

## Active Sprint

| ID | Title | Status | Priority | Phase |
|----|-------|--------|----------|-------|
| DSE-024 | Full-Corpus Parser Remediation for Zero-Clause Policies | in_progress | P0 | Phase 2 (E3B inspection done, E3C safe fixes pending) |
| DSE-021 | Remaining Deterministic Extractors Wave 2 | blocked | P1 | Phase 6 |

---

## Current Status

Product A has a working 20-policy reviewed benchmark, a local SQLite/source-span store, and a Product B export skeleton. DSE-020 confirmed full-corpus pipeline execution and DSE-024 has reduced zero-heading/zero-clause policies from 132 to 58. Parser remediation must continue before new extractors can materially improve full-corpus fill rate.

Current capability:
- 20 reviewed gold policies.
- 13/20 priority concepts have deterministic extractors.
- Product B export emits all 20 concept slots with explicit status.
- DSE-024 current triage: 58 policies with zero clauses (down from 110), 566/591 unique docs exported.
- DSE-024 E3B recovery abandoned a bad broad scorer attempt and produced an inspection-only safe-candidate audit for 33 residual `heading_miss` policies. Next parser changes must be narrow and evidence-backed.
- All 44 section_tree_fail policies resolved by section tree rebuild.

---

## Backlog

| ID | Title | Status | Priority | Phase |
|----|-------|--------|----------|-------|
| DSE-014 | LLM Refinement Integration | planned | P3 | Phase 6 |
| DSE-021 | Remaining Deterministic Extractors Wave 2 | blocked | P1 | Phase 6 |
| DSE-022 | 20-Policy Table Eval Expansion + Table Remediation | planned | P1 | Phase 3 |
| DSE-023 | Product B Export v1 Freeze + Handoff Dataset | planned | P1 | Phase 8 |

---

## Completed

| ID | Title | Completed | Phase |
|----|-------|-----------|-------|
| DSE-000 | Project scaffold + documentation setup | 2026-05-29 | Infrastructure |
| DSE-001 | Corpus Lockdown | 2026-05-29 | Phase -1 |
| DSE-002 | UIN Matcher v1 | 2026-05-29 | Phase 0 |
| DSE-003 | Gold annotation of 5 policies | 2026-05-29 | Phase 7 |
| DSE-004 | Physical Layout Extractor v1 | 2026-05-29 | Phase 1 |
| DSE-005 | Heading Candidate Scorer | 2026-05-30 | Phase 2 |
| DSE-006 | Section Tree Builder | 2026-05-30 | Phase 2 |
| DSE-007 | First 5 Extractors (free look, grace, PED, initial wait, co-pay) | 2026-05-30 | Phase 6 |
| DSE-008 | Normalizers Library v1 | 2026-05-30 | Phase 6 |
| DSE-009 | Table Engine v1 | 2026-05-31 | Phase 3 |
| DSE-010 | Clause Store + Source Spans | 2026-05-31 | Phase 4 |
| DSE-011 | Fact Candidate Scoring + Conflict Resolution | 2026-06-01 | Phase 5 |
| DSE-012 | Expand gold corpus 5 → 20 | 2026-06-01 | Phase 7 |
| DSE-013 | Derived Export (20-Concept Skeleton) | 2026-06-01 | Phase 8 |
| DSE-015 | Insurer/Plan Normalizer Library | 2026-06-01 | Phase 0 |
| DSE-017 | 20-Policy Pipeline Rebuild + Scale Validation | 2026-06-02 | Scale |
| DSE-018 | Deterministic Extractor Expansion Wave 1 | 2026-06-02 | Phase 6 |
| DSE-019 | Canonical Insurance Concept Ontology Registry v1 | 2026-06-02 | Ontology / Product A Control Plane |
| DSE-020 | Full 647-Policy Pipeline Dry Run + Scale Triage | 2026-06-04 | Scale |

---

## Task Detail

### DSE-019 — Canonical Insurance Concept Ontology Registry v1

**Status:** done
**Priority:** P0
**Phase:** Ontology / Product A Control Plane
**Goal:** Create a single canonical registry for all Product A insurance concepts, value shapes, fact statuses, export mappings, evidence requirements, extractor implementation status, and Product B display semantics.
**Acceptance criteria:**
- `ontology/concepts.v1.json` exists and defines all 20 priority concepts.
- Existing export mapping agrees with ontology.
- Existing extractor target concepts agree with ontology.
- Existing gold facts agree with ontology.
- No behavior regression in extractors/export.
- Gold corpus validator passes.
- Full pytest passes.
- Docs and session log are updated.
- Product B remains untouched.
- Raw PDFs remain untouched.
**Results:** ontology registry defines all 20 priority concepts; 13 concepts marked active deterministic and 7 marked planned. Ontology tests verify agreement with export mapping, extractor target concepts, fact statuses, and all reviewed gold `facts.json` concept labels. Gold corpus validator passed and full pytest passed.
**Branch:** feat/dse-019-ontology-registry-v1
**Related docs:** data_contracts.md, export_contract.md, decisions.md, changelog.md, runs/sessions/2026-06-02-ontology-registry-v1.md

### DSE-020 — Full 647-Policy Pipeline Dry Run + Scale Triage

**Status:** done
**Priority:** P0
**Phase:** Scale
**Goal:** Run the full Product A pipeline across all 647 active policy wordings and produce a scale-readiness report without manually annotating all PDFs.
**Acceptance criteria:**
- Every active policy wording is attempted or skipped with a recorded reason.
- End-to-end success/failure counts are reported by stage.
- Export production count is reported.
- Frequent `not_found`, parser, table, and source-span failure modes are summarized.
- Failures are classified as parser fix, extractor fix, table fix, identity/data issue, or human review.
- Raw PDFs remain read-only.
**Results:**
- Manifest: 647 entries, 647 unique slugs, 20 reviewed-gold mappings, 9 collision groups.
- Per-policy run: 647/647 passed all 5 stages (physical, heading, section, tables, facts).
- DB ingestion: 591/647 unique docs (56 duplicate-hash skipped). Source-span validation ALL PASSED.
- Fact scoring: 598/647 manifest entries, 14792 candidates, 3759 facts, 0 conflicts.
- Export: 566/591 unique docs exported.
- Triage report: `data/reports/dse020_scale_triage_report_v1.json` + `.md`.
- Gold corpus validator: PASSED. Full pytest: 393/393 PASSED.
**Known limitations:**
- 132 policies with zero headings and zero clauses — parser/section-tree gaps to fix.
- 133 policies with zero fact candidates — extractor input coverage gap.
- Top not_found concepts: claim_intimation_timeline, deductible, icu_limit (566 each).
- 56 duplicate-hash manifest entries share document_ids with other entries; clause store skips second occurrence.
- 566/591 unique docs exported (25 had 0 resolved facts).
**Branch:** feat/dse-020-full-corpus-scale-triage
**Related docs:** evaluation.md, risk_register.md, database_strategy.md, docs/decisions.md (ADR-0039)

### DSE-024 — Full-Corpus Parser Remediation for Zero-Clause Policies

**Status:** in_progress
**Priority:** P0
**Phase:** Phase 2
**Goal:** Classify and fix 132 policies with zero headings and zero clauses found by DSE-020 scale triage. Reduce zero-clause count without weakening 20-policy gold heading/section evals.
**Input:** DSE-020 triage report zero-heading/zero-clause policy list.
**Phase A — Classification:**
- Classify each of the 132 policies by root cause:
  - true non-policy / brochure / prospectus misclassified in corpus
  - heading scorer missed headings (font/size/numbering not matching current features)
  - section tree failed despite headings (synthetic body-number detection gaps)
  - physical text extraction malformed (pdfplumber issues)
  - duplicate/non-canonical document
  - unsupported product format (tables-only, image-based text, etc.)
- Output: `data/reports/dse024_zero_clause_policy_audit_plan.md` with classified list.
**Phase B — Representative Sample Inspection:**
- Select 20 representative failures across insurers and product types.
- Inspect physical JSON + debug HTML + PDF raw text for each.
- Document exact heading/section failure mechanism per sample.
**Phase C — Targeted Fixes:**
- Implement heading scorer improvements (e.g., additional numbering patterns, format-aware features for flattened/all-caps formats, lower threshold for certain layouts).
  - TOC suppression: `has_toc_dots` +0.10 → -0.30 (Phase C, reverted in D2 after regression)
  - Short all-caps numbered penalty: -0.25 for medical supply codes (Phase C, removed in D2 after regression)
  - Tab character penalty: -0.30 for table data lines (Phase C, removed in D2 after regression)
  - Letter-numbering pattern: `^[A-Z]\.\s(?!No)` for "A. Definitions" (Phase C, retained in D2)
  - Reduced sentence-case penalty: -0.10 for bold+numbered+sentence-case (Phase C, retained in D2)
- Implement section tree builder improvements (synthetic detection for non-standard clause formats).
- Do not weaken existing gold eval thresholds. — **20/20 PASS, no regression**
- Do not add extractors or LLM.
**Phase D — Re-validation:**
- Rerun heading scorer and section tree evals against 20-policy gold corpus — must not regress.
- Re-run section tree builder over DSE-020 heading outputs (D1, DONE).
- Regenerate DSE-020 triage report (D1, DONE).
- Run full pytest (D1, DONE).
- Measure zero-clause reduction (D1, DONE).
**Phase D1 Results (2026-06-04):**
- **Zero-clause reduction: NOT achieved.** Count increased from 132 to 156 (+24).
- **Root cause:** Phase C stricter penalties (TOC dots -0.40, tab -0.30, short all-caps -0.25) pushed 24 policies' marginal headings below t=0.5. Permissive additions (letter-numbering +0.30, reduced sentence-case penalty) did not help any zero-heading policies.
- **22/24 regressed policies are Star Health, United India, Bajaj Allianz.** They relied on marginal numbered headings (score 0.48-0.50).
- **Gold heading eval: 20/20 PASS** — no regression.
- **Gold section tree eval: 19/20 FAIL** — pre-existing `oriental_cancer_protect` unchanged.
- **Full pytest: 37/37 PASS** (heading scorer + manifest).
- **Triage report regenerated:** reflects 156 zero-clause (up from 132).
- **Recommendation:** Zero-clause reduction at t=0.5 requires targeted heading additions per insurer format (Star Health, HDFC ERGO, Aditya Birla). Lowering threshold to 0.45 would help 56/132 but requires FP suppression infra (44.4% FP ratio).
**Phase D2 Results (2026-06-04):**
- **Regression recovered and improved:** zero-clause count decreased from D1 `156` to `122`, beating the original DSE-020 baseline of `132`.
- **No new baseline regressions:** 10 policies improved from the original 132 zero-clause set; 0 new zero-clause policies appeared outside that baseline set.
- **Harmful penalties reverted:** TOC-dot negative penalty, short all-caps numbered penalty, and tab-character penalty were removed/restored.
- **Safe improvements retained:** letter-numbering support and reduced sentence-case penalty for bold numbered headings.
- **Gold heading eval: 20/20 PASS.**
- **Gold section tree eval: 19/20 FAIL** — unchanged pre-existing `oriental_cancer_protect` tree-accuracy issue.
- **Focused pytest: 41/41 PASS** (heading scorer + DSE-020 manifest).
- **Triage report regenerated:** reflects 122 zero-clause / zero-heading policies.
- **Recommendation:** stop global weight/threshold tuning; continue with a fallback heading promotion layer for low-confidence but structurally plausible headings.
**Fallback Promotion Results (2026-06-04):**
- **Zero-clause count reduced further:** D2 `122` → fallback `110`.
- **Zero-heading count reduced:** D2 `122` → fallback `84`.
- **No new regressions versus D2:** 12 policies improved and 0 new zero-clause policies appeared.
- **Fallback scope:** activates only when normal scoring finds 0 headings; no global threshold lowering.
- **Audit metadata emitted:** promoted candidates include `promotion_source`, `promotion_reason`, `original_score`, and fallback evaluation details.
- **Gold heading eval: 20/20 PASS.**
- **Gold section tree eval: 19/20 FAIL** — unchanged pre-existing `oriental_cancer_protect` tree-accuracy issue.
- **Triage report regenerated:** reflects 110 zero-clause policies.
- **Recommendation:** continue DSE-024 with remaining zero-clause classification/corpus filtering or more format-specific fallback guards. DSE-021 remains blocked.
**Phase E1 — Residual Zero-Clause Classification Results (2026-06-04):**
- **110 remaining zero-clause policies classified into 6 actionable buckets:**
  - **section_tree_fail (44):** fallback-headings exist, section tree not rebuilt; highest-confidence fix (just re-run section tree with fallback headings)
  - **heading_miss (34):** plausible near-miss headings below t=0.5; need format-specific heading pattern additions
  - **duplicate_or_superseded (14):** same-hash duplicates; deduplication removes them
  - **needs_manual_review (10):** unclear without human PDF inspection
  - **non_policy_or_rider (6):** brochures, riders, prospectuses; document-type filtering
  - **unsupported_format (2):** very short (<6 pages) or product-list documents
- **Top 20 parser-fix candidates** identified: highest max_score (0.4738–0.499) among section_tree_fail + heading_miss categories.
- **0 unclassified, 0 code behavior changes** in this packet.
- **Outputs:** `data/reports/dse024_residual_zero_clause_classification_v1.json`, `.md`.
- **Next step:** Fix 44 section_tree_fail policies (rebuild section tree after fallback), then tackle 34 heading_miss policies.
**Phase E2 — Section Tree Rebuild for section_tree_fail Policies (2026-06-04):**
- **All 44 section_tree_fail policies resolved** by rebuilding section tree from post-fallback heading candidates.
- **No code changes needed** — verified section tree builder already handles fallback-promoted headings, compact headings (`10.Renewal`), and alpha headings (`D. BENEFITS:`).
- **647/647 section trees built successfully**, 0 errors.
- **Zero-clause count: 110 → 58** (52 policies gained clauses).
- **Zero-heading count: 84 → 58** (tied with zero-clause).
- **Investigation report:** `data/reports/dse024_section_tree_fail_investigation_v1.md` documents edge case verification (compact headings, alpha headings, ICICI 0.25-years data quality).
- **Gold heading eval: 20/20 PASS** — no regression.
- **Gold section tree eval: 19/20 FAIL** — unchanged pre-existing `oriental_cancer_protect` tree-accuracy issue.
- **Gold corpus validation: PASS** — 20 policies, 400 facts, 2739 sections, 6251 clauses.
- **Full pytest: 400/400 PASS** — no regressions.
- **Triage report regenerated:** reflects 58 zero-clause policies.
- **Raw PDFs untouched:** verified.
- **Product B untouched:** verified.
- **Recommendation:** section_tree_fail bucket resolved. Next: tackle 34 heading_miss policies with format-specific heading pattern additions, then deduplicate 14 duplicates, then review 10 needs_manual_review.
**Phase E3A — Residual 58 Classification (2026-06-04):**
- **58 remaining zero-clause policies classified into 6 buckets (0 unclassified):**
  - **heading_miss (33):** plausible near-miss headings below t=0.5; need format-specific heading pattern additions.
  - **duplicate_or_superseded (8):** same-hash duplicates; deduplication removes them.
  - **physical_text_issue (8):** max_score ≤ 0 (negative/zero); pdfplumber extraction quality issue (Aditya Birla 5, Kotak Mahindra 3).
  - **non_policy_or_rider (4):** brochures/prospectuses; document-type filtering.
  - **unsupported_format (3):** very short or product-list documents.
  - **manual_review_required (2):** unclear without human PDF inspection.
  - **section_tree_fail (0):** confirmed resolved by E2.
- **Fix parser:** 41 (33 heading_miss + 8 physical_text_issue).
- **Filter/defer corpus:** 15 (8 duplicate + 4 non_policy + 3 unsupported).
- **Manual review:** 2.
- **No stale E1 counts carried forward.**
- **Outputs:** `scripts/dse024_classify_residual58.py`, `data/reports/dse024_residual58_classification_v1.json`, `.md`.
- **Next step:** Tackle 33 heading_miss policies with format-specific heading pattern additions, or investigate 8 physical_text_issue policies for pdfplumber extraction quality.
**Phase E3B — Recovery + Heading-Miss Safe Candidate Inspection (2026-06-04):**
- **Bad E3B attempt abandoned:** broad heading scorer/test edits and stray report artifacts were removed before commit.
- **DSE-020 parser artifacts regenerated** from the restored scorer state.
- **Current DSE-020 triage restored:** 58 zero-heading / 58 zero-clause policies.
- **33 residual `heading_miss` policies audited** without code behavior changes:
  - **27 `safe_pattern_fix` candidates** — narrow structural patterns only.
  - **6 `false_top_candidate` policies** — top candidates are percentage rows, table fragments, procedure/list rows, or bare numbers and must not be promoted blindly.
- **Safe pattern candidates:** numbered short-title headings, section-token headings, roman policy-section headings, numbered named policy headings, lettered named headings, and part headings.
- **High-risk rejected patterns:** generic `POLICY WORDINGS`, generic `Contents`, address-like dotted initials, percentage rows (`4 80%`), procedure/item rows (`5 BUDS`), duration table rows (`1 Month 75%`), and bare numbers.
- **Important reproducibility finding:** regenerating 20-policy gold heading candidates from the restored scorer produced **17/20 PASS**, failing `aditya_birla_activ_care`, `care_health_care_plus`, and `tata_aig_arogya_sanjeevani`. Earlier 20/20 heading eval artifacts are not currently reproducible from regenerated artifacts and must not be used as blind E3C acceptance evidence.
- **Outputs:** `data/reports/dse024_heading_miss_safe_candidates_v1.json`, `.md`; `runs/evals/2026-06-04-heading-scorer-dse024-e3b-recovery-baseline.json`.
- **Next step:** E3C must first reconcile the gold heading reproducibility gap, then implement only inspection-backed narrow heading fixes.
**Acceptance Criteria:**
- [x] Phase A — 132 zero-clause list classified 100% by root cause (DONE).
- [x] Phase B — 20 representative failures documented (DONE).
- [x] Phase C — Heading scorer/section tree improvements within gold eval thresholds (DONE, reverted in D2).
- [x] Phase D1 — Zero-clause reduction from 132 (156 — regression, reverted in D2).
- [x] Phase D2 — Regression recovered, zero-clause 122, beating original baseline (DONE).
- [x] Fallback promotion — Zero-clause 110, gold heading 20/20 (DONE).
- [x] Phase E1 — Residual zero-clause classification into 6 buckets (DONE).
- [x] **Phase E2 — Section tree rebuild for 44 section_tree_fail policies (DONE).**
  - [x] All 44 resolved (zero-clause: 110 → 58).
  - [x] No code changes needed.
  - [x] Gold heading eval: 20/20 PASS (no regression).
  - [x] Gold section tree eval: 19/20 FAIL (pre-existing `oriental_cancer_protect` unchanged).
  - [x] Full pytest: 400/400 PASS.
  - [x] DSE-020 triage report regenerated (zero-clause: 58).
  - [x] Raw PDFs read-only, Product B untouched.
  - [x] Session log, changelog updated.
- [x] **Phase E3A — Residual 58 classification (DONE).**
  - [x] 58 policies classified into 6 buckets (0 unclassified).
  - [x] No stale E1 counts.
  - [x] "Fix parser" vs "Filter/defer" clearly separated.
  - [x] Reports: `dse024_residual58_classification_v1.json` and `.md`.
  - [x] Session log, changelog, tasks.md updated.
- [x] **Phase E3B — Recovery + inspection-only heading-miss audit (DONE).**
  - [x] Failed broad scorer attempt abandoned before commit.
  - [x] DSE-020 triage restored to 58 zero-heading / 58 zero-clause policies.
  - [x] 33 `heading_miss` policies audited.
  - [x] Safe candidates separated from false top candidates.
  - [x] No parser behavior changes implemented in this packet.
  - [x] Session log, changelog, tasks.md updated.
- [ ] **Phase E3C — Safe heading fixes (PENDING).**
  - [ ] Reconcile current 17/20 regenerated gold heading eval before accepting new parser changes.
  - [ ] Implement only narrow patterns backed by E3B inspection.
  - [ ] Regenerate DSE-020 parser artifacts and triage.
  - [ ] Gold heading eval and section tree eval documented honestly.
  - [ ] Full pytest and gold validator pass.
**Branch:** feat/dse-024-parser-remediation
**Related docs:** evaluation.md, risk_register.md, data/reports/dse020_scale_triage_report_v1.md, data/reports/dse024_zero_clause_policy_audit_plan.md

### DSE-021 — Remaining Deterministic Extractors Wave 2

**Status:** blocked
**Priority:** P1
**Phase:** Phase 6
**Goal:** Implement deterministic extractors for the remaining priority concepts not covered by DSE-018.
**Blocked by:** DSE-024 — parser remediation must reduce zero-clause policies before extractor wave 2 can improve fill rate.
**Remaining concepts:** room rent limit, ICU limit, deductible, restoration benefit, modern treatment coverage, newborn coverage, claim intimation timeline.
**Acceptance criteria:**
- All 20 priority concepts have deterministic or explicitly deferred extraction strategy.
- Precision >= 95%, evidence accuracy >= 95%, false-present count 0 on reviewed gold policies.
- Product B export fill rate improves without weakening status/evidence rules.
**Branch:** feat/dse-021-extractor-wave2
**Related docs:** evaluation.md, ontology/concepts.v1.json, export_contract.md

### DSE-022 — 20-Policy Table Eval Expansion + Table Remediation

**Status:** planned
**Priority:** P1
**Phase:** Phase 3
**Goal:** Expand table-engine evaluation from the original physical-table labels to the reviewed 20-policy corpus and fix repeated table extraction/header lineage failures.
**Acceptance criteria:**
- DSE-009 physical-table labels/eval support all 20 reviewed policies.
- Priority physical table detection recall >= 85%.
- Header lineage accuracy >= 85%.
- Table type accuracy >= 80%.
- Prose-derived summaries remain out of the physical table hard gate.
**Branch:** fix/dse-022-table-eval-20-policy
**Related docs:** evaluation.md, data_contracts.md, risk_register.md

### DSE-023 — Product B Export v1 Freeze + Handoff Dataset

**Status:** planned
**Priority:** P1
**Phase:** Phase 8
**Goal:** Freeze the first Product B consumable export package and handoff contract after ontology, scale triage, and remaining extractor decisions are stable.
**Acceptance criteria:**
- Export schema version and ontology version are linked.
- Product B receives a stable JSON package with all fields, statuses, evidence, and parse quality.
- Known limitations and display rules are documented.
- No Product A raw parser tables are exposed to Product B.
**Branch:** feat/dse-023-product-b-export-v1
**Related docs:** export_contract.md, database_strategy.md, ontology/concepts.v1.json

### DSE-018 — Deterministic Extractor Expansion Wave 1

**Status:** done
**Priority:** P1
**Phase:** Phase 6
**Goal:** Expand deterministic extraction from the original 5 concepts to 13 Wave 1 concepts across the 20-policy reviewed gold corpus.
**Concepts:** free look, grace period, PED waiting, initial waiting, co-pay, renewability, claim settlement timeline, AYUSH coverage, ambulance coverage, cumulative bonus/NCB, specific disease waiting periods, maternity waiting, organ donor coverage.
**Acceptance criteria:**
- Fact extraction eval passes on all 20 reviewed policies.
- Precision >= 95%, recall >= 70%, normalized value accuracy >= 95%, status accuracy >= 95%, evidence accuracy >= 95%.
- False-present count is 0.
- Full clause-store, source-span, fact-scoring, export, and pytest regression chain passes.
- Mismatch audit, session log, changelog, evaluation docs, decisions, and risk register updated.
**Results:** final fact extraction eval passed with 20/20 policies, precision 100.00%, recall 99.49%, normalized value accuracy 100.00%, status accuracy 98.46%, evidence accuracy 100.00%, false-present count 0. Full acceptance chain passed: clause store/source spans, fact scoring, export, and 382/382 pytest tests.
**Known limitation:** Reliance Health Gain claim-settlement primary 30-day source text is present in the PDF but missing from current section-tree clauses, so DSE-018 emits `not_found` rather than a wrong 45-day investigation value.
**Branch:** feat/dse-018-extractor-expansion-wave1
**Related docs:** evaluation.md, decisions.md, risk_register.md, data/reports/dse018_wave1_mismatch_audit.md, runs/sessions/2026-06-02-extractor-expansion-wave1.md

### DSE-001 — Corpus Lockdown

**Status:** in_progress
**Priority:** P0
**Phase:** Phase -1
**Goal:** Filter 1067 indexed PDFs into 647 active, 139 needs_review, 281 excluded, with SHA-256 hashes and triage flags.
**Acceptance criteria:**
- `scripts/corpus_lockdown.py` reads `policy_index.json` + `classification_report.json`
- Output: `data/manifests/active_policy_wordings_v1.json`, `data/manifests/excluded_documents_v1.json`, `data/manifests/status_unset_review_v1.csv`
- 647 active entries all have: file_hash, document_type, corpus_status, insurer, source_domain, match_status
- 281 excluded entries all have exclusion_reason
- No file silently dropped: 647 + 139 + 281 = 1067
- 70 non-canonical duplicates flagged with `possible_duplicate` triage flag
- 18 brochures in active set flagged with `document_type_brochure` triage flag
**Branch:** feat/corpus-lockdown
**Related docs:** evaluation.md (Layer 1 gates), database_strategy.md

### DSE-002 — UIN Matcher v1

**Status:** done
**Priority:** P0
**Phase:** Phase 0
**Goal:** Verify UIN-insurer-plan assignments for all 647 active policy wordings against uin_lifecycle.json.
**Approach:** All 647 entries pre-assigned UINs in policy_index.json. Work was verification (not discovery): insurer normalizer (folder→lifecycle name mapping), plan name normalizer (filename→product name extraction), tiered confidence scoring.
**Results:**
- Verified: 646 (99.8%)
- Plan name matched: 584 (high confidence)
- Insurer match only: 62 (medium confidence)
- Special case: 1 (non_policy_wordings brochure)
- Conflicts: 0
- Unmatched: 0
- Verified + special: 100.0%
**Outputs:**
- `data/manifests/uin_match_report_v1.json` — full 647-entry report
- `data/manifests/unmatched_triage_report_v1.csv` — triage entries
- `data/manifests/uin_match_summary_v1.json` — summary stats
**Files created:**
- `identity/__init__.py`
- `identity/insurer_normalizer.py` — 23 folder→lifecycle mappings
- `identity/plan_name_normalizer.py` — filename extraction + fuzzy matching
- `identity/uin_matcher.py` — orchestrator with 3-tier confidence
- `scripts/uin_match_report.py` — CLI runner
**Branch:** feat/uin-matcher-v1
**Related docs:** evaluation.md (UIN Match layer)

### DSE-003 — Gold Annotation of 5 Policies

**Status:** done
**Priority:** P0
**Phase:** Phase 7
**Goal:** Manually annotate 5 diverse policy PDFs with section trees, clause boundaries, tables, and critical facts.
**Policies:**
1. New India Assurance — Floater MediClaim
2. Star Health — Medi Classic Accident Care Individual
3. HDFC ERGO — Arogya Sanjeevani
4. ICICI Lombard — Family Shield
5. Care Health — Care Plus
**Acceptance criteria:**
- Each policy has: metadata.json, sections.json, clauses.json, tables.json, facts.json
- Every annotation has source page reference
- Annotations are reproducible by a second person (annotation guide)
- `scripts/validate_gold_corpus.py` passes
- 100 fact annotations exist across the 20 priority concepts
- Raw PDFs remain external read-only references under `policy_data/`
**Branch:** gold/annotate-5-policies
**Results:**
- Policies: 5
- Policy JSON files: 25
- Sections: 445
- Clauses: 453
- Table regions: 26
- Facts: 100
- Fact statuses: 77 present, 3 explicitly_not_covered, 2 not_applicable, 18 not_found, 0 requires_manual_review
- Docling coverage: all 5 policies now have readable markdown cross-check artifacts; Star and Care markdown was generated with OCR disabled and placeholder image export
- Second pass: cross-checked New India, HDFC, and ICICI against available IBM Docling markdown and enriched table summaries
- Third pass: precision review downgraded weak schedule-dependent facts to `requires_manual_review`
- Fourth pass: re-ran structure/table/fact provenance checks for Star and Care using the generated Docling markdown
- Fifth pass: applied source-PDF-only manual review patch for the 11 previously unresolved facts
**Outputs:**
- `gold_corpus/annotation_guide.md`
- `gold_corpus/schemas/*.schema.json`
- `gold_corpus/policies/*/{metadata,sections,clauses,tables,facts}.json`
- `gold_corpus/docling_markdown/*.md`
- `data/reports/gold_corpus_manual_review_11_facts_v1.md`
- `scripts/validate_gold_corpus.py`
**Related docs:** evaluation.md (Gold Corpus eval), open_questions.md (OQ-005)

### DSE-004 — Physical Layout Extractor v1

**Status:** done
**Priority:** P1
**Phase:** Phase 1
**Goal:** Extract page/block/line/span physical layout from PDFs using pdfplumber (no OCR/vision). Produce `document_physical.json` and debug HTML per page. Tag header/footer candidates without deleting text.
**Acceptance criteria:**
- `pdf_parser/layout_extractor.py` — core extraction (pages → blocks → lines → spans)
- `pdf_parser/models.py` — Pydantic models for PhysicalDocument, Page, Block, Line, Span
- `pdf_parser/header_footer_detector.py` — region classification + repeated-line tagging
- `pdf_parser/debug_html_generator.py` — per-page text-block overlay HTML
- `scripts/validate_physical_outputs.py` — schema, bbox, page count, font metadata validation
- `scripts/run_physical_eval.py` — hard gate metrics against 5 gold PDFs
- `tests/test_layout_extractor.py` — unit tests (bbox, IDs, header/footer, roundtrip)
- Hard gates: all pages extracted, file hash/page count match, text coverage >= 95%, font metadata >= 90%, 0 catastrophic failures, debug HTML for every page, span referential integrity = 100%, no hardcoded absolute paths, session log and eval artifact present
- Evidence coverage: reported metric only; hard gate deferred to DSE-010
- Runs on 5 gold PDFs (218 pages total), produces eval report
**Files created:**
- `pdf_parser/__init__.py`
- `pdf_parser/models.py`
- `pdf_parser/layout_extractor.py`
- `pdf_parser/header_footer_detector.py`
- `pdf_parser/debug_html_generator.py`
- `scripts/validate_physical_outputs.py`
- `scripts/run_physical_eval.py`
- `tests/test_layout_extractor.py`
**Results:**
- 5/5 gold PDFs processed (218 pages)
- 5/5 file hashes match gold metadata
- 5/5 page counts match gold metadata
- Text coverage: 100% all policies
- Font metadata: 100% all policies
- Catastrophic failures: 0
- Debug HTML: 218/218 pages
- Span referential integrity: 100.0% all policies (617,060/617,060 refs valid)
- Tests: 21/21 passed
- Gold corpus validator: passed
**Branch:** feat/physical-layout-extractor-v1
**Related docs:** evaluation.md (Physical Parser eval), data_contracts.md (Contract 3), decisions.md (ADR-0011), runs/sessions/2026-05-29-physical-layout-extractor-v1.md

### DSE-005 — Heading Candidate Scorer

**Status:** done
**Priority:** P1
**Phase:** Phase 2
**Goal:** Implement scored heading detection using weighted feature signals (font size, bold, numbering, heading dictionary, TOC dots) to identify visual headings from physical layout lines. Penalize non-headings (sentence-case body text, footer/header regions, all-caps false positives).
**ADR:** 0004-scored-heading-detection.md — weights: numbering +0.3, font above body +0.25, bold/italic +0.15, spacing +0.1, heading dict +0.1, TOC +0.1; penalties: sentence-like -0.3, too long -0.2, footer/header -0.3, all-caps FP -0.2; threshold 0.5
**Files created:**
- `structure_parser/__init__.py` — package init
- `structure_parser/heading_patterns.py` — numbering regexes (decimal, compact, SECTION, PART, Roman), TOC dots, 40+ heading dictionary terms, ALL CAPS/sentence case detection, normalize_heading_text
- `structure_parser/heading_scorer.py` — `HeadingScorer` class with scored features, spacing signal, candidate metadata, and contribution breakdown
- `scripts/run_heading_scorer.py` — entry point: loads physical JSON, runs scorer, saves candidates, writes run summary, exits non-zero on missing inputs
- `scripts/eval_heading_scorer.py` — eval against DSE-005 visual heading labels with one-to-one page-aware matching
- `tests/test_heading_scorer.py` — 32 tests (unit, eval matching, CLI behavior, 3 gold integration)
- `gold_corpus/policies/*/heading_labels.json` — DSE-005 visual-heading gold labels separate from DSE-003 logical sections
**Results:**
- v1 eval failed: 0/5 policies passed because visual heading candidates were evaluated against all logical section entries in `sections.json`, and the matcher allowed generic headings to overmatch many rows.
- v2 eval passed: 5/5 policies passed against 101 visual-heading labels.
- Precision/recall/F1: 100.00% on all 5 gold policies with one-to-one page-aware matching.
- Tests: 54/54 pass in full suite.
- Gold corpus validator: passed with 30 policy JSON files and 101 heading labels.
**Outputs:**
- `data/interim/logical/*/heading_candidates.json` — 5 policies scored
- `data/interim/logical/heading_run_summary.json` — heading scoring run summary
- `runs/evals/2026-05-30-heading-scorer-v1.json` — failed first-pass eval retained for history
- `runs/evals/2026-05-30-heading-scorer-v2.json` — passing remediation eval
**Known limitations:**
- DSE-005 evaluates visual heading candidates only; DSE-006 must build section trees and clause boundaries from visual headings plus logical labels.
- ICICI family_shield: headings same font size as body (11.04pt), relies solely on bold
- All-caps and boilerplate penalties may need more tuning after expansion to 20-policy gold corpus.
**Branch:** fix/dse-005-heading-scorer-gates
**Related docs:** docs/adr/0004-scored-heading-detection.md, evaluation.md (Heading Candidate Scorer), runs/sessions/2026-05-30-heading-scorer-v1.md

### DSE-006 — Section Tree Builder

**Status:** done
**Priority:** P1
**Phase:** Phase 2
**Goal:** Build hierarchical section trees and clause boundaries from DSE-005 visual heading candidates plus DSE-004 physical lines.
**ADR:** 0012-section-tree-builder.md — stack-based visual-heading tree with iterative synthetic body-numbered detection.
**Files created:**
- `structure_parser/section_tree.py` — stack-based tree builder, compact body-number parser, synthetic section detection, stable section IDs
- `structure_parser/clause_segmenter.py` — clause segmentation from compact numbered prefixes and paragraph gaps
- `scripts/run_section_tree.py` — batch CLI for section tree generation
- `scripts/eval_section_tree.py` — DSE-006 eval against logical gold sections/clauses
- `tests/test_section_tree.py` — unit, eval, CLI, and gold integration coverage
- `docs/adr/0012-section-tree-builder.md` — section tree ADR
**Results:**
- First remediation eval failed because compact no-space headings were missed and dense numbered lists were over-generated.
- Final v3 eval passed: 5/5 gold policies passed.
- Final metrics: Care 97.75% section F1 / 96.67% tree accuracy; HDFC 97.44% / 95.00%; ICICI 92.47% / 92.13%; New India 100.00% / 100.00%; Star 90.51% / 88.41%.
- Gold corpus validator: passed.
- Full pytest suite: passed.
**Outputs:**
- `data/interim/logical/*/section_tree.json` — 5 policy section trees and clauses
- `data/interim/logical/section_tree_run_summary.json` — DSE-006 run summary
- `runs/evals/2026-05-30-section-tree-v3.json` — passing DSE-006 eval
**Known limitations:**
- Clause boundary F1 is a section-aligned proxy until gold clauses carry physical line/span IDs.
- Section precision excludes predicted numeric sections outside the current gold labels because DSE-003 gold is partial in some policies; this should be revisited when DSE-012 expands the corpus.
- Dense item lists are kept as clauses/list content unless they align with gold-labeled structure.
**Branch:** feat/section-tree-builder-v1
**Related docs:** evaluation.md (Section Tree / Clause Boundary), data_contracts.md (Contract 3B), decisions.md, runs/sessions/2026-05-30-section-tree-builder-v1.md

### DSE-007 — First 5 Deterministic Extractors

**Status:** done
**Priority:** P1
**Phase:** Phase 6
**Goal:** Extract the first five deterministic policy facts from DSE-006 section trees using a candidate-first, evidence-verified pipeline.
**Concepts:**
- `free_look_period`
- `grace_period`
- `ped_waiting_period`
- `initial_waiting_period`
- `co_pay`
**Files created:**
- `normalizers/duration.py` — minimal day/month/year duration parsing for DSE-007 concepts
- `normalizers/percentage.py` — minimal percentage parsing for co-pay values
- `extractors/models.py` — candidate and accepted fact models with AGENTS §14 fields
- `extractors/evidence.py` — evidence text verification helpers
- `extractors/deterministic.py` — first five deterministic concept extractors
- `extractors/registry.py` — candidate-first registry and conflict resolution
- `scripts/run_fact_extractors.py` — batch extractor CLI
- `scripts/eval_fact_extractors.py` — DSE-007 gold eval
- `tests/test_fact_extractors.py` — normalizer, extractor, registry, and integration tests
**Results:**
- 5/5 gold policies processed.
- 25/25 target concepts attempted.
- Gold corpus validator passed.
- DSE-007 eval passed: deterministic present precision 100%, present recall 100%, normalized value accuracy 100%, status accuracy 100%, evidence accuracy 100%, false present for gold `not_found`: 0.
- Full pytest suite passed.
**Outputs:**
- `data/interim/facts/*/fact_candidates.json`
- `data/interim/facts/*/accepted_facts.json`
- `data/interim/facts/fact_extraction_run_summary.json`
- `runs/evals/2026-05-30-fact-extraction-dse007-v1.json`
**Known limitations:**
- Evidence spans are provisional `clause:{clause_id}` IDs until DSE-010 creates true source spans.
- DSE-007 only implements duration and percentage normalization needed by the five concepts; broader money, age, and coverage-status normalization remains DSE-008.
- Tables, SQLite clause store, source-span DB, LLM refinement, derived export, and Product B integration remain untouched.
**Branch:** feat/dse-007-first-extractors-v1
**Related docs:** evaluation.md (Fact Extraction), data_contracts.md (Contract 5), decisions.md, runs/sessions/2026-05-30-first-five-extractors-v1.md

### DSE-008 — Normalizers Library v1

**Status:** done
**Priority:** P1
**Phase:** Phase 6
**Goal:** Expand the minimal DSE-007 duration/percentage helpers into reusable normalizers for future deterministic extractors.
**Files created/changed:**
- `normalizers/indian_number_words.py` — shared number-word parsing, Indian magnitudes, numeric cleanup
- `normalizers/money.py` — INR amount and special money-value normalization
- `normalizers/duration.py` — backward-compatible duration parsing with `yr/yrs` and hyphenated words
- `normalizers/percentage.py` — backward-compatible percentage parsing with word percentages
- `normalizers/age.py` — age and age-comparator normalization
- `normalizers/coverage_status.py` — coverage status normalization with negation precedence
- `scripts/eval_normalizers.py` — fixed-vector normalizer eval
- `tests/test_normalizers/test_normalizers.py` — normalizer unit tests
**Results:**
- Normalizer eval passed: 35/35 vectors, 100% pass rate.
- Full pytest suite passed: 110 tests.
- DSE-007 fact extraction regression eval passed with no metric regression.
- Gold corpus validator passed.
**Outputs:**
- `runs/evals/2026-05-30-normalizers-dse008-v1.json`
- `runs/evals/2026-05-30-fact-extraction-dse007-regression-after-dse008.json`
**Known limitations:**
- DSE-008 normalizes scalar values and simple statuses only; it does not implement table extraction, source spans, SQLite storage, new fact extractors, LLM refinement, derived export, or Product B integration.
- Money special values are explicit symbolic statuses (`actuals`, `as_charged`, `subject_to_limit`) and must be interpreted by future extractors/export code.
**Branch:** feat/dse-008-normalizers-v1
**Related docs:** evaluation.md (Normalizer Unit Tests), data_contracts.md (Contract 4A), runs/sessions/2026-05-30-normalizers-library-v1.md

### DSE-009 — Table Engine v1

**Status:** done
**Priority:** P2
**Phase:** Phase 3
**Goal:** Build a two-tier table detection and extraction engine for 5 gold policies.
**Approach:**
- Primary: pdfplumber lattice extraction for tables with visible grid lines (`pdfplumber_lattice`).
- Fallback: text alignment heuristic for borderless tables (`text_alignment_candidate`).
- Secondary: conservative `pdfplumber_text` strategy, retained only for small headered grids.
- Keyword-based type classifier (no ML): 6 types + unknown.
- Header row detection across the first 3 table rows with per-cell column/row header lineage.
- Parent clause assignment by shortest containing clause page span plus owning section depth (provisional).
- DSE-009-specific physical table labels split from DSE-003 semantic `tables.json`.
**Files created:**
- `table_engine/__init__.py`
- `table_engine/models.py` — Pydantic models (TableCell, ExtractedTable, TableDocument, ExtractionMethod, TableType, ColumnCluster)
- `table_engine/table_detector.py` — pdfplumber lattice extraction
- `table_engine/text_alignment_detector.py` — column x-cluster fallback
- `table_engine/table_type_classifier.py` — keyword scorer
- `table_engine/cell_extractor.py` — cell grid → TableCell list
- `scripts/run_table_engine.py` — batch CLI
- `scripts/eval_table_engine.py` — eval against gold corpus
- `tests/test_table_engine.py` — 49 focused non-slow unit tests
- `data/reports/dse009_table_bbox_review_candidates.json` — bbox review for DSE-012
- `data/reports/dse009_header_lineage_review.json` — header lineage review
- `data/reports/dse009_gold_table_annotation_audit.json` — gold/table mismatch audit
- `data/reports/dse009_gold_table_source_review.md` — legacy table disposition report
**Results:**
- 5/5 gold policies processed.
- Strict v3 eval passed against 18 physical table labels.
- Physical table detection recall: 100%.
- Priority physical table detection recall: 100%.
- Header lineage pass rate: 100%.
- Type accuracy on matched physical labels: 94.44%.
- 42 tables with missing cell bboxes now record explicit `cell_bbox_missing:<count>` issues.
- Unrecorded missing cell bbox count: 0.
- Focused non-slow table tests passed: 57/57.
**Outputs:**
- `data/interim/tables/*/document_tables.json` — 5 policies
- `data/interim/tables/*/document_table_cells.json` — 5 policies
- `data/interim/tables/table_run_summary.json`
- `runs/evals/2026-05-31-table-engine-dse009-v1.json`
- `runs/evals/2026-05-31-table-engine-dse009-v2.json`
- `runs/evals/2026-05-31-table-engine-dse009-v3.json`
- `data/reports/dse009_table_bbox_review_candidates.json`
- `data/reports/dse009_header_lineage_review.json`
- `data/reports/dse009_gold_table_annotation_audit.json`
- `data/reports/dse009_gold_table_source_review.json`
- `data/reports/dse009_gold_table_source_review.md`
**Known limitations:**
- DSE-003 `tables.json` remains semantic/manual annotation history. DSE-009 hard gates now use `physical_table_labels.json`.
- `text_alignment_candidate` preserves raw lines but intentionally emits `cells=[]` when borderless column splitting is unreliable.
- Legacy gold table source dispositions are documented, including prose summaries that should be handled by clause/fact extraction rather than physical table parsing.
- Parent clause ID is provisional (page-range lookup); replaced by bbox overlap in DSE-010.
**Branch:** fix/dse-009-table-engine-gates
**Related docs:** evaluation.md (Table Extraction), data_contracts.md (Contract 3C), decisions.md (ADR-0014, ADR-0015), runs/sessions/2026-05-31-table-engine-v1.md

### DSE-010 — Clause Store + Source Spans

**Status:** done
**Priority:** P2
**Phase:** Phase 4
**Goal:** Persist all 5 gold-policy interim JSON into SQLite (`data/engine.sqlite`), build real `source_spans` records (clause → lines → bbox coordinates), replace provisional `"clause:{id}"` evidence IDs with real span IDs, and resolve table parent clause assignment via bbox spatial overlap.
**Acceptance criteria:**
- 5/5 gold policies ingested into SQLite — PASS
- 0 dangling FK references — PASS
- Source artifact count parity — PASS (`document_lines=12,715`, `document_sections=1,156`, `policy_clauses=2,522`)
- 0 cross-document source span mismatches — PASS
- 0 resolved fact span mismatches — PASS
- 0 unresolved present facts — PASS
- Clause span coverage >= 95% — PASS (100%)
- 0 provisional IDs in resolved facts — PASS
- DB size < 30 MB — PASS (18.42 MB)
- 232/232 tests (new + prior) — PASS
- Gold corpus validator — PASS
**Files created:**
- `clause_store/__init__.py`
- `clause_store/schema.sql` — 19-table SQLite DDL (15 populated, 4 deferred)
- `clause_store/models.py` — Python dataclasses for SQLite row types
- `clause_store/repository.py` — init_db(), insert_*, query_*, backfill_table_parent_clauses()
- `clause_store/span_builder.py` — clause spans, fact evidence spans, table cell spans
- `clause_store/fact_resolver.py` — provisional → real evidence ID resolution
- `scripts/run_clause_store.py` — batch ingest CLI
- `scripts/validate_source_spans.py` — structural integrity validator
- `scripts/eval_clause_store.py` — hard gate eval with source-count parity and cross-document checks
- `tests/test_clause_store.py` — 60 unit tests
**Results:**
- 6,136 total source_spans (2,522 clause_body, 3,591 table_cell, 23 fact_evidence)
- 192/197 tables (97.5%) parent_clause_id resolved via bbox overlap (avg IoU: 0.48)
- 23/23 accepted present facts resolved to real span IDs
- 113 cross-page clause spans across 5 policies
- DB size: 18.42 MB
**Key design decisions (ADRs):**
- ADR-0017: `document_text_spans` deferred (char-level spans stay in physical JSON)
- ADR-0018: `page_regions_json` handles cross-page clauses
- ADR-0019: `char_start`/`char_end` are clause-text offsets
- ADR-0020: resolved facts are a separate artifact; DSE-007 output is immutable
- ADR-0021: heading score in `document_sections`; OQ-001 closed
- ADR-0022: document-local IDs are namespaced in SQLite and original IDs are preserved in source_* columns
**Known limitations:**
- 16/23 (69.6%) fact evidence spans have clause-level char offsets (not subspan-level) because DSE-007 evidence_text boundaries shifted slightly with clause re-segmentation
- `document_text_spans` DDL exists but is not populated (ADR-0017)
- One block per page (physical parser limitation)
- `extracted_facts`, `fact_conflicts`, `derived_policy_features` not populated (DSE-011/013)
**Branch:** fix/dse-010-global-sqlite-ids
**Related docs:** evaluation.md (Clause Store + Source Spans), decisions.md (ADR-0017 through ADR-0022), docs/open_questions.md (OQ-001 closed), runs/sessions/2026-05-31-clause-store-source-spans-v2.md

### DSE-012 — Expand Gold Corpus 5 → 20

**Status:** done
**Priority:** P2
**Phase:** Phase 7
**Goal:** Expand the reviewed gold corpus from 5 to 20 policy wordings with 7 annotation files per policy.
**Approach:**
- Selected 15 additional policies for insurer/product diversity.
- Ran the existing pipeline to generate draft annotations.
- Performed source-PDF human review using `pdftotext`, physical JSON, pipeline drafts, and targeted page checks.
- Promoted all 15 new policies from draft to reviewed gold.
**Results:**
- 20/20 policies reviewed.
- 140 annotation JSON files present (20 policies × 7 files).
- 400 reviewed fact labels present (20 policies × 20 concepts).
- Status distribution: 257 `present`, 11 `explicitly_not_covered`, 5 `not_applicable`, 127 `not_found`.
- Tata AIG and Aditya Birla degenerate section trees manually rebuilt from source-PDF/physical-line review.
- Gold corpus validator passed with 20 reviewed policies and 0 draft policies.
- Full pytest suite passed.
**Outputs:**
- `data/manifests/dse012_gold_expansion_candidates_v1.json`
- `data/reports/dse012_human_review/human_review_summary.md`
- `runs/evals/2026-06-01-gold-corpus-dse012-reviewed.json`
- `runs/evals/2026-06-01-heading-scorer-dse012-reviewed.json`
- `runs/evals/2026-06-01-section-tree-dse012-reviewed.json`
- `runs/evals/2026-06-01-table-engine-dse012-reviewed.json`
- `runs/evals/2026-06-01-fact-extraction-dse012-reviewed.json`
**Known limitations:**
- Expanded heading/section evals now fail on Tata AIG and Aditya Birla, exposing parser gaps discovered by the larger gold corpus.
- Table eval script still has 5-policy-era hard-gate wording and reports DSE-012 run failure despite strong detection metrics on the expanded labels.
- DSE-012 is annotation completion only; parser remediation is deferred.
**Branch:** feat/dse-012-gold-corpus-expansion
**Related docs:** evaluation.md (Gold Corpus / expanded parser regression), risk_register.md, runs/sessions/2026-06-01-gold-corpus-human-review.md
