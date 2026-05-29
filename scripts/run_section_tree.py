import argparse
import json
import os
import sys
from typing import Any, Dict, List

from structure_parser.section_tree import SectionTreeBuilder
from structure_parser.clause_segmenter import ClauseSegmenter


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_line_index(pages: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    index = {}
    for page in pages:
        for line in page.get("lines", []):
            lid = line.get("line_id", "")
            if lid:
                index[lid] = line
    return index


def _build_line_to_idx_mapping(pages: List[Dict[str, Any]]) -> Dict[str, int]:
    mapping = {}
    idx = 0
    for page in pages:
        for line in page.get("lines", []):
            lid = line.get("line_id", "")
            if lid:
                mapping[lid] = idx
                idx += 1
    return mapping


def main():
    parser = argparse.ArgumentParser(description="DSE-006 Section Tree Builder")
    parser.add_argument("--physical-root", required=True, help="Root of physical parser outputs")
    parser.add_argument(
        "--logical-root",
        "--heading-root",
        dest="logical_root",
        required=True,
        help="Root of heading candidate outputs",
    )
    parser.add_argument("--output-root", required=True, help="Root for section tree outputs")
    parser.add_argument("--policy", help="Specific policy slug to process (optional)")

    args = parser.parse_args()

    if not os.path.isdir(args.physical_root):
        print(f"ERROR: physical root not found: {args.physical_root}", file=sys.stderr)
        return 1

    if args.policy:
        slugs = [args.policy]
    else:
        slugs = sorted(
            d
            for d in os.listdir(args.logical_root)
            if os.path.isdir(os.path.join(args.logical_root, d)) and not d.startswith(".")
        )

    results: List[Dict[str, Any]] = []

    for slug in slugs:
        doc_path = os.path.join(args.physical_root, slug, "document_physical.json")
        cand_path = os.path.join(args.logical_root, slug, "heading_candidates.json")

        if not os.path.isfile(doc_path):
            msg = f"no document_physical.json at {doc_path}"
            print(f"  ERROR {slug}: {msg}", file=sys.stderr)
            results.append({"slug": slug, "status": "missing_physical_output", "message": msg})
            continue

        if not os.path.isfile(cand_path):
            msg = f"no heading_candidates.json at {cand_path}"
            print(f"  ERROR {slug}: {msg}", file=sys.stderr)
            results.append({"slug": slug, "status": "missing_candidates", "message": msg})
            continue

        print(f"Building section tree for {slug} ...")
        try:
            doc = load_json(doc_path)
            candidates_data = load_json(cand_path)
        except Exception as exc:
            msg = f"failed to load input JSON: {exc}"
            print(f"  ERROR {slug}: {msg}", file=sys.stderr)
            results.append({"slug": slug, "status": "load_failed", "message": msg})
            continue

        physical_pages = doc.get("pages", [])
        heading_candidates = candidates_data.get("candidates", [])
        pipeline_run_id = candidates_data.get("config", {}).get("pipeline_run_id") or doc.get(
            "pipeline_run_id", ""
        )
        issues = []

        try:
            builder = SectionTreeBuilder(
                heading_candidates=heading_candidates,
                physical_pages=physical_pages,
                policy_id=slug,
                pipeline_run_id=pipeline_run_id,
            )
            result = builder.build()

            line_index = _build_line_index(physical_pages)
            line_to_idx = _build_line_to_idx_mapping(physical_pages)
            segmenter = ClauseSegmenter(
                physical_pages=physical_pages,
                line_index=line_index,
                line_to_idx=line_to_idx,
            )
            clauses = segmenter.segment_document(result["sections"])
        except Exception as exc:
            import traceback

            msg = f"section tree build failed: {exc}\n{traceback.format_exc()}"
            print(f"  ERROR {slug}: {msg}", file=sys.stderr)
            results.append({"slug": slug, "status": "build_failed", "message": str(exc)})
            continue

        out_dir = os.path.join(args.output_root, slug)
        os.makedirs(out_dir, exist_ok=True)

        out_tree = {
            "schema_version": "section_tree.v1",
            "parser_version": "section_tree_builder.v2",
            "document_id": candidates_data.get("document_id") or doc.get("document_id"),
            "policy_id": candidates_data.get("policy_id") or doc.get("policy_id") or slug,
            "pipeline_run_id": pipeline_run_id,
            "config": {
                "heading_threshold": candidates_data.get("config", {}).get("threshold", 0.5),
                "synthetic_detection": "compact_numbered_iterative_v2",
                "clause_segmentation": "numbered_prefix_and_paragraph_gap_v2",
            },
            "source_paths": {
                "physical": doc_path,
                "heading_candidates": cand_path,
            },
            "issues": issues,
            "total_sections": len(result["sections"]),
            "total_clauses": len(clauses),
            "total_visual_headings": sum(
                1 for s in result["sections"] if s.get("heading_type") == "visual"
            ),
            "total_synthetic_sections": sum(
                1
                for s in result["sections"]
                if str(s.get("heading_type", "")).startswith("synthetic_")
            ),
            "sections": result["sections"],
            "section_tree": result["section_tree"],
            "clauses": clauses,
        }

        out_path = os.path.join(out_dir, "section_tree.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out_tree, f, indent=2)

        visual = out_tree["total_visual_headings"]
        synth = out_tree["total_synthetic_sections"]
        clauses_count = out_tree["total_clauses"]
        print(
            f"  {slug}: {len(result['sections'])} sections ({visual} visual, {synth} synthetic), "
            f"{clauses_count} clauses"
        )
        results.append(
            {
                "slug": slug,
                "status": "ok",
                "output_path": out_path,
                "total_sections": len(result["sections"]),
                "total_visual_headings": visual,
                "total_synthetic_sections": synth,
                "total_clauses": clauses_count,
            }
        )

    os.makedirs(args.output_root, exist_ok=True)
    summary_path = os.path.join(args.output_root, "section_tree_run_summary.json")
    summary = {
        "processed": sum(1 for r in results if r["status"] == "ok"),
        "errors": sum(1 for r in results if r["status"] != "ok"),
        "results": results,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary written to {summary_path}")
    print("\nDone.")
    return 0 if summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
