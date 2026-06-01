from __future__ import annotations

from typing import Any, Dict, List, Optional

from extractors.evidence import clause_source, contains_evidence
from extractors.models import FactCandidate


class BaseExtractor:
    concept = ""
    extractor_name = ""
    extractor_version = "1.0.0"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        raise NotImplementedError

    def make_candidate(
        self,
        *,
        index: int,
        clause: Dict[str, Any],
        value_json: Dict[str, Any],
        normalized_value_json: Dict[str, Any],
        evidence_text: str,
        pipeline_run_id: str,
        confidence: float,
        pattern_id: str,
        fact_status: str = "present",
        scope_json: Optional[Dict[str, Any]] = None,
        condition_json: Optional[Dict[str, Any]] = None,
        rejection_reason: Optional[str] = None,
        debug: Optional[Dict[str, Any]] = None,
    ) -> FactCandidate:
        verified = contains_evidence(clause.get("text", ""), evidence_text)
        if not verified and not rejection_reason:
            rejection_reason = "evidence_text_not_found_in_clause"
        return FactCandidate(
            candidate_id=f"{self.extractor_name}_{index:04d}",
            concept=self.concept,
            value_json=value_json,
            normalized_value_json=normalized_value_json,
            fact_status=fact_status,
            scope_json=scope_json or {"cover": "base_policy"},
            condition_json=condition_json,
            extraction_method="deterministic",
            confidence=confidence if verified else min(confidence, 0.4),
            evidence_span_id=clause_source(clause) if verified else None,
            pipeline_run_id=pipeline_run_id,
            evidence_page=clause.get("page_start") if verified else None,
            evidence_text=evidence_text if verified else None,
            evidence_clause_id=clause.get("clause_id") if verified else None,
            evidence_line_ids=clause.get("line_ids", []) if verified else [],
            extractor_name=self.extractor_name,
            extractor_version=self.extractor_version,
            pattern_id=pattern_id,
            source="section_tree_clause",
            accepted=False,
            rejection_reason=rejection_reason,
            debug=debug or {},
        )
