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
    is_sentence_case,
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
        "is_sentence_case": -0.30,
        "line_length_penalty": -0.20,
        "position_penalty": -0.30,
        "all_caps_fp_penalty": -0.20,
        "boilerplate_company_penalty": -0.30,
    }

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

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

        line_len = len(text)
        length_ratio = line_len / median_len if median_len > 0 else 1.0

        region = line.get("region", "body")
        is_header = line.get("is_header_candidate", False)
        is_footer = line.get("is_footer_candidate", False)
        pos_penalty = 1.0 if (region in ("top", "bottom") or is_header or is_footer) else 0.0

        all_caps_fp = 1.0 if (all_caps and line_len > 80) else 0.0
        gap_features = self._line_gap_features(page.get("lines", []), line_index)
        looks_heading_like = numbered or dict_match or all_caps or bold or toc
        spacing_signal = 1.0 if looks_heading_like and gap_features["gap_before_ratio"] >= 1.5 else 0.0
        boilerplate_company = 1.0 if (
            not numbered
            and re.search(r"\b(?:insurance|assurance)\s+(?:company\s+)?limited\.?$", text, re.I)
        ) else 0.0

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
        sentence = features.get("is_sentence_case", 0.0)
        if numbered and long_line and not all_caps:
            return -0.15
        return 0.0

    def feature_contributions(self, features: Dict[str, float]) -> Dict[str, float]:
        return {
            "font_size_ratio": round(self._font_contribution(features), 4),
            "is_bold": round(features.get("is_bold", 0.0) * self.WEIGHTS["is_bold"], 4),
            "is_all_caps": round(
                features.get("is_all_caps", 0.0) * self.WEIGHTS["is_all_caps"], 4
            ),
            "matches_numbering": round(
                features.get("matches_numbering", 0.0) * self.WEIGHTS["matches_numbering"], 4
            ),
            "matches_heading_dict": round(
                features.get("matches_heading_dict", 0.0)
                * self.WEIGHTS["matches_heading_dict"],
                4,
            ),
            "has_toc_dots": round(
                features.get("has_toc_dots", 0.0) * self.WEIGHTS["has_toc_dots"], 4
            ),
            "spacing_signal": round(
                features.get("spacing_signal", 0.0) * self.WEIGHTS["spacing_signal"], 4
            ),
            "is_sentence_case": round(
                features.get("is_sentence_case", 0.0) * self.WEIGHTS["is_sentence_case"], 4
            ),
            "line_length_penalty": round(
                -features.get("line_length_ratio", 0.0)
                * abs(self.WEIGHTS["line_length_penalty"]),
                4,
            ),
            "position_penalty": round(
                features.get("position_penalty", 0.0) * self.WEIGHTS["position_penalty"],
                4,
            ),
            "all_caps_fp_penalty": round(
                features.get("all_caps_fp_penalty", 0.0)
                * self.WEIGHTS["all_caps_fp_penalty"],
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

    def _numbering_token(self, text: str) -> Optional[str]:
        match = re.match(
            r"^\s*((?:SECTION|PART)\s+[A-Z0-9]+|[IVX]+[\.\)]|\d+(?:\.\d+)*[\.\)]?)",
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

        return {
            "candidates": candidates,
            "config": {
                "threshold": self.threshold,
                "weights": dict(self.WEIGHTS),
                "body_font_mode": doc_stats["body_font_mode"],
                "median_line_length": doc_stats["median_line_length"],
                "pipeline_run_id": pipeline_run_id or doc.get("pipeline_run_id", ""),
            },
            "document_id": doc.get("document_id", ""),
            "policy_id": doc.get("policy_id", ""),
            "total_lines_scored": len(candidates),
            "total_headings": sum(1 for c in candidates if c["decision"] == "heading"),
        }
