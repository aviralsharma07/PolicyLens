import argparse
import json
import os
import sys
from typing import Any, Dict, List

from structure_parser.heading_scorer import HeadingScorer


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="DSE-005 Heading Candidate Scorer")
    parser.add_argument("--physical-root", required=True, help="Root of physical parser outputs")
    parser.add_argument("--output-root", required=True, help="Root for heading candidate outputs")
    parser.add_argument("--threshold", type=float, default=0.5, help="Heading score threshold")
    parser.add_argument("--policy", help="Specific policy slug to process (optional)")

    args = parser.parse_args()
    if not os.path.isdir(args.physical_root):
        print(f"ERROR: physical root not found: {args.physical_root}", file=sys.stderr)
        return 1

    if args.policy:
        slugs = [args.policy]
    else:
        physical_root = args.physical_root
        slugs = sorted(
            d
            for d in os.listdir(physical_root)
            if os.path.isdir(os.path.join(physical_root, d)) and not d.startswith(".")
        )

    scorer = HeadingScorer(threshold=args.threshold)
    results: List[Dict[str, Any]] = []

    for slug in slugs:
        doc_path = os.path.join(args.physical_root, slug, "document_physical.json")
        if not os.path.isfile(doc_path):
            msg = f"no document_physical.json at {doc_path}"
            print(f"  ERROR {slug}: {msg}", file=sys.stderr)
            results.append({"slug": slug, "status": "missing_physical_output", "message": msg})
            continue

        print(f"Scoring {slug} ...")
        try:
            doc = load_json(doc_path)
        except Exception as exc:
            msg = f"failed to load physical JSON: {exc}"
            print(f"  ERROR {slug}: {msg}", file=sys.stderr)
            results.append({"slug": slug, "status": "load_failed", "message": msg})
            continue

        result = scorer.score_document(doc)

        out_dir = os.path.join(args.output_root, slug)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "heading_candidates.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        headings = result["total_headings"]
        total = result["total_lines_scored"]
        print(
            f"  {slug}: {headings}/{total} lines scored as headings "
            f"(threshold={args.threshold}), body_mode={result['config']['body_font_mode']}"
        )
        results.append(
            {
                "slug": slug,
                "status": "ok",
                "output_path": out_path,
                "total_lines_scored": total,
                "total_headings": headings,
            }
        )

    os.makedirs(args.output_root, exist_ok=True)
    summary_path = os.path.join(args.output_root, "heading_run_summary.json")
    summary = {
        "threshold": args.threshold,
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
