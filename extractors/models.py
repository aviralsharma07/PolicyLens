from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


TARGET_CONCEPTS = [
    # Wave 0 — original 5
    "free_look_period",
    "grace_period",
    "ped_waiting_period",
    "initial_waiting_period",
    "co_pay",
    # Wave 1 — DSE-018
    "renewability",
    "claim_settlement_timeline",
    "ayush_coverage",
    "ambulance_coverage",
    "cumulative_bonus_ncb",
    "specific_disease_waiting_periods",
    "maternity_waiting",
    "organ_donor_coverage",
    # Wave 2 — DSE-021
    "claim_intimation_timeline",
]

FACT_STATUSES = {
    "present",
    "explicitly_not_covered",
    "not_applicable",
    "not_found",
    "ambiguous",
    "conflicting",
    "requires_manual_review",
}


@dataclass
class FactCandidate:
    candidate_id: str
    concept: str
    value_json: Optional[Dict[str, Any]]
    normalized_value_json: Optional[Dict[str, Any]]
    fact_status: str
    scope_json: Optional[Dict[str, Any]]
    condition_json: Optional[Dict[str, Any]]
    extraction_method: str
    confidence: float
    evidence_span_id: Optional[str]
    pipeline_run_id: str
    evidence_page: Optional[int]
    evidence_text: Optional[str]
    evidence_clause_id: Optional[str]
    evidence_line_ids: List[str]
    extractor_name: str
    extractor_version: str
    pattern_id: str
    source: str
    accepted: bool = False
    rejection_reason: Optional[str] = None
    debug: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def not_found_fact(
    *,
    concept: str,
    pipeline_run_id: str,
    extractor_name: str,
    extractor_version: str = "1.0.0",
) -> Dict[str, Any]:
    return {
        "concept": concept,
        "value_json": None,
        "normalized_value_json": None,
        "fact_status": "not_found",
        "scope_json": None,
        "condition_json": None,
        "extraction_method": "deterministic",
        "confidence": 0.0,
        "evidence_span_id": None,
        "pipeline_run_id": pipeline_run_id,
        "evidence_page": None,
        "evidence_text": None,
        "evidence_clause_id": None,
        "evidence_line_ids": [],
        "extractor_name": extractor_name,
        "extractor_version": extractor_version,
    }
