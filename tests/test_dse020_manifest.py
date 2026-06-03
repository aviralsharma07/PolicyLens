from pathlib import Path

from scripts.build_dse020_manifest import build_manifest_entries, generated_slug_base, validate_manifest


def _entry(file_path: str, file_hash: str = "sha256:abc123", **extra):
    data = {
        "document_id": file_hash,
        "file_hash": file_hash,
        "file_path": file_path,
        "filename": Path(file_path).name,
        "insurer": Path(file_path).parent.name,
        "uin": "ABC",
        "page_count": 10,
        "source_domain": "irdai",
        "document_type": "policy_wording",
        "corpus_status": "active",
        "match_status": "verified",
        "triage_flags": [],
    }
    data.update(extra)
    return data


def test_generated_slug_base_uses_folder_and_filename():
    entry = _entry("01_New_India_Assurance/NewIndia_Floater_Mediclaim_IRDAI.pdf")
    assert generated_slug_base(entry) == "01_new_india_assurance_newindia_floater_mediclaim_irdai"


def test_gold_hash_mapping_uses_existing_gold_slug():
    entries, collisions = build_manifest_entries(
        [_entry("09_HDFC_ERGO/HDFC_ERGO_Arogya_Sanjeevani.pdf", "sha256:gold")],
        {"sha256:gold": "hdfc_arogya_sanjeevani"},
    )
    assert entries[0]["slug"] == "hdfc_arogya_sanjeevani"
    assert entries[0]["is_reviewed_gold"] is True
    assert entries[0]["gold_slug"] == "hdfc_arogya_sanjeevani"
    assert collisions == []


def test_colliding_generated_slugs_get_hash_suffixes():
    active = [
        _entry("02_Star_Health/Foo-Bar.pdf", "sha256:11111111aaaaaaaa"),
        _entry("02_Star_Health/Foo_Bar.pdf", "sha256:22222222bbbbbbbb"),
    ]
    entries, collisions = build_manifest_entries(active, {})
    slugs = {entry["slug"] for entry in entries}
    assert slugs == {
        "02_star_health_foo_bar_11111111",
        "02_star_health_foo_bar_22222222",
    }
    assert collisions[0]["slug"] == "02_star_health_foo_bar"
    assert collisions[0]["count"] == 2


def test_manifest_validator_rejects_wrong_count_and_duplicate_slugs():
    manifest = {
        "policy_count": 2,
        "unique_slug_count": 1,
        "policies": [
            _entry("a/Foo.pdf", "sha256:1", slug="dup"),
            _entry("b/Bar.pdf", "sha256:2", slug="dup"),
        ],
    }
    issues = validate_manifest(manifest)
    assert any("policy_count=2 expected=647" in issue for issue in issues)
    assert any("final slugs are not unique" in issue for issue in issues)
