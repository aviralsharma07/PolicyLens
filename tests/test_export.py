"""
Tests for DSE-013/DSE-023 Product B JSON Export

All tests use in-memory SQLite and synthetic data — no PDF or external file access.
"""

from __future__ import annotations

import json
import sqlite3

import pytest

from clause_store.models import (
    DocumentSection,
    ExtractedFact,
    ExtractedFactCandidate,
    PipelineRun,
    PolicyClause,
    Product,
    ProductVersion,
    SourceDocument,
    SourceSpan,
)
from clause_store.repository import (
    init_db,
    insert_clauses,
    insert_extracted_facts,
    insert_fact_candidates,
    insert_pipeline_run,
    insert_product,
    insert_product_version,
    insert_sections,
    insert_source_document,
    insert_source_spans,
)
from derived.export_builder import (
    build_policy_clauses_minimal,
    build_policy_fact_sources,
    build_policy_features,
)
from derived.field_mapping import (
    ALL_EXPORT_CONCEPTS,
    CONCEPT_FIELD_MAP,
    VALID_FACT_STATUSES,
    extract_scalar_value,
    get_export_field_name,
    get_unit,
)
from derived.schema_validator import validate_policy_features
from scripts.build_product_b_handoff import build_handoff

DOC_ID = "sha256:test_export_001"
POLICY_ID = "test_policy"
RUN_ID = "run_export_test"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def conn():
    """In-memory SQLite with full schema + seed data for export tests."""
    db = init_db(":memory:")
    insert_pipeline_run(db, PipelineRun(id=RUN_ID, started_at="2026-06-01T00:00:00"))
    insert_product(
        db,
        Product(
            product_id=POLICY_ID,
            uin_base="TSTHLIP00000",
            normalized_insurer="Test Insurer",
            normalized_plan_name="Test Plan",
            display_name="Test Insurer Test Plan",
            short_name="Test Plan",
            match_confidence="high",
            match_method="uin_insurer_plan_verified",
        ),
    )
    insert_product_version(
        db,
        ProductVersion(
            version_id=f"{POLICY_ID}_v1",
            product_id=POLICY_ID,
            full_uin="TSTHLIP00000V000000",
            version_number=1,
            approval_date="01-01-2025",
        ),
    )
    insert_source_document(
        db,
        SourceDocument(
            document_id=DOC_ID,
            policy_id=POLICY_ID,
            source_pdf_path="test/Test_Policy.pdf",
            file_hash=DOC_ID,
            page_count=30,
            version_id=f"{POLICY_ID}_v1",
        ),
    )
    insert_sections(
        db,
        [
            DocumentSection(
                section_id=f"{DOC_ID}:sec_1",
                source_section_id="sec_1",
                document_id=DOC_ID,
                pipeline_run_id=RUN_ID,
                level=1,
                heading_type="visual",
                title="4. Waiting Period",
                section_number="4",
                page_start=8,
                page_end=10,
            )
        ],
    )
    insert_clauses(
        db,
        [
            PolicyClause(
                clause_id=f"{DOC_ID}:clause_0050",
                source_clause_id="clause_0050",
                document_id=DOC_ID,
                section_id=f"{DOC_ID}:sec_1",
                pipeline_run_id=RUN_ID,
                raw_text="Free look period of 15 days from date of receipt.",
                page_start=8,
                page_end=8,
                clause_number="4.1",
                title="Free Look Period",
                line_ids_json=json.dumps([f"{DOC_ID}:p8l_1"]),
                source_line_ids_json=json.dumps(["p8l_1"]),
            )
        ],
    )
    insert_source_spans(
        db,
        [
            SourceSpan(
                span_id="ss_test_fl_0000_evidence",
                document_id=DOC_ID,
                clause_id=f"{DOC_ID}:clause_0050",
                span_type="fact_evidence",
                text="Free look period of 15 days from date of receipt.",
                char_start=0,
                char_end=49,
                page_regions_json='[{"page":8,"bbox":[72,100,500,120],"line_ids":[]}]',
                pipeline_run_id=RUN_ID,
            )
        ],
    )
    insert_extracted_facts(
        db,
        [
            ExtractedFact(
                id=f"{DOC_ID}:free_look_period_0000",
                source_candidate_id="free_look_period_0000",
                clause_id=f"{DOC_ID}:clause_0050",
                source_clause_id="clause_0050",
                document_id=DOC_ID,
                concept="free_look_period",
                extraction_method="deterministic",
                pipeline_run_id=RUN_ID,
                fact_status="present",
                confidence=0.98,
                value_json='{"days": 15}',
                normalized_value_json='{"days": 15}',
                scope_json='{"cover": "base_policy"}',
                evidence_span_id="ss_test_fl_0000_evidence",
            )
        ],
    )
    insert_fact_candidates(
        db,
        [
            ExtractedFactCandidate(
                id=f"{DOC_ID}:free_look_period_0000",
                source_candidate_id="free_look_period_0000",
                clause_id=f"{DOC_ID}:clause_0050",
                source_clause_id="clause_0050",
                document_id=DOC_ID,
                concept="free_look_period",
                extractor_name="free_look_period",
                pipeline_run_id=RUN_ID,
                confidence=0.98,
                score=0.99,
                accepted=True,
                evidence_text="Free look period of 15 days from date of receipt.",
                evidence_page=8,
                pattern_id="free_look_15_days",
                evidence_span_id="ss_test_fl_0000_evidence",
            ),
            ExtractedFactCandidate(
                id=f"{DOC_ID}:free_look_period_0001",
                source_candidate_id="free_look_period_0001",
                clause_id=f"{DOC_ID}:clause_0050",
                source_clause_id="clause_0050",
                document_id=DOC_ID,
                concept="free_look_period",
                extractor_name="free_look_period",
                pipeline_run_id=RUN_ID,
                confidence=0.55,
                score=0.45,
                accepted=False,
                rejection_reason="non_primary_duration",
                pattern_id="free_look_non_primary_duration",
            ),
        ],
    )
    db.commit()
    yield db
    db.close()


# ---------------------------------------------------------------------------
# TestFieldMapping
# ---------------------------------------------------------------------------


class TestFieldMapping:
    def test_all_20_concepts_mapped(self):
        assert len(ALL_EXPORT_CONCEPTS) == 20

    def test_extract_scalar_days_15(self):
        val = extract_scalar_value("free_look_period", {"days": 15})
        assert val == 15

    def test_extract_scalar_months_48(self):
        val = extract_scalar_value("ped_waiting_period", {"months": 48})
        assert val == 48

    def test_extract_compound_copay_components(self):
        copay = {"components": [{"percentage": 20}]}
        val = extract_scalar_value("co_pay", copay)
        assert val == copay  # full dict passed through

    def test_extract_value_null_for_none(self):
        val = extract_scalar_value("free_look_period", None)
        assert val is None

    def test_get_export_field_name_known(self):
        assert get_export_field_name("free_look_period") == "free_look_days"
        assert get_export_field_name("ped_waiting_period") == "ped_waiting_months"
        assert get_export_field_name("co_pay") == "copay_percentage"

    def test_get_unit_days_months(self):
        assert get_unit("free_look_period") == "days"
        assert get_unit("ped_waiting_period") == "months"
        assert get_unit("co_pay") is None

    def test_unknown_concept_raises(self):
        with pytest.raises(KeyError):
            get_export_field_name("nonexistent_concept")

    def test_extract_from_json_string(self):
        val = extract_scalar_value("free_look_period", '{"days": 15}')
        assert val == 15

    def test_valid_fact_statuses_count(self):
        assert len(VALID_FACT_STATUSES) == 7


# ---------------------------------------------------------------------------
# TestExportBuilder
# ---------------------------------------------------------------------------


class TestExportBuilder:
    def test_build_features_has_20_concept_keys(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        assert len(result["features"]) == 20

    def test_present_fact_has_value_and_evidence(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        fl = result["features"]["free_look_days"]
        assert fl["value"] == 15
        assert fl["fact_status"] == "present"
        assert fl["evidence"] is not None
        assert fl["evidence_page"] == 8
        assert fl["source_span_id"] == "ss_test_fl_0000_evidence"
        assert fl["confidence"] == 0.98

    def test_not_found_fact_has_null_value(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        # ped_waiting_months is not extracted in this fixture
        ped = result["features"]["ped_waiting_months"]
        assert ped["value"] is None
        assert ped["fact_status"] == "not_found"
        assert ped["evidence"] is None
        assert ped["source_span_id"] is None

    def test_source_document_block_shape(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        sd = result["source_document"]
        assert sd["filename"] == "Test_Policy.pdf"
        assert sd["file_hash"] == DOC_ID
        assert sd["page_count"] == 30

    def test_product_identity_block_shape(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        pi = result["product_identity"]
        assert pi["insurer"] == "Test Insurer"
        assert pi["plan_name"] == "Test Plan"
        assert pi["uin"] == "TSTHLIP00000V000000"

    def test_product_identity_has_all_9_fields(self, conn):
        """All 9 contract fields must be present as keys in product_identity."""
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        pi = result["product_identity"]
        required = [
            "insurer",
            "plan_name",
            "display_name",
            "uin",
            "uin_base",
            "product_version",
            "effective_date",
            "match_confidence",
            "match_method",
        ]
        for field in required:
            assert field in pi, f"product_identity missing key: {field}"

    def test_parse_quality_fill_rate(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        pq = result["parse_quality"]
        assert pq["total_concepts_attempted"] == 20
        assert pq["concepts_resolved"] == 1  # only free_look present
        assert pq["concepts_not_found"] == 19
        assert pq["overall_fill_rate"] == 0.05

    def test_unresolved_concepts_list(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        assert "ped_waiting_period" in result["unresolved_concepts"]
        assert "free_look_period" not in result["unresolved_concepts"]

    def test_export_schema_version_present(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        assert result["export_schema_version"] == "1.0"

    def test_evidence_clause_from_policy_clauses(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        fl = result["features"]["free_look_days"]
        assert fl["evidence_clause"] == "4.1"

    def test_method_from_extraction_method(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        fl = result["features"]["free_look_days"]
        assert fl["method"] == "deterministic"

    def test_evidence_clause_fallback_when_clause_number_null(self, conn):
        """When clause_number is null, evidence_clause falls back to source_clause_id."""
        # The fixture clause has clause_number="4.1" — insert one without
        insert_clauses(
            conn,
            [
                PolicyClause(
                    clause_id=f"{DOC_ID}:clause_nonum",
                    source_clause_id="clause_nonum",
                    document_id=DOC_ID,
                    section_id=f"{DOC_ID}:sec_1",
                    pipeline_run_id=RUN_ID,
                    raw_text="No numbered clause.",
                    page_start=9,
                    page_end=9,
                    clause_number=None,
                    title=None,
                    line_ids_json="[]",
                    source_line_ids_json="[]",
                )
            ],
        )
        insert_source_spans(
            conn,
            [
                SourceSpan(
                    span_id="ss_test_gp_evidence",
                    document_id=DOC_ID,
                    clause_id=f"{DOC_ID}:clause_nonum",
                    span_type="fact_evidence",
                    text="Grace period of 30 days.",
                    char_start=0,
                    char_end=24,
                    page_regions_json='[{"page":9,"bbox":null,"line_ids":[]}]',
                    pipeline_run_id=RUN_ID,
                )
            ],
        )
        insert_extracted_facts(
            conn,
            [
                ExtractedFact(
                    id=f"{DOC_ID}:grace_period_0000",
                    source_candidate_id="grace_period_0000",
                    clause_id=f"{DOC_ID}:clause_nonum",
                    source_clause_id="clause_nonum",
                    document_id=DOC_ID,
                    concept="grace_period",
                    extraction_method="deterministic",
                    pipeline_run_id=RUN_ID,
                    fact_status="present",
                    confidence=0.96,
                    normalized_value_json='{"days": 30}',
                    evidence_span_id="ss_test_gp_evidence",
                )
            ],
        )
        conn.commit()
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        gp = result["features"]["grace_period_days"]
        assert gp["evidence_clause"] == "clause_nonum"  # fallback to source_clause_id
        assert gp["evidence_clause"] is not None

    def test_scope_from_extracted_facts(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        fl = result["features"]["free_look_days"]
        assert fl["scope"] == {"cover": "base_policy"}


# ---------------------------------------------------------------------------
# TestFactSources
# ---------------------------------------------------------------------------


class TestFactSources:
    def test_sources_has_all_20_concepts(self, conn):
        result = build_policy_fact_sources(conn, DOC_ID, POLICY_ID, RUN_ID)
        assert len(result["sources"]) == 20

    def test_provenance_includes_rejected_candidates(self, conn):
        result = build_policy_fact_sources(conn, DOC_ID, POLICY_ID, RUN_ID)
        fl = result["sources"]["free_look_period"]
        assert len(fl["provenance"]) == 2  # 1 accepted + 1 rejected
        rejected = [p for p in fl["provenance"] if not p["accepted"]]
        assert len(rejected) == 1
        assert rejected[0]["rejection_reason"] == "non_primary_duration"

    def test_accepted_candidate_id_present(self, conn):
        result = build_policy_fact_sources(conn, DOC_ID, POLICY_ID, RUN_ID)
        fl = result["sources"]["free_look_period"]
        assert fl["accepted_candidate_id"] == "free_look_period_0000"

    def test_conflicts_empty(self, conn):
        result = build_policy_fact_sources(conn, DOC_ID, POLICY_ID, RUN_ID)
        assert result["conflicts_resolved"] == []
        assert result["unresolved_conflicts"] == []

    def test_pipeline_run_id_present(self, conn):
        result = build_policy_fact_sources(conn, DOC_ID, POLICY_ID, RUN_ID)
        assert result["pipeline_run_id"] == RUN_ID

    def test_concept_without_candidates_has_empty_provenance(self, conn):
        result = build_policy_fact_sources(conn, DOC_ID, POLICY_ID, RUN_ID)
        ped = result["sources"]["ped_waiting_period"]
        assert ped["provenance"] == []
        assert ped["accepted_candidate_id"] is None


# ---------------------------------------------------------------------------
# TestClausesMinimal
# ---------------------------------------------------------------------------


class TestClausesMinimal:
    def test_sections_have_number_and_title(self, conn):
        result = build_policy_clauses_minimal(conn, DOC_ID, POLICY_ID)
        assert len(result["sections"]) >= 1
        sec = result["sections"][0]
        assert "number" in sec
        assert "title" in sec

    def test_clauses_have_text_and_page(self, conn):
        result = build_policy_clauses_minimal(conn, DOC_ID, POLICY_ID)
        clauses = result["sections"][0]["clauses"]
        assert len(clauses) >= 1
        cl = clauses[0]
        assert "text" in cl
        assert "page" in cl
        assert cl["page"] == 8

    def test_clause_text_truncated_at_500(self, conn):
        # Insert a long clause
        insert_clauses(
            conn,
            [
                PolicyClause(
                    clause_id=f"{DOC_ID}:clause_long",
                    source_clause_id="clause_long",
                    document_id=DOC_ID,
                    section_id=f"{DOC_ID}:sec_1",
                    pipeline_run_id=RUN_ID,
                    raw_text="X" * 1000,
                    page_start=9,
                    page_end=9,
                    line_ids_json="[]",
                    source_line_ids_json="[]",
                )
            ],
        )
        conn.commit()
        result = build_policy_clauses_minimal(conn, DOC_ID, POLICY_ID)
        long_clauses = [c for s in result["sections"] for c in s["clauses"] if len(c["text"]) > 500]
        for cl in long_clauses:
            assert cl["text"].endswith("...")
            assert len(cl["text"]) == 503  # 500 + "..."

    def test_total_counts_present(self, conn):
        result = build_policy_clauses_minimal(conn, DOC_ID, POLICY_ID)
        assert "total_sections" in result
        assert "total_clauses" in result
        assert result["total_clauses"] >= 1


# ---------------------------------------------------------------------------
# TestSchemaValidator
# ---------------------------------------------------------------------------


class TestSchemaValidator:
    def test_valid_export_passes(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        errors = validate_policy_features(result)
        assert errors == [], f"Validation errors: {errors}"

    def test_missing_concept_key_fails(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        del result["features"]["free_look_days"]
        errors = validate_policy_features(result)
        assert any("Missing concept fields" in e for e in errors)

    def test_present_fact_without_evidence_fails(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        result["features"]["free_look_days"]["evidence"] = None
        errors = validate_policy_features(result)
        assert any("present fact missing evidence" in e for e in errors)

    def test_not_found_with_value_fails(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        result["features"]["ped_waiting_months"]["value"] = 48
        errors = validate_policy_features(result)
        assert any("not_found fact has non-null value" in e for e in errors)

    def test_invalid_fact_status_fails(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        result["features"]["free_look_days"]["fact_status"] = "BOGUS"
        errors = validate_policy_features(result)
        assert any("invalid fact_status" in e for e in errors)

    def test_missing_schema_version_fails(self, conn):
        result = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        del result["export_schema_version"]
        errors = validate_policy_features(result)
        assert any("Missing top-level key" in e for e in errors)


# ---------------------------------------------------------------------------
# TestEndToEnd
# ---------------------------------------------------------------------------


class TestEndToEnd:
    def test_full_export_synthetic_policy(self, conn):
        """Build all 3 files and validate the features file."""
        features = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        sources = build_policy_fact_sources(conn, DOC_ID, POLICY_ID, RUN_ID)
        clauses = build_policy_clauses_minimal(conn, DOC_ID, POLICY_ID)

        # Features valid
        errors = validate_policy_features(features)
        assert errors == [], f"Validation errors: {errors}"

        # Sources consistent with features
        assert features["pipeline_run_id"] == sources["pipeline_run_id"]
        assert len(sources["sources"]) == 20

        # Clauses present
        assert clauses["total_sections"] >= 1

    def test_features_and_sources_pages_agree(self, conn):
        """Accepted fact evidence_page must be the same in features and fact_sources."""
        features = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        sources = build_policy_fact_sources(conn, DOC_ID, POLICY_ID, RUN_ID)

        from derived.field_mapping import CONCEPT_FIELD_MAP

        field_to_concept = {v["field"]: k for k, v in CONCEPT_FIELD_MAP.items()}

        for field_name, feature in features["features"].items():
            if feature["fact_status"] != "present":
                continue
            concept = field_to_concept.get(field_name)
            if not concept:
                continue
            feat_page = feature["evidence_page"]
            src = sources["sources"].get(concept, {})
            accepted_id = src.get("accepted_candidate_id")
            for prov in src.get("provenance", []):
                if prov.get("candidate_id") == accepted_id:
                    assert feat_page == prov["page"], (
                        f"Page disagrees for {concept}: features={feat_page}, sources={prov['page']}"
                    )

    def test_export_roundtrip_json(self, conn):
        """Exported JSON must be valid JSON (serializable and parseable)."""
        features = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        json_str = json.dumps(features, ensure_ascii=False)
        parsed = json.loads(json_str)
        assert parsed["policy_id"] == POLICY_ID
        assert len(parsed["features"]) == 20


# ---------------------------------------------------------------------------
# TestProductBHandoff
# ---------------------------------------------------------------------------


class TestProductBHandoff:
    def _write_handoff_inputs(self, tmp_path, conn):
        export_root = tmp_path / "exports"
        policy_dir = export_root / POLICY_ID
        policy_dir.mkdir(parents=True)

        features = build_policy_features(conn, DOC_ID, POLICY_ID, RUN_ID)
        sources = build_policy_fact_sources(conn, DOC_ID, POLICY_ID, RUN_ID)
        clauses = build_policy_clauses_minimal(conn, DOC_ID, POLICY_ID)

        (policy_dir / "policy_features.json").write_text(
            json.dumps(features, indent=2), encoding="utf-8"
        )
        (policy_dir / "policy_fact_sources.json").write_text(
            json.dumps(sources, indent=2), encoding="utf-8"
        )
        (policy_dir / "policy_clauses_minimal.json").write_text(
            json.dumps(clauses, indent=2), encoding="utf-8"
        )

        gold = tmp_path / "gold"
        metadata_dir = gold / "policies" / POLICY_ID
        metadata_dir.mkdir(parents=True)
        metadata = {
            "policy_id": POLICY_ID,
            "policy_slug": POLICY_ID,
            "insurer": "Test Insurer",
            "plan_name": "Test Plan",
            "uin": "TSTHLIP00000V000000",
            "uin_base": "TSTHLIP00000",
            "file_hash": DOC_ID,
            "label_status": "reviewed",
        }
        (metadata_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
        return export_root, gold

    def _copy_export_policy(self, export_root, old_policy_id, new_policy_id):
        src = export_root / old_policy_id
        dst = export_root / new_policy_id
        dst.mkdir(parents=True)
        for filename in (
            "policy_features.json",
            "policy_fact_sources.json",
            "policy_clauses_minimal.json",
        ):
            data = json.loads((src / filename).read_text(encoding="utf-8"))
            data["policy_id"] = new_policy_id
            (dst / filename).write_text(json.dumps(data), encoding="utf-8")

    def test_handoff_package_manifest_includes_reviewed_policy(self, tmp_path, conn):
        export_root, gold = self._write_handoff_inputs(tmp_path, conn)
        output_root = tmp_path / "data" / "processed" / "product_b_export_v1"

        manifest = build_handoff(export_root, gold, output_root)

        assert manifest["policy_count"] == 1
        assert manifest["policies"][0]["policy_id"] == POLICY_ID
        assert (output_root / "manifest.json").is_file()
        assert (
            output_root / "benchmark_20_reviewed" / POLICY_ID / "policy_features.json"
        ).is_file()

    def test_handoff_package_copies_no_raw_interim_or_sqlite_files(self, tmp_path, conn):
        export_root, gold = self._write_handoff_inputs(tmp_path, conn)
        output_root = tmp_path / "data" / "processed" / "product_b_export_v1"

        build_handoff(export_root, gold, output_root)

        all_files = [str(p.relative_to(output_root)) for p in output_root.rglob("*") if p.is_file()]
        assert all(not f.endswith(".pdf") for f in all_files)
        assert all(".sqlite" not in f for f in all_files)
        assert all(not f.startswith("interim/") for f in all_files)

    def test_handoff_package_writes_checksums(self, tmp_path, conn):
        export_root, gold = self._write_handoff_inputs(tmp_path, conn)
        output_root = tmp_path / "data" / "processed" / "product_b_export_v1"

        build_handoff(export_root, gold, output_root)

        checksums = (output_root / "checksums.sha256").read_text(encoding="utf-8")
        assert "manifest.json" in checksums
        assert "benchmark_20_reviewed/test_policy/policy_features.json" in checksums

    def test_handoff_fails_when_policy_features_missing(self, tmp_path, conn):
        export_root, gold = self._write_handoff_inputs(tmp_path, conn)
        (export_root / POLICY_ID / "policy_features.json").unlink()
        output_root = tmp_path / "data" / "processed" / "product_b_export_v1"

        with pytest.raises(FileNotFoundError):
            build_handoff(export_root, gold, output_root)

    def test_handoff_includes_legacy_reviewed_metadata_without_label_status(self, tmp_path, conn):
        export_root, gold = self._write_handoff_inputs(tmp_path, conn)
        legacy_policy_id = "legacy_reviewed_policy"
        self._copy_export_policy(export_root, POLICY_ID, legacy_policy_id)

        metadata_dir = gold / "policies" / legacy_policy_id
        metadata_dir.mkdir(parents=True)
        metadata = {
            "policy_id": legacy_policy_id,
            "policy_slug": legacy_policy_id,
            "insurer": "Legacy Insurer",
            "plan_name": "Legacy Plan",
            "uin": "LGCHLIP00000V000000",
            "uin_base": "LGCHLIP00000",
            "file_hash": "sha256:legacy",
        }
        (metadata_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
        output_root = tmp_path / "data" / "processed" / "product_b_export_v1"

        manifest = build_handoff(export_root, gold, output_root)

        assert manifest["policy_count"] == 2
        assert {row["policy_id"] for row in manifest["policies"]} == {
            POLICY_ID,
            legacy_policy_id,
        }
