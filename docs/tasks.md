# Tasks

Lightweight local issue tracker. All IDs are `DSE-XXX` (Document Structure Engine).

## Active Sprint

| ID | Title | Status | Priority | Phase |
|----|-------|--------|----------|-------|
| DSE-002 | UIN Matcher v1 | done | P0 | Phase 0 |
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
| DSE-001 | Corpus Lockdown | 2026-05-29 | Phase -1 |
| DSE-002 | UIN Matcher v1 | 2026-05-29 | Phase 0 |

---

## Task Detail

### DSE-001 — Corpus Lockdown

**Status:** done
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
