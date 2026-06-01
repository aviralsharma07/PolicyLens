from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

from extractors.deterministic import EXTRACTORS
from extractors.models import FACT_STATUSES, TARGET_CONCEPTS, FactCandidate, not_found_fact


MIN_ACCEPT_CONFIDENCE = 0.9


def _candidate_sort_key(candidate: FactCandidate) -> Tuple[float, int, str]:
    page = candidate.evidence_page if candidate.evidence_page is not None else 9999
    return (-candidate.confidence, page, candidate.candidate_id)


def _accepted_dict(candidate: FactCandidate) -> Dict[str, Any]:
    accepted = candidate.to_dict()
    accepted["accepted"] = True
    accepted["rejection_reason"] = None
    return accepted


def resolve_concept(
    *,
    concept: str,
    candidates: List[FactCandidate],
    pipeline_run_id: str,
    extractor_name: str,
) -> Dict[str, Any]:
    usable = [
        candidate
        for candidate in candidates
        if candidate.concept == concept
        and candidate.fact_status in {"present", "explicitly_not_covered"}
        and not candidate.rejection_reason
        and candidate.confidence >= MIN_ACCEPT_CONFIDENCE
        and candidate.evidence_text
        and candidate.evidence_clause_id
    ]
    if not usable:
        return not_found_fact(
            concept=concept,
            pipeline_run_id=pipeline_run_id,
            extractor_name=extractor_name,
        )
    usable.sort(key=_candidate_sort_key)
    return _accepted_dict(usable[0])


def run_extractors(
    clauses: List[Dict[str, Any]],
    pipeline_run_id: str,
    concepts: Iterable[str] = TARGET_CONCEPTS,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    concept_set = set(concepts)
    candidates: List[FactCandidate] = []
    extractor_by_concept = {}
    for extractor in EXTRACTORS:
        if extractor.concept not in concept_set:
            continue
        extractor_by_concept[extractor.concept] = extractor.extractor_name
        candidates.extend(extractor.extract(clauses, pipeline_run_id))

    accepted = []
    for concept in TARGET_CONCEPTS:
        if concept not in concept_set:
            continue
        accepted.append(
            resolve_concept(
                concept=concept,
                candidates=candidates,
                pipeline_run_id=pipeline_run_id,
                extractor_name=extractor_by_concept.get(concept, concept),
            )
        )

    candidate_dicts = [candidate.to_dict() for candidate in candidates]
    accepted_ids = {
        fact.get("candidate_id")
        for fact in accepted
        if fact.get("candidate_id")
    }
    for candidate in candidate_dicts:
        if candidate["candidate_id"] in accepted_ids:
            candidate["accepted"] = True
            candidate["rejection_reason"] = None
        elif not candidate.get("rejection_reason"):
            candidate["rejection_reason"] = "lower_scoring_candidate"

    for fact in accepted:
        if fact["fact_status"] not in FACT_STATUSES:
            raise ValueError(f"Invalid fact_status for {fact['concept']}: {fact['fact_status']}")

    return candidate_dicts, accepted
