import json
import os
import re
import uuid
from collections import Counter
from typing import Any, Dict, List, Optional

from structure_parser.heading_patterns import (
    has_toc_dots,
    is_all_caps,
    is_bold_line,
    is_lettered_named_heading,
    is_numbered_short_title_heading,
    is_parenthesized_letter_heading,
    is_part_token_heading,
    is_roman_policy_section_heading,
    is_section_token_heading,
    is_sentence_case,
    is_short_colon_label_heading,
    matches_heading_dict,
    matches_numbering,
    normalize_heading_text,
)


class HeadingScorer:
    WEIGHTS = {
        "font_size_ratio": 0.25,
        "is_bold": 0.15,
        "is_all_caps": 0.10,
        "matches_numbering": 0.30,
        "matches_heading_dict": 0.10,
        "has_toc_dots": 0.10,
        "spacing_signal": 0.10,
        "section_token_heading": 0.0,
        "part_token_heading": 0.0,
        "parenthesized_letter_heading": 0.0,
        "short_colon_label_heading": 0.0,
        "numbered_short_title_heading": 0.0,
        "roman_policy_section_heading": 0.0,
        "lettered_named_heading": 0.0,
        "short_dictionary_heading": 0.0,
        "is_sentence_case": -0.30,
        "line_length_penalty": -0.20,
        "position_penalty": -0.30,
        "all_caps_fp_penalty": -0.20,
        "boilerplate_company_penalty": -0.30,
    }

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.fallback_min_score = 0.42
        self.fallback_max_promotions = 90

    def compute_document_stats(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        all_sizes = []
        line_lengths = []
        for page in doc.get("pages", []):
            for line in page.get("lines", []):
                text = line.get("text", "").strip()
                if text:
                    line_lengths.append(len(text))
            for span in page.get("spans", []):
                fs = span.get("font_size")
                if fs is not None:
                    all_sizes.append(round(fs, 2))

        body_mode = None
        if all_sizes:
            counter = Counter(all_sizes)
            body_mode = counter.most_common(1)[0][0]

        median_line_len = 0
        if line_lengths:
            sorted_l = sorted(line_lengths)
            mid = len(sorted_l) // 2
            median_line_len = sorted_l[mid]

        unique_sizes = sorted(set(all_sizes)) if all_sizes else []

        return {
            "body_font_mode": body_mode,
            "median_line_length": median_line_len,
            "total_lines": len(line_lengths),
            "total_spans": len(all_sizes),
            "unique_font_sizes": unique_sizes,
            "font_size_distribution": dict(Counter(all_sizes).most_common(20)) if all_sizes else {},
        }

    def _line_gap_features(
        self,
        lines: List[Dict[str, Any]],
        line_index: int,
    ) -> Dict[str, float]:
        line = lines[line_index]
        bbox = line.get("bbox") or [0, 0, 0, 0]
        top = float(bbox[1] or 0)
        bottom = float(bbox[3] or 0)

        gaps = []
        for idx, item in enumerate(lines):
            if idx == 0:
                continue
            prev_bbox = lines[idx - 1].get("bbox") or [0, 0, 0, 0]
            cur_bbox = item.get("bbox") or [0, 0, 0, 0]
            gap = float(cur_bbox[1] or 0) - float(prev_bbox[3] or 0)
            if 0 < gap < 80:
                gaps.append(gap)

        median_gap = 0.0
        if gaps:
            sorted_gaps = sorted(gaps)
            mid = len(sorted_gaps) // 2
            if len(sorted_gaps) % 2 == 0:
                median_gap = (sorted_gaps[mid - 1] + sorted_gaps[mid]) / 2
            else:
                median_gap = sorted_gaps[mid]

        gap_before = 0.0
        if line_index > 0:
            prev_bbox = lines[line_index - 1].get("bbox") or [0, 0, 0, 0]
            gap_before = max(0.0, top - float(prev_bbox[3] or 0))

        gap_after = 0.0
        if line_index + 1 < len(lines):
            next_bbox = lines[line_index + 1].get("bbox") or [0, 0, 0, 0]
            gap_after = max(0.0, float(next_bbox[1] or 0) - bottom)

        before_ratio = gap_before / median_gap if median_gap > 0 else 0.0
        after_ratio = gap_after / median_gap if median_gap > 0 else 0.0
        return {
            "gap_before": round(gap_before, 4),
            "gap_after": round(gap_after, 4),
            "median_line_gap": round(median_gap, 4),
            "gap_before_ratio": round(before_ratio, 4),
            "gap_after_ratio": round(after_ratio, 4),
        }

    def compute_features(
        self,
        line: Dict[str, Any],
        page: Dict[str, Any],
        doc_stats: Dict[str, Any],
        line_index: int = 0,
    ) -> Dict[str, float]:

        text = line.get("text", "").strip()
        body_mode = doc_stats.get("body_font_mode")
        median_len = doc_stats.get("median_line_length", 50)

        span_ids = line.get("span_ids", [])
        span_map = {s.get("span_id"): s for s in page.get("spans", [])}
        line_spans = [span_map[sid] for sid in span_ids if sid in span_map]

        max_font_size = None
        for s in line_spans:
            fs = s.get("font_size")
            if fs is not None:
                rounded = round(fs, 2)
                if max_font_size is None or rounded > max_font_size:
                    max_font_size = rounded

        font_size_ratio = 0.0
        if max_font_size is not None and body_mode and body_mode > 0:
            font_size_ratio = round(max_font_size / body_mode, 4)

        bold = is_bold_line(line_spans)
        all_caps = is_all_caps(text)
        sentence_case = is_sentence_case(text)
        numbered = matches_numbering(text)
        dict_match = matches_heading_dict(text)
        toc = has_toc_dots(text)
        section_token = is_section_token_heading(text)
        part_token = is_part_token_heading(text)
        parenthesized_letter = is_parenthesized_letter_heading(text)
        short_colon_label = is_short_colon_label_heading(text)
        numbered_short_title = is_numbered_short_title_heading(text)
        roman_policy_section = is_roman_policy_section_heading(text)
        lettered_named = is_lettered_named_heading(text)

        line_len = len(text)
        length_ratio = line_len / median_len if median_len > 0 else 1.0

        region = line.get("region", "body")
        is_header = line.get("is_header_candidate", False)
        is_footer = line.get("is_footer_candidate", False)
        pos_penalty = 1.0 if (region in ("top", "bottom") or is_header or is_footer) else 0.0

        all_caps_fp = 1.0 if (all_caps and line_len > 80) else 0.0
        gap_features = self._line_gap_features(page.get("lines", []), line_index)
        looks_heading_like = numbered or dict_match or all_caps or bold or toc
        spacing_signal = (
            1.0 if looks_heading_like and gap_features["gap_before_ratio"] >= 1.5 else 0.0
        )
        boilerplate_company = (
            1.0
            if (
                not numbered
                and re.search(r"\b(?:insurance|assurance)\s+(?:company\s+)?limited\.?$", text, re.I)
            )
            else 0.0
        )
        short_dictionary_heading = (
            1.0
            if (
                dict_match
                and (bold or spacing_signal)
                and not numbered
                and not toc
                and line_len <= 45
            )
            else 0.0
        )

        return {
            "font_size_ratio": font_size_ratio,
            "max_font_size": max_font_size,
            "is_bold": 1.0 if bold else 0.0,
            "is_all_caps": 1.0 if all_caps else 0.0,
            "is_sentence_case": 1.0 if sentence_case else 0.0,
            "matches_numbering": 1.0 if numbered else 0.0,
            "matches_heading_dict": 1.0 if dict_match else 0.0,
            "has_toc_dots": 1.0 if toc else 0.0,
            "line_length_ratio": round(length_ratio, 4),
            "is_header_region": 1.0 if (region == "top") else 0.0,
            "is_footer_region": 1.0 if (region == "bottom") else 0.0,
            "position_penalty": pos_penalty,
            "all_caps_fp_penalty": all_caps_fp,
            "boilerplate_company_penalty": boilerplate_company,
            "spacing_signal": spacing_signal,
            "section_token_heading": 1.0 if section_token else 0.0,
            "part_token_heading": 1.0 if part_token else 0.0,
            "parenthesized_letter_heading": 1.0 if parenthesized_letter else 0.0,
            "short_colon_label_heading": 1.0 if short_colon_label else 0.0,
            "numbered_short_title_heading": 1.0 if numbered_short_title else 0.0,
            "roman_policy_section_heading": 1.0 if roman_policy_section else 0.0,
            "lettered_named_heading": 1.0 if lettered_named else 0.0,
            "short_dictionary_heading": short_dictionary_heading,
            **gap_features,
        }

    def _font_contribution(self, features: Dict[str, float]) -> float:
        ratio = features.get("font_size_ratio", 0.0)
        if ratio > 1.0:
            return self.WEIGHTS["font_size_ratio"]
        return 0.0

    def _numbered_def_penalty(self, features: Dict[str, float]) -> float:
        numbered = features.get("matches_numbering", 0.0)
        long_line = features.get("line_length_ratio", 0.0) > 0.8
        all_caps = features.get("is_all_caps", 0.0)
        structural = any(
            features.get(name, 0.0)
            for name in (
                "section_token_heading",
                "part_token_heading",
                "parenthesized_letter_heading",
                "numbered_short_title_heading",
                "roman_policy_section_heading",
            )
        )
        if numbered and long_line and not all_caps:
            return -0.15
        return 0.0

    def feature_contributions(self, features: Dict[str, float]) -> Dict[str, float]:
        sentence = features.get("is_sentence_case", 0.0)
        numbered = features.get("matches_numbering", 0.0)
        bold = features.get("is_bold", 0.0)
        sentence_penalty = (
            -0.10
            if (sentence and bold and numbered)
            else self.WEIGHTS["is_sentence_case"] * sentence
        )
        length_penalty = -features.get("line_length_ratio", 0.0) * abs(
            self.WEIGHTS["line_length_penalty"]
        )
        return {
            "font_size_ratio": round(self._font_contribution(features), 4),
            "is_bold": round(features.get("is_bold", 0.0) * self.WEIGHTS["is_bold"], 4),
            "is_all_caps": round(features.get("is_all_caps", 0.0) * self.WEIGHTS["is_all_caps"], 4),
            "matches_numbering": round(
                features.get("matches_numbering", 0.0) * self.WEIGHTS["matches_numbering"], 4
            ),
            "matches_heading_dict": round(
                features.get("matches_heading_dict", 0.0) * self.WEIGHTS["matches_heading_dict"],
                4,
            ),
            "has_toc_dots": round(
                features.get("has_toc_dots", 0.0) * self.WEIGHTS["has_toc_dots"], 4
            ),
            "spacing_signal": round(
                features.get("spacing_signal", 0.0) * self.WEIGHTS["spacing_signal"], 4
            ),
            "section_token_heading": round(
                features.get("section_token_heading", 0.0)
                * self.WEIGHTS["section_token_heading"],
                4,
            ),
            "part_token_heading": round(
                features.get("part_token_heading", 0.0) * self.WEIGHTS["part_token_heading"],
                4,
            ),
            "parenthesized_letter_heading": round(
                features.get("parenthesized_letter_heading", 0.0)
                * self.WEIGHTS["parenthesized_letter_heading"],
                4,
            ),
            "short_colon_label_heading": round(
                features.get("short_colon_label_heading", 0.0)
                * self.WEIGHTS["short_colon_label_heading"],
                4,
            ),
            "numbered_short_title_heading": round(
                features.get("numbered_short_title_heading", 0.0)
                * self.WEIGHTS["numbered_short_title_heading"],
                4,
            ),
            "roman_policy_section_heading": round(
                features.get("roman_policy_section_heading", 0.0)
                * self.WEIGHTS["roman_policy_section_heading"],
                4,
            ),
            "lettered_named_heading": round(
                features.get("lettered_named_heading", 0.0)
                * self.WEIGHTS["lettered_named_heading"],
                4,
            ),
            "short_dictionary_heading": round(
                features.get("short_dictionary_heading", 0.0)
                * self.WEIGHTS["short_dictionary_heading"],
                4,
            ),
            "is_sentence_case": round(sentence_penalty, 4),
            "line_length_penalty": round(length_penalty, 4),
            "position_penalty": round(
                features.get("position_penalty", 0.0) * self.WEIGHTS["position_penalty"],
                4,
            ),
            "all_caps_fp_penalty": round(
                features.get("all_caps_fp_penalty", 0.0) * self.WEIGHTS["all_caps_fp_penalty"],
                4,
            ),
            "boilerplate_company_penalty": round(
                features.get("boilerplate_company_penalty", 0.0)
                * self.WEIGHTS["boilerplate_company_penalty"],
                4,
            ),
            "numbered_definition_penalty": round(self._numbered_def_penalty(features), 4),
        }

    def score_features(self, features: Dict[str, float]) -> float:
        score = sum(self.feature_contributions(features).values())
        return round(score, 4)

    def _fallback_guard_reasons(self, candidate: Dict[str, Any]) -> List[str]:
        text = candidate.get("text", "").strip()
        features = candidate.get("features", {})
        reasons: List[str] = []

        if features.get("has_toc_dots", 0.0):
            reasons.append("toc_dot_leader")
        if features.get("position_penalty", 0.0):
            reasons.append("header_footer_region")
        if re.match(r"^\s*(?:S\.?\s*No\.?|Sr\.?\s*No\.?|Sl\.?\s*No\.?)\b", text, re.I):
            reasons.append("serial_number_row")
        if "\t" in text:
            reasons.append("tabular_text")
        if re.search(r"(?:₹|Rs\.?|INR)\s*\d|\d+\s*%|\b\d+\s*(?:lakh|lac|crore)\b", text, re.I):
            reasons.append("price_or_benefit_value_row")
        if len(text) > 110:
            reasons.append("long_text")
        if re.match(r"^\s*\d+\s+[A-Z][A-Z\s/&().,-]{2,}$", text) and not features.get(
            "matches_heading_dict", 0.0
        ):
            reasons.append("procedure_or_item_list")
        if re.search(r"\b(?:page\s+\d+|uin\s*:|irda|certificate\s+of\s+insurance)\b", text, re.I):
            reasons.append("boilerplate_or_page_artifact")

        return reasons

    def _fallback_promotion_reasons(self, candidate: Dict[str, Any]) -> List[str]:
        text = candidate.get("text", "").strip()
        features = candidate.get("features", {})
        token = candidate.get("numbering_token")
        reasons: List[str] = []

        numbered = features.get("matches_numbering", 0.0) == 1.0
        bold = features.get("is_bold", 0.0) == 1.0
        all_caps = features.get("is_all_caps", 0.0) == 1.0
        dict_match = features.get("matches_heading_dict", 0.0) == 1.0
        spacing = features.get("spacing_signal", 0.0) == 1.0
        enlarged = features.get("font_size_ratio", 0.0) >= 1.05

        upper_token = token.upper() if isinstance(token, str) else ""
        if upper_token.startswith(("SECTION", "PART")):
            reasons.append("section_or_part_token")
        if features.get("section_token_heading", 0.0):
            reasons.append("section_token_heading")
        if features.get("part_token_heading", 0.0):
            reasons.append("part_token_heading")
        if features.get("parenthesized_letter_heading", 0.0):
            reasons.append("parenthesized_letter_heading")
        if features.get("short_colon_label_heading", 0.0):
            reasons.append("short_colon_label_heading")
        if features.get("numbered_short_title_heading", 0.0):
            reasons.append("numbered_short_title_heading")
        if features.get("roman_policy_section_heading", 0.0):
            reasons.append("roman_policy_section_heading")
        if features.get("lettered_named_heading", 0.0):
            reasons.append("lettered_named_heading")
        if features.get("short_dictionary_heading", 0.0):
            reasons.append("short_dictionary_heading")
        if re.match(r"^[A-Z]\.$", upper_token) and (dict_match or bold or all_caps):
            reasons.append("letter_heading_with_support")
        if numbered and dict_match:
            reasons.append("numbered_dictionary_heading")
        if numbered and bold:
            reasons.append("bold_numbered_heading")
        if numbered and all_caps:
            reasons.append("all_caps_numbered_heading")
        if numbered and spacing:
            reasons.append("numbered_spacing_signal")
        if numbered and enlarged:
            reasons.append("numbered_enlarged_font")

        # Allow compact policy heading forms like "10.Renewal" when the token parser
        # recognizes numbering but dictionary matching misses due to punctuation.
        if numbered and re.match(r"^\s*\d+(?:\.\d+)*\.?[A-Z][A-Za-z ]{2,40}:?\s*$", text):
            reasons.append("compact_numbered_heading")

        return reasons

    def _apply_zero_heading_fallback(self, candidates: List[Dict[str, Any]]) -> int:
        if any(c.get("decision") == "heading" for c in candidates):
            return 0

        structural_override_reasons = {
            "section_token_heading",
            "part_token_heading",
            "parenthesized_letter_heading",
            "short_colon_label_heading",
            "roman_policy_section_heading",
            "lettered_named_heading",
            "short_dictionary_heading",
        }
        priority_order = {
            "section_token_heading": 0,
            "part_token_heading": 1,
            "roman_policy_section_heading": 2,
            "parenthesized_letter_heading": 3,
            "lettered_named_heading": 4,
            "short_dictionary_heading": 5,
            "short_colon_label_heading": 6,
            "numbered_short_title_heading": 7,
        }

        prepared = []
        for candidate in candidates:
            guards = self._fallback_guard_reasons(candidate)
            reasons = self._fallback_promotion_reasons(candidate)
            structural_override = any(reason in structural_override_reasons for reason in reasons)
            eligible_score_band = candidate.get("score", 0.0) >= self.fallback_min_score
            best_priority = min(
                (priority_order[reason] for reason in reasons if reason in priority_order),
                default=99,
            )
            candidate["fallback_evaluation"] = {
                "eligible_score_band": eligible_score_band,
                "structural_override": structural_override,
                "guard_reasons": guards,
                "promotion_reasons": reasons,
            }
            prepared.append((best_priority, -candidate.get("score", 0.0), candidate))

        promoted = 0
        for _, _, candidate in sorted(prepared, key=lambda item: (item[0], item[1])):
            score = candidate.get("score", 0.0)
            if score >= self.threshold:
                continue

            evaluation = candidate["fallback_evaluation"]
            guards = evaluation["guard_reasons"]
            reasons = evaluation["promotion_reasons"]
            structural_override = evaluation["structural_override"]
            eligible_score_band = evaluation["eligible_score_band"]

            if not eligible_score_band and not structural_override:
                continue
            if guards or not reasons:
                continue

            candidate["original_decision"] = candidate.get("decision")
            candidate["original_score"] = score
            candidate["decision"] = "heading"
            candidate["promotion_source"] = "fallback_zero_heading"
            candidate["promotion_reason"] = ";".join(reasons)
            promoted += 1

            if promoted >= self.fallback_max_promotions:
                break

        return promoted

    def _numbering_token(self, text: str) -> Optional[str]:
        match = re.match(
            r"^\s*((?:SECTION|PART)\s+[A-Z0-9]+|[IVX]+[\.\)]|\([a-z]\)|\d+(?:\.\d+)*[\.\)]?|[A-Z]\.)",
            text,
            flags=re.IGNORECASE,
        )
        if not match:
            return None
        return match.group(1).strip().rstrip(")")

    def _level_hint(self, text: str) -> int:
        token = self._numbering_token(text)
        if not token:
            return 1
        upper = token.upper()
        if upper.startswith(("SECTION", "PART")):
            return 1
        if re.match(r"^[A-Z]\.$", upper):
            return 1
        numbers = re.findall(r"\d+", token)
        if numbers:
            return max(1, min(4, len(numbers)))
        return 1

    def score_document(
        self, doc: Dict[str, Any], pipeline_run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        doc_stats = self.compute_document_stats(doc)
        candidates = []
        candidate_index = 0

        for page in doc.get("pages", []):
            page_num = page.get("page_number", 0)
            for line_index, line in enumerate(page.get("lines", [])):
                text = line.get("text", "").strip()
                if not text:
                    continue

                features = self.compute_features(line, page, doc_stats, line_index)
                score = self.score_features(features)
                decision = "heading" if score >= self.threshold else "non-heading"

                candidates.append(
                    {
                        "candidate_id": f"{doc.get('policy_id', 'doc')}_candidate_{candidate_index:05d}",
                        "line_id": line.get("line_id", ""),
                        "text": text,
                        "page_number": page_num,
                        "bbox": line.get("bbox", []),
                        "span_ids": line.get("span_ids", []),
                        "normalized_text": normalize_heading_text(text),
                        "numbering_token": self._numbering_token(text),
                        "level_hint": self._level_hint(text),
                        "score": score,
                        "features": features,
                        "feature_contributions": self.feature_contributions(features),
                        "decision": decision,
                        "threshold_applied": self.threshold,
                    }
                )
                candidate_index += 1

        fallback_promotions = self._apply_zero_heading_fallback(candidates)

        return {
            "candidates": candidates,
            "config": {
                "threshold": self.threshold,
                "fallback_zero_heading": {
                    "enabled": True,
                    "min_score": self.fallback_min_score,
                    "max_promotions": self.fallback_max_promotions,
                    "promotions": fallback_promotions,
                },
                "weights": dict(self.WEIGHTS),
                "body_font_mode": doc_stats["body_font_mode"],
                "median_line_length": doc_stats["median_line_length"],
                "pipeline_run_id": pipeline_run_id or doc.get("pipeline_run_id", ""),
            },
            "document_id": doc.get("document_id", ""),
            "policy_id": doc.get("policy_id", ""),
            "total_lines_scored": len(candidates),
            "total_headings": sum(1 for c in candidates if c["decision"] == "heading"),
            "fallback_promotions": fallback_promotions,
        }
