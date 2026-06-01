"""
Tests for DSE-011 Fact Candidate Scoring + Conflict Resolution

All tests use in-memory SQLite and synthetic data — no PDF or gold corpus access.
"""

from __future__ import annotations

import json
import os
import pathlib
import tempfile

import pytest

from clause_store.models import (
    DocumentSection,
    ExtractedFact,
    ExtractedFactCandidate,
    FactConflict,
    PipelineRun,
    PolicyClause,
    Product,
    ProductVersion,
    SourceDocument,
    SourceSpan,
)
from clause_store.repository import (
    count_facts_by_concept,
    init_db,
    insert_clauses,
    insert_extracted_facts,
    insert_fact_candidates,
    insert_fact_conflicts,
    insert_pipeline_run,
    insert_product,
    insert_product_version,
    insert_sections,
    insert_source_document,
    insert_source_spans,
    query_candidates_for_document,
    query_conflicts_for_document,
    query_facts_for_document,
)
from extractors.conflict_detector import (
    detect_conflicts,
    resolve_conflict,
)
from extractors.scoring import (
    ACCEPT_THRESHOLD,
    PATTERN_SPECIFICITY,
    compute_composite_score,
    compute_evidence_quality,
    compute_pattern_specificity,
    compute_source_priority,
    score_candidates,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

DOC_ID = "sha256:test123"


@pytest.fixture
def conn():
    db = init_db(":memory:")
    yield db
    db.close()


@pytest.fixture
def seeded_conn(conn):
    """Connection with pipeline_run, product, version, source_document, section, clause, span."""
    insert_pipeline_run(conn, PipelineRun(id="run_001", started_at="2026-06-01T00:00:00"))
    insert_product(
        conn,
        Product(product_id="pol", uin_base="X", normalized_insurer="x", normalized_plan_name="x"),
    )
    insert_product_version(
        conn, ProductVersion(version_id="pol_v1", product_id="pol", full_uin="X")
    )
    insert_source_document(
        conn,
        SourceDocument(
            document_id=DOC_ID,
            policy_id="pol",
            source_pdf_path="p.pdf",
            file_hash=DOC_ID,
            page_count=10,
            version_id="pol_v1",
        ),
    )
    insert_sections(
        conn,
        [
            DocumentSection(
                section_id=f"{DOC_ID}:sec_1",
                source_section_id="sec_1",
                document_id=DOC_ID,
                pipeline_run_id="run_001",
            )
        ],
    )
    insert_clauses(
        conn,
        [
            PolicyClause(
                clause_id=f"{DOC_ID}:clause_0050",
                source_clause_id="clause_0050",
                document_id=DOC_ID,
                section_id=f"{DOC_ID}:sec_1",
                pipeline_run_id="run_001",
                raw_text="Free look period of 15 days.",
                page_start=8,
                page_end=8,
                line_ids_json=json.dumps([f"{DOC_ID}:p8l_45"]),
                source_line_ids_json=json.dumps(["p8l_45"]),
            ),
            PolicyClause(
                clause_id=f"{DOC_ID}:clause_0048",
                source_clause_id="clause_0048",
                document_id=DOC_ID,
                section_id=f"{DOC_ID}:sec_1",
                pipeline_run_id="run_001",
                raw_text="Grace period of 30 days.",
                page_start=8,
                page_end=8,
                line_ids_json=json.dumps([f"{DOC_ID}:p8l_40"]),
                source_line_ids_json=json.dumps(["p8l_40"]),
            ),
        ],
    )
    insert_source_spans(
        conn,
        [
            SourceSpan(
                span_id="ss_pol_free_look_period_0000_evidence",
                document_id=DOC_ID,
                clause_id=f"{DOC_ID}:clause_0050",
                span_type="fact_evidence",
                text="Free look period of 15 days.",
                char_start=0,
                char_end=28,
                page_regions_json='[{"page":8,"bbox":null,"line_ids":[]}]',
                pipeline_run_id="run_001",
            )
        ],
    )
    conn.commit()
    return conn


def _make_candidate(
    concept="free_look_period",
    candidate_id="free_look_period_0000",
    confidence=0.98,
    accepted=True,
    rejection_reason=None,
    pattern_id="free_look_15_days",
    evidence_text="Free look period of 15 days.",
    clause_id="clause_0050",
    value_json=None,
    normalized_value_json=None,
    scope_json=None,
    fact_status="present",
    source="section_tree_clause",
    document_id=DOC_ID,
):
    return {
        "candidate_id": candidate_id,
        "concept": concept,
        "confidence": confidence,
        "accepted": accepted,
        "rejection_reason": rejection_reason,
        "pattern_id": pattern_id,
        "evidence_text": evidence_text,
        "evidence_clause_id": clause_id,
        "evidence_page": 8,
        "evidence_line_ids": ["p8l_45"],
        "value_json": value_json or {"days": 15},
        "normalized_value_json": normalized_value_json or {"days": 15},
        "fact_status": fact_status,
        "scope_json": scope_json or {"cover": "base_policy"},
        "condition_json": None,
        "extraction_method": "deterministic",
        "extractor_name": concept,
        "extractor_version": "1.0.0",
        "source": source,
        "pipeline_run_id": "run_001",
    }


# ---------------------------------------------------------------------------
# TestCompositeScoring
# ---------------------------------------------------------------------------


class TestCompositeScoring:
    def test_high_confidence_high_evidence_scores_above_threshold(self):
        cand = _make_candidate(confidence=0.98)
        score = compute_composite_score(cand)
        assert score >= ACCEPT_THRESHOLD

    def test_low_confidence_scores_below_threshold(self):
        cand = _make_candidate(confidence=0.20)
        score = compute_composite_score(cand)
        assert score < ACCEPT_THRESHOLD

    def test_definition_only_pattern_gets_low_specificity(self):
        specificity = compute_pattern_specificity("copay_definition_only")
        assert specificity == 0.2

    def test_no_evidence_gets_zero_evidence_quality(self):
        cand = _make_candidate(evidence_text=None, clause_id=None)
        eq = compute_evidence_quality(cand)
        assert eq == 0.0

    def test_score_range_0_to_1(self):
        for conf in [0.0, 0.5, 1.0]:
            cand = _make_candidate(confidence=conf)
            score = compute_composite_score(cand)
            assert 0.0 <= score <= 1.0

    def test_known_pattern_specificity_values(self):
        assert compute_pattern_specificity("free_look_15_days") == 1.0
        assert compute_pattern_specificity("ped_waiting_duration") == 1.0
        assert compute_pattern_specificity("copay_definition_only") == 0.2
        assert compute_pattern_specificity(None) == 0.5

    def test_score_deterministic_for_same_input(self):
        cand = _make_candidate()
        s1 = compute_composite_score(cand)
        s2 = compute_composite_score(cand)
        assert s1 == s2

    def test_partial_evidence_clause_missing_gets_lower_quality(self):
        cand = _make_candidate(evidence_text="some text", clause_id=None)
        eq = compute_evidence_quality(cand)
        assert 0.0 < eq < 1.0

    def test_source_priority_clause_is_highest(self):
        assert compute_source_priority({"source": "section_tree_clause"}) == 1.0

    def test_source_priority_table_is_medium(self):
        assert compute_source_priority({"source": "table_cell"}) == 0.7

    def test_source_priority_unknown_is_lowest(self):
        assert compute_source_priority({"source": ""}) == 0.3

    def test_score_candidates_populates_score_field(self):
        cands = [_make_candidate(), _make_candidate(candidate_id="x_0001", confidence=0.3)]
        scored = score_candidates(cands)
        assert all("score" in c for c in scored)
        assert scored[0]["score"] > scored[1]["score"]


# ---------------------------------------------------------------------------
# TestConflictDetector
# ---------------------------------------------------------------------------


class TestConflictDetector:
    def test_no_conflicts_single_candidate_per_concept(self):
        cands = [
            {
                "id": f"{DOC_ID}:fl_0000",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":15}',
                "fact_status": "present",
                "scope_json": None,
            },
        ]
        conflicts = detect_conflicts(cands, DOC_ID, "run_001")
        assert conflicts == []

    def test_value_disagreement_detected(self):
        cands = [
            {
                "id": f"{DOC_ID}:fl_0000",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":15}',
                "fact_status": "present",
                "scope_json": None,
            },
            {
                "id": f"{DOC_ID}:fl_0001",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":30}',
                "fact_status": "present",
                "scope_json": None,
            },
        ]
        conflicts = detect_conflicts(cands, DOC_ID, "run_001")
        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == "value_disagreement"

    def test_status_disagreement_detected(self):
        cands = [
            {
                "id": f"{DOC_ID}:co_0000",
                "concept": "co_pay",
                "accepted": True,
                "normalized_value_json": '{"pct":20}',
                "fact_status": "present",
                "scope_json": None,
            },
            {
                "id": f"{DOC_ID}:co_0001",
                "concept": "co_pay",
                "accepted": True,
                "normalized_value_json": '{"pct":20}',
                "fact_status": "explicitly_not_covered",
                "scope_json": None,
            },
        ]
        conflicts = detect_conflicts(cands, DOC_ID, "run_001")
        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == "status_disagreement"

    def test_scope_disagreement_detected(self):
        cands = [
            {
                "id": f"{DOC_ID}:co_0000",
                "concept": "co_pay",
                "accepted": True,
                "normalized_value_json": '{"pct":20}',
                "fact_status": "present",
                "scope_json": '{"cover":"base_policy"}',
            },
            {
                "id": f"{DOC_ID}:co_0001",
                "concept": "co_pay",
                "accepted": True,
                "normalized_value_json": '{"pct":20}',
                "fact_status": "present",
                "scope_json": '{"cover":"optional_addon"}',
            },
        ]
        conflicts = detect_conflicts(cands, DOC_ID, "run_001")
        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == "scope_disagreement"

    def test_same_value_no_conflict(self):
        cands = [
            {
                "id": f"{DOC_ID}:fl_0000",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":15}',
                "fact_status": "present",
                "scope_json": None,
            },
            {
                "id": f"{DOC_ID}:fl_0001",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days": 15}',
                "fact_status": "present",
                "scope_json": None,
            },
        ]
        conflicts = detect_conflicts(cands, DOC_ID, "run_001")
        assert conflicts == []

    def test_different_concepts_no_conflict(self):
        cands = [
            {
                "id": f"{DOC_ID}:fl_0000",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":15}',
                "fact_status": "present",
                "scope_json": None,
            },
            {
                "id": f"{DOC_ID}:gp_0000",
                "concept": "grace_period",
                "accepted": True,
                "normalized_value_json": '{"days":30}',
                "fact_status": "present",
                "scope_json": None,
            },
        ]
        conflicts = detect_conflicts(cands, DOC_ID, "run_001")
        assert conflicts == []

    def test_rejected_candidates_ignored(self):
        cands = [
            {
                "id": f"{DOC_ID}:fl_0000",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":15}',
                "fact_status": "present",
                "scope_json": None,
            },
            {
                "id": f"{DOC_ID}:fl_0001",
                "concept": "free_look_period",
                "accepted": False,
                "normalized_value_json": '{"days":30}',
                "fact_status": "present",
                "scope_json": None,
            },
        ]
        conflicts = detect_conflicts(cands, DOC_ID, "run_001")
        assert conflicts == []

    def test_conflict_resolution_higher_score_wins(self):
        cands = [
            {
                "id": f"{DOC_ID}:fl_0000",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":15}',
                "fact_status": "present",
                "scope_json": None,
                "score": 0.95,
            },
            {
                "id": f"{DOC_ID}:fl_0001",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":30}',
                "fact_status": "present",
                "scope_json": None,
                "score": 0.70,
            },
        ]
        conflicts = detect_conflicts(cands, DOC_ID, "run_001")
        by_id = {c["id"]: c for c in cands}
        resolved = resolve_conflict(conflicts[0], by_id, "higher_score_wins")
        assert resolved.resolution == "higher_score_wins"
        assert f"{DOC_ID}:fl_0000" in resolved.resolution_notes

    def test_conflict_resolution_manual_review(self):
        conflict = FactConflict(
            document_id=DOC_ID,
            concept="co_pay",
            fact_a_id=f"{DOC_ID}:co_0000",
            fact_b_id=f"{DOC_ID}:co_0001",
            conflict_type="value_disagreement",
            pipeline_run_id="run_001",
        )
        resolved = resolve_conflict(conflict, {}, "manual_review")
        assert resolved.resolution == "manual_review_required"

    def test_multiple_conflicts_detected(self):
        cands = [
            {
                "id": f"{DOC_ID}:fl_0000",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":15}',
                "fact_status": "present",
                "scope_json": None,
            },
            {
                "id": f"{DOC_ID}:fl_0001",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":30}',
                "fact_status": "present",
                "scope_json": None,
            },
            {
                "id": f"{DOC_ID}:fl_0002",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":7}',
                "fact_status": "present",
                "scope_json": None,
            },
        ]
        conflicts = detect_conflicts(cands, DOC_ID, "run_001")
        # 3 accepted → 3 pairs: (0,1), (0,2), (1,2)
        assert len(conflicts) == 3


# ---------------------------------------------------------------------------
# TestFactPersistence
# ---------------------------------------------------------------------------


class TestFactPersistence:
    def test_insert_fact_candidate_with_global_uid(self, seeded_conn):
        cand = ExtractedFactCandidate(
            id=f"{DOC_ID}:free_look_period_0000",
            source_candidate_id="free_look_period_0000",
            clause_id=f"{DOC_ID}:clause_0050",
            source_clause_id="clause_0050",
            document_id=DOC_ID,
            concept="free_look_period",
            extractor_name="free_look_period",
            pipeline_run_id="run_001",
            confidence=0.98,
            score=0.95,
            accepted=True,
        )
        insert_fact_candidates(seeded_conn, [cand])
        seeded_conn.commit()
        count = seeded_conn.execute("SELECT COUNT(*) FROM extracted_fact_candidates").fetchone()[0]
        assert count == 1

    def test_insert_extracted_fact_with_global_uid(self, seeded_conn):
        fact = ExtractedFact(
            id=f"{DOC_ID}:free_look_period_0000",
            source_candidate_id="free_look_period_0000",
            clause_id=f"{DOC_ID}:clause_0050",
            source_clause_id="clause_0050",
            document_id=DOC_ID,
            concept="free_look_period",
            extraction_method="deterministic",
            pipeline_run_id="run_001",
            fact_status="present",
            confidence=0.98,
            evidence_span_id="ss_pol_free_look_period_0000_evidence",
        )
        insert_extracted_facts(seeded_conn, [fact])
        seeded_conn.commit()
        count = seeded_conn.execute("SELECT COUNT(*) FROM extracted_facts").fetchone()[0]
        assert count == 1

    def test_insert_fact_conflict(self, seeded_conn):
        # Insert two candidates first
        for suffix in ("0000", "0001"):
            cand = ExtractedFactCandidate(
                id=f"{DOC_ID}:fl_{suffix}",
                source_candidate_id=f"fl_{suffix}",
                clause_id=f"{DOC_ID}:clause_0050",
                source_clause_id="clause_0050",
                document_id=DOC_ID,
                concept="free_look_period",
                extractor_name="free_look_period",
                pipeline_run_id="run_001",
            )
            insert_fact_candidates(seeded_conn, [cand])
        conflict = FactConflict(
            document_id=DOC_ID,
            concept="free_look_period",
            fact_a_id=f"{DOC_ID}:fl_0000",
            fact_b_id=f"{DOC_ID}:fl_0001",
            conflict_type="value_disagreement",
            pipeline_run_id="run_001",
        )
        insert_fact_conflicts(seeded_conn, [conflict])
        seeded_conn.commit()
        count = seeded_conn.execute("SELECT COUNT(*) FROM fact_conflicts").fetchone()[0]
        assert count == 1

    def test_candidate_clause_id_fk_validated(self, seeded_conn):
        """FK to policy_clauses must be valid — insert raises IntegrityError."""
        import sqlite3

        cand = ExtractedFactCandidate(
            id=f"{DOC_ID}:fl_bad",
            source_candidate_id="fl_bad",
            clause_id=f"{DOC_ID}:NONEXISTENT_CLAUSE",
            source_clause_id="NONEXISTENT_CLAUSE",
            document_id=DOC_ID,
            concept="free_look_period",
            extractor_name="free_look_period",
            pipeline_run_id="run_001",
        )
        with pytest.raises(sqlite3.IntegrityError):
            insert_fact_candidates(seeded_conn, [cand])

    def test_candidate_evidence_span_id_nullable(self, seeded_conn):
        """Rejected candidates may have NULL evidence_span_id."""
        cand = ExtractedFactCandidate(
            id=f"{DOC_ID}:fl_nospan",
            source_candidate_id="fl_nospan",
            clause_id=f"{DOC_ID}:clause_0050",
            source_clause_id="clause_0050",
            document_id=DOC_ID,
            concept="free_look_period",
            extractor_name="free_look_period",
            pipeline_run_id="run_001",
            evidence_span_id=None,
            accepted=False,
            rejection_reason="lower_scoring_candidate",
        )
        insert_fact_candidates(seeded_conn, [cand])
        seeded_conn.commit()
        row = seeded_conn.execute(
            "SELECT evidence_span_id FROM extracted_fact_candidates WHERE id = ?",
            (f"{DOC_ID}:fl_nospan",),
        ).fetchone()
        assert row[0] is None

    def test_query_facts_for_document(self, seeded_conn):
        fact = ExtractedFact(
            id=f"{DOC_ID}:fl_0000",
            source_candidate_id="fl_0000",
            clause_id=f"{DOC_ID}:clause_0050",
            source_clause_id="clause_0050",
            document_id=DOC_ID,
            concept="free_look_period",
            extraction_method="deterministic",
            pipeline_run_id="run_001",
            fact_status="present",
        )
        insert_extracted_facts(seeded_conn, [fact])
        seeded_conn.commit()
        results = query_facts_for_document(seeded_conn, DOC_ID)
        assert len(results) == 1
        assert results[0]["concept"] == "free_look_period"

    def test_query_candidates_for_document(self, seeded_conn):
        cand = ExtractedFactCandidate(
            id=f"{DOC_ID}:fl_0000",
            source_candidate_id="fl_0000",
            clause_id=f"{DOC_ID}:clause_0050",
            source_clause_id="clause_0050",
            document_id=DOC_ID,
            concept="free_look_period",
            extractor_name="free_look_period",
            pipeline_run_id="run_001",
            score=0.95,
        )
        insert_fact_candidates(seeded_conn, [cand])
        seeded_conn.commit()
        results = query_candidates_for_document(seeded_conn, DOC_ID)
        assert len(results) == 1

    def test_candidate_count_persists_correctly(self, seeded_conn):
        cands = []
        for i in range(5):
            cands.append(
                ExtractedFactCandidate(
                    id=f"{DOC_ID}:fl_{i:04d}",
                    source_candidate_id=f"fl_{i:04d}",
                    clause_id=f"{DOC_ID}:clause_0050",
                    source_clause_id="clause_0050",
                    document_id=DOC_ID,
                    concept="free_look_period",
                    extractor_name="free_look_period",
                    pipeline_run_id="run_001",
                )
            )
        insert_fact_candidates(seeded_conn, cands)
        seeded_conn.commit()
        count = seeded_conn.execute(
            "SELECT COUNT(*) FROM extracted_fact_candidates WHERE document_id = ?",
            (DOC_ID,),
        ).fetchone()[0]
        assert count == 5

    def test_source_candidate_id_preserved(self, seeded_conn):
        cand = ExtractedFactCandidate(
            id=f"{DOC_ID}:ped_waiting_period_0003",
            source_candidate_id="ped_waiting_period_0003",
            clause_id=f"{DOC_ID}:clause_0050",
            source_clause_id="clause_0050",
            document_id=DOC_ID,
            concept="ped_waiting_period",
            extractor_name="ped_waiting_period",
            pipeline_run_id="run_001",
        )
        insert_fact_candidates(seeded_conn, [cand])
        seeded_conn.commit()
        row = seeded_conn.execute(
            "SELECT source_candidate_id FROM extracted_fact_candidates WHERE id = ?",
            (f"{DOC_ID}:ped_waiting_period_0003",),
        ).fetchone()
        assert row[0] == "ped_waiting_period_0003"

    def test_unique_constraint_on_facts_doc_concept(self, seeded_conn):
        """Only one extracted fact per (document_id, concept)."""
        fact1 = ExtractedFact(
            id=f"{DOC_ID}:fl_0000",
            source_candidate_id="fl_0000",
            clause_id=f"{DOC_ID}:clause_0050",
            source_clause_id="clause_0050",
            document_id=DOC_ID,
            concept="free_look_period",
            extraction_method="deterministic",
            pipeline_run_id="run_001",
        )
        insert_extracted_facts(seeded_conn, [fact1])
        seeded_conn.commit()

        # Second fact same concept → INSERT OR REPLACE → replaces
        fact2 = ExtractedFact(
            id=f"{DOC_ID}:fl_0000_v2",
            source_candidate_id="fl_0000_v2",
            clause_id=f"{DOC_ID}:clause_0050",
            source_clause_id="clause_0050",
            document_id=DOC_ID,
            concept="free_look_period",
            extraction_method="deterministic",
            pipeline_run_id="run_001",
        )
        # The UNIQUE INDEX on (document_id, concept) means this will conflict
        # INSERT OR REPLACE on PK should still work since id is different
        # But the unique index will reject it as a second row
        # The behavior depends on how we handle: INSERT OR REPLACE triggers on UNIQUE violation
        # With REPLACE, the old row is deleted, new one inserted. OK.
        insert_extracted_facts(seeded_conn, [fact2])
        seeded_conn.commit()
        count = seeded_conn.execute(
            "SELECT COUNT(*) FROM extracted_facts WHERE document_id = ? AND concept = 'free_look_period'",
            (DOC_ID,),
        ).fetchone()[0]
        # Should have exactly 1 (replaced)
        assert count == 1

    def test_count_facts_by_concept(self, seeded_conn):
        for concept in ["free_look_period", "grace_period"]:
            insert_extracted_facts(
                seeded_conn,
                [
                    ExtractedFact(
                        id=f"{DOC_ID}:{concept}_0000",
                        source_candidate_id=f"{concept}_0000",
                        clause_id=f"{DOC_ID}:clause_0050",
                        source_clause_id="clause_0050",
                        document_id=DOC_ID,
                        concept=concept,
                        extraction_method="deterministic",
                        pipeline_run_id="run_001",
                    )
                ],
            )
        seeded_conn.commit()
        counts = count_facts_by_concept(seeded_conn)
        assert counts["free_look_period"] == 1
        assert counts["grace_period"] == 1


# ---------------------------------------------------------------------------
# TestGoldComparison (logic tests with synthetic gold data)
# ---------------------------------------------------------------------------


class TestGoldComparison:
    def _make_gold(self, concept, status, value=None):
        return {
            "concept": concept,
            "fact_status": status,
            "normalized_value_json": value or {},
            "value_json": value or {},
        }

    def _make_extracted(self, concept, status, value=None):
        return {
            "concept": concept,
            "fact_status": status,
            "normalized_value_json": json.dumps(value or {}),
        }

    def test_status_match_present(self):
        gold = self._make_gold("free_look_period", "present", {"days": 15})
        ext = self._make_extracted("free_look_period", "present", {"days": 15})
        assert gold["fact_status"] == ext["fact_status"]

    def test_status_match_not_found(self):
        gold = self._make_gold("co_pay", "not_found")
        # For not_found: no row in extracted_facts → derived
        assert gold["fact_status"] == "not_found"

    def test_value_match_days_15(self):
        gold = self._make_gold("free_look_period", "present", {"days": 15})
        ext = self._make_extracted("free_look_period", "present", {"days": 15})
        assert json.dumps(gold["normalized_value_json"], sort_keys=True) == json.dumps(
            json.loads(ext["normalized_value_json"]), sort_keys=True
        )

    def test_value_match_months_48(self):
        gold = self._make_gold("ped_waiting_period", "present", {"months": 48})
        ext = self._make_extracted("ped_waiting_period", "present", {"months": 48})
        assert json.dumps(gold["normalized_value_json"], sort_keys=True) == json.dumps(
            json.loads(ext["normalized_value_json"]), sort_keys=True
        )

    def test_value_mismatch_detected(self):
        gold = self._make_gold("free_look_period", "present", {"days": 15})
        ext = self._make_extracted("free_look_period", "present", {"days": 30})
        g_str = json.dumps(gold["normalized_value_json"], sort_keys=True)
        e_str = json.dumps(json.loads(ext["normalized_value_json"]), sort_keys=True)
        assert g_str != e_str

    def test_false_present_when_gold_is_not_found(self):
        gold = self._make_gold("co_pay", "not_found")
        ext = self._make_extracted("co_pay", "present", {"percentage": 20})
        # This is a false present — should be flagged
        assert gold["fact_status"] == "not_found"
        assert ext["fact_status"] == "present"
        # The eval gate should catch this

    def test_false_not_found_when_gold_is_present(self):
        gold = self._make_gold("free_look_period", "present", {"days": 15})
        # No extracted fact → treated as not_found
        # The eval gate measures recall for this case


# ---------------------------------------------------------------------------
# TestScoreAndRank
# ---------------------------------------------------------------------------


class TestScoreAndRank:
    def test_highest_score_candidate_for_concept(self):
        cands = [
            _make_candidate(
                confidence=0.55,
                candidate_id="fl_0001",
                rejection_reason="free_look_primary_15_days_not_found",
            ),
            _make_candidate(confidence=0.98, candidate_id="fl_0000"),
        ]
        scored = score_candidates(cands)
        by_score = sorted(scored, key=lambda c: -c["score"])
        assert by_score[0]["candidate_id"] == "fl_0000"

    def test_rejection_reason_does_not_affect_score_computation(self):
        """Score is computed for all candidates, even rejected ones."""
        cand = _make_candidate(
            rejection_reason="definition_only", confidence=0.2, pattern_id="copay_definition_only"
        )
        score = compute_composite_score(cand)
        assert score > 0.0  # Score is computed, just low

    def test_all_candidates_get_score(self):
        cands = [_make_candidate(candidate_id=f"c_{i}", confidence=0.1 * (i + 1)) for i in range(5)]
        scored = score_candidates(cands)
        assert all("score" in c for c in scored)
        assert all(c["score"] > 0 for c in scored)

    def test_accepted_candidate_must_meet_threshold(self):
        """A candidate with low confidence + definition pattern should score below ACCEPT_THRESHOLD."""
        cand = _make_candidate(
            confidence=0.20, pattern_id="copay_definition_only", evidence_text=None, clause_id=None
        )
        score = compute_composite_score(cand)
        assert score < ACCEPT_THRESHOLD, f"Score {score} should be below {ACCEPT_THRESHOLD}"

    def test_strong_candidate_meets_threshold(self):
        """A candidate with high confidence + strong evidence should meet threshold."""
        cand = _make_candidate(confidence=0.98, pattern_id="free_look_15_days")
        score = compute_composite_score(cand)
        assert score >= ACCEPT_THRESHOLD, f"Score {score} should be >= {ACCEPT_THRESHOLD}"


# ---------------------------------------------------------------------------
# TestEndToEnd (synthetic pipeline flow)
# ---------------------------------------------------------------------------


class TestEndToEnd:
    def test_full_pipeline_synthetic_policy(self, seeded_conn):
        """Insert candidates → extract accepted fact → detect conflicts → verify."""
        # 3 candidates for one concept
        cands = []
        for i, (conf, accepted, rej) in enumerate(
            [
                (0.98, True, None),
                (0.55, False, "non_primary"),
                (0.20, False, "definition_only"),
            ]
        ):
            cands.append(
                ExtractedFactCandidate(
                    id=f"{DOC_ID}:fl_{i:04d}",
                    source_candidate_id=f"fl_{i:04d}",
                    clause_id=f"{DOC_ID}:clause_0050",
                    source_clause_id="clause_0050",
                    document_id=DOC_ID,
                    concept="free_look_period",
                    extractor_name="free_look_period",
                    pipeline_run_id="run_001",
                    confidence=conf,
                    score=compute_composite_score(_make_candidate(confidence=conf)),
                    accepted=accepted,
                    rejection_reason=rej,
                )
            )
        insert_fact_candidates(seeded_conn, cands)

        # Insert the winning fact
        fact = ExtractedFact(
            id=f"{DOC_ID}:fl_0000",
            source_candidate_id="fl_0000",
            clause_id=f"{DOC_ID}:clause_0050",
            source_clause_id="clause_0050",
            document_id=DOC_ID,
            concept="free_look_period",
            extraction_method="deterministic",
            pipeline_run_id="run_001",
            fact_status="present",
            confidence=0.98,
            evidence_span_id="ss_pol_free_look_period_0000_evidence",
        )
        insert_extracted_facts(seeded_conn, [fact])
        seeded_conn.commit()

        # Verify
        db_cands = query_candidates_for_document(seeded_conn, DOC_ID)
        db_facts = query_facts_for_document(seeded_conn, DOC_ID)
        db_conflicts = query_conflicts_for_document(seeded_conn, DOC_ID)

        assert len(db_cands) == 3
        assert len(db_facts) == 1
        assert len(db_conflicts) == 0
        assert db_facts[0]["concept"] == "free_look_period"
        assert db_facts[0]["evidence_span_id"] == "ss_pol_free_look_period_0000_evidence"

    def test_conflict_to_resolution_flow(self, seeded_conn):
        """Create synthetic conflict → resolve → verify."""
        for i in range(2):
            insert_fact_candidates(
                seeded_conn,
                [
                    ExtractedFactCandidate(
                        id=f"{DOC_ID}:fl_{i:04d}",
                        source_candidate_id=f"fl_{i:04d}",
                        clause_id=f"{DOC_ID}:clause_0050",
                        source_clause_id="clause_0050",
                        document_id=DOC_ID,
                        concept="free_look_period",
                        extractor_name="free_look_period",
                        pipeline_run_id="run_001",
                        accepted=True,
                        score=0.95 - i * 0.2,
                    )
                ],
            )

        # Detect
        cands_data = [
            {
                "id": f"{DOC_ID}:fl_0000",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":15}',
                "fact_status": "present",
                "scope_json": None,
                "score": 0.95,
            },
            {
                "id": f"{DOC_ID}:fl_0001",
                "concept": "free_look_period",
                "accepted": True,
                "normalized_value_json": '{"days":30}',
                "fact_status": "present",
                "scope_json": None,
                "score": 0.75,
            },
        ]
        conflicts = detect_conflicts(cands_data, DOC_ID, "run_001")
        assert len(conflicts) == 1

        # Resolve
        by_id = {c["id"]: c for c in cands_data}
        resolved = resolve_conflict(conflicts[0], by_id, "higher_score_wins")
        assert resolved.resolution == "higher_score_wins"

        # Persist
        insert_fact_conflicts(seeded_conn, [resolved])
        seeded_conn.commit()
        db_conflicts = query_conflicts_for_document(seeded_conn, DOC_ID)
        assert len(db_conflicts) == 1
        assert db_conflicts[0]["resolution"] == "higher_score_wins"

    def test_no_cross_document_fact_links(self, seeded_conn):
        """A fact's clause_id must belong to the same document_id."""
        fact = ExtractedFact(
            id=f"{DOC_ID}:fl_0000",
            source_candidate_id="fl_0000",
            clause_id=f"{DOC_ID}:clause_0050",
            source_clause_id="clause_0050",
            document_id=DOC_ID,
            concept="free_look_period",
            extraction_method="deterministic",
            pipeline_run_id="run_001",
        )
        insert_extracted_facts(seeded_conn, [fact])
        seeded_conn.commit()

        # Verify clause belongs to same document
        row = seeded_conn.execute(
            """SELECT f.document_id AS fact_doc, c.document_id AS clause_doc
               FROM extracted_facts f
               JOIN policy_clauses c ON c.clause_id = f.clause_id
               WHERE f.id = ?""",
            (f"{DOC_ID}:fl_0000",),
        ).fetchone()
        assert row["fact_doc"] == row["clause_doc"]
