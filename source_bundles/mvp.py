"""Helpers for DSE-027 curated MVP verification and bundle assembly."""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - optional dependency fallback
    PdfReader = None

from source_bundles.builder import product_version_from_uin, slugify, uin_base
from source_bundles.validator import validate_registry


SELECTION_STATUSES = {
    "verified_current",
    "verified_current_with_gap",
    "replaced",
    "unresolved",
    "dropped",
}

SELLABILITY_STATUSES = {"live", "unclear", "not_live"}
REVIEW_CONFIDENCES = {"high", "medium", "low"}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def validation_errors_for_verified_manifest(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    candidates = doc.get("candidates")
    if not isinstance(candidates, list):
        return ["candidates must be a list"]

    by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(candidates):
        prefix = f"candidates[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue
        candidate_id = row.get("candidate_id")
        if not candidate_id:
            errors.append(f"{prefix}.candidate_id is required")
            continue
        if candidate_id in by_id:
            errors.append(f"{prefix}.candidate_id duplicate: {candidate_id}")
        by_id[candidate_id] = row

        if row.get("selection_status") not in SELECTION_STATUSES:
            errors.append(f"{prefix}.selection_status invalid: {row.get('selection_status')!r}")
        if row.get("latest_sellability_status") not in SELLABILITY_STATUSES:
            errors.append(
                f"{prefix}.latest_sellability_status invalid: {row.get('latest_sellability_status')!r}"
            )
        if row.get("review_confidence") not in REVIEW_CONFIDENCES:
            errors.append(f"{prefix}.review_confidence invalid: {row.get('review_confidence')!r}")
        if not row.get("proposed_product_name"):
            errors.append(f"{prefix}.proposed_product_name is required")
        if not row.get("verified_product_name"):
            errors.append(f"{prefix}.verified_product_name is required")
        if not row.get("official_product_page_url"):
            errors.append(f"{prefix}.official_product_page_url is required")

    for candidate_id, row in by_id.items():
        replacement_for = row.get("replacement_for_candidate_id")
        if replacement_for and replacement_for not in by_id:
            errors.append(
                f"candidate {candidate_id} replacement_for_candidate_id missing target: {replacement_for}"
            )
        if replacement_for and row.get("insurer_id") != by_id[replacement_for].get("insurer_id"):
            errors.append(
                f"candidate {candidate_id} replacement crosses insurer boundary: {replacement_for}"
            )

    return errors


def build_verified_candidates(
    candidates_manifest: dict[str, Any],
    manual_doc: dict[str, Any],
) -> dict[str, Any]:
    candidates = candidates_manifest["candidates"]
    manual_rows = {row["candidate_id"]: row for row in manual_doc["candidates"]}
    missing = [row["candidate_id"] for row in candidates if row["candidate_id"] not in manual_rows]
    if missing:
        raise ValueError(f"Manual verification rows missing for candidates: {missing}")

    output_rows: list[dict[str, Any]] = []
    for candidate in candidates:
        manual = manual_rows[candidate["candidate_id"]]
        verified_uin = manual.get("verified_uin", candidate.get("likely_uin"))
        output_rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "insurer_id": candidate["insurer_id"],
                "insurer_display_name": candidate["insurer_display_name"],
                "product_role": candidate["product_role"],
                "collection_priority": candidate["collection_priority"],
                "expected_source_bundle_difficulty": candidate["expected_source_bundle_difficulty"],
                "proposed_product_name": candidate["product_name"],
                "verified_product_name": manual.get("verified_product_name", candidate["product_name"]),
                "selection_status": manual["selection_status"],
                "latest_sellability_status": manual["latest_sellability_status"],
                "verified_uin": verified_uin,
                "verified_uin_base": uin_base(verified_uin),
                "verified_product_version": manual.get("verified_product_version")
                or product_version_from_uin(verified_uin),
                "official_product_page_url": manual.get(
                    "official_product_page_url", candidate["official_reference_url"]
                ),
                "official_wording_url": manual.get("official_wording_url"),
                "official_cis_url": manual.get("official_cis_url"),
                "official_brochure_or_prospectus_url": manual.get(
                    "official_brochure_or_prospectus_url"
                ),
                "official_pbt_or_table_url": manual.get("official_pbt_or_table_url"),
                "irdai_cross_check_status": manual["irdai_cross_check_status"],
                "archive_used": bool(manual.get("archive_used", False)),
                "replacement_for_candidate_id": manual.get("replacement_for_candidate_id"),
                "verification_notes": manual["verification_notes"],
                "review_confidence": manual["review_confidence"],
                "why_it_matters": candidate["why_it_matters"],
                "legacy_aliases": manual.get("legacy_aliases", []),
                "official_reference_url": candidate["official_reference_url"],
            }
        )

    manifest = {
        "schema_version": "mvp_product_candidates_verified.v1",
        "task_id": "DSE-027",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_manifest": candidates_manifest.get("schema_version"),
        "selection_rules": [
            "Current official insurer pages/docs are primary truth.",
            "IRDAI and prior Product A corpus UIN evidence are used as cross-check layers.",
            "Archived or legacy-only evidence cannot upgrade a candidate to complete or latest-current.",
            "Replacement, when needed, must stay within the same insurer.",
        ],
        "candidate_count": len(output_rows),
        "candidates": output_rows,
    }

    errors = validation_errors_for_verified_manifest(manifest)
    if errors:
        raise ValueError("Invalid verified candidate manifest:\n- " + "\n- ".join(errors))
    return manifest


def build_latest_audit(verified_manifest: dict[str, Any]) -> dict[str, Any]:
    status_counts = Counter()
    sellability_counts = Counter()
    insurer_counts: dict[str, Counter[str]] = defaultdict(Counter)
    replacement_rows: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []

    for row in verified_manifest["candidates"]:
        status_counts[row["selection_status"]] += 1
        sellability_counts[row["latest_sellability_status"]] += 1
        insurer_counts[row["insurer_display_name"]][row["selection_status"]] += 1
        if row.get("replacement_for_candidate_id"):
            replacement_rows.append(row)
        if row["selection_status"] != "verified_current":
            gaps.append(
                {
                    "candidate_id": row["candidate_id"],
                    "verified_product_name": row["verified_product_name"],
                    "selection_status": row["selection_status"],
                    "latest_sellability_status": row["latest_sellability_status"],
                    "review_confidence": row["review_confidence"],
                    "verification_notes": row["verification_notes"],
                }
            )

    return {
        "schema_version": "dse027_mvp_candidate_latest_audit.v1",
        "task_id": "DSE-027",
        "generated_at": verified_manifest["generated_at"],
        "candidate_count": verified_manifest["candidate_count"],
        "selection_status_counts": dict(sorted(status_counts.items())),
        "latest_sellability_counts": dict(sorted(sellability_counts.items())),
        "insurer_status_counts": {
            insurer: dict(sorted(counter.items()))
            for insurer, counter in sorted(insurer_counts.items())
        },
        "replacement_rows": replacement_rows,
        "non_clean_rows": gaps,
    }


def render_latest_audit_markdown(
    verified_manifest: dict[str, Any], audit_doc: dict[str, Any]
) -> str:
    lines = [
        "# DSE-027 MVP Candidate Latest Audit v1",
        "",
        f"Date: {verified_manifest['generated_at'][:10]}",
        "Task ID: DSE-027",
        "",
        "## Summary",
        "",
        "- Goal: verify the full 30-product DSE-026 MVP list against current official insurer surfaces before bundle collection.",
        "- Authority order: current official insurer sources first, cross-checked with Product A UIN evidence and IRDAI-linked evidence where available.",
        "- Archived-only evidence is not treated as current.",
        "",
        "## Counts",
        "",
        f"- Candidate count: {audit_doc['candidate_count']}",
        f"- Selection statuses: {audit_doc['selection_status_counts']}",
        f"- Latest sellability: {audit_doc['latest_sellability_counts']}",
        "",
        "## Insurer Breakdown",
        "",
    ]
    for insurer, counts in audit_doc["insurer_status_counts"].items():
        lines.append(f"- {insurer}: {counts}")

    lines.extend(["", "## Notable Adjustments", ""])
    rows = audit_doc["replacement_rows"] or audit_doc["non_clean_rows"]
    if not rows:
        lines.append("- All 30 candidates verified cleanly with no replacements.")
    else:
        for row in rows:
            lines.append(
                f"- `{row['candidate_id']}` -> `{row.get('verified_product_name', '')}`: "
                f"{row['selection_status']} / {row['latest_sellability_status']} / "
                f"{row['review_confidence']}. {row['verification_notes']}"
            )

    lines.extend(["", "## Verified Candidates", ""])
    for row in verified_manifest["candidates"]:
        lines.extend(
            [
                f"### {row['insurer_display_name']} — {row['verified_product_name']}",
                "",
                f"- Candidate ID: `{row['candidate_id']}`",
                f"- Proposed name: `{row['proposed_product_name']}`",
                f"- Selection status: `{row['selection_status']}`",
                f"- Latest sellability: `{row['latest_sellability_status']}`",
                f"- Verified UIN: `{row['verified_uin']}`",
                f"- Official product page: {row['official_product_page_url']}",
                f"- Official wording: {row['official_wording_url'] or 'not identified yet'}",
                f"- Official CIS: {row['official_cis_url'] or 'not identified yet'}",
                f"- Official brochure/prospectus: {row['official_brochure_or_prospectus_url'] or 'not identified yet'}",
                f"- Official PBT/table: {row['official_pbt_or_table_url'] or 'not identified yet'}",
                f"- IRDAI cross-check: `{row['irdai_cross_check_status']}`",
                f"- Confidence: `{row['review_confidence']}`",
                f"- Notes: {row['verification_notes']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _read_download_index(path: Path | None) -> dict[str, dict[str, Any]]:
    if not path or not path.exists():
        return {}
    rows = load_json(path).get("documents", [])
    return {row["source_url"]: row for row in rows if row.get("source_url")}


def _exact_current_match(local_doc: dict[str, Any], verified_row: dict[str, Any]) -> bool:
    verified_uin = verified_row.get("verified_uin")
    local_uin = local_doc.get("uin") or local_doc.get("matched_uin") or local_doc.get("verified_uin")
    if verified_uin and local_uin:
        return verified_uin == local_uin
    base = verified_row.get("verified_uin_base")
    return bool(base and local_uin and uin_base(local_uin) == base)


def build_local_document_candidates(
    active_manifest: list[dict[str, Any]],
    uin_report: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    active_by_id = {row["document_id"]: row for row in active_manifest}
    candidates: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in uin_report.get("results", []):
        document_id = row.get("document_id")
        active = active_by_id.get(document_id)
        if not active:
            continue
        product_name = row.get("lifecycle_product_name")
        if product_name:
            candidates[normalize_text(product_name)].append(
                {
                    **active,
                    "matched_uin": row.get("matched_uin") or row.get("verified_uin"),
                    "uin_base": row.get("uin_base") or uin_base(active.get("uin")),
                    "normalized_insurer": row.get("normalized_insurer"),
                    "lifecycle_product_name": product_name,
                    "plan_match_score": row.get("plan_match_score"),
                }
            )
    return candidates


def _convert_local_doc(local_doc: dict[str, Any], verified_row: dict[str, Any]) -> dict[str, Any]:
    notes = "Imported from reviewed Product A corpus wording/CIS file."
    source_url = None
    if local_doc["document_type"] == "policy_wording" and _exact_current_match(local_doc, verified_row):
        source_url = verified_row.get("official_wording_url")
    elif local_doc["document_type"] == "cis" and _exact_current_match(local_doc, verified_row):
        source_url = verified_row.get("official_cis_url")
    return {
        "document_id": local_doc.get("document_id"),
        "document_type": local_doc.get("document_type") or "unknown",
        "source_url": source_url,
        "source_domain": local_doc.get("source_domain"),
        "source_authority": "official_insurer"
        if local_doc.get("source_domain") == "website"
        else local_doc.get("source_domain"),
        "file_hash": local_doc.get("file_hash"),
        "filename": local_doc.get("filename"),
        "file_path": local_doc.get("file_path"),
        "page_count": local_doc.get("page_count"),
        "uin_match_status": "matched" if _exact_current_match(local_doc, verified_row) else "legacy_version",
        "product_name_match_status": "matched",
        "downloaded_at": None,
        "review_status": "reviewed",
        "notes": notes,
        "local_uin": local_doc.get("uin"),
    }


def _source_identified_doc(
    *,
    document_type: str,
    source_url: str,
    verified_row: dict[str, Any],
    download_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    filename = os.path.basename(source_url.split("?", 1)[0]) or None
    downloaded = download_index.get(source_url)
    document = {
        "document_id": downloaded.get("document_id") if downloaded else None,
        "document_type": document_type,
        "source_url": source_url,
        "source_domain": "insurer_website",
        "source_authority": "official_insurer",
        "file_hash": downloaded.get("file_hash") if downloaded else None,
        "filename": downloaded.get("filename") if downloaded else filename,
        "file_path": downloaded.get("file_path") if downloaded else None,
        "page_count": downloaded.get("page_count") if downloaded else None,
        "uin_match_status": "matched"
        if verified_row.get("verified_uin")
        else "needs_download_verification",
        "product_name_match_status": "matched",
        "downloaded_at": downloaded.get("downloaded_at") if downloaded else None,
        "review_status": "downloaded_unreviewed" if downloaded else "source_identified",
        "notes": "Current official source identified during DSE-027 latest-version verification.",
    }
    return document


def _doc_types_present(documents: list[dict[str, Any]]) -> set[str]:
    return {doc["document_type"] for doc in documents}


def _is_current_doc(document: dict[str, Any]) -> bool:
    return document.get("uin_match_status") == "matched"


def infer_source_quality(
    verified_row: dict[str, Any],
    documents: list[dict[str, Any]],
    override: dict[str, Any] | None = None,
) -> tuple[str, str]:
    if override and override.get("source_quality") and override.get("source_quality_notes"):
        return override["source_quality"], override["source_quality_notes"]

    selection_status = verified_row["selection_status"]
    if selection_status in {"unresolved", "dropped"}:
        return "rejected", "Candidate did not pass latest-version verification for MVP collection."

    types = _doc_types_present(documents)
    current_policy = any(doc["document_type"] == "policy_wording" and _is_current_doc(doc) for doc in documents)
    current_cis = any(doc["document_type"] == "cis" and _is_current_doc(doc) for doc in documents)
    current_pbt = any(
        doc["document_type"] == "product_benefit_table" and _is_current_doc(doc) for doc in documents
    )
    current_policy_surface = any(
        doc["document_type"] == "policy_wording"
        and doc.get("source_url")
        and doc.get("review_status") in {"source_identified", "downloaded_unreviewed", "reviewed"}
        for doc in documents
    )
    current_cis_surface = any(
        doc["document_type"] == "cis"
        and doc.get("source_url")
        and doc.get("review_status") in {"source_identified", "downloaded_unreviewed", "reviewed"}
        for doc in documents
    )
    legacy_policy = any(
        doc["document_type"] == "policy_wording" and doc.get("uin_match_status") == "legacy_version"
        for doc in documents
    )
    any_archive = verified_row.get("archive_used", False)

    if current_policy and current_cis and current_pbt and not any_archive:
        return "complete", "Current official wording, CIS, and Product Benefit Table are all linked."
    if current_policy and current_pbt and not current_cis:
        return "missing_cis", "Current wording and Product Benefit Table are identified, but CIS is still missing."
    if current_policy and current_cis and not current_pbt:
        return (
            "missing_pbt",
            "Current wording and CIS are identified, but Product Benefit Table / table of benefits is still missing.",
        )
    if current_policy_surface and current_cis_surface and not current_pbt:
        return (
            "missing_pbt",
            "Current official wording and CIS URLs are identified, but Product Benefit Table / table of benefits is still missing or not yet downloaded.",
        )
    if current_policy:
        return (
            "acceptable_with_known_gap",
            "Current official policy wording is linked, but one or more supporting product documents are still missing.",
        )
    if current_policy_surface:
        return (
            "acceptable_with_known_gap",
            "Current official policy wording URL is identified, but the downloaded reviewed current wording is not fully locked yet.",
        )
    if legacy_policy and (verified_row.get("official_wording_url") or verified_row.get("official_cis_url")):
        return (
            "stale_version",
            "Current product footprint is verified, but the locally reviewed policy wording is from an older version and current wording still needs download review.",
        )
    if "policy_wording" in types:
        return (
            "acceptable_with_known_gap",
            "A policy wording is available, but current official product-document provenance remains incomplete.",
        )
    return "rejected", "No usable policy wording document is attached to this MVP candidate."


def build_mvp_bundle_registry(
    *,
    verified_manifest: dict[str, Any],
    active_manifest: list[dict[str, Any]],
    uin_report: dict[str, Any],
    bundle_overrides: dict[str, Any] | None = None,
    download_index_path: Path | None = None,
) -> dict[str, Any]:
    overrides_by_candidate = {
        row["candidate_id"]: row for row in (bundle_overrides or {}).get("bundles", [])
    }
    local_candidates = build_local_document_candidates(active_manifest, uin_report)
    download_index = _read_download_index(download_index_path)

    bundles: list[dict[str, Any]] = []
    for verified_row in verified_manifest["candidates"]:
        key = normalize_text(verified_row["verified_product_name"])
        local_rows = list(local_candidates.get(key, []))
        verified_base = verified_row.get("verified_uin_base")
        if verified_base:
            local_rows.extend(
                row
                for rows in local_candidates.values()
                for row in rows
                if (row.get("uin_base") or uin_base(row.get("uin"))) == verified_base
            )

        unique_local = []
        seen_ids = set()
        for row in sorted(local_rows, key=lambda r: (r.get("filename") or "", r.get("document_id") or "")):
            if row["document_id"] not in seen_ids:
                unique_local.append(row)
                seen_ids.add(row["document_id"])

        documents = [_convert_local_doc(row, verified_row) for row in unique_local]
        existing_urls = {doc.get("source_url") for doc in documents if doc.get("source_url")}

        url_fields = [
            ("policy_wording", verified_row.get("official_wording_url")),
            ("cis", verified_row.get("official_cis_url")),
            ("brochure", verified_row.get("official_brochure_or_prospectus_url")),
            ("product_benefit_table", verified_row.get("official_pbt_or_table_url")),
        ]
        for doc_type, source_url in url_fields:
            if source_url and source_url not in existing_urls:
                documents.append(
                    _source_identified_doc(
                        document_type=doc_type,
                        source_url=source_url,
                        verified_row=verified_row,
                        download_index=download_index,
                    )
                )
                existing_urls.add(source_url)

        override = overrides_by_candidate.get(verified_row["candidate_id"], {})
        source_quality, quality_notes = infer_source_quality(verified_row, documents, override)
        bundle = {
            "product_id": verified_row["candidate_id"],
            "insurer": verified_row["insurer_display_name"],
            "product_name": verified_row["verified_product_name"],
            "uin": verified_row.get("verified_uin"),
            "uin_base": verified_row.get("verified_uin_base"),
            "product_version": verified_row.get("verified_product_version"),
            "effective_date": None,
            "variants": override.get("variants", []),
            "source_quality": source_quality,
            "source_quality_notes": quality_notes,
            "documents": documents,
            "official_product_page_url": verified_row["official_product_page_url"],
            "latest_sellability_status": verified_row["latest_sellability_status"],
            "irdai_cross_check_status": verified_row["irdai_cross_check_status"],
            "review_confidence": verified_row["review_confidence"],
            "verification_notes": verified_row["verification_notes"],
            "archive_used": verified_row["archive_used"],
            "replacement_for_candidate_id": verified_row.get("replacement_for_candidate_id"),
        }
        bundles.append(bundle)

    quality_counts = Counter(bundle["source_quality"] for bundle in bundles)
    doc_type_counts = Counter()
    for bundle in bundles:
        for doc in bundle["documents"]:
            doc_type_counts[doc["document_type"]] += 1

    registry = {
        "schema_version": "product_source_bundle.v1",
        "task_id": "DSE-027",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_manifests": [
            "data/manifests/mvp_product_candidates_verified_v1.json",
            "data/manifests/product_source_bundle_mvp_manual_overrides_v1.json",
        ],
        "bundle_count": len(bundles),
        "source_quality_counts": dict(sorted(quality_counts.items())),
        "document_type_counts": dict(sorted(doc_type_counts.items())),
        "known_limitations": [
            "This curated MVP bundle registry mixes current official source URLs with reviewed local corpus files.",
            "source_identified documents still need download and review before they become launch-grade bundle documents.",
            "Archived or legacy-only evidence must not upgrade a bundle to complete.",
        ],
        "bundles": sorted(bundles, key=lambda row: row["product_id"]),
    }

    errors = validate_registry(registry)
    if errors:
        raise ValueError("Invalid MVP bundle registry:\n- " + "\n- ".join(errors))
    return registry


def sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def page_count_for_pdf(path: Path) -> int | None:
    if PdfReader is None:
        return None
    try:
        with path.open("rb") as f:
            return len(PdfReader(f).pages)
    except Exception:
        return None
