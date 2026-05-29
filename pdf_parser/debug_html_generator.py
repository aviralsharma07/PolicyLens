import html
import os
from typing import List

from pdf_parser.models import Page, PhysicalDocument


def generate_page_html(page: Page, page_number: int) -> str:
    scale = 0.75
    w = int(page.width * scale)
    h = int(page.height * scale)

    lines_html = ""
    for line in page.lines:
        x0, top, x1, bottom = line.bbox
        l = int(x0 * scale)
        t = int(top * scale)
        r = int(x1 * scale)
        b = int(bottom * scale)
        cls = "line"
        if line.is_header_candidate:
            cls += " header"
        if line.is_footer_candidate:
            cls += " footer"
        escaped = html.escape(line.text)
        lines_html += (
            f'<div class="{cls}" style="left:{l}px;top:{t}px;'
            f"width:{r - l}px;height:{b - t}px;"
            f'font-size:{max(6, b - t - 2)}px;">{escaped}</div>\n'
        )

    spans_html = ""
    for span in page.spans:
        x0, top, x1, bottom = span.bbox
        l = int(x0 * scale)
        t = int(top * scale)
        r = int(x1 * scale)
        b = int(bottom * scale)
        fs = span.font_size if span.font_size else 8
        fw = "bold" if span.is_bold else "normal"
        escaped = html.escape(span.text)
        spans_html += (
            f'<div class="span" style="left:{l}px;top:{t}px;'
            f"width:{r - l}px;height:{b - t}px;"
            f"font-size:{max(6, int(fs * 0.75))}px;"
            f'font-weight:{fw};">{escaped}</div>\n'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Page {page_number}</title>
<style>
body {{ margin:0; background:#f5f5f5; }}
.page {{ position:relative; width:{w}px; height:{h}px; margin:20px auto;
        background:white; box-shadow:0 2px 8px rgba(0,0,0,0.15);
        overflow:hidden; }}
.line {{ position:absolute; overflow:hidden; white-space:nowrap;
        text-overflow:ellipsis; color:#000; }}
.span {{ position:absolute; overflow:hidden; white-space:nowrap;
        text-overflow:ellipsis; color:#006; }}
.header {{ background:rgba(255,200,200,0.3); }}
.footer {{ background:rgba(200,200,255,0.3); }}
.info {{ padding:8px; font-family:sans-serif; font-size:12px; color:#666; }}
</style>
</head>
<body>
<div class="info">Page {page_number} &mdash; {w}&times;{h}px (scaled {scale}x)</div>
<div class="page">
{spans_html}
{lines_html}
</div>
</body>
</html>"""


def generate_all(doc: PhysicalDocument, output_dir: str) -> List[str]:
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for page in doc.pages:
        html_content = generate_page_html(page, page.page_number)
        fname = f"page_{page.page_number:03d}.html"
        fpath = os.path.join(output_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html_content)
        paths.append(fpath)
    return paths
