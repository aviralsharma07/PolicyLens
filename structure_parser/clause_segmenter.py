import re
from typing import Any, Dict, List, Optional, Tuple

from structure_parser.section_tree import parse_numbered_prefix


def _is_toc_dot_leader(text: str) -> bool:
    return bool(re.search(r"\.\s*\.\s*\.\s*\.\s*\.+", text))


def _is_header_footer_text(line_data: Optional[Dict[str, Any]]) -> bool:
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


def _compact_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def _normalize_clause_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class ClauseSegmenter:
    def __init__(
        self,
        physical_pages: List[Dict[str, Any]],
        line_index: Dict[str, Dict[str, Any]],
        line_to_idx: Dict[str, int],
    ):
        self.physical_pages = physical_pages
        self.line_index = line_index
        self.line_to_idx = line_to_idx

        self._page_lines: Dict[int, List[Dict[str, Any]]] = {}
        self._median_gap_per_page: Dict[int, float] = {}
        self._line_page: Dict[str, int] = {}
        self._build_page_data()

    def _build_page_data(self):
        for page in self.physical_pages:
            pnum = page.get("page_number", 0)
            lines = page.get("lines", [])
            self._page_lines[pnum] = lines
            bboxes = []
            for line in lines:
                lid = line.get("line_id")
                if lid:
                    self._line_page[lid] = pnum
                bbox = line.get("bbox", [0, 0, 0, 0])
                bboxes.append((float(bbox[1]), float(bbox[3])))
            self._median_gap_per_page[pnum] = self._compute_median_gap(bboxes)

    def _compute_median_gap(self, bboxes: List[Tuple[float, float]]) -> float:
        gaps = []
        for i in range(1, len(bboxes)):
            gap = bboxes[i][0] - bboxes[i - 1][1]
            if 0 < gap < 80:
                gaps.append(gap)
        if not gaps:
            return 20.0
        sorted_gaps = sorted(gaps)
        mid = len(sorted_gaps) // 2
        if len(sorted_gaps) % 2 == 0:
            return (sorted_gaps[mid - 1] + sorted_gaps[mid]) / 2
        return sorted_gaps[mid]

    def segment_section(
        self,
        section: Dict[str, Any],
        line_ids: List[str],
        section_id: str,
        clause_index: int,
    ) -> List[Dict[str, Any]]:
        if not line_ids:
            return self._default_clause(section, section_id, clause_index)

        blocks = self._split_into_blocks(line_ids, section)

        clauses = []
        for block in blocks:
            clauses.append(self._block_to_clause(block, section_id, clause_index))
            clause_index += 1

        return clauses if clauses else [self._default_clause(section, section_id, clause_index)]

    def _split_into_blocks(self, line_ids: List[str], section: Dict[str, Any]) -> List[List[str]]:
        blocks: List[List[str]] = []
        current_block: List[str] = []

        for lid in line_ids:
            line = self.line_index.get(lid)
            if not line:
                continue
            text = line.get("text", "").strip()
            if not text:
                continue
            if _is_toc_dot_leader(text):
                continue
            if _is_header_footer_text(line):
                continue

            line_is_numbered = parse_numbered_prefix(text) is not None

            if line_is_numbered:
                if current_block:
                    blocks.append(current_block)
                    current_block = []
                current_block.append(lid)
            else:
                gap_large = self._is_large_gap(line_ids, lid)
                if gap_large and current_block:
                    blocks.append(current_block)
                    current_block = [lid]
                else:
                    current_block.append(lid)

        if current_block:
            blocks.append(current_block)

        return blocks or [line_ids]

    def _is_large_gap(self, line_ids: List[str], lid: str) -> bool:
        idx = next((i for i, x in enumerate(line_ids) if x == lid), None)
        if idx is None or idx == 0:
            return False
        prev_lid = line_ids[idx - 1]
        prev_line = self.line_index.get(prev_lid)
        cur_line = self.line_index.get(lid)
        if not prev_line or not cur_line:
            return False
        prev_bbox = prev_line.get("bbox", [0, 0, 0, 0])
        cur_bbox = cur_line.get("bbox", [0, 0, 0, 0])
        gap = float(cur_bbox[1] or 0) - float(prev_bbox[3] or 0)
        prev_page = self._line_page.get(prev_lid)
        cur_page = self._line_page.get(lid)
        if prev_page != cur_page:
            return False
        if prev_page is not None and prev_page in self._median_gap_per_page:
            median_gap = self._median_gap_per_page[prev_page]
            return gap > median_gap * 3
        return False

    def _block_to_clause(
        self,
        block: List[str],
        section_id: str,
        clause_index: int,
    ) -> Dict[str, Any]:
        cid = f"clause_{clause_index:04d}"
        text_parts = []
        page_start = None
        page_end = None

        for lid in block:
            line = self.line_index.get(lid)
            if line:
                t = line.get("text", "").strip()
                if t:
                    text_parts.append(t)
                pnum = self._line_page.get(lid)
                if pnum is not None:
                    if page_start is None or pnum < page_start:
                        page_start = pnum
                    if page_end is None or pnum > page_end:
                        page_end = pnum

        title = ""
        clause_number = None
        if block:
            first_line = self.line_index.get(block[0])
            if first_line:
                t = first_line.get("text", "").strip()
                parsed = parse_numbered_prefix(t)
                if parsed:
                    clause_number = parsed["number"]
                    title = parsed["title"].strip()

        text = " ".join(text_parts)

        return {
            "clause_id": cid,
            "section_id": section_id,
            "clause_number": clause_number,
            "title": title[:100] if title else "",
            "page_start": page_start or 0,
            "page_end": page_end or page_start or 0,
            "line_ids": block,
            "text": text,
            "segmentation_method": "numbered_body" if clause_number else "paragraph_gap",
            "confidence": 0.9 if clause_number else 0.7,
        }

    def _default_clause(
        self,
        section: Dict[str, Any],
        section_id: str,
        clause_index: int,
    ) -> List[Dict[str, Any]]:
        cid = f"clause_{clause_index:04d}"
        return [
            {
                "clause_id": cid,
                "section_id": section_id,
                "clause_number": section.get("number"),
                "title": section.get("title", "")[:100],
                "page_start": section.get("page_start", 0),
                "page_end": section.get("page_end", 0),
                "line_ids": [],
                "text": section.get("text", ""),
                "segmentation_method": "default",
                "confidence": 0.5,
            }
        ]

    def segment_document(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_clauses: List[Dict[str, Any]] = []
        clause_index = 0

        for section in sections:
            if section["level"] == 0:
                continue
            line_ids = section.get("content_line_ids", [])
            clauses = self.segment_section(section, line_ids, section["section_id"], clause_index)
            all_clauses.extend(clauses)
            clause_index += len(clauses)

        return all_clauses
