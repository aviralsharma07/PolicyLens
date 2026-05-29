# ADR-0011: Use pdfplumber for physical layout extraction (no OCR/vision)

**Status:** accepted

**Decision:** Use pdfplumber as the primary physical layout extractor for DSE-004. Produce text-block-outline debug HTML (not full PDF-replica). Store all coordinates in PDF point units with pdfplumber's top-left-origin bbox convention: `[x0, top, x1, bottom]`.

**Context:** Phase 1 of the doc-structure-engine needs reliable text-layer extraction from the 647 active policy wording PDFs. The corpus is confirmed 100% text-layer (no scanned documents). Key requirements: extract page/block/line/span layout with bbox coordinates, font metadata, and reading order. Never use OCR or vision. Generate lightweight debug HTML for visual inspection.

**Options considered:**
1. **PyMuPDF (fitz)** — Fast C-based parser, good text extraction, but no native block/line/span grouping api as simple as pdfplumber's.
2. **pdfplumber (chosen)** — Built on pdfminer.six, provides `page.chars`, `page.lines`, `page.rects`, `page.curves`, `page.images` directly with bbox coordinates and font metadata. Also provides `page.find_tables()` for later DSE-009 table extraction.
3. **pypdf** — Lighter but provides char-level extraction only; no line/block grouping or table detection.
4. **IBM Docling** — Full pipeline with layout detection and markdown output, but heavier than needed for Phase 1; planned as secondary cross-check tool only.
5. **OCR (tesseract/paddleocr)** — Unnecessary; corpus confirmed 100% text-layer.

**Reasoning:** pdfplumber provides the right granularity (chars, lines, rects, curves) without unnecessary abstraction. It doesn't do its own line grouping that obscures raw coordinates. `find_tables()` is directly usable for DSE-009. It handles rotated pages and non-embedded fonts gracefully. Debug HTML uses simple CSS-positioned divs — fast to generate, easy to inspect.

**Consequences:**
- Positive: Direct access to char-level layout with bbox and font metadata.
- Positive: `find_tables()` available without additional dependencies.
- Positive: Lightweight debug HTML with positioned text blocks.
- Positive: Same parser works for all 647 text-layer PDFs.
- Negative: Debug HTML is text-block-outline only (no images, no exact page replica, no font rendering).
- Negative: pdfplumber may have edge cases with highly compressed or encrypted PDFs (handled via error logging).
- Negative: pdfplumber table detection is heuristic-based; DSE-009 may need additional refinement.

**Revisit when:** pdfplumber cannot handle a meaningful subset of the corpus (>5% failure rate), or when debug HTML fidelity is insufficient for debugging structure parser issues.
