#!/usr/bin/env python3
"""Build the DSE-020 647-policy scale-run manifest.

The DSE-020 manifest must be collision-safe because slugs become output
directory names, resume keys, SQLite policy IDs, and export folders.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


EXPECTED_ACTIVE_COUNT = 647


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", value)
    text = re.sub(r"_+", "_", text).strip("_").lower()
    return text or "policy"


def generated_slug_base(entry: Dict[str, Any]) -> str:
    path = Path(entry["file_path"])
    return slugify(f"{path.parent.name}_{path.stem}")


def load_gold_hash_map(gold_corpus: Path) -> Dict[str, str]:
    """Return lookup keys for reviewed gold policies.

    Exact source paths are preferred over file hashes. The active corpus can
    contain duplicate files with the same hash, and assigning all of them the
    same reviewed-gold slug would poison DSE-020 output directories.
    """
    mapping: Dict[str, str] = {}
    policies_root = gold_corpus / "policies"
    if not policies_root.is_dir():
        return mapping

    for metadata_path in sorted(policies_root.glob("*/metadata.json")):
        metadata = _read_json(metadata_path)
        slug = metadata_path.parent.name
        source_pdf_path = metadata.get("source_pdf_path")
        if source_pdf_path:
            mapping[f"path:{source_pdf_path}"] = slug
            continue
        for key in ("file_hash", "document_id"):
            value = metadata.get(key)
            if value:
                mapping[f"hash:{value}"] = slug
    return mapping


def build_manifest_entries(
    active_entries: Iterable[Dict[str, Any]], gold_hash_map: Dict[str, str]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Build collision-safe manifest entries and collision report."""
    draft_entries: List[Dict[str, Any]] = []
    bases: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for entry in active_entries:
        file_hash = entry.get("file_hash") or entry.get("document_id")
        gold_slug = (
            gold_hash_map.get(f"path:{entry.get('file_path')}")
            or gold_hash_map.get(f"hash:{file_hash}")
            # Backward-compatible direct key lookup for focused unit tests.
            or gold_hash_map.get(file_hash or "")
        )
        slug_base = generated_slug_base(entry)
        is_reviewed_gold = bool(gold_slug)
        draft = {
            "slug": gold_slug or slug_base,
            "slug_base": slug_base,
            "document_id": entry.get("document_id") or file_hash,
            "file_hash": file_hash,
            "file_path": entry.get("file_path"),
            "filename": entry.get("filename") or Path(entry.get("file_path", "")).name,
            "insurer": entry.get("insurer"),
            "uin": entry.get("uin"),
            "page_count": entry.get("page_count"),
            "source_domain": entry.get("source_domain"),
            "document_type": entry.get("document_type"),
            "corpus_status": entry.get("corpus_status"),
            "match_status": entry.get("match_status"),
            "triage_flags": entry.get("triage_flags", []),
            "is_reviewed_gold": is_reviewed_gold,
            "gold_slug": gold_slug,
            "skip_reason": None,
        }
        bases[draft["slug"]].append(draft)
        draft_entries.append(draft)

    collisions: List[Dict[str, Any]] = []
    for base_slug, entries in bases.items():
        if len(entries) <= 1:
            continue
        collisions.append(
            {
                "slug": base_slug,
                "count": len(entries),
                "file_paths": [entry["file_path"] for entry in entries],
            }
        )
        for entry in entries:
            if entry.get("is_reviewed_gold"):
                continue
            digest = str(entry.get("file_hash") or entry.get("document_id") or "")
            suffix = re.sub(r"^sha256:", "", digest)[:8]
            if not suffix:
                suffix = slugify(entry["filename"])[:8] or "unknown"
            entry["slug"] = f"{entry['slug']}_{suffix}"

    final_slugs = [entry["slug"] for entry in draft_entries]
    duplicate_final = sorted(
        slug for slug, count in defaultdict(int, ((slug, final_slugs.count(slug)) for slug in final_slugs)).items() if count > 1
    )
    if duplicate_final:
        raise ValueError(f"Final slug collision(s): {duplicate_final}")

    return draft_entries, collisions


def build_manifest(active_manifest: Path, gold_corpus: Path, policy_data_root: Path) -> Dict[str, Any]:
    active_entries = _read_json(active_manifest)
    if not isinstance(active_entries, list):
        raise ValueError(f"{active_manifest} must contain a JSON list")

    gold_hash_map = load_gold_hash_map(gold_corpus)
    entries, collisions = build_manifest_entries(active_entries, gold_hash_map)

    missing_files = []
    for entry in entries:
        file_path = entry.get("file_path")
        if not file_path:
            entry["skip_reason"] = "missing_file_path"
            missing_files.append(entry["slug"])
            continue
        absolute_pdf = policy_data_root / file_path
        if not absolute_pdf.is_file():
            entry["skip_reason"] = "pdf_not_found"
            missing_files.append(entry["slug"])

    return {
        "schema_version": "dse020_run_manifest.v1",
        "task_id": "DSE-020",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "active_manifest": str(active_manifest),
        "gold_corpus": str(gold_corpus),
        "policy_data_root": str(policy_data_root),
        "expected_policy_count": EXPECTED_ACTIVE_COUNT,
        "policy_count": len(entries),
        "unique_slug_count": len({entry["slug"] for entry in entries}),
        "reviewed_gold_mapped_count": sum(1 for entry in entries if entry["is_reviewed_gold"]),
        "missing_file_count": len(missing_files),
        "collision_groups": collisions,
        "policies": entries,
    }


def validate_manifest(manifest: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    policies = manifest.get("policies", [])
    slugs = [entry.get("slug") for entry in policies]
    if manifest.get("policy_count") != EXPECTED_ACTIVE_COUNT:
        issues.append(f"policy_count={manifest.get('policy_count')} expected={EXPECTED_ACTIVE_COUNT}")
    if len(slugs) != len(set(slugs)):
        issues.append("final slugs are not unique")
    if manifest.get("unique_slug_count") != len(set(slugs)):
        issues.append("unique_slug_count does not match actual unique slugs")
    for entry in policies:
        for field in ("slug", "document_id", "file_hash", "file_path", "filename"):
            if not entry.get(field):
                issues.append(f"{entry.get('slug') or '<unknown>'}: missing {field}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Build DSE-020 scale-run manifest")
    parser.add_argument("--active-manifest", type=Path, required=True)
    parser.add_argument("--gold-corpus", type=Path, default=Path("gold_corpus"))
    parser.add_argument("--policy-data-root", type=Path, default=Path("../policy_data"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = build_manifest(args.active_manifest, args.gold_corpus, args.policy_data_root)
    issues = validate_manifest(manifest)
    if issues:
        print("ERROR: DSE-020 manifest validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1

    _write_json(args.output, manifest)
    print(
        "DSE-020 manifest written: "
        f"{args.output} | policies={manifest['policy_count']} | "
        f"unique_slugs={manifest['unique_slug_count']} | "
        f"gold_mapped={manifest['reviewed_gold_mapped_count']} | "
        f"missing_files={manifest['missing_file_count']} | "
        f"collision_groups={len(manifest['collision_groups'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
