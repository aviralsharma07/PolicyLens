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


def _slash_month_options(text: str) -> List[Dict[str, Any]]:
    """Parse compact policy shorthand such as "24/48 months"."""
    options: List[Dict[str, Any]] = []
    slash_re = re.compile(
        r"(?:(?:ninety|90)\s+days\s*/\s*)?"
        r"(?P<first>24|48)\s*/\s*(?P<second>24|48)\s*months?\b",
        re.IGNORECASE,
    )
    for match in slash_re.finditer(text):
        for group in ("first", "second"):
            value = int(match.group(group))
            options.append(
                {
                    "value": value,
                    "unit": "months",
                    "normalized": {"months": value},
                    "span": match.span(group),
                    "text": match.group(0),
                }
            )
    return options


def _noisy_day_candidates(text: str) -> List[Dict[str, Any]]:
    """Recover day durations split by PDF column noise, e.g. "15 r i days"."""
    durations = list(find_durations(text))
    seen_spans = {tuple(item["span"]) for item in durations}
    noisy_re = re.compile(r"\b(?P<num>7|15|30|45|60|90)(?:\W+\w{1,3}){0,3}\W+days?\b", re.I)
    for match in noisy_re.finditer(text):
        if match.span() in seen_spans:
            continue
        value = int(match.group("num"))
        durations.append(
            {
                "value": value,
                "unit": "days",
                "normalized": {"days": value},
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
                _has_any(
                    lower,
                    ["pre-existing disease waiting period", "pre existing disease waiting period"],
                )
                and _has_any(
                    lower, ["policy schedule", "product benefit table", "time period specified"]
                )
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
                if _has_any(
                    around_lower, ["instalment", "installment", "premium due"]
                ) and _has_any(around_lower, ["continuity benefits", "initial 30 days"]):
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
                        [
                            "illness",
                            "disease",
                            "condition",
                            "treatment",
                            "expenses",
                            "hospitalization",
                        ],
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

            if (
                has_copay_term
                and ("61 years" in lower or "61 yrs" in lower)
                and "schedule" in lower
            ):
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
                value_json["condition"] = (
                    "insured persons beyond 60 years at entry level and renewals thereafter"
                )
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
                    evidence_text=_window(
                        care_smart["text"], pct["span"][0], pct["span"][1], radius=260
                    ),
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


class RenewabilityExtractor(BaseExtractor):
    concept = "renewability"
    extractor_name = "renewability"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        for idx, clause in enumerate(clauses):
            text = clean_space(clause.get("text", ""))
            lower = _lower(text)
            if not _has_any(lower, ["renewal", "renewable", "renewed", "renews"]):
                continue
            isolation_signals = [
                "renewal means",
                "renewal of the policy",
                "renewal of policy",
                "renewable for life",
                "renewable on",
                "renewal on same terms",
                "shall be renewed",
                "may be renewed",
                "can be renewed",
                "will be renewed",
                "renewal is subject",
                "renewal shall",
                "lifetime renewal",
                "renewed annually",
                "renewal of this policy",
                "renewal of cover",
                "policy renewal",
                "consent to renewal",
            ]
            if not _has_any(lower, isolation_signals):
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
                        pattern_id="renewability_definition_only",
                        rejection_reason="definition_only_without_renewal_language",
                    )
                )
                continue
            candidates.append(
                self.make_candidate(
                    index=len(candidates),
                    clause=clause,
                    value_json={"renewable": True},
                    normalized_value_json={"renewable": True},
                    evidence_text=text[: min(len(text), 300)],
                    pipeline_run_id=pipeline_run_id,
                    confidence=0.96,
                    pattern_id="renewability_lifetime",
                )
            )
        return candidates


class ClaimSettlementTimelineExtractor(BaseExtractor):
    concept = "claim_settlement_timeline"
    extractor_name = "claim_settlement_timeline"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        for idx, clause in enumerate(clauses):
            text = clean_space(clause.get("text", ""))
            lower = _lower(text)
            neighbor_context = clean_space(
                " ".join(
                    str(clauses[i].get("text", ""))
                    for i in range(max(0, idx - 1), min(len(clauses), idx + 2))
                )
            )
            signal_context = _lower(neighbor_context)
            if not re.search(
                r"(?:shall\s+)?settle\b|settlement\b|repudiate\b|reject\s+a\s+claim",
                signal_context,
            ):
                continue
            if not _has_any(signal_context, ["claim", "clam", "penal interest"]):
                continue

            durations = _noisy_day_candidates(text)
            scored_durations = []
            for duration in durations:
                days = _duration_value(duration, "days")
                if not days or days not in {7, 15, 30, 45, 60, 90}:
                    continue
                d_window_text = _window(text, duration["span"][0], duration["span"][1], radius=280)
                d_window = _lower(d_window_text)
                if not _has_any(d_window, ["claim", "clam", "penal interest"]):
                    if not _has_any(signal_context, ["claim", "clam", "penal interest"]):
                        continue
                if not _has_any(
                    f"{d_window} {signal_context}",
                    ["settle", "settlement", "repudiate", "reject a claim", "reject the claim"],
                ):
                    continue
                has_document_context = _has_any(
                    f"{d_window} {signal_context}",
                    [
                        "last necessary",
                        "receipt",
                        "recept",
                        "document",
                        "documentation",
                        "payment of claim",
                        "penal interest",
                    ],
                )
                if not has_document_context:
                    continue
                settle_score = 0
                intimation_terms = [
                    "intimation",
                    "notification",
                    "report",
                    "submission",
                    "furnish",
                    "hospitalization",
                    "discharge",
                    "submit",
                    "pre-author",
                    "pre author",
                    "authorization",
                    "authorisation",
                    "portability",
                    "renewal",
                    "premium",
                ]
                settlement_terms = [
                    "settle",
                    "settlement",
                    "penal interest",
                    "penalty",
                    "discharge of claim",
                    "repudiate",
                    "reject a claim",
                    "reject the claim",
                    "last necessary",
                ]
                for t in intimation_terms:
                    if t in d_window:
                        settle_score -= 2
                for t in settlement_terms:
                    if t in d_window:
                        settle_score += 3
                if _has_any(d_window, ["deficiency", "reminder", "initial request"]) and not _has_any(
                    d_window, ["investigation", "settle or repudiate", "settle or reject"]
                ):
                    settle_score -= 5
                if _has_any(
                    d_window,
                    ["intimated", "intimation", "submission", "submit", "documents to the company"],
                ) and not _has_any(d_window, ["settle claim", "settle or", "repudiate", "reject"]):
                    continue
                if "delay beyond stipulated" in d_window:
                    continue
                if settle_score <= 0:
                    continue
                has_investigation = _has_any(
                    d_window, ["investigation", "enquiry", "inquiry", "query"]
                )
                is_investigation_settlement = (
                    has_investigation
                    and days >= 45
                    and _has_any(d_window, ["settle the claim", "settle or reject", "settle or repudiate"])
                )
                is_investigation_completion = (
                    has_investigation
                    and days <= 30
                    and _has_any(d_window, ["complete such investigation", "complete such"])
                    and not _has_any(d_window, ["settle or reject a claim", "settle or repudiate a claim"])
                )
                if is_investigation_completion:
                    continue
                scored_durations.append(
                    (days, duration, settle_score, has_investigation, is_investigation_settlement)
                )
            if not scored_durations:
                continue
            non_investigation = [
                (d, dur, sc, inv, inv_settle)
                for d, dur, sc, inv, inv_settle in scored_durations
                if not inv
            ]
            if non_investigation:
                primary_group = non_investigation
            else:
                primary_group = [
                    (d, dur, sc, inv, inv_settle)
                    for d, dur, sc, inv, inv_settle in scored_durations
                    if not inv_settle
                ] or scored_durations
            primary_group.sort(key=lambda x: (-x[2], x[0], x[1]["span"][0]))
            primary_days, primary_dur, _, _, _ = primary_group[0]
            value_json: Dict[str, Any] = {"days": primary_days}
            normalized: Dict[str, Any] = {"days": primary_days}
            all_others = [
                (d, dur)
                for d, dur, sc, inv, inv_settle in scored_durations
                if d != primary_days and inv_settle and d > primary_days
            ]
            if all_others:
                all_others.sort(key=lambda x: x[0])
                value_json["investigation_days"] = all_others[0][0]
                normalized["investigation_days"] = all_others[0][0]
            has_inv = "investigation_days" in value_json
            evidence_start = min([primary_dur["span"][0]] + [dur["span"][0] for _, dur in all_others])
            evidence_end = max([primary_dur["span"][1]] + [dur["span"][1] for _, dur in all_others])
            confidence = 0.96
            if primary_days >= 45 and _has_any(_lower(text), ["investigation", "settle the claim"]):
                confidence = 0.91
            candidates.append(
                self.make_candidate(
                    index=len(candidates),
                    clause=clause,
                    value_json=value_json,
                    normalized_value_json=normalized,
                    evidence_text=_window(text, evidence_start, evidence_end, radius=260),
                    pipeline_run_id=pipeline_run_id,
                    confidence=confidence,
                    pattern_id="claim_settlement_investigation_days"
                    if has_inv
                    else "claim_settlement_days",
                    debug={"durations": durations, "days_options": scored_durations},
                )
            )
        return candidates


class AyushCoverageExtractor(BaseExtractor):
    concept = "ayush_coverage"
    extractor_name = "ayush_coverage"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        _has_ayush_definition = False
        _definition_clause = None
        _has_exclusion_clause = False
        for idx, clause in enumerate(clauses):
            text = clean_space(clause.get("text", ""))
            lower = _lower(text)
            ayush_terms = [
                "ayush",
                "ayurveda",
                "unani",
                "siddha",
                "homeopathy",
                "alternate medicine",
                "alternative medicine",
                "alternate system",
                "alternative system",
                "non-allopathic",
                "non allopathic",
            ]
            if not _has_any(lower, ayush_terms):
                continue
            if _is_definition_only(lower):
                # Only count as AYUSH definition if AYUSH term is the SUBJECT
                # (text before "means"/"is a"/"refers to"), not a passing mention.
                subject_end = len(lower)
                for m in [" means ", " shall mean ", " refers to "]:
                    p = lower.find(m)
                    if p >= 0:
                        subject_end = min(subject_end, p)
                subject = lower[:subject_end]
                if _has_any(subject, ayush_terms):
                    _has_ayush_definition = True
                    if _definition_clause is None:
                        _definition_clause = clause
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={},
                        normalized_value_json={},
                        evidence_text=text[: min(len(text), 220)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.2,
                        pattern_id="ayush_definition_only",
                        rejection_reason="definition_only_without_coverage_language",
                    )
                )
                continue
            if _has_any(
                lower, ["shall not cover", "not cover", "excluded", "not payable", "not admissible"]
            ):
                _has_exclusion_clause = True
                continue
            ayush_term_pos = -1
            for term in ayush_terms:
                pos = lower.find(term)
                if pos >= 0:
                    if ayush_term_pos == -1 or pos < ayush_term_pos:
                        ayush_term_pos = pos
            if ayush_term_pos >= 0:
                near_ayush = lower[max(0, ayush_term_pos - 200) : ayush_term_pos + 300]
                coverage_nearby = _has_any(
                    near_ayush,
                    ["cover", "covered", "coverage", "pay", "reimburse", "expenses", "benefit"],
                )
                clause_has_coverage = _has_any(
                    lower,
                    ["cover", "covered", "coverage", "pay", "reimburse", "expenses", "benefit"],
                )
                in_practitioner_context = _has_any(lower, ["practitioner"]) and _has_any(
                    lower, ["council", "register", "license", "licence"]
                )
                in_definition_context = _has_any(
                    near_ayush, [" means ", " shall mean ", " refers to "]
                )
                if in_practitioner_context and in_definition_context:
                    candidates.append(
                        self.make_candidate(
                            index=len(candidates),
                            clause=clause,
                            value_json={},
                            normalized_value_json={},
                            evidence_text=text[: min(len(text), 220)],
                            pipeline_run_id=pipeline_run_id,
                            confidence=0.2,
                            pattern_id="ayush_practitioner_qualification",
                            rejection_reason="ayush_term_in_practitioner_qualification_not_coverage",
                        )
                    )
                    continue
                if coverage_nearby:
                    candidates.append(
                        self.make_candidate(
                            index=len(candidates),
                            clause=clause,
                            value_json={"covered": True},
                            normalized_value_json={"covered": True},
                            evidence_text=text[: min(len(text), 250)],
                            pipeline_run_id=pipeline_run_id,
                            confidence=0.95,
                            pattern_id="ayush_coverage_present",
                        )
                    )
                elif clause_has_coverage:
                    candidates.append(
                        self.make_candidate(
                            index=len(candidates),
                            clause=clause,
                            value_json={"covered": True},
                            normalized_value_json={"covered": True},
                            evidence_text=text[: min(len(text), 250)],
                            pipeline_run_id=pipeline_run_id,
                            confidence=0.85,
                            pattern_id="ayush_coverage_far_from_term",
                        )
                    )
            else:
                if not _has_any(
                    lower,
                    ["cover", "covered", "coverage", "pay", "reimburse", "expenses", "benefit"],
                ):
                    continue
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"covered": True},
                        normalized_value_json={"covered": True},
                        evidence_text=text[: min(len(text), 250)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.85,
                        pattern_id="ayush_coverage_far_from_term",
                    )
                )
        # Fallback: if no high-confidence present candidate found, but AYUSH is defined
        # and not explicitly excluded, emit present.
        has_usable_present = any(
            c.value_json
            and c.value_json.get("covered") is True
            and c.confidence >= 0.9
            and c.evidence_text
            and c.evidence_clause_id
            for c in candidates
        )
        if not has_usable_present and _has_ayush_definition and not _has_exclusion_clause:
            candidates.append(
                self.make_candidate(
                    index=len(candidates),
                    clause=_definition_clause,
                    value_json={"covered": True},
                    normalized_value_json={"covered": True},
                    evidence_text=(_definition_clause.get("text", "")[:250]),
                    pipeline_run_id=pipeline_run_id,
                    confidence=0.9,
                    pattern_id="ayush_coverage_implied_by_definition",
                )
            )
        return candidates


class AmbulanceCoverageExtractor(BaseExtractor):
    concept = "ambulance_coverage"
    extractor_name = "ambulance_coverage"

    def _has_ambulance_nearby(self, search_lower: str, pos: int, radius: int = 80) -> bool:
        left = max(0, pos - radius)
        right = min(len(search_lower), pos + radius)
        return "ambulance" in search_lower[left:right]

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        for idx, clause in enumerate(clauses):
            text = clean_space(clause.get("text", ""))
            lower = _lower(text)
            amb_pos = lower.find("ambulance")
            if amb_pos < 0:
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
                        pattern_id="ambulance_definition_only",
                        rejection_reason="definition_only_without_ambulance_coverage",
                    )
                )
                continue
            amb_window = _window(text, amb_pos, amb_pos + 10, radius=200)
            amb_lower = _lower(amb_window)
            if "ambulance" not in amb_lower:
                continue
            if not _has_any(
                amb_lower,
                [
                    "charge",
                    "expense",
                    "cover",
                    "pay",
                    "reimburse",
                    "up to",
                    "rs.",
                    "benefit",
                    "provided",
                    "limit",
                    "sum insured",
                    "available",
                    "included",
                    "entitled",
                ],
            ):
                continue
            if _has_any(
                amb_lower, ["not cover", "not payable", "not admissible", "excluded", "exclusion"]
            ):
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"conditional": True},
                        normalized_value_json={"coverage_status": "conditional"},
                        evidence_text=amb_window[: min(len(amb_window), 250)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.7,
                        pattern_id="ambulance_conditional",
                    )
                )
                continue
            has_sum_insured = (
                "% of sum insured" in amb_lower
                or "% of the sum insured" in amb_lower
                or "percent of sum insured" in amb_lower
                or "percent of the sum insured" in amb_lower
            )
            has_schedule_signals = _has_any(
                amb_lower,
                [
                    "schedule",
                    "as specified",
                    "as per",
                    "benefit schedule",
                    "policy schedule",
                    "as per the schedule",
                ],
            )
            rc_signals = _has_any(amb_lower, ["rs.", "limit of", "maximum of"])
            if has_schedule_signals and not rc_signals and not has_sum_insured:
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"schedule_dependent": True},
                        normalized_value_json={"schedule_dependent": True},
                        evidence_text=amb_window[: min(len(amb_window), 300)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.9,
                        pattern_id="ambulance_schedule_dependent",
                    )
                )
                continue
            if has_sum_insured:
                percentages = find_percentages(amb_window)
                for pct in percentages:
                    pct_center = (pct["span"][0] + pct["span"][1]) // 2
                    pct_sub = _lower(amb_window[max(0, pct_center - 80) : pct_center + 80])
                    if _has_any(
                        pct_sub, ["ambulance", "% of sum insured", "percent of sum insured"]
                    ):
                        around = _window(amb_window, pct["span"][0], pct["span"][1], radius=180)
                        candidates.append(
                            self.make_candidate(
                                index=len(candidates),
                                clause=clause,
                                value_json={
                                    "percentage": pct["value"],
                                    "unit": "percent_of_sum_insured",
                                },
                                normalized_value_json={
                                    "percentage": pct["value"],
                                    "unit": "percent_of_sum_insured",
                                },
                                evidence_text=around,
                                pipeline_run_id=pipeline_run_id,
                                confidence=0.95,
                                pattern_id="ambulance_percentage_sum_insured",
                                debug={"percentage": pct},
                            )
                        )
                        break
                continue
            amount_match = re.search(
                r"(?:up to|upto|limit of|maximum of|@|inr)\s*(?:rs\.?\s*:?\s*|inr\s*:?\s*)?([\d,]+)",
                amb_lower,
            )
            if not amount_match:
                amount_match = re.search(
                    r"(?:rs\.?\s*:?\s*|inr\s*:?\s*)([\d,]+)(?:\s*/\s*-?\s*)?\s*(?:per|for|towards|limit)",
                    amb_lower,
                )
            if amount_match:
                amount = int(amount_match.group(1).replace(",", ""))
                amt_center = (amount_match.start() + amount_match.end()) // 2
                if not self._has_ambulance_nearby(amb_lower, amt_center, radius=120):
                    continue
                if amount < 100:
                    continue
                around = _window(amb_window, amount_match.start(), amount_match.end(), radius=200)
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"amount": amount, "currency": "INR"},
                        normalized_value_json={"amount": amount, "currency": "INR"},
                        evidence_text=around,
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.95,
                        pattern_id="ambulance_amount_inr",
                        debug={"amount": amount},
                    )
                )
                continue
            percentages = find_percentages(amb_window)
            if percentages:
                for pct in percentages:
                    pct_center = (pct["span"][0] + pct["span"][1]) // 2
                    pct_sub = _lower(amb_window[max(0, pct_center - 80) : pct_center + 80])
                    if not self._has_ambulance_nearby(amb_lower, pct_center, radius=120):
                        continue
                    if _has_any(
                        pct_sub,
                        [
                            "ambulance",
                            "% of sum insured",
                            "percent of sum insured",
                            "ambulance charge",
                        ],
                    ):
                        around = _window(amb_window, pct["span"][0], pct["span"][1], radius=180)
                        candidates.append(
                            self.make_candidate(
                                index=len(candidates),
                                clause=clause,
                                value_json={"percentage": pct["value"]},
                                normalized_value_json={"percentage": pct["value"]},
                                evidence_text=around,
                                pipeline_run_id=pipeline_run_id,
                                confidence=0.95,
                                pattern_id="ambulance_percentage",
                                debug={"percentage": pct},
                            )
                        )
                        break
                continue
            if _has_any(amb_lower, ["cover", "covered", "coverage", "payable", "reimbursement"]):
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"covered": True},
                        normalized_value_json={"covered": True},
                        evidence_text=amb_window[: min(len(amb_window), 250)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.9,
                        pattern_id="ambulance_covered",
                    )
                )
                continue
        return candidates


class CumulativeBonusNCBExtractor(BaseExtractor):
    concept = "cumulative_bonus_ncb"
    extractor_name = "cumulative_bonus_ncb"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        for idx, clause in enumerate(clauses):
            text = clean_space(clause.get("text", ""))
            lower = _lower(text)
            bonus_signals = [
                "no claim bonus",
                "no-claim bonus",
                "ncb",
                "cumulative bonus",
                "claim free year",
                "claim-free year",
                "claim free period",
                "no claim discount",
            ]
            if not _has_any(lower, bonus_signals):
                continue
            resto_signals = ["restoration", "restore", "reinstatement", "recharge"]
            if _has_any(lower, resto_signals):
                resto_count = sum(1 for t in resto_signals if t in lower)
                bonus_count = sum(1 for t in bonus_signals if t in lower)
                if resto_count > bonus_count:
                    continue
            sig_positions = [lower.find(s) for s in bonus_signals if s in lower]
            if not sig_positions:
                continue
            sig_start = min(sig_positions)
            bonus_around = _window(text, sig_start, sig_start + 30, radius=500)
            bonus_lower = _lower(bonus_around)
            if not _has_any(
                bonus_lower, ["no claim", "no-claim", "ncb", "cumulative bonus", "claim free"]
            ):
                continue
            schedule_signals = [
                "schedule",
                "as specified",
                "as per schedule",
                "as per the schedule",
                "benefit schedule",
                "policy schedule",
                "as shown in the schedule",
                "specified in the schedule",
                "set out in the schedule",
                "as per the benefit schedule",
                "as per the policy schedule",
                "in the schedule",
                "per schedule",
            ]
            has_schedule = _has_any(bonus_lower, schedule_signals)
            percentages = find_percentages(bonus_around)
            if has_schedule:
                ncb_near_pcts = []
                for pct in percentages:
                    pct_center = (pct["span"][0] + pct["span"][1]) // 2
                    pct_sub = bonus_lower[max(0, pct_center - 150) : pct_center + 150]
                    if not _has_any(
                        pct_sub,
                        [
                            "no claim",
                            "ncb",
                            "bonus",
                            "claim free",
                            "cumulative",
                            "loyalty addition",
                        ],
                    ):
                        continue
                    if _has_any(pct_sub, ["co-pay", "copay", "co pay", "room rent", "deductible"]):
                        continue
                    ncb_near_pcts.append(pct)
                if len(ncb_near_pcts) >= 2:
                    sorted_pcts = sorted(ncb_near_pcts, key=lambda p: p["value"])
                    increase_pct = int(sorted_pcts[0]["value"])
                    max_pct = int(sorted_pcts[-1]["value"])
                    candidates.append(
                        self.make_candidate(
                            index=len(candidates),
                            clause=clause,
                            value_json={
                                "increase_percent": increase_pct,
                                "maximum_percent": max_pct,
                                "schedule_dependent": True,
                            },
                            normalized_value_json={
                                "increase_percent": increase_pct,
                                "maximum_percent": max_pct,
                                "schedule_dependent": True,
                            },
                            evidence_text=bonus_around[: min(len(bonus_around), 300)],
                            pipeline_run_id=pipeline_run_id,
                            confidence=0.96,
                            pattern_id="cumulative_bonus_schedule_with_pct",
                            debug={"percentages": ncb_near_pcts},
                        )
                    )
                    continue
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"schedule_dependent": True},
                        normalized_value_json={"schedule_dependent": True},
                        evidence_text=bonus_around[: min(len(bonus_around), 300)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.9,
                        pattern_id="cumulative_bonus_schedule_dependent",
                    )
                )
                continue
            if not percentages:
                continue
            ncb_near_percentages = []
            for pct in percentages:
                pct_center = (pct["span"][0] + pct["span"][1]) // 2
                pct_sub = bonus_lower[max(0, pct_center - 120) : pct_center + 120]
                if not _has_any(
                    pct_sub,
                    ["no claim", "ncb", "bonus", "cumulative", "loyalty"],
                ):
                    continue
                if _has_any(
                    pct_sub,
                    [
                        "co-pay",
                        "copay",
                        "co pay",
                        "co-payment",
                        "room rent",
                        "health checkup",
                        "health check-up",
                        "preventive",
                    ],
                ):
                    continue
                if _has_any(pct_sub, ["bonus", "cumulative", "ncb"]):
                    ncb_near_percentages.append(pct)
                elif _has_any(pct_sub, ["claim free", "loyalty", "renewal bonus"]):
                    ncb_near_percentages.append(pct)
            if len(ncb_near_percentages) >= 2:
                sorted_pcts = sorted(ncb_near_percentages, key=lambda p: p["value"])
                # Only use percentages where the context has strong NCB signals
                strong_ncb = [
                    p
                    for p in sorted_pcts
                    if _has_any(
                        bonus_lower[
                            max(0, (p["span"][0] + p["span"][1]) // 2 - 80) : (
                                p["span"][0] + p["span"][1]
                            )
                            // 2
                            + 80
                        ],
                        ["bonus", "cumulative", "ncb", "subject to a maximum", "maximum of"],
                    )
                ]
                if strong_ncb:
                    increase_pct = int(strong_ncb[0]["value"])
                    max_pct = int(strong_ncb[-1]["value"])
                else:
                    increase_pct = int(sorted_pcts[0]["value"])
                    max_pct = int(sorted_pcts[-1]["value"])
                value = {
                    "increase_percent": increase_pct,
                    "maximum_percent": max_pct,
                    "schedule_dependent": True,
                }
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json=value,
                        normalized_value_json=value,
                        evidence_text=bonus_around,
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.95,
                        pattern_id="cumulative_bonus_percentage",
                        debug={"percentages": ncb_near_percentages},
                    )
                )
                continue
            if len(ncb_near_percentages) == 1:
                pct = int(ncb_near_percentages[0]["value"])
                if pct > 50:
                    continue
                sub = bonus_lower[
                    max(
                        0,
                        (ncb_near_percentages[0]["span"][0] + ncb_near_percentages[0]["span"][1])
                        // 2
                        - 80,
                    ) : (ncb_near_percentages[0]["span"][0] + ncb_near_percentages[0]["span"][1])
                    // 2
                    + 80
                ]
                if not _has_any(sub, ["bonus", "cumulative", "ncb", "maximum", "increase"]):
                    continue
                value = {"maximum_percent": pct, "schedule_dependent": True}
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json=value,
                        normalized_value_json=value,
                        evidence_text=bonus_around,
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.9,
                        pattern_id="cumulative_bonus_percentage",
                        debug={"percentages": ncb_near_percentages},
                    )
                )
                continue
        return candidates


class SpecificDiseaseWaitingPeriodsExtractor(BaseExtractor):
    concept = "specific_disease_waiting_periods"
    extractor_name = "specific_disease_waiting_periods"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        for idx, clause in enumerate(clauses):
            text = clean_space(clause.get("text", ""))
            lower = _lower(text)
            disease_signals = [
                "specific disease",
                "specified disease",
                "named disease",
                "cataract",
                "hernia",
                "sinusitis",
                "fistula",
                "pile",
                "piles",
                "haemorrhoid",
                "hemorrhoid",
                "hydrocele",
                "tumor",
                "tumour",
                "cyst",
                "stone",
                "gallstone",
                "kidney stone",
                "joint replacement",
                "knee replacement",
                "hip replacement",
                "ent disorder",
                "tonsillectomy",
                "adenoid",
                "specific waiting",
                "specified waiting",
                "specific disease waiting period",
                "specified disease waiting period",
                "specific diseases",
                "specified diseases",
                "following listed conditions",
                "conditions, surgeries/treatments",
            ]
            if not _has_any(lower, disease_signals):
                continue
            if _has_any(
                lower,
                [
                    "initial waiting",
                    "first 30 days",
                    "first thirty days",
                    "free look",
                    "grace period",
                ],
            ):
                continue
            if _has_any(lower, ["pre-existing", "pre existing", "ped"]):
                ped_count = sum(1 for t in ["pre-existing", "pre existing", "ped"] if t in lower)
                disease_count = sum(1 for t in disease_signals if t in lower)
                if ped_count >= disease_count:
                    continue
            broad_waiting_signals = [
                "waiting period",
                "excluded until",
                "covered after",
                "24 months",
                "48 months",
                "twenty four months",
                "forty eight months",
            ]
            if not _has_any(lower, broad_waiting_signals):
                continue
            durations = _ped_duration_candidates(text)
            slash_durations = _slash_month_options(text)
            months_found = []
            for duration in durations + slash_durations:
                months = _duration_value(duration, "months")
                if months and months in {3, 6, 12, 24, 48, 60, 90}:
                    d_center = (duration["span"][0] + duration["span"][1]) // 2
                    d_sub = _lower(text[max(0, d_center - 120) : d_center + 120])
                    if _has_any(
                        d_sub, ["initial waiting", "first 30 days", "free look", "grace period"]
                    ):
                        continue
                    definition_sub = _lower(text[max(0, d_center - 35) : d_center + 25])
                    if _has_any(
                        definition_sub,
                        [
                            "diagnosed within",
                            "prior to the policy",
                            "effective date",
                            "medical advice or treatment",
                        ],
                    ):
                        continue
                    if _has_any(d_sub, ["pre-existing", "pre existing", "ped"]):
                        if not _has_any(d_sub, disease_signals):
                            continue
                    months_found.append(months)
            if not months_found:
                continue
            months_unique = sorted(set(months_found))
            # Higher confidence for main SWP clauses (EXCL02 is IRDAI regulatory code)
            has_excl02 = "excl02" in lower or "excl 02" in lower
            confidence = 0.96 if has_excl02 else 0.92
            evidence_durations = durations + slash_durations
            around = _window(
                text,
                evidence_durations[0]["span"][0],
                evidence_durations[-1]["span"][1],
                radius=260,
            )
            candidates.append(
                self.make_candidate(
                    index=len(candidates),
                    clause=clause,
                    value_json={"months_options": months_unique},
                    normalized_value_json={"months_options": months_unique},
                    evidence_text=around,
                    pipeline_run_id=pipeline_run_id,
                    confidence=confidence,
                    pattern_id="specific_disease_waiting_multi"
                    if len(months_unique) > 1
                    else "specific_disease_waiting_single",
                    debug={
                        "durations": durations,
                        "slash_durations": slash_durations,
                        "months_found": months_found,
                    },
                )
            )
        return candidates


class MaternityWaitingExtractor(BaseExtractor):
    concept = "maternity_waiting"
    extractor_name = "maternity_waiting"

    def _find_maternity_durations(self, text: str, maternity_pos: int) -> List[int]:
        """Find waiting period months near the first maternity term."""
        left = max(0, maternity_pos - 260)
        right = min(len(text), maternity_pos + 360)
        near_text = text[left:right]
        months_found = []
        for duration in find_durations(near_text):
            months = _duration_value(duration, "months")
            if months and months in {9, 12, 24, 36, 48}:
                months_found.append(months)
        loose_re = re.compile(
            r"(?P<num>\d+|twenty four|thirty six|forty eight|twelve|twenty four|thirty six)"
            r"(?:\s*-\s*|\s+)"
            r"(?:month|months)(?:\s+waiting|\s+period)",
            re.IGNORECASE,
        )
        for match in loose_re.finditer(near_text):
            value = parse_number_token(match.group("num"))
            if value and value in {9, 12, 24, 36, 48}:
                months_found.append(value)
        return months_found

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        for idx, clause in enumerate(clauses):
            text = clean_space(clause.get("text", ""))
            lower = _lower(text)
            maternity_terms = [
                "maternity",
                "childbirth",
                "child birth",
                "pregnancy",
                "pregnant",
                "antenatal",
                "postnatal",
                "caesarean",
                "c-section",
                "obstetric",
            ]
            mat_pos = -1
            for term in maternity_terms:
                pos = 0
                while True:
                    found = lower.find(term, pos)
                    if found < 0:
                        break
                    mat_pos = max(mat_pos, found)
                    pos = found + 1
            if mat_pos < 0:
                continue
            if _is_definition_only(lower):
                continue
            if "new born" in lower[:120] and "maternity" not in lower[:120]:
                continue
            mat_positions = []
            for term in maternity_terms:
                pos = 0
                while True:
                    found = lower.find(term, pos)
                    if found < 0:
                        break
                    mat_positions.append(found)
                    pos = found + 1
            months_found = []
            for pos in sorted(set(mat_positions)):
                months_found.extend(self._find_maternity_durations(text, pos))
            if months_found:
                months = max(months_found)
                evidence_pos = min(mat_positions) if mat_positions else mat_pos
                around = _window(text, max(0, evidence_pos - 80), evidence_pos + 260, radius=220)
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"months": months},
                        normalized_value_json={"months": months},
                        evidence_text=around,
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.97,
                        pattern_id="maternity_waiting_present",
                        debug={"months_found": months_found},
                    )
                )
                continue
            excluded = _has_any(
                lower,
                [
                    "not covered",
                    "not covered under",
                    "excluded",
                    "exclusion",
                    "shall not be payable",
                    "shall not be admissible",
                    "not admissible",
                    "not payable",
                    "no benefit",
                    "no liability",
                    "does not cover",
                ],
            ) and _has_any(lower, maternity_terms)
            if excluded:
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"covered": False},
                        normalized_value_json={"covered": False},
                        evidence_text=text[: min(len(text), 250)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.96,
                        fact_status="explicitly_not_covered",
                        pattern_id="maternity_waiting_excluded",
                    )
                )
                continue
        return candidates


class OrganDonorCoverageExtractor(BaseExtractor):
    concept = "organ_donor_coverage"
    extractor_name = "organ_donor_coverage"

    def extract(self, clauses: List[Dict[str, Any]], pipeline_run_id: str) -> List[FactCandidate]:
        candidates: List[FactCandidate] = []
        for idx, clause in enumerate(clauses):
            text = clean_space(clause.get("text", ""))
            lower = _lower(text)
            donor_terms = [
                "organ donor",
                "organ transplant",
                "donor expenses",
                "donor's expenses",
                "organ donation",
                "transplant of organ",
                "organ retrieval",
                "person donating",
                "donating an organ",
                "organ donation",
                "living donor",
                "cadaver donor",
            ]
            donor_pos = -1
            for term in donor_terms:
                pos = lower.find(term)
                if pos >= 0:
                    donor_pos = pos
                    break
            if donor_pos < 0:
                continue
            if "organ transplant" in lower or "transplant of organ" in lower:
                has_donor_nearby = _has_any(
                    lower[max(0, donor_pos - 50) : donor_pos + 200],
                    ["donor", "donation", "retrieval", "donating"],
                )
                if not has_donor_nearby:
                    ci_signals = [
                        "cancer",
                        "heart attack",
                        "kidney",
                        "liver",
                        "lung",
                        "stroke",
                        "illness",
                        "condition",
                        "disease",
                    ]
                    if _has_any(lower[max(0, donor_pos - 50) : donor_pos + 200], ci_signals):
                        candidates.append(
                            self.make_candidate(
                                index=len(candidates),
                                clause=clause,
                                value_json={},
                                normalized_value_json={},
                                evidence_text=text[: min(len(text), 220)],
                                pipeline_run_id=pipeline_run_id,
                                confidence=0.3,
                                pattern_id="organ_donor_critical_illness_list",
                                rejection_reason="organ_transplant_in_critical_illness_list_not_donor_coverage",
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
                        pattern_id="organ_donor_definition_only",
                        rejection_reason="definition_only_without_coverage_language",
                    )
                )
                continue
            if not _has_any(
                lower[max(0, donor_pos - 50) : donor_pos + 250],
                [
                    "cover",
                    "covered",
                    "coverage",
                    "pay",
                    "payable",
                    "reimburse",
                    "reimbursement",
                    "expenses",
                    "benefit",
                ],
            ):
                continue
            if _has_any(
                lower[max(0, donor_pos - 50) : donor_pos + 150],
                ["not cover", "not payable", "not admissible", "excluded", "exclusion"],
            ):
                candidates.append(
                    self.make_candidate(
                        index=len(candidates),
                        clause=clause,
                        value_json={"covered": True, "scope": "organ_donor_expenses"},
                        normalized_value_json={"covered": True, "scope": "organ_donor_expenses"},
                        evidence_text=text[: min(len(text), 250)],
                        pipeline_run_id=pipeline_run_id,
                        confidence=0.5,
                        pattern_id="organ_donor_covered",
                    )
                )
                continue
            candidates.append(
                self.make_candidate(
                    index=len(candidates),
                    clause=clause,
                    value_json={"covered": True, "scope": "organ_donor_expenses"},
                    normalized_value_json={"covered": True, "scope": "organ_donor_expenses"},
                    evidence_text=text[: min(len(text), 250)],
                    pipeline_run_id=pipeline_run_id,
                    confidence=0.95,
                    pattern_id="organ_donor_covered",
                )
            )
        return candidates


EXTRACTORS = [
    FreeLookExtractor(),
    GracePeriodExtractor(),
    PedWaitingPeriodExtractor(),
    InitialWaitingPeriodExtractor(),
    CoPayExtractor(),
    # DSE-018 Wave 1
    RenewabilityExtractor(),
    ClaimSettlementTimelineExtractor(),
    AyushCoverageExtractor(),
    AmbulanceCoverageExtractor(),
    CumulativeBonusNCBExtractor(),
    SpecificDiseaseWaitingPeriodsExtractor(),
    MaternityWaitingExtractor(),
    OrganDonorCoverageExtractor(),
]
