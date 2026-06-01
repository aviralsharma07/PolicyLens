"""
Concept → export field mapping — DSE-013

Maps each of the 20 priority concepts to its export field name, unit, and
value extraction strategy.

ADR-0027: All 20 concepts emitted in every export.
ADR-0028: Scalar extraction for simple types, full JSON for compound types.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# The 20-concept field map
# ---------------------------------------------------------------------------

# value_key: if set, extract that key from normalized_value_json as the scalar value.
#            if None, pass the full normalized_value_json dict as the value.
CONCEPT_FIELD_MAP: Dict[str, Dict[str, Any]] = {
    "ped_waiting_period": {
        "field": "ped_waiting_months",
        "unit": "months",
        "value_key": "months",
        "category": "waiting_period",
    },
    "initial_waiting_period": {
        "field": "initial_waiting_days",
        "unit": "days",
        "value_key": "days",
        "category": "waiting_period",
    },
    "specific_disease_waiting_periods": {
        "field": "specific_disease_waiting",
        "unit": "months",
        "value_key": None,
        "category": "waiting_period",
    },
    "room_rent_limit": {
        "field": "room_rent_limit",
        "unit": None,
        "value_key": None,
        "category": "room_rent",
    },
    "icu_limit": {
        "field": "icu_limit",
        "unit": None,
        "value_key": None,
        "category": "room_rent",
    },
    "co_pay": {
        "field": "copay_percentage",
        "unit": None,
        "value_key": None,
        "category": "cost",
    },
    "deductible": {
        "field": "deductible",
        "unit": None,
        "value_key": None,
        "category": "cost",
    },
    "cumulative_bonus_ncb": {
        "field": "cumulative_bonus_ncb",
        "unit": None,
        "value_key": None,
        "category": "benefit",
    },
    "restoration_benefit": {
        "field": "restoration_benefit",
        "unit": None,
        "value_key": None,
        "category": "benefit",
    },
    "ayush_coverage": {
        "field": "ayush_coverage",
        "unit": None,
        "value_key": None,
        "category": "benefit",
    },
    "modern_treatment_coverage": {
        "field": "modern_treatment_coverage",
        "unit": None,
        "value_key": None,
        "category": "benefit",
    },
    "maternity_waiting": {
        "field": "maternity_waiting_months",
        "unit": "months",
        "value_key": "months",
        "category": "waiting_period",
    },
    "newborn_coverage": {
        "field": "newborn_coverage",
        "unit": None,
        "value_key": None,
        "category": "benefit",
    },
    "organ_donor_coverage": {
        "field": "organ_donor_coverage",
        "unit": None,
        "value_key": None,
        "category": "benefit",
    },
    "ambulance_coverage": {
        "field": "ambulance_coverage",
        "unit": None,
        "value_key": None,
        "category": "benefit",
    },
    "free_look_period": {
        "field": "free_look_days",
        "unit": "days",
        "value_key": "days",
        "category": "regulatory",
    },
    "grace_period": {
        "field": "grace_period_days",
        "unit": "days",
        "value_key": "days",
        "category": "regulatory",
    },
    "renewability": {
        "field": "renewability",
        "unit": None,
        "value_key": None,
        "category": "regulatory",
    },
    "claim_intimation_timeline": {
        "field": "claim_intimation_days",
        "unit": "days",
        "value_key": None,
        "category": "claim",
    },
    "claim_settlement_timeline": {
        "field": "claim_settlement_days",
        "unit": "days",
        "value_key": None,
        "category": "claim",
    },
}

ALL_EXPORT_CONCEPTS: List[str] = sorted(CONCEPT_FIELD_MAP.keys())

VALID_FACT_STATUSES = {
    "present",
    "explicitly_not_covered",
    "not_applicable",
    "not_found",
    "ambiguous",
    "conflicting",
    "requires_manual_review",
}


def get_export_field_name(concept: str) -> str:
    """Map concept slug to export field name. Raises KeyError if unknown."""
    return CONCEPT_FIELD_MAP[concept]["field"]


def get_unit(concept: str) -> Optional[str]:
    """Map concept to unit string (days, months, percentage, or None)."""
    return CONCEPT_FIELD_MAP[concept]["unit"]


def extract_scalar_value(concept: str, normalized_value_json: Any) -> Any:
    """
    Extract the scalar export value from normalized_value_json.

    For simple types with value_key (e.g., free_look_period → "days"):
      {"days": 15} → 15

    For compound types without value_key (e.g., co_pay):
      {"components": [...]} → {"components": [...]}  (pass through)

    Returns None if no value extractable.
    """
    if normalized_value_json is None:
        return None

    # Parse JSON string if needed
    if isinstance(normalized_value_json, str):
        try:
            normalized_value_json = json.loads(normalized_value_json)
        except (json.JSONDecodeError, TypeError):
            return None

    if not isinstance(normalized_value_json, dict):
        return normalized_value_json

    mapping = CONCEPT_FIELD_MAP.get(concept)
    if not mapping:
        return normalized_value_json

    value_key = mapping.get("value_key")
    if value_key and value_key in normalized_value_json:
        return normalized_value_json[value_key]

    # No scalar key or key not present — return full dict
    return normalized_value_json if normalized_value_json else None
