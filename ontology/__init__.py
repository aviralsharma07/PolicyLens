"""Canonical Product A insurance concept ontology."""

from ontology.loader import concepts_by_id, load_ontology
from ontology.validator import validate_ontology, validate_ontology_or_raise

__all__ = [
    "concepts_by_id",
    "load_ontology",
    "validate_ontology",
    "validate_ontology_or_raise",
]
