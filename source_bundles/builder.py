"""Build draft Product Source Bundle Registry documents."""

from __future__ import annotations

import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from source_bundles.validator import validate_registry


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def slugify(value: str) -> str:
    value = value.lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unknown"


def uin_base(uin: str | None) -> str | None:
    if not uin:
        return None
    if "V" in uin:
        return uin.split("V", 1)[0]
    return uin[:12] if len(uin) >= 12 else uin


def product_version_from_uin(uin: str | None) -> str | None:
    if not uin or "V" not in uin:
        return None
    return "V" + uin.split("V", 1)[1]


def build_uin_lookup(uin_report: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not uin_report:
        return {}
    return {
        row["document_id"]: row
        for row in uin_report.get("results", [])
        if isinstance(row, dict) and row.get("document_id")
    }


def build_document(entry: dict[str, Any], uin_row: dict[str, Any] | None) -> dict[str, Any]:
    product_name_match = "unknown"
    if uin_row:
        score = uin_row.get("plan_match_score")
        if isinstance(score, (int, float)):
            product_name_match = "matched" if score >= 0.65 else "weak_match"
    return {
        "document_id": entry.get("document_id"),
        "document_type": entry.get("document_type") or "unknown",
        "source_url": entry.get("source_url"),
        "source_domain": entry.get("source_domain"),
        "source_authority": entry.get("source_domain"),
        "file_hash": entry.get("file_hash"),
        "filename": entry.get("filename"),
        "file_path": entry.get("file_path"),
        "page_count": entry.get("page_count"),
        "uin_match_status": (uin_row or {}).get("match_status", entry.get("match_status", "unknown")),
        "product_name_match_status": product_name_match,
        "downloaded_at": None,
        "review_status": "machine_imported",
        "notes": "Imported from active policy wording manifest; source_url is absent in current corpus."
        if not entry.get("source_url")
        else "Imported from active policy wording manifest.",
    }


def bundle_key(entry: dict[str, Any], uin_row: dict[str, Any] | None) -> tuple[str, str, str]:
    insurer = (uin_row or {}).get("normalized_insurer") or entry.get("insurer") or "Unknown Insurer"
    product_name = (
        (uin_row or {}).get("lifecycle_product_name")
        or entry.get("plan_name")
        or Path(entry.get("filename", "unknown")).stem
    )
    base = (uin_row or {}).get("uin_base") or uin_base(entry.get("uin")) or entry.get("document_id")
    return insurer, product_name, base


def initial_source_quality(doc_types: set[str]) -> tuple[str, str]:
    if "policy_wording" not in doc_types:
        return "rejected", "No policy wording document is present in the current bundle."
    if "product_benefit_table" not in doc_types:
        return (
            "missing_pbt",
            "Policy wording is present, but no Product Benefit Table / table of benefits "
            "is linked yet. Variant-specific comparison values are not recommendation-ready.",
        )
    if "cis" not in doc_types:
        return "missing_cis", "Policy wording and PBT are present, but CIS is not linked yet."
    return "complete", "Policy wording, Product Benefit Table, and CIS are linked."


def build_bundles_from_active_manifest(
    active_manifest: list[dict[str, Any]],
    uin_report: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    uin_lookup = build_uin_lookup(uin_report)
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)

    for entry in active_manifest:
        uin_row = uin_lookup.get(entry.get("document_id"))
        grouped[bundle_key(entry, uin_row)].append(entry)

    bundles: list[dict[str, Any]] = []
    for (insurer, product_name, base), entries in sorted(grouped.items()):
        documents = [
            build_document(entry, uin_lookup.get(entry.get("document_id")))
            for entry in sorted(entries, key=lambda e: (e.get("file_path") or "", e.get("filename") or ""))
        ]
        doc_types = {doc["document_type"] for doc in documents}
        source_quality, notes = initial_source_quality(doc_types)
        representative = entries[0]
        product_id = slugify(f"{insurer}_{product_name}_{base}")
        bundles.append(
            {
                "product_id": product_id,
                "insurer": insurer,
                "product_name": product_name,
                "uin": representative.get("uin"),
                "uin_base": base,
                "product_version": product_version_from_uin(representative.get("uin")),
                "effective_date": None,
                "variants": [],
                "source_quality": source_quality,
                "source_quality_notes": notes,
                "documents": documents,
            }
        )
    return bundles


def apply_manual_overrides(
    bundles: list[dict[str, Any]],
    manual_overrides: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not manual_overrides:
        return bundles

    by_product_id = {bundle["product_id"]: bundle for bundle in bundles}
    by_uin_base = {bundle.get("uin_base"): bundle for bundle in bundles if bundle.get("uin_base")}

    for override in manual_overrides.get("bundles", []):
        match = override.get("match", {})
        bundle = None
        if override.get("product_id") in by_product_id:
            bundle = by_product_id[override["product_id"]]
        elif match.get("uin_base") in by_uin_base:
            bundle = by_uin_base[match["uin_base"]]

        if bundle is None:
            bundle = {
                "product_id": override["product_id"],
                "insurer": override["insurer"],
                "product_name": override["product_name"],
                "uin": override.get("uin"),
                "uin_base": override.get("uin_base") or match.get("uin_base"),
                "product_version": product_version_from_uin(override.get("uin")),
                "effective_date": override.get("effective_date"),
                "variants": [],
                "source_quality": "missing_pbt",
                "source_quality_notes": "Created from manual override.",
                "documents": [],
            }
            bundles.append(bundle)

        if override.get("product_id"):
            old_id = bundle["product_id"]
            bundle["product_id"] = override["product_id"]
            by_product_id.pop(old_id, None)
            by_product_id[bundle["product_id"]] = bundle
        for field in ["insurer", "product_name", "uin", "uin_base", "product_version", "effective_date"]:
            if field in override:
                bundle[field] = override[field]
        if "variants" in override:
            bundle["variants"] = sorted(set(bundle.get("variants", [])) | set(override["variants"]))
        if "source_quality" in override:
            bundle["source_quality"] = override["source_quality"]
        if "source_quality_notes" in override:
            bundle["source_quality_notes"] = override["source_quality_notes"]

        existing_keys = {
            (
                doc.get("document_type"),
                doc.get("source_url"),
                doc.get("file_hash"),
                doc.get("file_path"),
            )
            for doc in bundle["documents"]
        }
        for document in override.get("documents", []):
            key = (
                document.get("document_type"),
                document.get("source_url"),
                document.get("file_hash"),
                document.get("file_path"),
            )
            if key not in existing_keys:
                bundle["documents"].append(document)
                existing_keys.add(key)

    return sorted(bundles, key=lambda b: b["product_id"])


def build_registry(
    active_manifest: Path,
    uin_report: Path | None = None,
    manual_overrides: Path | None = None,
) -> dict[str, Any]:
    active_rows = load_json(active_manifest)
    uin_doc = load_json(uin_report) if uin_report and uin_report.exists() else None
    manual_doc = (
        load_json(manual_overrides)
        if manual_overrides and manual_overrides.exists()
        else None
    )

    bundles = build_bundles_from_active_manifest(active_rows, uin_doc)
    bundles = apply_manual_overrides(bundles, manual_doc)

    quality_counts: Counter[str] = Counter()
    doc_type_counts: Counter[str] = Counter()
    for bundle in bundles:
        quality_counts[bundle["source_quality"]] += 1
        for document in bundle["documents"]:
            doc_type_counts[document["document_type"]] += 1

    registry = {
        "schema_version": "product_source_bundle.v1",
        "task_id": "DSE-025",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_manifests": [
            str(active_manifest),
            str(uin_report) if uin_report else None,
            str(manual_overrides) if manual_overrides else None,
        ],
        "bundle_count": len(bundles),
        "source_quality_counts": dict(sorted(quality_counts.items())),
        "document_type_counts": dict(sorted(doc_type_counts.items())),
        "known_limitations": [
            "Current active manifest has no source_url values.",
            "Most bundles only contain policy wording PDFs and are missing PBT/CIS documents.",
            "source_identified documents record official URLs but must be downloaded and hashed before launch use.",
            "Draft grouping uses UIN base, normalized insurer, and lifecycle product name where available.",
        ],
        "bundles": bundles,
    }
    errors = validate_registry(registry)
    if errors:
        raise ValueError("Built invalid source bundle registry:\n" + "\n".join(errors[:50]))
    return registry

