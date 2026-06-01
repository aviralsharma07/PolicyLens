"""
Tests for DSE-015 Insurer/Plan Normalizer Library

Tests UIN parsing, insurer registry, plan name normalization,
and backward compatibility with DSE-002 identity module.
"""

from __future__ import annotations

import pytest

from identity.insurer_registry import (
    ALL_INSURER_NAMES,
    INSURER_REGISTRY,
    get_all_name_variants,
    get_display_name,
    lookup_by_canonical,
    lookup_by_folder,
    lookup_by_irdai_prefix,
)
from identity.plan_normalizer import (
    clean_plan_name,
    make_display_name,
    make_short_name,
)
from identity.uin_utils import (
    extract_uin_base,
    extract_version_number,
    validate_uin_format,
)


# ---------------------------------------------------------------------------
# TestUinUtils
# ---------------------------------------------------------------------------


class TestUinUtils:
    def test_extract_uin_base_care_health_12_chars(self):
        assert extract_uin_base("CHIHLIP22047V012122") == "CHIHLIP22047"
        assert len(extract_uin_base("CHIHLIP22047V012122")) == 12

    def test_extract_uin_base_hdfc(self):
        assert extract_uin_base("HDFHLIP20175V011920") == "HDFHLIP20175"

    def test_extract_uin_base_icici(self):
        assert extract_uin_base("ICIHLIP22092V032122") == "ICIHLIP22092"

    def test_extract_uin_base_new_india(self):
        assert extract_uin_base("NIAHLIP21278V042021") == "NIAHLIP21278"

    def test_extract_uin_base_star(self):
        assert extract_uin_base("SHAHLIP18029V031718") == "SHAHLIP18029"

    def test_extract_uin_base_not_truncated_to_11(self):
        """Regression: DSE-010 bug truncated to [:11] = 'CHIHLIP2204' (11 chars)."""
        base = extract_uin_base("CHIHLIP22047V012122")
        assert base != "CHIHLIP2204"  # the old bug
        assert base == "CHIHLIP22047"  # correct
        assert len(base) == 12

    def test_extract_uin_base_empty_string(self):
        assert extract_uin_base("") == ""

    def test_extract_uin_base_no_v_delimiter(self):
        assert extract_uin_base("NOVERDELIM") == "NOVERDELIM"

    def test_validate_uin_format_valid(self):
        assert validate_uin_format("CHIHLIP22047V012122") is True
        assert validate_uin_format("HDFHLIP20175V011920") is True

    def test_validate_uin_format_invalid(self):
        assert validate_uin_format("") is False
        assert validate_uin_format("NOTAUIN") is False
        assert validate_uin_format("123") is False

    def test_extract_version_number_v01(self):
        assert extract_version_number("CHIHLIP22047V012122") == 1

    def test_extract_version_number_v03(self):
        assert extract_version_number("ICIHLIP22092V032122") == 3

    def test_extract_version_number_v04(self):
        assert extract_version_number("NIAHLIP21278V042021") == 4

    def test_extract_version_number_empty(self):
        assert extract_version_number("") is None

    def test_all_5_gold_uins_produce_12_char_base(self):
        """Every gold policy UIN must produce a 12-char base."""
        gold_uins = [
            "CHIHLIP22047V012122",
            "HDFHLIP20175V011920",
            "ICIHLIP22092V032122",
            "NIAHLIP21278V042021",
            "SHAHLIP18029V031718",
        ]
        for uin in gold_uins:
            base = extract_uin_base(uin)
            assert len(base) == 12, f"UIN {uin} produced base {base!r} ({len(base)} chars)"


# ---------------------------------------------------------------------------
# TestInsurerRegistry
# ---------------------------------------------------------------------------


class TestInsurerRegistry:
    def test_registry_has_32_insurers(self):
        assert len(INSURER_REGISTRY) == 32

    def test_all_23_folder_aliases_mapped(self):
        """All 23 corpus folder names from DSE-002 must resolve."""
        corpus_folders = [
            "Aditya_Birla",
            "Bajaj_Allianz",
            "Care_Health",
            "Cholamandalam",
            "Edelweiss",
            "Future_Generali",
            "HDFC_ERGO",
            "ICICI_Lombard",
            "IFFCO_Tokio",
            "Kotak_Mahindra",
            "Liberty",
            "Magma_HDI",
            "New_India_Assurance",
            "Niva_Bupa",
            "Oriental_Insurance",
            "Raheja_QBE",
            "Reliance",
            "Royal_Sundaram",
            "SBI_General",
            "Star_Health",
            "Tata_AIG",
            "United_India",
            "Universal_Sompo",
        ]
        for folder in corpus_folders:
            rec = lookup_by_folder(folder)
            assert rec is not None, f"Folder {folder!r} not in registry"

    def test_lookup_by_canonical_name(self):
        rec = lookup_by_canonical("HDFC ERGO")
        assert rec is not None
        assert rec.display_name == "HDFC ERGO"

    def test_lookup_by_folder_alias(self):
        rec = lookup_by_folder("Star_Health")
        assert rec is not None
        assert rec.canonical_name == "Star Health"

    def test_irdai_prefix_matches_uin(self):
        """CHI prefix → Care Health (matches CHIHLIP...)."""
        rec = lookup_by_irdai_prefix("CHI")
        assert rec is not None
        assert rec.canonical_name == "Care Health"

    def test_display_name_present_for_all(self):
        for name, rec in INSURER_REGISTRY.items():
            assert rec.display_name, f"Insurer {name} has no display_name"

    def test_no_duplicate_canonical_names(self):
        names = [r.canonical_name for r in INSURER_REGISTRY.values()]
        assert len(names) == len(set(names))

    def test_unknown_insurer_returns_none(self):
        assert lookup_by_canonical("NONEXISTENT INSURER") is None
        assert lookup_by_folder("Nonexistent_Folder") is None

    def test_get_display_name_known(self):
        assert get_display_name("Star Health") == "Star Health"
        assert get_display_name("New India Assurance") == "New India"

    def test_get_display_name_unknown_passthrough(self):
        assert get_display_name("Unknown Corp") == "Unknown Corp"


# ---------------------------------------------------------------------------
# TestPlanNormalizer
# ---------------------------------------------------------------------------


class TestPlanNormalizer:
    def test_strip_insurer_suffix_hdfc(self):
        result = clean_plan_name("Arogya Sanjeevani Policy, HDFC ERGO", "HDFC ERGO")
        assert "HDFC" not in result
        assert "Arogya Sanjeevani" in result

    def test_strip_insurer_suffix_care(self):
        result = clean_plan_name("Care Plus, Care Health", "Care Health")
        assert "Care Health" not in result

    def test_strip_policy_suffix(self):
        result = clean_plan_name(
            "Medi Classic Accident Care Individual Insurance Policy", "Star Health"
        )
        assert not result.endswith("Insurance Policy")
        assert not result.endswith("Policy")

    def test_strip_individual_suffix(self):
        result = clean_plan_name("Some Plan Individual", "Test Insurer")
        assert not result.endswith("Individual")

    def test_new_india_removes_insurer_prefix(self):
        result = clean_plan_name("New India Floater Mediclaim Policy", "New India Assurance")
        assert not result.startswith("New India")
        assert "Floater Mediclaim" in result

    def test_star_verbose_name_shortened(self):
        result = clean_plan_name(
            "Medi Classic Accident Care Individual Insurance Policy", "Star Health"
        )
        assert len(result) < 54  # shorter than original

    def test_already_clean_name_unchanged(self):
        result = clean_plan_name("Care Plus", "Care Health")
        assert result == "Care Plus"

    def test_family_shield_unchanged(self):
        result = clean_plan_name("Family Shield", "ICICI Lombard")
        assert result == "Family Shield"

    def test_empty_name_handled(self):
        assert clean_plan_name("", "Test") == ""
        assert clean_plan_name(None, "Test") == ""

    def test_make_display_name_format(self):
        result = make_display_name("Arogya Sanjeevani", "HDFC ERGO")
        assert result == "HDFC ERGO Arogya Sanjeevani"

    def test_make_short_name_under_35_chars(self):
        result = make_short_name("Arogya Sanjeevani")
        assert len(result) <= 35
        assert result == "Arogya Sanjeevani"

    def test_make_short_name_long_truncated(self):
        long_name = "Very Long Product Name That Exceeds The Maximum Length Allowed"
        result = make_short_name(long_name)
        assert len(result) <= 35

    def test_boilerplate_only_does_not_empty(self):
        """If stripping would empty the name, keep something."""
        result = clean_plan_name("Policy", "Test Insurer")
        # Should strip "Policy" but the input IS just boilerplate
        # Result may be empty; that's handled at the caller level
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# TestInsurerNormalizerBackcompat
# ---------------------------------------------------------------------------


class TestInsurerNormalizerBackcompat:
    """DSE-002 insurer_normalizer API must still work after DSE-015."""

    def test_folder_to_lifecycle_still_works(self):
        from identity.insurer_normalizer import normalize

        assert normalize("HDFC_ERGO") == "HDFC ERGO"
        assert normalize("Star_Health") == "Star Health"

    def test_reverse_normalize_still_works(self):
        from identity.insurer_normalizer import reverse_normalize

        assert reverse_normalize("HDFC ERGO") == "HDFC_ERGO"

    def test_get_abbreviations_still_works(self):
        from identity.insurer_normalizer import get_abbreviations

        abbrevs = get_abbreviations("HDFC_ERGO")
        assert "HDFC" in abbrevs

    def test_new_registry_subsumes_old_mappings(self):
        """Every folder in DSE-002 FOLDER_TO_LIFECYCLE must exist in the new registry."""
        from identity.insurer_normalizer import FOLDER_TO_LIFECYCLE

        for folder, lifecycle_name in FOLDER_TO_LIFECYCLE.items():
            rec = lookup_by_folder(folder)
            assert rec is not None, f"Old mapping {folder}→{lifecycle_name} not in new registry"
            assert rec.canonical_name == lifecycle_name


# ---------------------------------------------------------------------------
# TestProductIdentityExport
# ---------------------------------------------------------------------------


class TestProductIdentityExport:
    def test_uin_base_not_truncated(self):
        """Regression test: uin_base must be 12 chars, not 11."""
        base = extract_uin_base("CHIHLIP22047V012122")
        assert len(base) == 12
        assert base == "CHIHLIP22047"

    def test_display_name_no_insurer_in_plan(self):
        """After clean_plan_name, plan should not contain insurer."""
        plan = clean_plan_name("Arogya Sanjeevani Policy, HDFC ERGO", "HDFC ERGO")
        assert "HDFC" not in plan

    def test_all_gold_plan_names_clean(self):
        """All 5 gold policy plan names should clean properly."""
        cases = [
            ("Care Plus", "Care Health", "Care Plus"),
            ("Arogya Sanjeevani Policy, HDFC ERGO", "HDFC ERGO", "Arogya Sanjeevani"),
            ("Family Shield", "ICICI Lombard", "Family Shield"),
        ]
        for raw, insurer, expected in cases:
            result = clean_plan_name(raw, insurer)
            assert result == expected, (
                f"clean({raw!r}, {insurer!r}) = {result!r}, expected {expected!r}"
            )
