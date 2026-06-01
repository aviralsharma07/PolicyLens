import json
import os
import re
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple


ARABIC_NUMBER_RE = re.compile(
    r"^\s*(?P<number>\d+(?:\.\d+)*)(?:[.)])?\s*[:.-]?\s*(?P<title>[A-Z][\s\S]*)$"
)
ROMAN_NUMBER_RE = re.compile(
    r"^\s*(?P<number>I{1,3}|IV|V|VI{0,3}|IX|X)(?:[.)])\s*(?P<title>[A-Z][\s\S]*)$",
    re.IGNORECASE,
)


def _safe_id_part(value: str) -> str:
    safe = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return safe or "policy"


def _infer_level(numbering_token: Optional[str], level_hint: int = 1) -> int:
    if not numbering_token:
        return max(1, level_hint)
    upper = numbering_token.strip().upper()
    if upper.startswith(("SECTION", "PART")):
        parts = re.findall(r"\d+|[A-Z](?=\.)", numbering_token)
        if len(parts) > 1:
            return min(4, len(parts))
        return 1
    roman_match = re.match(r"^[IVXLCDM]+\.?$", upper)
    if roman_match:
        return 1
    numbers = re.findall(r"\d+", numbering_token)
    if numbers:
        if len(numbers) == 2 and numbers[1] == "0":
            return 1
        return max(1, min(4, len(numbers)))
    return 1


def _normalize_title(text: str) -> str:
    text = re.sub(r"\.\s*\.\s*\.\s*\.\s*\.+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().rstrip(".")


def _compact_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", _normalize_title(text).lower())


def _extract_number_from_heading(heading: Dict[str, Any]) -> Optional[str]:
    token = heading.get("numbering_token")
    if token:
        num_match = re.search(r"\d+(?:\.\d+)*", token)
        if num_match:
            return num_match.group(0)
    text = heading.get("text", "")
    # Fallback: parse number from "3.1. Accident means"
    num_match = re.match(r"\s*(\d+(?:\.\d+)*)\s*\.?\s*", text)
    if num_match:
        return num_match.group(1)
    return None


def _is_unnumbered_heading(heading: Dict[str, Any]) -> bool:
    token = heading.get("numbering_token")
    if token:
        return False
    text = heading.get("text", "").strip()
    # Some headings like "FAMILY SHIELD" or "CARE PLUS" have no numbering
    return bool(text)


def _is_body_numbered_line(text: str) -> bool:
    return parse_numbered_prefix(text) is not None


def parse_numbered_prefix(text: str) -> Optional[Dict[str, str]]:
    """Parse body numbering, including compact policy text like 2.1.1Accident."""
    stripped = text.strip()
    if not stripped:
        return None

    match = ARABIC_NUMBER_RE.match(stripped)
    if match:
        number = match.group("number").strip(".")
        title = match.group("title").strip()
        if title:
            return {"number": number, "title": title, "kind": "arabic"}

    match = ROMAN_NUMBER_RE.match(stripped)
    if match:
        number = match.group("number").upper().strip(".")
        title = match.group("title").strip()
        if title:
            return {"number": number, "title": title, "kind": "roman"}

    return None


def _number_depth(number: Optional[str]) -> int:
    if not number:
        return 0
    if re.fullmatch(r"[IVXLCDM]+", number.upper()):
        return 1
    return len(re.findall(r"\d+", number))


def _number_parent(number: str) -> Optional[str]:
    if not number or re.fullmatch(r"[IVXLCDM]+", number.upper()):
        return None
    parts = number.split(".")
    if len(parts) <= 1:
        return None
    return ".".join(parts[:-1])


def _is_immediate_child_number(parent_number: Optional[str], child_number: str) -> bool:
    if re.fullmatch(r"[IVXLCDM]+", child_number.upper()):
        return _number_depth(parent_number) >= 3
    if not parent_number:
        return _number_depth(child_number) == 1
    if re.fullmatch(r"[IVXLCDM]+", str(parent_number).upper()):
        return False
    return _number_parent(child_number) == str(parent_number).strip(".")


def _is_toc_or_cis_line(text: str, line_id: Optional[str] = None) -> bool:
    text_lower = text.strip().lower()
    if re.search(r"\.{4,}\s*\d+\s*$", text):
        return True
    if re.search(r"\d+\s*\.{4,}\s*\d+$", text):
        return True
    return False


def _is_header_footer(line_data: Optional[Dict[str, Any]]) -> bool:
    if line_data is None:
        return False
    if parse_numbered_prefix(line_data.get("text", "")):
        return False
    if line_data.get("is_header_candidate") or line_data.get("is_footer_candidate"):
        return True
    region = line_data.get("region", "")
    if region in ("top", "bottom"):
        return True
    return False


def _log10_ceil_gap_for_page(lines_bbox: List[Tuple[float, float]]) -> float:
    gaps = []
    for i in range(1, len(lines_bbox)):
        gap = lines_bbox[i][0] - lines_bbox[i - 1][1]
        if 0 < gap < 80:
            gaps.append(gap)
    if not gaps:
        return 20.0
    sorted_gaps = sorted(gaps)
    mid = len(sorted_gaps) // 2
    if len(sorted_gaps) % 2 == 0:
        return (sorted_gaps[mid - 1] + sorted_gaps[mid]) / 2
    return sorted_gaps[mid]


class SectionTreeBuilder:
    def __init__(
        self,
        heading_candidates: List[Dict[str, Any]],
        physical_pages: List[Dict[str, Any]],
        policy_id: str = "",
        pipeline_run_id: str = "",
    ):
        self.heading_candidates = heading_candidates
        self.physical_pages = physical_pages
        self.policy_id = policy_id or "policy"
        self.pipeline_run_id = pipeline_run_id or ""
        self._policy_id_safe = _safe_id_part(self.policy_id)

        self._filtered_headings: List[Dict[str, Any]] = []
        self._line_index: Dict[str, Dict[str, Any]] = {}
        self._page_lines: Dict[int, List[Dict[str, Any]]] = {}
        self._all_ordered_lines: List[Tuple[int, int, str]] = []
        self._line_to_idx: Dict[str, int] = {}
        self._line_page: Dict[str, int] = {}
        self._median_gap_per_page: Dict[int, float] = {}

        self._build_indexes()

    def _build_indexes(self):
        self._filtered_headings = sorted(
            [c for c in self.heading_candidates if c.get("decision") == "heading"],
            key=lambda c: (c.get("page_number", 0), c.get("bbox", [0, 0, 0, 0])[1]),
        )
        for page in self.physical_pages:
            pnum = page.get("page_number", 0)
            lines = page.get("lines", [])
            self._page_lines[pnum] = lines
            bboxes = []
            for line in lines:
                lid = line.get("line_id", "")
                self._line_index[lid] = line
                bbox = line.get("bbox", [0, 0, 0, 0])
                bboxes.append((float(bbox[1]), float(bbox[3])))
            self._median_gap_per_page[pnum] = _log10_ceil_gap_for_page(bboxes)

        flat_idx = 0
        for page in self.physical_pages:
            pnum = page.get("page_number", 0)
            for line in page.get("lines", []):
                lid = line.get("line_id", "")
                self._all_ordered_lines.append((pnum, flat_idx, lid))
                self._line_to_idx[lid] = flat_idx
                self._line_page[lid] = pnum
                flat_idx += 1

    def build_tree(self) -> List[Dict[str, Any]]:
        sections: List[Dict[str, Any]] = []
        section_id = self._make_section_id(0, "root")
        root = {
            "section_id": section_id,
            "heading_candidate_id": None,
            "heading_line_id": None,
            "number": None,
            "title": "Document root",
            "normalized_title": "document root",
            "level": 0,
            "heading_type": "root",
            "heading_score": None,
            "parent_id": None,
            "children": [],
            "page_start": 1,
            "page_end": max((p.get("page_number", 1) for p in self.physical_pages), default=1),
            "line_ids": [],
            "content_line_ids": [],
            "text": "",
        }
        sections.append(root)

        stack: List[Dict[str, Any]] = [root]
        id_map: Dict[str, Dict[str, Any]] = {section_id: root}

        if self._needs_preheading_body_section():
            preheading = self._preheading_body_section(len(sections))
            preheading["parent_id"] = root["section_id"]
            root["children"].append(preheading["section_id"])
            sections.append(preheading)
            id_map[preheading["section_id"]] = preheading

        for heading in self._filtered_headings:
            sec = self._heading_to_section(heading, len(sections))
            level = sec["level"]

            while stack and stack[-1]["level"] >= level:
                stack.pop()

            parent = stack[-1] if stack else root
            sec["parent_id"] = parent["section_id"]
            parent["children"].append(sec["section_id"])

            sec_id = sec["section_id"]
            sections.append(sec)
            id_map[sec_id] = sec
            stack.append(sec)

        return sections

    def _needs_preheading_body_section(self) -> bool:
        if not self._filtered_headings:
            return False
        first_heading = self._filtered_headings[0]
        first_line_id = first_heading.get("line_id", "")
        first_idx = self._line_to_idx.get(first_line_id, -1)
        first_page = first_heading.get("page_number", 0)
        if first_idx <= 0 or first_page <= 3:
            return False

        meaningful_lines = 0
        for _, flat_idx, lid in self._all_ordered_lines:
            if flat_idx >= first_idx:
                break
            line = self._line_index.get(lid)
            if not line or _is_header_footer(line):
                continue
            text = line.get("text", "").strip()
            if len(text) >= 4:
                meaningful_lines += 1
            if meaningful_lines >= 50:
                return True
        return False

    def _preheading_body_section(self, index: int) -> Dict[str, Any]:
        return {
            "section_id": self._make_section_id(index, "sec"),
            "heading_candidate_id": None,
            "heading_line_id": None,
            "number": None,
            "title": "Pre-heading body text",
            "normalized_title": "pre-heading body text",
            "level": 1,
            "heading_type": "synthetic_preheading_body",
            "heading_score": None,
            "parent_id": None,
            "children": [],
            "page_start": 1,
            "page_end": 1,
            "line_ids": [],
            "content_line_ids": [],
            "text": "",
            "pipeline_run_id": self.pipeline_run_id,
        }

    def _make_section_id(self, index: int, prefix: str = "sec") -> str:
        return f"{self._policy_id_safe}_{prefix}_{index:04d}"

    def _heading_to_section(self, heading: Dict[str, Any], index: int) -> Dict[str, Any]:
        sec_id = self._make_section_id(index, "sec")
        text = heading.get("text", "").strip()
        norm = heading.get("normalized_text", "") or _normalize_title(text)
        number = _extract_number_from_heading(heading)
        level = _infer_level(
            heading.get("numbering_token"),
            heading.get("level_hint", 1),
        )
        line_id = heading.get("line_id", "")
        page_num = heading.get("page_number", 0)

        return {
            "section_id": sec_id,
            "heading_candidate_id": heading.get("candidate_id"),
            "heading_line_id": line_id,
            "number": number,
            "title": _normalize_title(text),
            "normalized_title": norm,
            "level": level,
            "heading_type": "visual",
            "heading_score": heading.get("score"),
            "parent_id": None,
            "children": [],
            "page_start": page_num,
            "page_end": page_num,
            "line_ids": [line_id] if line_id else [],
            "content_line_ids": [],
            "text": "",
            "pipeline_run_id": self.pipeline_run_id,
        }

    def assign_content_lines(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        id_map = {s["section_id"]: s for s in sections}
        root = next(s for s in sections if s["level"] == 0)

        ordered_non_root = sorted(
            [s for s in sections if s["level"] > 0],
            key=lambda s: self._heading_sort_key(s),
        )

        for i, sec in enumerate(ordered_non_root):
            start_line_id = sec.get("heading_line_id", "")
            start_idx = self._line_to_idx.get(start_line_id, -1)

            if i + 1 < len(ordered_non_root):
                next_sec = ordered_non_root[i + 1]
                next_line_id = next_sec.get("heading_line_id", "")
                end_idx = self._line_to_idx.get(next_line_id, len(self._all_ordered_lines))
            else:
                end_idx = len(self._all_ordered_lines)

            sec_line_ids = []
            for j in range(start_idx + 1, end_idx):
                if j < len(self._all_ordered_lines):
                    sec_line_ids.append(self._all_ordered_lines[j][2])

            sec["line_ids"] = [start_line_id] + sec_line_ids if start_line_id else sec_line_ids

        root_total_lines = []
        for sec in ordered_non_root:
            root_total_lines.extend(sec.get("line_ids", []))
        root["line_ids"] = root_total_lines

        children_map: Dict[str, List[str]] = {}
        for s in sections:
            pid = s.get("parent_id")
            if pid:
                children_map.setdefault(pid, []).append(s["section_id"])

        child_line_sets: Dict[str, set] = {}

        def _compute_child_lines(sec_id: str) -> set:
            if sec_id in child_line_sets:
                return child_line_sets[sec_id]
            all_children = set()
            for cid in children_map.get(sec_id, []):
                child_sec = id_map.get(cid)
                if child_sec:
                    all_children.update(child_sec.get("line_ids", []))
                    all_children.update(_compute_child_lines(cid))
            child_line_sets[sec_id] = all_children
            return all_children

        for s in sections:
            sid = s["section_id"]
            own_line_ids = s.get("line_ids", [])
            child_lines = _compute_child_lines(sid)
            s["content_line_ids"] = [
                lid
                for lid in own_line_ids
                if lid not in child_lines and lid != s.get("heading_line_id")
            ]
            s["text"] = self._line_ids_to_text(s["content_line_ids"])

        for s in sections:
            all_lids = s.get("line_ids", [])
            if not all_lids:
                continue
            pages_found = set()
            for lid in all_lids:
                pnum = self._line_page.get(lid)
                if pnum is not None:
                    pages_found.add(pnum)
            if pages_found:
                s["page_start"] = min(pages_found)
                s["page_end"] = max(pages_found)

        return sections

    def _heading_sort_key(self, sec: Dict[str, Any]) -> Tuple:
        line_id = sec.get("heading_line_id", "")
        idx = self._line_to_idx.get(line_id, -1)
        return (sec.get("page_start", 0), idx)

    def _line_ids_to_text(self, line_ids: List[str]) -> str:
        texts = []
        for lid in line_ids:
            line = self._line_index.get(lid)
            if line:
                t = line.get("text", "").strip()
                if t:
                    texts.append(t)
        return " ".join(texts)

    def detect_synthetic_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for _ in range(5):
            existing_line_ids = {s.get("heading_line_id") for s in sections if s.get("heading_line_id")}
            new_sections: List[Dict[str, Any]] = []
            leaf_sections = [
                s
                for s in sections
                if s["level"] > 0
                and not s.get("children")
                and s.get("heading_type") != "synthetic_preheading_body"
            ]

            for leaf in leaf_sections:
                numbered_lines = self._synthetic_candidates_for_leaf(leaf, existing_line_ids)
                if len(numbered_lines) < 2 and not (
                    len(numbered_lines) == 1
                    and (
                        numbered_lines[0][3] == "unnumbered"
                        or (leaf.get("number") and "." in str(leaf.get("number")))
                    )
                ):
                    continue

                for lid, num_str, title_text, _kind, _ in numbered_lines:
                    synth_id = self._make_section_id(len(sections) + len(new_sections), "sec")
                    heading_text = f"{num_str}. {title_text}" if num_str else title_text
                    norm = _normalize_title(heading_text)
                    synth_page = self._line_page.get(lid, leaf.get("page_start", 0))
                    synth_level = max(leaf["level"] + 1, _infer_level(num_str, leaf["level"] + 1))
                    synth = {
                        "section_id": synth_id,
                        "heading_candidate_id": None,
                        "heading_line_id": lid,
                        "number": num_str or None,
                        "title": _normalize_title(heading_text),
                        "normalized_title": norm,
                        "level": synth_level,
                        "heading_type": (
                            "synthetic_body_numbered" if num_str else "synthetic_body_heading"
                        ),
                        "heading_score": None,
                        "parent_id": leaf["section_id"],
                        "children": [],
                        "page_start": synth_page,
                        "page_end": synth_page,
                        "line_ids": [lid],
                        "content_line_ids": [],
                        "text": "",
                        "pipeline_run_id": self.pipeline_run_id,
                    }
                    new_sections.append(synth)
                    leaf["children"].append(synth_id)
                    existing_line_ids.add(lid)

            if not new_sections:
                break

            sections.extend(new_sections)
            sections = self.assign_content_lines(sections)

        return sections

    def _synthetic_candidates_for_leaf(
        self,
        leaf: Dict[str, Any],
        existing_line_ids: set,
    ) -> List[Tuple[str, str, str, str, int]]:
        parent_number = leaf.get("number")
        numbered_lines: List[Tuple[str, str, str, str, int]] = []

        for lid in leaf.get("content_line_ids", []):
            if lid in existing_line_ids:
                continue
            line = self._line_index.get(lid)
            if not line:
                continue
            text = line.get("text", "").strip()
            if not text:
                continue
            if _is_toc_or_cis_line(text, lid):
                continue
            if _is_header_footer(line):
                continue
            parsed = parse_numbered_prefix(text)
            if not parsed:
                parsed = self._parse_unnumbered_structural_heading(text)
            if not parsed:
                continue
            num_str = parsed["number"]
            allow_restart = self._allows_restart_numbering(leaf, num_str)
            if num_str and not _is_immediate_child_number(parent_number, num_str) and not allow_restart:
                continue
            title_text = parsed["title"].strip()
            if self._looks_like_table_or_list_item(leaf, text, num_str, title_text, allow_restart):
                continue
            numbered_lines.append(
                (lid, num_str, title_text, parsed["kind"], self._line_to_idx.get(lid, 0))
            )

        numbered_lines.sort(key=lambda x: x[4])
        return numbered_lines

    def _parse_unnumbered_structural_heading(self, text: str) -> Optional[Dict[str, str]]:
        stripped = text.strip()
        compact = re.sub(r"\s+", " ", stripped)
        if not (8 <= len(compact) <= 100):
            return None
        upper_ratio = sum(1 for ch in compact if ch.isupper()) / max(
            1, sum(1 for ch in compact if ch.isalpha())
        )
        if upper_ratio < 0.75:
            return None
        title_lower = compact.lower()
        structural_terms = (
            "benefits covered",
            "general conditions",
            "exclusions and limitations",
        )
        if not any(term in title_lower for term in structural_terms):
            return None
        return {"number": "", "title": compact.rstrip(" .:"), "kind": "unnumbered"}

    def _allows_restart_numbering(self, leaf: Dict[str, Any], number: str) -> bool:
        title = (leaf.get("title") or "").lower()
        restart_context_terms = (
            "definition",
            "exclusion",
            "condition",
            "scope of cover",
            "coverage",
            "benefits",
            "claim",
            "waiting",
        )
        if not any(term in title for term in restart_context_terms):
            return False
        if re.fullmatch(r"\d{1,2}", number):
            return True
        return False

    def _looks_like_table_or_list_item(
        self,
        leaf: Dict[str, Any],
        text: str,
        number: str,
        title: str,
        allow_restart: bool = False,
    ) -> bool:
        parent_title = (leaf.get("title") or "").lower()
        if re.fullmatch(r"\d+", number):
            if leaf.get("number") and str(leaf.get("number")) != number and not allow_restart:
                return True
            list_context_terms = (
                "day care",
                "health services",
                "excluded items",
                "items",
                "annexure",
                "reward",
                "test",
                "expense",
                "expenses",
            )
            if any(term in parent_title for term in list_context_terms):
                return True
            if re.search(r"\s+\d{1,3}\s+[A-Z]", text):
                return True
        if len(title) <= 2:
            return True
        return False

    def build(self) -> Dict[str, Any]:
        sections = self.build_tree()
        sections = self.assign_content_lines(sections)
        sections = self.detect_synthetic_sections(sections)
        section_tree = self._build_nested_tree(sections)
        return {
            "sections": sections,
            "section_tree": section_tree,
        }

    def _build_nested_tree(self, sections: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        id_map = {s["section_id"]: s for s in sections}
        root = next((s for s in sections if s["level"] == 0), None)
        if not root:
            return None
        return self._nest_section(root["section_id"], id_map)

    def _nest_section(self, sec_id: str, id_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        sec = deepcopy(id_map.get(sec_id, {}))
        if not sec:
            return {}
        children_ids = sec.get("children", [])
        sec["children"] = [self._nest_section(cid, id_map) for cid in children_ids]
        return sec
