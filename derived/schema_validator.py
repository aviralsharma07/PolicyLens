"""
Export schema validator — DSE-013

Validates exported JSON against the export_contract.md shape.
Returns a list of validation errors (empty = valid).
"""

from __future__ import annotations

from typing import Any, Dict, List

from derived.field_mapping import ALL_EXPORT_CONCEPTS, CONCEPT_FIELD_MAP, VALID_FACT_STATUSES

_REQUIRED_TOP_LEVEL = {
    "policy_id",
    "export_schema_version",
    "exported_at",
    "pipeline_run_id",
    "source_document",
    "product_identity",
    "features",
    "unresolved_concepts",
    "parse_quality",
}

_REQUIRED_FEATURE_FIELDS = {
    "value",
    "unit",
    "fact_status",
    "confidence",
    "method",
    "evidence",
    "evidence_page",
    "evidence_clause",
    "scope",
    "condition",
    "source_span_id",
}

_PRESENT_EVIDENCE_FIELDS = {"evidence", "evidence_page", "evidence_clause", "source_span_id"}


def validate_policy_features(features_doc: dict) -> List[str]:
    """
    Validate a policy_features.json document.

    Returns list of error strings. Empty list = valid.
    """
    errors: List[str] = []

    # Top-level keys
    for key in _REQUIRED_TOP_LEVEL:
        if key not in features_doc:
            errors.append(f"Missing top-level key: {key}")

    # Schema version
    if features_doc.get("export_schema_version") != "1.0":
        errors.append(
            f"export_schema_version must be '1.0', got {features_doc.get('export_schema_version')!r}"
        )

    # Features block
    features = features_doc.get("features", {})
    if not isinstance(features, dict):
        errors.append("features must be a dict")
        return errors

    # All 20 concepts must be present (mapped to their field names)
    expected_fields = {CONCEPT_FIELD_MAP[c]["field"] for c in ALL_EXPORT_CONCEPTS}
    actual_fields = set(features.keys())
    missing = expected_fields - actual_fields
    extra = actual_fields - expected_fields
    if missing:
        errors.append(f"Missing concept fields in features: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected fields in features: {sorted(extra)}")

    # Per-feature validation
    for field_name, feature in features.items():
        if not isinstance(feature, dict):
            errors.append(f"Feature {field_name} must be a dict")
            continue

        # Required feature fields
        for fkey in _REQUIRED_FEATURE_FIELDS:
            if fkey not in feature:
                errors.append(f"Feature {field_name} missing key: {fkey}")

        # Fact status must be valid
        status = feature.get("fact_status")
        if status not in VALID_FACT_STATUSES:
            errors.append(f"Feature {field_name}: invalid fact_status {status!r}")

        # Present facts must have evidence
        if status == "present":
            for ev_field in _PRESENT_EVIDENCE_FIELDS:
                if feature.get(ev_field) is None:
                    errors.append(f"Feature {field_name}: present fact missing {ev_field}")

        # Not-found facts must have null value
        if status == "not_found" and feature.get("value") is not None:
            errors.append(f"Feature {field_name}: not_found fact has non-null value")

    # Parse quality
    pq = features_doc.get("parse_quality", {})
    if not isinstance(pq, dict):
        errors.append("parse_quality must be a dict")
    else:
        for key in (
            "total_concepts_attempted",
            "concepts_resolved",
            "concepts_not_found",
            "overall_fill_rate",
        ):
            if key not in pq:
                errors.append(f"parse_quality missing key: {key}")

    return errors
