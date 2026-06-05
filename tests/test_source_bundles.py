import copy
import json
from pathlib import Path

from source_bundles.builder import build_registry
from source_bundles.validator import validate_registry, validate_registry_path


ROOT = Path(__file__).resolve().parents[1]


def test_example_source_bundle_registry_is_valid():
    errors = validate_registry_path(ROOT / "data/manifests/product_source_bundles_v1.example.json")
    assert errors == []


def test_validator_rejects_invalid_source_quality():
    registry = json.loads(
        (ROOT / "data/manifests/product_source_bundles_v1.example.json").read_text(
            encoding="utf-8"
        )
    )
    registry["bundles"][0]["source_quality"] = "trust_me_bro"
    errors = validate_registry(registry)
    assert any("source_quality invalid" in error for error in errors)


def test_validator_rejects_complete_bundle_without_pbt():
    registry = json.loads(
        (ROOT / "data/manifests/product_source_bundles_v1.example.json").read_text(
            encoding="utf-8"
        )
    )
    registry["bundles"][0]["documents"] = [
        doc
        for doc in registry["bundles"][0]["documents"]
        if doc["document_type"] != "product_benefit_table"
    ]
    registry["document_type_counts"] = {"cis": 1, "policy_wording": 1}
    errors = validate_registry(registry)
    assert any("complete missing docs" in error for error in errors)


def test_validator_rejects_source_identified_hash_until_downloaded():
    registry = json.loads(
        (ROOT / "data/manifests/product_source_bundles_v1.example.json").read_text(
            encoding="utf-8"
        )
    )
    document = registry["bundles"][0]["documents"][0]
    document["review_status"] = "source_identified"
    errors = validate_registry(registry)
    assert any("file_hash must be null until source_identified" in error for error in errors)


def test_builder_marks_policy_wording_only_bundle_missing_pbt(tmp_path):
    active = [
        {
            "document_id": "sha256:" + "a" * 64,
            "filename": "Example_Policy.pdf",
            "file_path": "Example/Example_Policy.pdf",
            "file_hash": "sha256:" + "a" * 64,
            "page_count": 10,
            "document_type": "policy_wording",
            "source_domain": "irdai",
            "uin": "EXAHLIP25001V012526",
            "match_status": "pending",
        }
    ]
    uin_report = {
        "results": [
            {
                "document_id": "sha256:" + "a" * 64,
                "uin_base": "EXAHLIP25001",
                "normalized_insurer": "Example Insurer",
                "lifecycle_product_name": "Example Health Plan",
                "match_status": "verified",
                "plan_match_score": 0.9,
            }
        ]
    }
    active_path = tmp_path / "active.json"
    uin_path = tmp_path / "uin.json"
    active_path.write_text(json.dumps(active), encoding="utf-8")
    uin_path.write_text(json.dumps(uin_report), encoding="utf-8")

    registry = build_registry(active_path, uin_path)

    assert registry["bundle_count"] == 1
    bundle = registry["bundles"][0]
    assert bundle["source_quality"] == "missing_pbt"
    assert bundle["product_name"] == "Example Health Plan"
    assert bundle["documents"][0]["document_type"] == "policy_wording"


def test_builder_applies_manual_aditya_birla_activ_care_override():
    registry = build_registry(
        active_manifest=ROOT / "data/manifests/active_policy_wordings_v1.json",
        uin_report=ROOT / "data/manifests/uin_match_report_v1.json",
        manual_overrides=ROOT / "data/manifests/product_source_bundle_manual_overrides_v1.json",
    )
    bundles = {bundle["product_id"]: bundle for bundle in registry["bundles"]}
    bundle = bundles["aditya_birla_activ_care"]
    assert bundle["source_quality"] == "acceptable_with_known_gap"
    assert bundle["variants"] == ["Classic", "Premier", "Standard"]
    document_types = {doc["document_type"] for doc in bundle["documents"]}
    assert {"policy_wording", "cis", "product_benefit_table"} <= document_types
    source_identified = [doc for doc in bundle["documents"] if doc["review_status"] == "source_identified"]
    assert source_identified
    assert all(doc["file_hash"] is None for doc in source_identified)
    assert validate_registry(registry) == []


def test_validator_detects_duplicate_product_id():
    registry = json.loads(
        (ROOT / "data/manifests/product_source_bundles_v1.example.json").read_text(
            encoding="utf-8"
        )
    )
    duplicate = copy.deepcopy(registry["bundles"][0])
    registry["bundles"].append(duplicate)
    registry["bundle_count"] = 2
    registry["source_quality_counts"] = {"complete": 2}
    registry["document_type_counts"] = {"cis": 2, "policy_wording": 2, "product_benefit_table": 2}
    errors = validate_registry(registry)
    assert any("product_id duplicate" in error for error in errors)

