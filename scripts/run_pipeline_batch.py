"""
Run Pipeline Batch — DSE-012

Runs the full extraction pipeline on a set of policies defined by a
selection manifest. Produces interim outputs under data/interim/.

Pipeline stages (sequential per policy):
  1. Physical layout extraction (pdfplumber via layout_extractor.py)
  2. Heading candidate scoring
  3. Section tree building
  4. Table engine extraction
  5. Fact extraction (5 deterministic concepts)

Usage:
  PYTHONPATH=. python scripts/run_pipeline_batch.py \\
    --manifest data/manifests/dse012_gold_expansion_candidates_v1.json \\
    --policy-data-root ../policy_data

Each stage runs in-process with error isolation. A policy that fails
one stage records the error but continues to the next stage.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import sys
import time
import traceback
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("run_pipeline_batch")

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _run_stage(fn, stage_name: str, slug: str) -> dict:
    """Run a pipeline stage function with error isolation."""
    logger.info("  %s: running %s", slug, stage_name)
    try:
        fn()
        return {"stage": stage_name, "status": "ok"}
    except Exception as exc:
        logger.warning("  %s: %s failed: %s", slug, stage_name, exc)
        return {
            "stage": stage_name,
            "status": "failed",
            "error": str(exc),
            "traceback": traceback.format_exc()[-500:],
        }


def process_policy(
    policy: dict,
    policy_data_root: str,
) -> dict:
    """Run all pipeline stages for one policy."""
    slug = policy["slug"]
    pdf_rel_path = policy["file_path"]
    pdf_path = os.path.join(policy_data_root, pdf_rel_path)
    pipeline_run_id = f"dse012_batch_{int(time.time())}"

    if not os.path.isfile(pdf_path):
        logger.error("  %s: PDF not found: %s", slug, pdf_path)
        return {"slug": slug, "status": "pdf_not_found", "stages": []}

    stages = []

    # Stage 1: Physical layout extraction
    def run_physical():
        from pdf_parser.layout_extractor import extract_pdf, save_document

        doc = extract_pdf(pdf_path, slug, pipeline_run_id)
        save_document(doc, "data/interim/physical", slug)

    stages.append(_run_stage(run_physical, "physical_parser", slug))

    # Stage 2: Heading candidate scoring
    def run_heading():
        from structure_parser.heading_scorer import HeadingScorer

        phys_path = f"data/interim/physical/{slug}/document_physical.json"
        if not os.path.isfile(phys_path):
            raise FileNotFoundError(f"Physical output not found: {phys_path}")
        phys = _load_json(phys_path)
        scorer = HeadingScorer()
        results = scorer.score_document(phys)
        out_dir = f"data/interim/logical/{slug}"
        os.makedirs(out_dir, exist_ok=True)
        _write_json(f"{out_dir}/heading_candidates.json", results)

    stages.append(_run_stage(run_heading, "heading_scorer", slug))

    # Stage 3: Section tree building (replicates scripts/run_section_tree.py logic)
    def run_section_tree():
        from structure_parser.section_tree import SectionTreeBuilder
        from structure_parser.clause_segmenter import ClauseSegmenter

        phys_path = f"data/interim/physical/{slug}/document_physical.json"
        heading_path = f"data/interim/logical/{slug}/heading_candidates.json"
        if not os.path.isfile(phys_path):
            raise FileNotFoundError(f"Physical output not found: {phys_path}")
        if not os.path.isfile(heading_path):
            raise FileNotFoundError(f"Heading candidates not found: {heading_path}")

        doc = _load_json(phys_path)
        candidates_data = _load_json(heading_path)

        physical_pages = doc.get("pages", [])
        heading_candidates = candidates_data.get("candidates", [])

        builder = SectionTreeBuilder(
            heading_candidates=heading_candidates,
            physical_pages=physical_pages,
            policy_id=slug,
            pipeline_run_id=pipeline_run_id,
        )
        result = builder.build()

        # Build line index for clause segmentation
        line_index = {}
        line_to_idx = {}
        global_idx = 0
        for page in physical_pages:
            for ln in page.get("lines", []):
                lid = ln.get("line_id")
                if lid:
                    line_index[lid] = {
                        "page": page.get("page_number"),
                        "bbox": ln.get("bbox"),
                        "text": ln.get("text", ""),
                    }
                    line_to_idx[lid] = global_idx
                    global_idx += 1

        segmenter = ClauseSegmenter(
            physical_pages=physical_pages,
            line_index=line_index,
            line_to_idx=line_to_idx,
        )
        clauses = segmenter.segment_document(result["sections"])

        out_tree = {
            "schema_version": "section_tree.v1",
            "document_id": doc.get("document_id"),
            "policy_id": slug,
            "pipeline_run_id": pipeline_run_id,
            "sections": result["sections"],
            "section_tree": result["section_tree"],
            "clauses": clauses,
            "total_sections": len(result["sections"]),
            "total_clauses": len(clauses),
        }

        out_dir = f"data/interim/logical/{slug}"
        os.makedirs(out_dir, exist_ok=True)
        _write_json(f"{out_dir}/section_tree.json", out_tree)

    stages.append(_run_stage(run_section_tree, "section_tree", slug))

    # Stage 4: Table engine
    def run_tables():
        import pdfplumber
        from table_engine.table_detector import extract_tables_from_page
        from table_engine.text_alignment_detector import try_page
        from table_engine.table_type_classifier import classify
        from table_engine.models import TableDocument, ExtractionMethod

        phys_path = f"data/interim/physical/{slug}/document_physical.json"
        if not os.path.isfile(phys_path):
            raise FileNotFoundError(f"Physical output not found: {phys_path}")

        phys = _load_json(phys_path)
        document_id = phys.get("document_id", "")

        all_tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, plumber_page in enumerate(pdf.pages, start=1):
                page_table_counter = 1
                lattice_tables, page_table_counter = extract_tables_from_page(
                    page=plumber_page,
                    page_num=page_num,
                    policy_id=slug,
                    document_id=document_id,
                    page_table_counter=page_table_counter,
                )
                if not lattice_tables:
                    phys_lines = []
                    for pg in phys.get("pages", []):
                        if pg.get("page_number") == page_num:
                            phys_lines = [
                                {
                                    "line_id": ln.get("line_id", ""),
                                    "text": ln.get("text", ""),
                                    "bbox": ln.get("bbox", []),
                                    "region": ln.get("region", "body"),
                                }
                                for ln in pg.get("lines", [])
                            ]
                            break
                    if phys_lines:
                        fallback, page_table_counter = try_page(
                            phys_lines,
                            page_num,
                            slug,
                            document_id,
                            page_table_counter,
                        )
                        lattice_tables.extend(fallback)

                for table in lattice_tables:
                    raw_grid = table.__dict__.get("_raw_grid") or []
                    heading_ctx = table.__dict__.get("_heading_context") or ""
                    if raw_grid:
                        from table_engine.models import TableType

                        t_type, t_conf = classify(raw_grid, heading_ctx)
                    else:
                        t_type, t_conf = TableType.unknown, 0.0
                    table.table_type = t_type
                    table.table_type_confidence = t_conf

                all_tables.extend(lattice_tables)

        structured = sum(
            1 for t in all_tables if t.extraction_method == ExtractionMethod.pdfplumber_lattice
        )
        candidates = sum(
            1
            for t in all_tables
            if t.extraction_method == ExtractionMethod.text_alignment_candidate
        )

        table_doc = TableDocument(
            pipeline_run_id=pipeline_run_id,
            document_id=document_id,
            policy_id=slug,
            source_pdf_path=pdf_rel_path,
            page_count=phys.get("page_count", 0),
            tables_found=len(all_tables),
            structured_tables=structured,
            candidate_tables=candidates,
            tables=all_tables,
        )

        out_dir = f"data/interim/tables/{slug}"
        os.makedirs(out_dir, exist_ok=True)
        data = json.loads(table_doc.model_dump_json(exclude_none=True))
        _write_json(f"{out_dir}/document_tables.json", data)
        all_cells = []
        for t in all_tables:
            for cell in t.cells:
                all_cells.append(json.loads(cell.model_dump_json(exclude_none=True)))
        _write_json(f"{out_dir}/document_table_cells.json", all_cells)

    stages.append(_run_stage(run_tables, "table_engine", slug))

    # Stage 5: Fact extraction (uses same logic as scripts/run_fact_extractors.py)
    def run_facts():
        from pathlib import Path

        # Import the fact extractor process_policy function directly
        sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))
        from run_fact_extractors import process_policy as fact_process_policy

        section_tree_path = Path(f"data/interim/logical/{slug}/section_tree.json")
        if not section_tree_path.is_file():
            raise FileNotFoundError(f"Section tree not found: {section_tree_path}")
        output_root = Path("data/interim/facts")
        fact_process_policy(section_tree_path, output_root)

    stages.append(_run_stage(run_facts, "fact_extractors", slug))

    ok_count = sum(1 for s in stages if s["status"] == "ok")
    total = len(stages)
    status = "ok" if ok_count == total else ("partial" if ok_count > 0 else "failed")

    logger.info("  %s: %d/%d stages passed → %s", slug, ok_count, total, status)
    return {
        "slug": slug,
        "status": status,
        "stages_ok": ok_count,
        "stages_total": total,
        "stages": stages,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline Batch Runner — DSE-012")
    parser.add_argument(
        "--manifest", default="data/manifests/dse012_gold_expansion_candidates_v1.json"
    )
    parser.add_argument("--policy-data-root", default=str(_PROJECT_ROOT.parent / "policy_data"))
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    policies = manifest.get("policies", [])

    logger.info("Pipeline batch: %d policies from %s", len(policies), args.manifest)
    results = []

    for i, policy in enumerate(policies, 1):
        slug = policy["slug"]
        logger.info(
            "[%d/%d] Processing %s (%s — %s)",
            i,
            len(policies),
            slug,
            policy["insurer_display"],
            policy["plan_name_clean"],
        )
        result = process_policy(policy, args.policy_data_root)
        results.append(result)

    ok = sum(1 for r in results if r["status"] == "ok")
    partial = sum(1 for r in results if r["status"] == "partial")
    failed = sum(1 for r in results if r["status"] in ("failed", "pdf_not_found"))

    summary = {
        "date": time.strftime("%Y-%m-%d"),
        "task_id": "DSE-012",
        "total_policies": len(results),
        "ok": ok,
        "partial": partial,
        "failed": failed,
        "results": results,
    }

    _write_json("data/reports/dse012_pipeline_batch_summary.json", summary)
    logger.info(
        "Batch complete: %d ok, %d partial, %d failed out of %d", ok, partial, failed, len(results)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
