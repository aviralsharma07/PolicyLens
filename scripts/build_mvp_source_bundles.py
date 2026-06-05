"""Build curated DSE-027 MVP source-bundle registry."""

from __future__ import annotations

import argparse
from pathlib import Path

from source_bundles.mvp import build_mvp_bundle_registry, load_json, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verified-candidates",
        default="data/manifests/mvp_product_candidates_verified_v1.json",
    )
    parser.add_argument(
        "--active-manifest",
        default="data/manifests/active_policy_wordings_v1.json",
    )
    parser.add_argument(
        "--uin-report",
        default="data/manifests/uin_match_report_v1.json",
    )
    parser.add_argument(
        "--bundle-overrides",
        default="data/manifests/product_source_bundle_mvp_manual_overrides_v1.json",
    )
    parser.add_argument(
        "--download-index",
        default="data/reports/dse027_source_download_index_v1.json",
        help="Optional downloaded-source index. Missing path is allowed.",
    )
    parser.add_argument(
        "--output",
        default="data/manifests/product_source_bundles_mvp_v1.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    verified_manifest = load_json(Path(args.verified_candidates))
    active_manifest = load_json(Path(args.active_manifest))
    uin_report = load_json(Path(args.uin_report))
    bundle_override_path = Path(args.bundle_overrides)
    bundle_overrides = load_json(bundle_override_path) if bundle_override_path.exists() else None
    download_index_path = Path(args.download_index)
    registry = build_mvp_bundle_registry(
        verified_manifest=verified_manifest,
        active_manifest=active_manifest,
        uin_report=uin_report,
        bundle_overrides=bundle_overrides,
        download_index_path=download_index_path if download_index_path.exists() else None,
    )
    write_json(Path(args.output), registry)


if __name__ == "__main__":
    main()
