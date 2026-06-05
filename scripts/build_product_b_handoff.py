#!/usr/bin/env python3
"""
Build Product B handoff package — DSE-023.

Copies only compiled Product A exports for reviewed gold policies into a stable
handoff directory. Raw PDFs, SQLite databases, and parser interim outputs are
never copied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import sys
import time
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Tuple

from derived.schema_validator import validate_policy_features

REQUIRED_EXPORT_FILES = (
    "policy_features.json",
    "policy_fact_sources.json",
    "policy_clauses_minimal.json",
)

FORBIDDEN_SUFFIXES = (".sqlite", ".sqlite-wal", ".sqlite-shm", ".db", ".db-wal", ".db-shm", ".pdf")
FORBIDDEN_PATH_PARTS = {"interim", "physical", "logical", "tables", "facts_resolved", "policy_data"}


def load_json(path: pathlib.Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def reviewed_policy_metadata(gold_corpus: pathlib.Path) -> List[Dict[str, Any]]:
    policies_root = gold_corpus / "policies"
    rows: List[Dict[str, Any]] = []
    for metadata_path in sorted(policies_root.glob("*/metadata.json")):
        metadata = load_json(metadata_path)
        if metadata.get("label_status") == "draft":
            continue
        metadata["_slug"] = metadata_path.parent.name
        rows.append(metadata)
    return rows


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_safe_package(path: pathlib.Path) -> None:
    parts = set(path.parts)
    if "data" not in parts or "processed" not in parts:
        raise ValueError(f"Refusing to write handoff outside data/processed: {path}")


def ensure_no_forbidden_files(root: pathlib.Path) -> None:
    violations = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = set(path.relative_to(root).parts)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            violations.append(str(path.relative_to(root)))
        elif rel_parts & FORBIDDEN_PATH_PARTS:
            violations.append(str(path.relative_to(root)))
    if violations:
        raise ValueError(f"Forbidden files in handoff package: {violations}")


def copy_text_file(src: pathlib.Path, dst: pathlib.Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def status_counts(features_doc: Dict[str, Any]) -> Counter:
    c: Counter = Counter()
    for feature in features_doc.get("features", {}).values():
        c[feature.get("fact_status", "missing")] += 1
    return c


def build_coverage_summary(policy_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    aggregate_status_counts: Counter = Counter()
    concept_status_counts: Dict[str, Counter] = defaultdict(Counter)

    for row in policy_rows:
        aggregate_status_counts.update(row["status_counts"])
        for field_name, feature in row["features"].items():
            concept_status_counts[field_name][feature.get("fact_status", "missing")] += 1

    return {
        "schema_version": "product_b_handoff_quality.v1",
        "policy_count": len(policy_rows),
        "aggregate_status_counts": dict(sorted(aggregate_status_counts.items())),
        "concept_status_counts": {
            field: dict(sorted(counter.items()))
            for field, counter in sorted(concept_status_counts.items())
        },
        "fill_rate": {
            row["policy_id"]: row["fill_rate"]
            for row in sorted(policy_rows, key=lambda r: r["policy_id"])
        },
    }


def write_checksums(root: pathlib.Path) -> None:
    checksum_path = root / "checksums.sha256"
    rows: List[Tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == checksum_path:
            continue
        rows.append((sha256_file(path), str(path.relative_to(root))))
    checksum_path.write_text(
        "".join(f"{digest}  {rel}\n" for digest, rel in rows),
        encoding="utf-8",
    )


def build_handoff(
    export_root: pathlib.Path,
    gold_corpus: pathlib.Path,
    output_root: pathlib.Path,
    export_eval: pathlib.Path | None = None,
) -> Dict[str, Any]:
    ensure_safe_package(output_root)

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    metadata_rows = reviewed_policy_metadata(gold_corpus)
    if not metadata_rows:
        raise ValueError(f"No reviewed policies found under {gold_corpus}")

    package_policy_root = output_root / "benchmark_20_reviewed"
    manifest_rows: List[Dict[str, Any]] = []
    quality_rows: List[Dict[str, Any]] = []
    schema_errors: Dict[str, List[str]] = {}

    for metadata in metadata_rows:
        policy_id = metadata["policy_id"]
        src_dir = export_root / policy_id
        dst_dir = package_policy_root / policy_id

        missing = [name for name in REQUIRED_EXPORT_FILES if not (src_dir / name).is_file()]
        if missing:
            raise FileNotFoundError(f"{policy_id} missing export files: {missing}")

        features_doc = load_json(src_dir / "policy_features.json")
        errors = validate_policy_features(features_doc)
        if errors:
            schema_errors[policy_id] = errors
            continue

        for filename in REQUIRED_EXPORT_FILES:
            copy_text_file(src_dir / filename, dst_dir / filename)

        counts = status_counts(features_doc)
        features = features_doc.get("features", {})
        fill_rate = features_doc.get("parse_quality", {}).get("overall_fill_rate")
        manifest_rows.append(
            {
                "policy_id": policy_id,
                "insurer": metadata.get("insurer"),
                "plan_name": metadata.get("plan_name"),
                "uin": metadata.get("uin"),
                "uin_base": metadata.get("uin_base"),
                "file_hash": metadata.get("file_hash"),
                "export_path": f"benchmark_20_reviewed/{policy_id}/policy_features.json",
                "feature_count": len(features),
                "fill_rate": fill_rate,
                "status_counts": dict(sorted(counts.items())),
            }
        )
        quality_rows.append(
            {
                "policy_id": policy_id,
                "fill_rate": fill_rate,
                "status_counts": counts,
                "features": features,
            }
        )

    if schema_errors:
        raise ValueError(f"Schema validation failed: {schema_errors}")

    copy_text_file(pathlib.Path("docs/export_contract.md"), output_root / "export_contract.md")
    copy_text_file(pathlib.Path("ontology/concepts.v1.json"), output_root / "ontology_concepts.v1.json")

    if export_eval and export_eval.is_file():
        copy_text_file(export_eval, output_root / "quality" / "export_eval.json")

    coverage_summary = build_coverage_summary(quality_rows)
    write_json(output_root / "quality" / "coverage_summary.json", coverage_summary)

    manifest = {
        "schema_version": "product_b_handoff_manifest.v1",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_export_root": str(export_root),
        "gold_corpus": str(gold_corpus),
        "policy_count": len(manifest_rows),
        "export_schema_version": "1.0",
        "ontology_version": load_json(pathlib.Path("ontology/concepts.v1.json")).get(
            "ontology_version"
        ),
        "package_scope": "benchmark_20_reviewed",
        "policies": sorted(manifest_rows, key=lambda r: r["policy_id"]),
    }
    write_json(output_root / "manifest.json", manifest)

    readme = """# Product B Export v1 Handoff

This package is produced by Product A (`doc-structure-engine`) for Product B (`insurance-agent`).

Scope:
- reviewed 20-policy benchmark
- 20 ontology-backed priority concepts
- compiled JSON only

Do not treat `not_found` as `not covered`. Product B may display "not covered" only when `fact_status` is `explicitly_not_covered`.

Files:
- `manifest.json` — policy identity, export path, fill rate, and status counts
- `export_contract.md` — Product A → Product B schema contract
- `ontology_concepts.v1.json` — canonical concept registry
- `benchmark_20_reviewed/{policy_id}/` — per-policy compiled exports
- `quality/coverage_summary.json` — aggregate concept/status coverage
- `quality/export_eval.json` — final export eval, when provided
- `checksums.sha256` — package integrity checksums
"""
    (output_root / "README.md").write_text(readme, encoding="utf-8")

    ensure_no_forbidden_files(output_root)
    write_checksums(output_root)
    return manifest


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Product B handoff package — DSE-023")
    parser.add_argument("--export-root", default="data/export")
    parser.add_argument("--gold-corpus", default="gold_corpus")
    parser.add_argument("--output-root", default="data/processed/product_b_export_v1")
    parser.add_argument("--export-eval", default=None)
    args = parser.parse_args(argv)

    try:
        manifest = build_handoff(
            export_root=pathlib.Path(args.export_root),
            gold_corpus=pathlib.Path(args.gold_corpus),
            output_root=pathlib.Path(args.output_root),
            export_eval=pathlib.Path(args.export_eval) if args.export_eval else None,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        f"Built Product B handoff package: {args.output_root} "
        f"({manifest['policy_count']} policies)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
