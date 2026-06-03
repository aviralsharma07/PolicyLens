"""Loader helpers for the canonical concept ontology registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


DEFAULT_ONTOLOGY_PATH = Path(__file__).with_name("concepts.v1.json")


def load_ontology(path: str | Path | None = None) -> Dict[str, Any]:
    """Load ontology JSON from disk."""
    ontology_path = Path(path) if path is not None else DEFAULT_ONTOLOGY_PATH
    with ontology_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def concepts_by_id(path: str | Path | None = None) -> Dict[str, Dict[str, Any]]:
    """Return ontology concepts keyed by concept_id."""
    ontology = load_ontology(path)
    return {concept["concept_id"]: concept for concept in ontology.get("concepts", [])}
