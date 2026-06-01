from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional

from extractors.base import BaseExtractor
from extractors.evidence import clean_space
from extractors.models import FactCandidate
from normalizers.duration import find_durations, normalize_duration, parse_number_token
from normalizers.percentage import find_percentages


def _lower(text: str) -> str:
    return (
        clean_space(text)
        .replace("ﬁ", "fi")
        .replace("ﬂ", "fl")
        .replace("ﬀ", "ff")
        .replace("ﬃ", "ffi")
        .replace("ﬄ", "ffl")
        .lower()
    )


def _has_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _window(text: str, start: int, end: int, radius: int = 190) -> str:
    cleaned = clean_space(text)
    left = max(0, start - radius)
    right = min(len(cleaned), end + radius)
    return cleaned[left:right].strip(" ,;:")


def _context_window(clauses: List[Dict[str, Any]], index: int, radius: int = 1) -> str:
    left = max(0, index - radius)
    right = min(len(clauses), index + radius + 1)
    return _lower(" ".join(str(clauses[i].get("text", "")) for i in range(left, right)))


def _duration_value(duration: Dict[str, Any], unit: str) -> Optional[int]:
    normalized = duration["normalized"]
    return normalized.get(unit)


def _ped_duration_candidates(text: str) -> List[Dict[str, Any]]:
    durations = list(find_durations(text))
    seen_spans = {tuple(item["span"]) for item in durations}
    loose_re = re.compile(
        r"(?:expiry of|waiting period of|covered after a)\s+"
        r"(?P<num>\d+|twenty four|thirty six|forty eight|four|three|two)"
        r"(?:\W+\w+){0,12}?\W+(?P<unit>months?|years?)\b",
        re.IGNORECASE,
    )
    for match in loose_re.finditer(text):
        if match.span() in seen_spans:
            continue
        value = parse_number_token(match.group("num"))
        if value is None:
            continue
        unit = match.group("unit")
        durations.append(
            {
                "value": value,
                "unit": unit.lower(),
                "normalized": normalize_duration(value, unit),
                "span": match.span("num"),
                "text": match.group(0),
            }
        )
    return durations


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
        for idx, clause in enumerate(clauses):
            text = clean_space(clause.get("text", ""))
            lower = _lower(text)
            context = _context_window(clauses, idx)
            has_free_look_context = "free look" in context or "free-look" in context
            current_has_period = _has_any(
                lower,
                [
                    "free look",
                    "free-look",
                    "allowed a period",
                    "allowed free look period",
                    "at least 15 days",
                    "fifteen days from date of receipt",
                    "thirty days beginning",
                ],
            )
            if not has_free_look_context or not current_has_period:
                continue
            durations = find_durations(text)
            primary = next((d for d in durations if _duration_value(d, "days") == 15), None)
            if not primary:
                primary = next(
                    (
                        d
                        for d in durations
                        if _duration_value(d, "days") == 30
                        and _has_any(lower, ["free look", "free-look", "thirty days beginning"])
                    ),
                    None,
                )
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

            primary_days = _duration_value(primary, "days") or 15
            value_json: Dict[str, Any] = {"days": primary_days}
            distance = next((d for d in durations if _duration_value(d, "days") == 30), None)
            if distance and primary_days == 15 and "distance" in lower:
                value_json["distance_marketing_days"] = 30
            candidates.append(
                self.make_candidate(
                    index=len(candidates),
                    clause=clause,
                    value_json=value_json,
                    normalized_value_json={"days": primary_days},
                    evidence_text=_window(text, primary["span"][0], primary["span"][1]),
                    pipeline_run_id=pipeline_run_id,
                    confidence=0.98,
                    pattern_id="free_look_15_days" if primary_days == 15 else "free_look_30_days",
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
            lower = _lower(text)
            if "free look" in lower or "free-look" in lower:
                continue
            renewal_grace = (
                "renewal" in lower
                and ("expiry" in lower or "due date" in lower)
                and (
                    "within thirty days" in lower
                    or "within 30 days" in lower
                    or "up to 30 days" in lower
                    or "period of 30 days" in lower
                )
            )
            if "grace period" not in lower and not renewal_grace:
                continue
            for duration in find_durations(text):
                days = _duration_value(duration, "days")
                if not days:
                    continue
                around = _window(text, duration["span"][0], duration["span"][1], radius=180)
                around_lower = _lower(around)
                if not _has_any(
                    around_lower,
                    [
                        "grace",
                        "renewal",
                        "renewed",
                        "premium due",
                        "installment premium",
                        "instalment premium",
                    ],
                ):
                    continue
                confidence = 0.96 if days == 30 else 0.58
                rejection_reason = None if days == 30 else "non_primary_grace_duration"
                if "installment" in lower or "instalment" in lower:
                    if days in {15, 30} and _has_any(around_lower, ["grace", "premium"]):
                        confidence = max(confidence, 0.93)
                        rejection_reason = None
                    else:
                        confidence -= 0.25
                        rejection_reason = rejection_reason or "installment_grace_not_renewal_grace"
                elif days == 15 and "grace period" in around_lower:
                    confidence = max(confidence, 0.93)
                    rejection_reason = None
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"days": days},
                        normalized_value_json={"days": days},
                        evidence_text=around,
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
            lower = _lower(text)
            if not _has_any(lower, ["pre-existing", "pre existing", "ped"]):
                continue
            definition_duration_only = (
                _has_any(lower, ["diagnosed by a physician", "medical advice or treatment"])
                and _has_any(lower, ["prior to the effective date", "within 48 months prior"])
                and not _has_any(
                    lower,
                    [
                        "waiting period",
                        "excluded until",
                        "after the expiry",
                        "continuous coverage",
                        "shall be covered after",
                    ],
                )
            )
            if definition_duration_only:
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
                        rejection_reason="definition_duration_not_waiting_period",
                    )
                )
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
            if (
                _has_any(lower, ["pre-existing disease waiting period", "pre existing disease waiting period"])
                and _has_any(lower, ["policy schedule", "product benefit table", "time period specified"])
                and not find_durations(text)
            ):
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"schedule_dependent": True},
                        normalized_value_json={"schedule_dependent": True},
                        evidence_text=text[: min(len(text), 320)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.94,
                        pattern_id="ped_schedule_dependent",
                    )
                )
                continue
            for duration in _ped_duration_candidates(text):
                months = _duration_value(duration, "months")
                if not months:
                    continue
                around = _window(text, duration["span"][0], duration["span"][1], radius=240)
                around_lower = _lower(around)
                if not _has_any(around_lower, ["pre-existing", "pre existing", "ped"]):
                    continue
                if not _has_any(
                    around_lower,
                    [
                        "waiting",
                        "excluded",
                        "after the expiry",
                        "continuous coverage",
                        "shall be covered after",
                    ],
                ):
                    continue
                if _has_any(around_lower, ["instalment", "installment", "premium due"]) and _has_any(
                    around_lower, ["continuity benefits", "initial 30 days"]
                ):
                    continue
                direct_ped_waiting = _has_any(
                    around_lower,
                    [
                        "pre-existing diseases",
                        "pre existing diseases",
                        "pre-existing disease (ped)",
                        "pre existing disease (ped)",
                        "pre-existing illness",
                    ],
                ) and _has_any(around_lower, ["excluded until", "expiry", "continuous coverage"])
                incidental_ped_reference = (
                    "if these are pre-existing" in around_lower
                    or "if these are pre existing" in around_lower
                )
                if incidental_ped_reference and not direct_ped_waiting:
                    confidence = 0.74
                else:
                    confidence = (
                        0.98
                        if direct_ped_waiting and months in {12, 24, 36, 48}
                        else 0.96
                        if months in {12, 24, 36, 48}
                        else 0.72
                    )
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
            lower = _lower(text)
            if _has_any(lower, ["free look", "free-look", "grace period"]):
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
                around = _window(text, duration["span"][0], duration["span"][1], radius=240)
                around_lower = _lower(around)
                if _has_any(
                    around_lower,
                    [
                        "claim intimation",
                        "claim notification",
                        "documents",
                        "arbitrator",
                        "arbitration",
                    ],
                ):
                    continue
                if not (
                    _has_any(
                        around_lower,
                        ["illness", "disease", "condition", "treatment", "expenses", "hospitalization"],
                    )
                    and _has_any(around_lower, ["excluded", "exclusion", "waiting"])
                    and _has_any(
                        around_lower,
                        [
                            "first policy",
                            "first 30 days",
                            "first thirty days",
                            "commencement",
                            "initial waiting",
                        ],
                    )
                ):
                    continue
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"days": 30},
                        normalized_value_json={"days": 30},
                        evidence_text=around,
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
            lower = _lower(text)
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

            if star_age_copay:
                pct = next((p for p in percentages if p["value"] == 10), percentages[0])
            else:
                copay_match = re.search(r"co\s*[-]?\s*payment|co\s*pay|copay", lower)
                if copay_match:
                    pct = min(percentages, key=lambda p: abs(p["span"][0] - copay_match.start()))
                else:
                    pct = percentages[0]
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
