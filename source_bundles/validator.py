"""Validation for Product Source Bundle Registry v1."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "product_source_bundle.v1"

DOCUMENT_TYPES = {
    "policy_wording",
    "product_benefit_table",
    "cis",
    "brochure",
    "prospectus",
    "rider",
    "premium_table",
    "proposal_form",
    "endorsement",
    "unknown",
}

SOURCE_QUALITIES = {
    "complete",
    "acceptable_with_known_gap",
    "missing_pbt",
    "missing_cis",
    "missing_brochure",
    "uin_mismatch",
    "variant_unclear",
    "stale_version",
    "rejected",
}

REVIEW_STATUSES = {
    "machine_imported",
    "source_identified",
    "downloaded_unreviewed",
    "reviewed",
    "rejected",
}

REQUIRED_BUNDLE_FIELDS = {
    "product_id",
    "insurer",
    "product_name",
    "uin",
    "uin_base",
    "documents",
    "variants",
    "source_quality",
    "source_quality_notes",
}

REQUIRED_DOCUMENT_FIELDS = {
    "document_type",
    "source_domain",
    "source_url",
    "file_hash",
    "filename",
    "file_path",
    "page_count",
    "uin_match_status",
    "product_name_match_status",
    "review_status",
}

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
PRODUCT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_]*[a-z0-9]$")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_registry(registry: dict[str, Any]) -> list[str]:
    """Return validation errors for a Product Source Bundle Registry document."""

    errors: list[str] = []
    if registry.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    bundles = registry.get("bundles")
    if not isinstance(bundles, list):
        return errors + ["bundles must be a list"]

    if registry.get("bundle_count") != len(bundles):
        errors.append("bundle_count must equal len(bundles)")

    product_ids: set[str] = set()
    quality_counts: Counter[str] = Counter()
    doc_type_counts: Counter[str] = Counter()

    for index, bundle in enumerate(bundles):
        prefix = f"bundles[{index}]"
        if not isinstance(bundle, dict):
            errors.append(f"{prefix} must be an object")
            continue

        missing = sorted(REQUIRED_BUNDLE_FIELDS - set(bundle))
        if missing:
            errors.append(f"{prefix} missing required fields: {missing}")
            continue

        product_id = bundle.get("product_id")
        if not isinstance(product_id, str) or not PRODUCT_ID_RE.match(product_id):
            errors.append(f"{prefix}.product_id invalid: {product_id!r}")
        elif product_id in product_ids:
            errors.append(f"{prefix}.product_id duplicate: {product_id}")
        else:
            product_ids.add(product_id)

        if not bundle.get("insurer"):
            errors.append(f"{prefix}.insurer is required")
        if not bundle.get("product_name"):
            errors.append(f"{prefix}.product_name is required")

        source_quality = bundle.get("source_quality")
        if source_quality not in SOURCE_QUALITIES:
            errors.append(f"{prefix}.source_quality invalid: {source_quality!r}")
        else:
            quality_counts[source_quality] += 1

        variants = bundle.get("variants")
        if not isinstance(variants, list) or any(not isinstance(v, str) for v in variants):
            errors.append(f"{prefix}.variants must be a list of strings")

        documents = bundle.get("documents")
        if not isinstance(documents, list) or not documents:
            errors.append(f"{prefix}.documents must be a non-empty list")
            continue

        types_in_bundle = set()
        for doc_index, document in enumerate(documents):
            doc_prefix = f"{prefix}.documents[{doc_index}]"
            errors.extend(validate_document(document, doc_prefix))
            if isinstance(document, dict):
                doc_type = document.get("document_type")
                if doc_type in DOCUMENT_TYPES:
                    types_in_bundle.add(doc_type)
                    doc_type_counts[doc_type] += 1
        if source_quality == "complete":
            required_types = {"policy_wording", "product_benefit_table", "cis"}
            missing_types = sorted(required_types - types_in_bundle)
            if missing_types:
                errors.append(f"{prefix}.source_quality complete missing docs: {missing_types}")
        if source_quality == "missing_pbt" and "product_benefit_table" in types_in_bundle:
            errors.append(f"{prefix}.source_quality missing_pbt but PBT document exists")
        if source_quality == "missing_cis" and "cis" in types_in_bundle:
            errors.append(f"{prefix}.source_quality missing_cis but CIS document exists")

    if "source_quality_counts" in registry:
        expected = dict(sorted(quality_counts.items()))
        if registry["source_quality_counts"] != expected:
            errors.append("source_quality_counts does not match bundles")
    if "document_type_counts" in registry:
        expected = dict(sorted(doc_type_counts.items()))
        if registry["document_type_counts"] != expected:
            errors.append("document_type_counts does not match bundles")

    return errors


def validate_document(document: Any, prefix: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return [f"{prefix} must be an object"]

    missing = sorted(REQUIRED_DOCUMENT_FIELDS - set(document))
    if missing:
        errors.append(f"{prefix} missing required fields: {missing}")
        return errors

    doc_type = document.get("document_type")
    if doc_type not in DOCUMENT_TYPES:
        errors.append(f"{prefix}.document_type invalid: {doc_type!r}")

    review_status = document.get("review_status")
    if review_status not in REVIEW_STATUSES:
        errors.append(f"{prefix}.review_status invalid: {review_status!r}")

    document_id = document.get("document_id")
    if document_id is not None and (
        not isinstance(document_id, str) or not SHA256_RE.match(document_id)
    ):
        errors.append(f"{prefix}.document_id must be sha256:<64 hex> or null")

    file_hash = document.get("file_hash")
    if file_hash is not None and (not isinstance(file_hash, str) or not SHA256_RE.match(file_hash)):
        errors.append(f"{prefix}.file_hash must be sha256:<64 hex> or null")

    source_url = document.get("source_url")
    if source_url is not None and (not isinstance(source_url, str) or not URL_RE.match(source_url)):
        errors.append(f"{prefix}.source_url must be http(s) URL or null")

    page_count = document.get("page_count")
    if page_count is not None and (
        not isinstance(page_count, int) or isinstance(page_count, bool) or page_count < 1
    ):
        errors.append(f"{prefix}.page_count must be positive integer or null")

    if review_status in {"reviewed", "downloaded_unreviewed", "machine_imported"}:
        if not file_hash:
            errors.append(f"{prefix}.file_hash required when review_status={review_status}")
        if not document.get("filename"):
            errors.append(f"{prefix}.filename required when review_status={review_status}")

    if review_status == "source_identified":
        if not source_url:
            errors.append(f"{prefix}.source_url required when review_status=source_identified")
        if file_hash is not None:
            errors.append(f"{prefix}.file_hash must be null until source_identified doc is downloaded")

    return errors


def validate_registry_path(path: Path) -> list[str]:
    return validate_registry(load_json(path))
