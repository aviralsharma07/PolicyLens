"""Validation helpers for the Product A ontology registry."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List


REQUIRED_CONCEPT_FIELDS = {
    "concept_id",
    "display_name",
    "category",
    "definition",
    "value_shape",
    "export_field",
    "unit",
    "active_deterministic",
    "extractor_status",
    "evidence_required_for_statuses",
    "allowed_statuses",
    "display_rules",
}

VALID_EXTRACTOR_STATUSES = {"implemented", "planned", "deferred"}


def validate_ontology(ontology: Dict[str, Any]) -> List[str]:
    """Return validation issue strings for an ontology document."""
    issues: List[str] = []
    valid_statuses = set(ontology.get("fact_statuses", []))
    concepts = ontology.get("concepts", [])

    if ontology.get("schema_version") != "ontology.v1":
        issues.append("schema_version must be ontology.v1")
    if not concepts:
        issues.append("concepts must not be empty")
    if not valid_statuses:
        issues.append("fact_statuses must not be empty")

    concept_ids = [concept.get("concept_id") for concept in concepts]
    export_fields = [concept.get("export_field") for concept in concepts]

    for concept_id, count in Counter(concept_ids).items():
        if count > 1:
            issues.append(f"duplicate concept_id: {concept_id}")
    for export_field, count in Counter(export_fields).items():
        if count > 1:
            issues.append(f"duplicate export_field: {export_field}")

    for concept in concepts:
        concept_id = concept.get("concept_id", "<missing>")
        missing = sorted(REQUIRED_CONCEPT_FIELDS - set(concept))
        if missing:
            issues.append(f"{concept_id}: missing fields {missing}")

        extractor_status = concept.get("extractor_status")
        if extractor_status not in VALID_EXTRACTOR_STATUSES:
            issues.append(f"{concept_id}: invalid extractor_status {extractor_status!r}")

        allowed_statuses = set(concept.get("allowed_statuses", []))
        invalid_statuses = sorted(allowed_statuses - valid_statuses)
        if invalid_statuses:
            issues.append(f"{concept_id}: invalid allowed_statuses {invalid_statuses}")

        required_evidence_statuses = set(concept.get("evidence_required_for_statuses", []))
        invalid_evidence_statuses = sorted(required_evidence_statuses - allowed_statuses)
        if invalid_evidence_statuses:
            issues.append(
                f"{concept_id}: evidence_required_for_statuses not allowed {invalid_evidence_statuses}"
            )

        display_rules = concept.get("display_rules", {})
        if not isinstance(display_rules, dict) or not display_rules.get("not_found"):
            issues.append(f"{concept_id}: missing display_rules.not_found")

    return issues


def validate_ontology_or_raise(ontology: Dict[str, Any]) -> None:
    """Raise ValueError if the ontology document is invalid."""
    issues = validate_ontology(ontology)
    if issues:
        raise ValueError("Invalid ontology:\n" + "\n".join(f"- {issue}" for issue in issues))
