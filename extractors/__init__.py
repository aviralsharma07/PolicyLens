"""Deterministic fact extractors."""
from extractors.models import TARGET_CONCEPTS, FactCandidate
from extractors.registry import run_extractors

__all__ = ["TARGET_CONCEPTS", "FactCandidate", "run_extractors"]
