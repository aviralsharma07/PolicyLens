import json
from pathlib import Path

from source_bundles.mvp import (
    build_latest_audit,
    build_mvp_bundle_registry,
    build_verified_candidates,
    validation_errors_for_verified_manifest,
)
from source_bundles.validator import validate_registry


ROOT = Path(__file__).resolve().parents[1]


def test_verified_candidate_manifest_is_valid():
    candidates = {
        "candidates": [
            {
                "candidate_id": "example_plan",
                "insurer_id": "example",
                "insurer_display_name": "Example",
                "product_name": "Example Plan",
                "product_role": "flagship",
                "collection_priority": "P1",
                "expected_source_bundle_difficulty": "low",
                "official_reference_url": "https://example.com/product",
                "why_it_matters": "Example",
                "likely_uin": "EXAHLIP25001V012526",
            }
        ]
    }
    manual = {
        "candidates": [
            {
                "candidate_id": "example_plan",
                "selection_status": "verified_current_with_gap",
                "latest_sellability_status": "live",
                "verified_product_name": "Example Plan",
                "verified_uin": "EXAHLIP25001V012526",
                "official_product_page_url": "https://example.com/product",
                "official_wording_url": "https://example.com/wording.pdf",
                "official_cis_url": "https://example.com/cis.pdf",
                "official_brochure_or_prospectus_url": None,
                "official_pbt_or_table_url": None,
                "irdai_cross_check_status": "official_uin_matches_candidate",
                "archive_used": False,
                "verification_notes": "Current official product page and current official wording/CIS are identified.",
                "review_confidence": "high",
            }
        ]
    }
    verified = build_verified_candidates(candidates, manual)
    assert validation_errors_for_verified_manifest(verified) == []
    audit = build_latest_audit(verified)
    assert audit["selection_status_counts"] == {"verified_current_with_gap": 1}


def test_mvp_bundle_builder_marks_gap_when_current_urls_exist_but_local_wording_is_legacy(tmp_path):
    verified_manifest = {
        "candidates": [
            {
                "candidate_id": "example_plan",
                "insurer_id": "example",
                "insurer_display_name": "Example",
                "verified_product_name": "Example Plan",
                "selection_status": "verified_current",
                "latest_sellability_status": "live",
                "verified_uin": "EXAHLIP26001V022626",
                "verified_uin_base": "EXAHLIP26001",
                "verified_product_version": "V022626",
                "official_product_page_url": "https://example.com/product",
                "official_wording_url": "https://example.com/current-wording.pdf",
                "official_cis_url": "https://example.com/current-cis.pdf",
                "official_brochure_or_prospectus_url": None,
                "official_pbt_or_table_url": None,
                "irdai_cross_check_status": "official_uin_differs_from_local_legacy_wording",
                "review_confidence": "high",
                "verification_notes": "Current live page found. Local wording is older than current official UIN.",
                "archive_used": False,
                "replacement_for_candidate_id": None,
            }
        ]
    }
    active_manifest = [
        {
            "document_id": "sha256:" + "a" * 64,
            "filename": "Example_Plan.pdf",
            "file_path": "Example/Example_Plan.pdf",
            "file_hash": "sha256:" + "a" * 64,
            "page_count": 10,
            "document_type": "policy_wording",
            "source_domain": "website",
            "insurer": "Example",
            "uin": "EXAHLIP25001V012526",
        }
    ]
    uin_report = {
        "results": [
            {
                "document_id": "sha256:" + "a" * 64,
                "lifecycle_product_name": "Example Plan",
                "matched_uin": "EXAHLIP25001V012526",
                "uin_base": "EXAHLIP25001",
                "normalized_insurer": "Example",
            }
        ]
    }

    registry = build_mvp_bundle_registry(
        verified_manifest=verified_manifest,
        active_manifest=active_manifest,
        uin_report=uin_report,
        bundle_overrides=None,
        download_index_path=None,
    )
    bundle = registry["bundles"][0]
    assert bundle["source_quality"] == "missing_pbt"
    assert validate_registry(registry) == []


def test_real_verified_manifest_and_bundle_registry_validate():
    verified_path = ROOT / "data/manifests/mvp_product_candidates_verified_v1.json"
    bundle_path = ROOT / "data/manifests/product_source_bundles_mvp_v1.json"
    if not verified_path.exists() or not bundle_path.exists():
        return
    verified = json.loads(verified_path.read_text(encoding="utf-8"))
    assert validation_errors_for_verified_manifest(verified) == []
    bundle_registry = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert validate_registry(bundle_registry) == []
