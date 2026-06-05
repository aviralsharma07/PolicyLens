#!/usr/bin/env python3
"""Validate Product Source Bundle Registry v1 documents."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from source_bundles.validator import validate_registry_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Product Source Bundle Registry v1")
    parser.add_argument("registry", nargs="?", default="data/manifests/product_source_bundles_v1.draft.json")
    args = parser.parse_args()

    path = Path(args.registry)
    errors = validate_registry_path(path)
    if errors:
        print(f"Source bundle validation failed for {path}:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Source bundle validation passed: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

