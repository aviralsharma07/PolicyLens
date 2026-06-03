import json
from pathlib import Path

from derived.field_mapping import ALL_EXPORT_CONCEPTS, CONCEPT_FIELD_MAP
from extractors.models import FACT_STATUSES, TARGET_CONCEPTS
from ontology.loader import concepts_by_id, load_ontology
from ontology.validator import validate_ontology


ROOT = Path(__file__).resolve().parents[1]


def test_ontology_is_valid():
    ontology = load_ontology()
    assert validate_ontology(ontology) == []


def test_ontology_contains_exactly_20_priority_concepts():
    concepts = concepts_by_id()
    assert len(concepts) == 20
    assert set(concepts) == set(ALL_EXPORT_CONCEPTS)


def test_required_concept_fields_present():
    for concept in concepts_by_id().values():
        assert concept["concept_id"]
        assert concept["display_name"]
        assert concept["category"]
        assert concept["definition"]
        assert concept["value_shape"]
        assert "export_field" in concept
        assert "unit" in concept
        assert isinstance(concept["active_deterministic"], bool)
        assert concept["extractor_status"] in {"implemented", "planned", "deferred"}
        assert concept["allowed_statuses"]
        assert concept["display_rules"]["not_found"]


def test_fact_statuses_match_agents_fact_status_contract():
    ontology = load_ontology()
    assert set(ontology["fact_statuses"]) == FACT_STATUSES
    for concept in ontology["concepts"]:
        assert set(concept["allowed_statuses"]) == FACT_STATUSES
        assert set(concept["evidence_required_for_statuses"]) <= FACT_STATUSES


def test_export_mapping_agrees_with_ontology():
    concepts = concepts_by_id()
    assert set(CONCEPT_FIELD_MAP) == set(concepts)
    export_fields = []
    for concept_id, mapping in CONCEPT_FIELD_MAP.items():
        concept = concepts[concept_id]
        assert concept["export_field"] == mapping["field"]
        assert concept["unit"] == mapping["unit"]
        assert concept["category"] == mapping["category"]
        export_fields.append(concept["export_field"])
    assert len(export_fields) == len(set(export_fields))


def test_active_deterministic_concepts_match_extractors():
    concepts = concepts_by_id()
    active = {
        concept_id
        for concept_id, concept in concepts.items()
        if concept["active_deterministic"]
    }
    assert active == set(TARGET_CONCEPTS)
    for concept_id in TARGET_CONCEPTS:
        assert concepts[concept_id]["extractor_status"] == "implemented"


def test_gold_fact_concepts_are_all_in_ontology():
    concepts = set(concepts_by_id())
    policies_root = ROOT / "gold_corpus" / "policies"
    missing = []
    for facts_path in policies_root.glob("*/facts.json"):
        facts = json.loads(facts_path.read_text(encoding="utf-8"))
        fact_concepts = {fact["concept"] for fact in facts}
        if fact_concepts != concepts:
            missing.append((facts_path, sorted(concepts - fact_concepts), sorted(fact_concepts - concepts)))
    assert missing == []
