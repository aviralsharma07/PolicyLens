from typing import Dict, List, Tuple

from pdf_parser.models import Line, Page, Region


TOP_MARGIN_FRACTION = 0.10
BOTTOM_MARGIN_FRACTION = 0.10


def classify_line_region(line: Line, page_height: float) -> Region:
    _, top, _, bottom = line.bbox
    y_center = (top + bottom) / 2.0
    if y_center < page_height * TOP_MARGIN_FRACTION:
        return Region.top
    elif y_center > page_height * (1.0 - BOTTOM_MARGIN_FRACTION):
        return Region.bottom
    return Region.body


def classify_regions(pages: List[Page]) -> None:
    for page in pages:
        for line in page.lines:
            line.region = classify_line_region(line, page.height)


_TLineKey = Tuple[str, Region]


def _build_region_signature_map(pages: List[Page]) -> Dict[_TLineKey, int]:
    freq: Dict[_TLineKey, int] = {}
    for page in pages:
        seen: set[_TLineKey] = set()
        for line in page.lines:
            stripped = line.text.strip()
            if not stripped:
                continue
            key = (stripped, line.region)
            if key not in seen:
                freq[key] = freq.get(key, 0) + 1
                seen.add(key)
    return freq


MIN_REPEAT_COUNT = 3


def tag_candidates(pages: List[Page]) -> None:
    freq = _build_region_signature_map(pages)
    for page in pages:
        for line in page.lines:
            stripped = line.text.strip()
            if not stripped:
                continue
            key = (stripped, line.region)
            count = freq.get(key, 0)
            if count >= MIN_REPEAT_COUNT:
                if line.region == Region.top:
                    line.is_header_candidate = True
                elif line.region == Region.bottom:
                    line.is_footer_candidate = True


def process(pages: List[Page]) -> None:
    classify_regions(pages)
    tag_candidates(pages)
