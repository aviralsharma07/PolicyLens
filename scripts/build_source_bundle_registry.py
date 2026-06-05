#!/usr/bin/env python3
"""Build Product Source Bundle Registry v1 — DSE-025."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from source_bundles.builder import build_registry, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Product Source Bundle Registry v1")
    parser.add_argument("--active-manifest", default="data/manifests/active_policy_wordings_v1.json")
    parser.add_argument("--uin-report", default="data/manifests/uin_match_report_v1.json")
    parser.add_argument(
        "--manual-overrides",
        default="data/manifests/product_source_bundle_manual_overrides_v1.json",
    )
    parser.add_argument("--output", default="data/manifests/product_source_bundles_v1.draft.json")
    args = parser.parse_args()

    registry = build_registry(
        active_manifest=Path(args.active_manifest),
        uin_report=Path(args.uin_report),
        manual_overrides=Path(args.manual_overrides),
    )
    write_json(Path(args.output), registry)
    print(
        "Built source bundle registry: "
        f"{registry['bundle_count']} bundles, "
        f"quality={registry['source_quality_counts']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

