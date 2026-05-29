# Tasks

Lightweight local issue tracker. All IDs are `DSE-XXX` (Document Structure Engine).

## Active Sprint

| ID | Title | Status | Priority | Phase |
|----|-------|--------|----------|-------|
| DSE-001 | Corpus Lockdown | planned | P0 | Phase -1 |
| DSE-002 | UIN Matcher v1 | planned | P0 | Phase 0 |
| DSE-003 | Gold annotation of 5 policies | planned | P0 | Phase -1/7 |
| DSE-004 | Physical Layout Extractor v1 | planned | P1 | Phase 1 |
| DSE-005 | Heading Candidate Scorer | planned | P1 | Phase 2 |
| DSE-006 | Section Tree Builder | planned | P1 | Phase 2 |
| DSE-007 | First 5 Extractors (free look, grace, PED, initial wait, co-pay) | planned | P1 | Phase 6 |
| DSE-008 | Normalizers Library (money, duration, percentage) | planned | P1 | Phase 6 |

---

## Backlog

| ID | Title | Status | Priority | Phase |
|----|-------|--------|----------|-------|
| DSE-009 | Table Engine v1 | planned | P2 | Phase 3 |
| DSE-010 | Clause Store + Source Spans | planned | P2 | Phase 4 |
| DSE-011 | Fact Candidate Scoring + Conflict Resolution | planned | P2 | Phase 5 |
| DSE-012 | Expand gold corpus 5 → 20 | planned | P2 | Phase 7 |
| DSE-013 | Derived 91-Field Export | planned | P2 | Phase 8 |
| DSE-014 | LLM Refinement Integration | planned | P3 | Phase 6 |
| DSE-015 | Insurer/Plan Normalizer Library | planned | P1 | Phase 0 |

---

## Completed

| ID | Title | Completed | Phase |
|----|-------|-----------|-------|
| DSE-000 | Project scaffold + documentation setup | 2026-05-29 | Infrastructure |

---

## Task Detail

### DSE-001 — Corpus Lockdown

**Status:** planned
**Priority:** P0
**Phase:** Phase -1
**Goal:** Filter 909 PDFs down to 647 active policy wordings with file_hash, document_type, insurer, source, and match_status.
**Acceptance criteria:**
- `scripts/corpus_lockdown.py` reads `classification_report.json` + `policy_index.csv`
- Output: `active_policy_wordings.json`, `excluded_documents.json`, `uin_match_report.json`
- Every file in active list has: file_hash, document_type, insurer, source, match_status
- No file silently dropped (active + excluded = total classified)
- The "to_be_pruned" list from classification report is handled (excluded vs investigated)
**Branch:** feat/corpus-lockdown
**Related docs:** evaluation.md (Layer 1 gates), database_strategy.md

### DSE-002 — UIN Matcher v1

**Status:** planned
**Priority:** P0
**Phase:** Phase 0
**Goal:** Match 647 active policy wordings against 1,099 UIN records from uin_lifecycle.json using 5-tier matching strategy.
**Acceptance criteria:**
- Tier 1: Search PDF text for UIN-like patterns
- Tier 2: Exact insurer + normalized plan name
- Tier 3: Fuzzy insurer + fuzzy plan name
- Tier 4: Source URL domain + plan name
- Tier 5: Unmatched with top-5 candidates
- >= 90% matched or explicitly classified as unmatched/legacy
**Branch:** feat/uin-matcher-v1
**Related docs:** evaluation.md (Layer 1 gates)

### DSE-003 — Gold Annotation of 5 Policies

**Status:** planned
**Priority:** P0
**Phase:** Phase 7
**Goal:** Manually annotate 5 diverse policy PDFs with section trees, clause boundaries, tables, and critical facts.
**Policies:**
1. New India Assurance — Floater MediClaim
2. Star Health — POS Accident Care Individual
3. HDFC ERGO — Arogya Sanjeevani
4. ICICI Lombard — Family Shield
5. Care Health — Care Health Care
**Acceptance criteria:**
- Each policy has: metadata.json, sections.json, clauses.json, tables.json, facts.json
- Every annotation has source page reference
- Annotations are reproducible by a second person (annotation guide)
**Branch:** gold/annotate-5-policies
