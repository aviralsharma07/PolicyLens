from argparse import Namespace
import json
from pathlib import Path

from scripts.dse020_triage_report import _markdown_report, build_report


def _write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_parser_target_override_excludes_zero_clause_from_parser_failures(tmp_path):
    manifest = {
        "policies": [
            {
                "slug": "excluded_product_list",
                "file_path": "23_Raheja_QBE/Raheja_QBE_Product_List.pdf",
                "file_hash": "sha256:excluded",
                "insurer": "Raheja_QBE",
            }
        ]
    }
    progress = {
        "policy_results": {
            "excluded_product_list": {
                "status": "ok",
                "stages": [
                    {"stage": "physical", "status": "ok"},
                    {"stage": "heading", "status": "ok"},
                    {"stage": "section", "status": "ok"},
                    {"stage": "tables", "status": "ok"},
                    {"stage": "facts", "status": "ok"},
                ],
            }
        }
    }
    overrides = {
        "overrides": [
            {
                "slug": "excluded_product_list",
                "file_hash": "sha256:excluded",
                "file_path": "23_Raheja_QBE/Raheja_QBE_Product_List.pdf",
                "parser_target": False,
                "reason_code": "non_policy_product_list",
                "classification": "identity_data_issue",
                "reviewer_note": "Not a policy wording parser target.",
            }
        ]
    }

    manifest_path = tmp_path / "manifest.json"
    progress_path = tmp_path / "progress.json"
    overrides_path = tmp_path / "overrides.json"
    output_root = tmp_path / "output"
    export_root = tmp_path / "export"

    _write_json(manifest_path, manifest)
    _write_json(progress_path, progress)
    _write_json(overrides_path, overrides)
    _write_json(
        output_root / "logical" / "excluded_product_list" / "heading_candidates.json",
        {"total_headings": 0},
    )
    _write_json(
        output_root / "logical" / "excluded_product_list" / "section_tree.json",
        {"total_clauses": 0},
    )
    _write_json(output_root / "facts" / "excluded_product_list" / "fact_candidates.json", [])

    report = build_report(
        Namespace(
            manifest=manifest_path,
            progress_summary=progress_path,
            output_root=output_root,
            db=tmp_path / "missing.sqlite",
            export_root=export_root,
            json_output=tmp_path / "report.json",
            md_output=tmp_path / "report.md",
            parser_target_overrides=overrides_path,
            date="2026-06-04",
        )
    )

    metrics = report["metrics"]
    assert metrics["zero_headings"] == []
    assert metrics["zero_clauses"] == []
    assert metrics["excluded_parser_targets"][0]["slug"] == "excluded_product_list"
    assert metrics["excluded_parser_targets"][0]["reason_code"] == "non_policy_product_list"
    assert not any("Fix parser/section-tree" in item for item in report["top_recommended_fixes"])

    markdown = _markdown_report(report)
    assert "- Zero headings: 0" in markdown
    assert "- Zero clauses: 0" in markdown
    assert "- Excluded parser targets: 1" in markdown
