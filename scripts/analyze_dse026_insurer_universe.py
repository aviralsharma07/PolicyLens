#!/usr/bin/env python3
"""DSE-026 insurer universe analysis.

Aggregate current Product A corpus readiness by canonical insurer using:
- active policy wording manifest
- UIN match report
- draft product source bundle registry

This script is intentionally read-only. It produces a JSON summary that feeds
the DSE-026 corpus availability report.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable

from identity.insurer_registry import INSURER_REGISTRY, lookup_by_folder


TARGET_INSURERS = [
    "HDFC ERGO",
    "ICICI Lombard",
    "Star Health",
    "Niva Bupa",
    "Care Health",
    "Tata AIG General Insurance",
    "Bajaj Allianz General Insurance",
    "SBI General Insurance",
    "Aditya Birla Health Insurance",
    "ManipalCigna Health Insurance",
    "New India Assurance",
    "United India Insurance",
    "Oriental Insurance",
    "Future Generali India Insurance",
    "Reliance General Insurance",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def normalize_active_insurer(raw_name: str) -> str:
    record = lookup_by_folder(raw_name)
    return record.canonical_name if record else raw_name.replace("_", " ")


def map_display_name(canonical_name: str) -> str:
    record = INSURER_REGISTRY.get(canonical_name)
    return record.display_name if record else canonical_name


def canonicalize_insurer_name(raw_name: str) -> str:
    if raw_name in INSURER_REGISTRY:
        return raw_name
    lowered = raw_name.lower()
    for canonical_name, record in INSURER_REGISTRY.items():
        if lowered == record.display_name.lower():
            return canonical_name
        if lowered == record.legal_name.lower():
            return canonical_name
        if lowered.startswith(record.display_name.lower()):
            return canonical_name
        if record.display_name.lower() in lowered:
            return canonical_name
    return raw_name


def classify_group_like(entry: Dict[str, Any]) -> bool:
    uin = (entry.get("uin") or "").upper()
    name_parts = " ".join(
        [
            entry.get("filename") or "",
            entry.get("lifecycle_product_name") or "",
            entry.get("product_name") or "",
        ]
    ).lower()
    if "group" in name_parts:
        return True
    return "HLGP" in uin or "GPA" in uin


def build_active_lookup(uin_results: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {row["document_id"]: row for row in uin_results}


def ensure_insurer(bucket: Dict[str, Any], canonical_name: str) -> Dict[str, Any]:
    if canonical_name not in bucket:
        bucket[canonical_name] = {
            "insurer": canonical_name,
            "display_name": map_display_name(canonical_name),
            "active_policy_wording_count": 0,
            "active_brochure_count": 0,
            "active_document_types": Counter(),
            "source_domain_counts": Counter(),
            "bundle_count": 0,
            "source_quality_counts": Counter(),
            "bundle_document_type_counts": Counter(),
            "known_pbt_bundle_count": 0,
            "known_cis_bundle_count": 0,
            "known_brochure_bundle_count": 0,
            "unique_uin_base_count": 0,
            "duplicate_uin_base_count": 0,
            "group_like_document_count": 0,
            "document_count_with_missing_source_url": 0,
            "raw_active_document_count": 0,
        }
    return bucket[canonical_name]


def finalize_bucket(row: Dict[str, Any], uin_base_counter: Counter) -> None:
    row["active_document_types"] = dict(row["active_document_types"])
    row["source_domain_counts"] = dict(row["source_domain_counts"])
    row["source_quality_counts"] = dict(row["source_quality_counts"])
    row["bundle_document_type_counts"] = dict(row["bundle_document_type_counts"])
    row["unique_uin_base_count"] = len(uin_base_counter)
    row["duplicate_uin_base_count"] = sum(1 for _, count in uin_base_counter.items() if count > 1)

    if row["known_pbt_bundle_count"] > 0 and row["known_cis_bundle_count"] > 0:
        row["readiness_band"] = "close"
    elif row["bundle_count"] >= 10 and row["active_policy_wording_count"] >= 10:
        row["readiness_band"] = "medium"
    else:
        row["readiness_band"] = "far"

    noisy = row["group_like_document_count"]
    if noisy >= 10 or row["duplicate_uin_base_count"] >= 3:
        row["noise_risk"] = "high"
    elif noisy >= 3 or row["duplicate_uin_base_count"] >= 1:
        row["noise_risk"] = "medium"
    else:
        row["noise_risk"] = "low"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--active-manifest",
        default="data/manifests/active_policy_wordings_v1.json",
        help="Path to active policy wording manifest.",
    )
    parser.add_argument(
        "--uin-report",
        default="data/manifests/uin_match_report_v1.json",
        help="Path to UIN match report.",
    )
    parser.add_argument(
        "--bundle-manifest",
        default="data/manifests/product_source_bundles_v1.draft.json",
        help="Path to draft source bundle registry.",
    )
    parser.add_argument(
        "--output",
        default="data/reports/dse026_corpus_availability_analysis.json",
        help="Path to write JSON output.",
    )
    args = parser.parse_args()

    active_manifest = load_json(Path(args.active_manifest))
    uin_report = load_json(Path(args.uin_report))
    bundle_manifest = load_json(Path(args.bundle_manifest))

    active_lookup = build_active_lookup(uin_report["results"])
    summary: Dict[str, Any] = {}
    uin_bases_by_insurer: Dict[str, Counter] = defaultdict(Counter)

    for entry in active_manifest:
        match_row = active_lookup.get(entry["document_id"], {})
        canonical_name = match_row.get("normalized_insurer") or normalize_active_insurer(
            entry.get("insurer", "")
        )
        row = ensure_insurer(summary, canonical_name)
        row["raw_active_document_count"] += 1
        row["active_document_types"][entry["document_type"]] += 1
        row["source_domain_counts"][entry.get("source_domain") or "unknown"] += 1
        row["document_count_with_missing_source_url"] += 1
        if entry["document_type"] == "policy_wording":
            row["active_policy_wording_count"] += 1
        if entry["document_type"] == "brochure":
            row["active_brochure_count"] += 1
        if classify_group_like(
            {
                "uin": entry.get("uin"),
                "filename": entry.get("filename"),
                "lifecycle_product_name": match_row.get("lifecycle_product_name"),
            }
        ):
            row["group_like_document_count"] += 1
        uin_base = match_row.get("uin_base")
        if uin_base:
            uin_bases_by_insurer[canonical_name][uin_base] += 1

    for bundle in bundle_manifest["bundles"]:
        canonical_name = canonicalize_insurer_name(bundle["insurer"])
        row = ensure_insurer(summary, canonical_name)
        row["bundle_count"] += 1
        row["source_quality_counts"][bundle["source_quality"]] += 1
        doc_types = {doc["document_type"] for doc in bundle["documents"]}
        for doc_type in doc_types:
            row["bundle_document_type_counts"][doc_type] += 1
        if "product_benefit_table" in doc_types:
            row["known_pbt_bundle_count"] += 1
        if "cis" in doc_types:
            row["known_cis_bundle_count"] += 1
        if "brochure" in doc_types:
            row["known_brochure_bundle_count"] += 1

    for canonical_name, row in summary.items():
        finalize_bucket(row, uin_bases_by_insurer[canonical_name])

    top15 = sorted(
        summary.values(),
        key=lambda item: (
            item["bundle_count"],
            item["active_policy_wording_count"],
            -item["group_like_document_count"],
        ),
        reverse=True,
    )[:15]

    target_summary = []
    for canonical_name in TARGET_INSURERS:
        row = summary.get(canonical_name)
        if row is None:
            target_summary.append(
                {
                    "insurer": canonical_name,
                    "display_name": map_display_name(canonical_name),
                    "missing_from_local_corpus": True,
                }
            )
        else:
            target_summary.append(row)

    output = {
        "report_type": "dse026_corpus_availability_analysis",
        "task_id": "DSE-026",
        "inputs": {
            "active_manifest": args.active_manifest,
            "uin_report": args.uin_report,
            "bundle_manifest": args.bundle_manifest,
        },
        "target_insurers": target_summary,
        "top_15_by_bundle_count": top15,
        "all_insurers": sorted(summary.values(), key=lambda item: item["insurer"]),
        "local_corpus_limitations": [
            "Active manifest entries do not carry source_url values; source-domain is present but precise official URL provenance is mostly missing.",
            "Draft source bundles are policy-wording heavy and mostly marked missing_pbt.",
            "Local corpus strength should not be confused with MVP desirability; DSE-026 uses separate external market/source research for that.",
        ],
    }

    output_path = Path(args.output)
    output_path.write_text(json.dumps(output, indent=2))
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
