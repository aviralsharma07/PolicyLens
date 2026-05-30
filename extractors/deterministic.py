from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional

from extractors.base import BaseExtractor
from extractors.evidence import clean_space
from extractors.models import FactCandidate
from normalizers.duration import find_durations
from normalizers.percentage import find_percentages


def _lower(text: str) -> str:
    return clean_space(text).lower()


def _has_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _window(text: str, start: int, end: int, radius: int = 190) -> str:
    cleaned = clean_space(text)
    left = max(0, start - radius)
    right = min(len(cleaned), end + radius)
    return cleaned[left:right].strip(" ,;:")


def _duration_value(duration: Dict[str, Any], unit: str) -> Optional[int]:
    normalized = duration["normalized"]
    return normalized.get(unit)


def _is_definition_only(text_lower: str) -> bool:
    definition_markers = [
        " means ",
        " shall mean ",
        " refers to ",
        " is a cost-sharing requirement ",
    ]
    waiting_markers = [
        "waiting period",
        "excluded",
        "covered after",
        "shall be covered",
        "after the expiry",
        "continuous coverage",
        "first policy",
    ]
    return _has_any(text_lower, definition_markers) and not _has_any(text_lower, waiting_markers)


class FreeLookExtractor(BaseExtractor):
    concept = "free_look_period"
    extractor_name = "free_look_period"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        for clause in clauses:
            text = clean_space(clause.get("text", ""))
            lower = text.lower()
            if "free look" not in lower and "free-look" not in lower:
                continue
            durations = find_durations(text)
            primary = next((d for d in durations if _duration_value(d, "days") == 15), None)
            if not primary:
                for duration in durations:
                    candidates.append(
                        self.make_candidate(
                            index=len(candidates),
                            clause=clause,
                            value_json=duration["normalized"],
                            normalized_value_json=duration["normalized"],
                            evidence_text=_window(text, duration["span"][0], duration["span"][1]),
                            pipeline_run_id=pipeline_run_id,
                            confidence=0.55,
                            pattern_id="free_look_non_primary_duration",
                            rejection_reason="free_look_primary_15_days_not_found",
                            debug={"duration": duration},
                        )
                    )
                continue

            value_json: Dict[str, Any] = {"days": 15}
            distance = next((d for d in durations if _duration_value(d, "days") == 30), None)
            if distance and "distance" in lower:
                value_json["distance_marketing_days"] = 30
            candidates.append(
                self.make_candidate(
                    index=len(candidates),
                    clause=clause,
                    value_json=value_json,
                    normalized_value_json={"days": 15},
                    evidence_text=_window(text, primary["span"][0], primary["span"][1]),
                    pipeline_run_id=pipeline_run_id,
                    confidence=0.98,
                    pattern_id="free_look_15_days",
                    debug={"durations": durations},
                )
            )
        return candidates


class GracePeriodExtractor(BaseExtractor):
    concept = "grace_period"
    extractor_name = "grace_period"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        for clause in clauses:
            text = clean_space(clause.get("text", ""))
            lower = text.lower()
            if "free look" in lower or "free-look" in lower:
                continue
            renewal_grace = (
                "renewal" in lower
                and "expiry" in lower
                and ("within thirty days" in lower or "within 30 days" in lower)
            )
            if "grace period" not in lower and not renewal_grace:
                continue
            for duration in find_durations(text):
                days = _duration_value(duration, "days")
                if not days:
                    continue
                confidence = 0.96 if days == 30 else 0.58
                rejection_reason = None if days == 30 else "non_primary_grace_duration"
                if "installment" in lower or "instalment" in lower:
                    confidence -= 0.25
                    rejection_reason = rejection_reason or "installment_grace_not_renewal_grace"
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"days": days},
                        normalized_value_json={"days": days},
                        evidence_text=_window(text, duration["span"][0], duration["span"][1]),
                        pipeline_run_id=pipeline_run_id,
                        confidence=confidence,
                        pattern_id="renewal_grace_days",
                        rejection_reason=rejection_reason,
                        debug={"duration": duration, "renewal_grace": renewal_grace},
                    )
                )
        return candidates


class PedWaitingPeriodExtractor(BaseExtractor):
    concept = "ped_waiting_period"
    extractor_name = "ped_waiting_period"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        for clause in clauses:
            text = clean_space(clause.get("text", ""))
            lower = text.lower()
            if not _has_any(lower, ["pre-existing", "pre existing", "ped"]):
                continue
            if _is_definition_only(lower):
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={},
                        normalized_value_json={},
                        evidence_text=text[: min(len(text), 220)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.2,
                        pattern_id="ped_definition_only",
                        rejection_reason="definition_only_without_waiting_duration",
                    )
                )
                continue
            for duration in find_durations(text):
                months = _duration_value(duration, "months")
                if not months:
                    continue
                around = _window(text, duration["span"][0], duration["span"][1], radius=240)
                around_lower = around.lower()
                if not _has_any(around_lower, ["pre-existing", "pre existing", "ped", "waiting", "excluded", "covered"]):
                    continue
                confidence = 0.96 if months in {24, 36, 48} else 0.72
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"months": months},
                        normalized_value_json={"months": months},
                        evidence_text=around,
                        pipeline_run_id=pipeline_run_id,
                        confidence=confidence,
                        pattern_id="ped_waiting_duration",
                        debug={"duration": duration},
                    )
                )
        return candidates


class InitialWaitingPeriodExtractor(BaseExtractor):
    concept = "initial_waiting_period"
    extractor_name = "initial_waiting_period"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        for clause in clauses:
            text = clean_space(clause.get("text", ""))
            lower = text.lower()
            if _has_any(lower, ["free look", "free-look", "grace period", "pre-existing", "pre existing"]):
                continue
            signals = [
                "first thirty days",
                "first 30 days",
                "30-day waiting",
                "30 day waiting",
                "initial waiting",
                "within thirty days",
                "within 30 days",
            ]
            if not _has_any(lower, signals):
                continue
            if "first" not in lower and "initial" not in lower and "waiting" not in lower:
                continue
            for duration in find_durations(text):
                days = _duration_value(duration, "days")
                if days != 30:
                    continue
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"days": 30},
                        normalized_value_json={"days": 30},
                        evidence_text=_window(text, duration["span"][0], duration["span"][1], radius=240),
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.96,
                        pattern_id="initial_wait_30_days",
                        debug={"duration": duration},
                    )
                )
        return candidates


class CoPayExtractor(BaseExtractor):
    concept = "co_pay"
    extractor_name = "co_pay"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        care_smart: Optional[Dict[str, Any]] = None
        care_age: Optional[Dict[str, Any]] = None

        for clause in clauses:
            text = clean_space(clause.get("text", ""))
            lower = text.lower()
            percentages = find_percentages(text)
            has_copay_term = _has_any(lower, ["co-payment", "co payment", "co-pay", "copay"])
            star_age_copay = (
                "10%" in lower
                and "each and every claim amount" in lower
                and ("beyond 60 years" in lower or "beyond sixty years" in lower)
            )

            if has_copay_term and not percentages and _is_definition_only(lower):
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={},
                        normalized_value_json={},
                        evidence_text=text[: min(len(text), 220)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.2,
                        pattern_id="copay_definition_only",
                        rejection_reason="definition_only_without_percentage",
                    )
                )
                continue

            if "smart select" in lower and percentages:
                pct = next((p for p in percentages if p["value"] == 20), percentages[0])
                care_smart = {"clause": clause, "percentage": pct, "text": text}
                continue

            if has_copay_term and ("61 years" in lower or "61 yrs" in lower) and "schedule" in lower:
                care_age = {"clause": clause, "text": text}
                continue

            if not percentages or (not has_copay_term and not star_age_copay):
                continue

            pct = next((p for p in percentages if star_age_copay and p["value"] == 10), percentages[0])
            percent_value = pct["value"]
            value_json: Dict[str, Any] = {"percentage": percent_value}
            normalized: Dict[str, Any] = {"percentage": percent_value}
            condition_json = None
            confidence = 0.94
            pattern_id = "copay_percentage"
            if "admissible claim amount" in lower or "claim amount admissible" in lower:
                normalized["basis"] = "admissible_claim_amount"
                value_json["basis"] = "admissible_claim_amount"
                confidence = 0.97
            if star_age_copay:
                condition_json = {"entry_age": "beyond_60_years"}
                value_json["condition"] = "insured persons beyond 60 years at entry level and renewals thereafter"
                confidence = 0.96
                pattern_id = "star_age_based_copay"
            candidates.append(
                self.make_candidate(
                    index=len(candidates),
                    clause=clause,
                    value_json=value_json,
                    normalized_value_json=normalized,
                    evidence_text=_window(text, pct["span"][0], pct["span"][1], radius=220),
                    pipeline_run_id=pipeline_run_id,
                    confidence=confidence,
                    pattern_id=pattern_id,
                    condition_json=condition_json,
                    debug={"percentage": pct},
                )
            )

        if care_smart:
            pct = care_smart["percentage"]
            components: List[Dict[str, Any]] = [
                {"scope": "smart_select_non_annexure_iii_hospital", "percentage": pct["value"]},
            ]
            if care_age:
                components.append(
                    {
                        "scope": "age_61_plus_optional_copayment",
                        "percentage": None,
                        "schedule_dependent": True,
                    }
                )
            candidates.append(
                self.make_candidate(
                    index=len(candidates),
                    clause=care_smart["clause"],
                    value_json={"components": components},
                    normalized_value_json={"components": components},
                    evidence_text=_window(care_smart["text"], pct["span"][0], pct["span"][1], radius=260),
                    pipeline_run_id=pipeline_run_id,
                    confidence=0.97,
                    pattern_id="care_smart_select_copay_components",
                    condition_json={"components": components},
                    debug={"merged_age_schedule_clause": bool(care_age)},
                )
            )
            if care_age:
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=care_age["clause"],
                        value_json={
                            "components": [
                                {
                                    "scope": "age_61_plus_optional_copayment",
                                    "percentage": None,
                                    "schedule_dependent": True,
                                }
                            ]
                        },
                        normalized_value_json={
                            "components": [
                                {
                                    "scope": "age_61_plus_optional_copayment",
                                    "percentage": None,
                                    "schedule_dependent": True,
                                }
                            ]
                        },
                        evidence_text=care_age["text"][: min(len(care_age["text"]), 260)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.72,
                        pattern_id="care_age_schedule_copay_component",
                        rejection_reason="merged_into_smart_select_component_fact",
                    )
                )

        return candidates


EXTRACTORS = [
    FreeLookExtractor(),
    GracePeriodExtractor(),
    PedWaitingPeriodExtractor(),
    InitialWaitingPeriodExtractor(),
    CoPayExtractor(),
]
