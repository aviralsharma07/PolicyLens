# Gold Corpus Annotation Guide

Date: 2026-06-01
Task ID: DSE-003 / DSE-012
Status: gold_v2_20_policy_reviewed

## Purpose

This guide defines the gold corpus annotation workflow for doc-structure-engine. The corpus is used to evaluate physical parsing, heading detection, section tree construction, table detection, and fact extraction.

## Source Data Rules

- Raw PDFs stay in `../policy_data/` and are read-only.
- Gold files store relative `source_pdf_path` references only.
- Do not copy source PDFs into `gold_corpus/`.
- Page numbers are 1-based and refer to the PDF page order.
- BBox and cell coordinates are nullable in semantic `tables.json`, but DSE-009 `physical_table_labels.json` stores physical table bboxes where a visual table was verified.

## Policy Selection

The first five policies intentionally cover public/private insurers, standardized and non-standard structures, shorter and longer documents, accident coverage, tables, optional benefits, and regulatory clauses. DSE-012 expands the reviewed corpus to 20 policies across additional insurers and specialty product types.

## Annotation Files

Each policy folder contains:

- `metadata.json` — identity, source document, UIN match, counts, and limitations.
- `sections.json` — hierarchy of headings/sections with page ranges.
- `clauses.json` — legal text chunks linked to sections and pages.
- `tables.json` — identified table-like regions and table type labels.
- `facts.json` — 20 priority concept labels with AGENTS §14 fields.
- `heading_labels.json` — visual heading labels used by heading scorer evals.
- `physical_table_labels.json` — verified physical table labels used by table engine evals.

## Fact Status Rules

Use exactly one of:

- `present`
- `explicitly_not_covered`
- `not_applicable`
- `not_found`
- `ambiguous`
- `conflicting`
- `requires_manual_review`

A fact with `present` or `explicitly_not_covered` must include `evidence_text` and `evidence_page`. `not_found` means the concept was searched but no safe supporting policy text was found. `requires_manual_review` means the text suggests the concept may exist but the label is unsafe without a reviewer.

## Review Workflow

1. Open the source PDF from `source_pdf_path`.
2. Check `metadata.json` identity and page count.
3. Review section headings against the visible PDF.
4. Review fact evidence strings against the cited page.
5. Confirm whether null facts are truly `not_found`, `not_applicable`, or should become `requires_manual_review`.
6. Run `python3 scripts/validate_gold_corpus.py` before using the labels in parser or extractor evals.

## Pass History

- Pass 1: extracted text-layer content with `pypdf` and created initial sections, clauses, table regions, and 20 priority facts per policy.
- Pass 2: cross-checked available IBM Docling markdown for New India, HDFC, and ICICI; added source-tool metadata and manually summarized table headers/rows where the text supported it.
- Pass 3: re-reviewed facts with precision-first rules and downgraded schedule-dependent or definition-only values to `requires_manual_review`.
- Pass 4: generated missing IBM Docling markdown for Star and Care with OCR disabled and placeholder image export; re-ran structure, table, and fact provenance cross-checks for those two policies.
- Pass 5: applied the source-PDF-only manual review report for the 11 `requires_manual_review` facts; 10 became `present` and 1 became `not_applicable`.
- Pass 6: DSE-012 expanded the corpus from 5 to 20 reviewed policies. The 15 new policies were drafted from pipeline output, then promoted after source-PDF text review with per-policy review reports.

## Known Limitations

Gold v2 is still text-layer first for facts and clauses. Physical table bboxes are available where DSE-009 provided reliable labels, while parser failures discovered by the 20-policy expansion are tracked in DSE-012 eval artifacts and risk register entries.
