import csv
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

from identity.insurer_normalizer import (
    get_abbreviations,
    normalize as normalize_insurer,
    validate_all_mappings,
)
from identity.plan_name_normalizer import (
    best_match_score,
    extract_plan_name,
    is_sufficient,
)

logger = logging.getLogger(__name__)

MATCH_STATUS_VERIFIED = "verified"
MATCH_STATUS_CONFLICT = "conflict"
MATCH_STATUS_SPECIAL = "special_case"
MATCH_STATUS_UNMATCHED = "unmatched"


def extract_uin_base(full_uin: str) -> str:
    idx = full_uin.rfind("V")
    if idx == -1:
        return full_uin
    return full_uin[:idx]


def match_entries(
    active_entries: List[Dict[str, Any]],
    lifecycle_products: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    results = []
    matched_count = 0
    conflict_count = 0
    special_count = 0
    plan_matched_count = 0

    for entry in active_entries:
        doc_id = entry["document_id"]
        filename = entry["filename"]
        folder_insurer = entry["insurer"]
        full_uin = entry.get("uin", "")
        triage_flags = list(entry.get("triage_flags", []))

        uin_base = extract_uin_base(full_uin)
        lifecycle_product = lifecycle_products.get(uin_base)

        score = 0.0
        verification_notes = ""
        match_status = ""
        match_confidence = ""

        if lifecycle_product is None:
            results.append(
                {
                    "document_id": doc_id,
                    "filename": filename,
                    "folder_insurer": folder_insurer,
                    "uin": full_uin,
                    "uin_base": uin_base,
                    "lifecycle_insurer": None,
                    "lifecycle_product_name": None,
                    "lifecycle_product_type": None,
                    "normalized_insurer": normalize_insurer(folder_insurer),
                    "match_status": MATCH_STATUS_UNMATCHED,
                    "match_confidence": "none",
                    "plan_match_score": None,
                    "verification_notes": "UIN base not found in lifecycle data",
                    "triage_flags": triage_flags,
                }
            )
            continue

        lc_insurer = lifecycle_product["insurer"]
        lc_product_name = lifecycle_product["product_name"]
        lc_product_type = lifecycle_product["product_type"]
        normalized_folder_insurer = normalize_insurer(folder_insurer)

        insurer_match = (
            normalized_folder_insurer == lc_insurer if normalized_folder_insurer else False
        )

        if folder_insurer == "non_policy_wordings":
            match_status = MATCH_STATUS_SPECIAL
            match_confidence = "low"
            verification_notes = (
                f"Document in _non_policy_wordings folder; "
                f"UIN belongs to {lc_insurer}/{lc_product_name}"
            )
            special_count += 1
        elif insurer_match:
            prefixes = get_abbreviations(folder_insurer)
            extracted = extract_plan_name(filename, prefixes)
            if is_sufficient(extracted):
                score = best_match_score(extracted, [lc_product_name])

            if score >= 0.5:
                match_status = MATCH_STATUS_VERIFIED
                match_confidence = "high"
                plan_matched_count += 1
                verification_notes = (
                    f"Insurer UIN match confirmed; plan name similarity={score:.2f}"
                )
            else:
                match_status = MATCH_STATUS_VERIFIED
                match_confidence = "medium"
                verification_notes = (
                    f"Insurer UIN match confirmed; plan name similarity={score:.2f}"
                )
            matched_count += 1
        else:
            match_status = MATCH_STATUS_CONFLICT
            match_confidence = "low"
            verification_notes = (
                f"Folder insurer '{folder_insurer}' "
                f"(normalized: {normalized_folder_insurer}) "
                f"does not match lifecycle insurer '{lc_insurer}' for UIN {full_uin}"
            )
            triage_flags.append("insurer_mismatch")
            conflict_count += 1

        results.append(
            {
                "document_id": doc_id,
                "filename": filename,
                "folder_insurer": folder_insurer,
                "uin": full_uin,
                "uin_base": uin_base,
                "lifecycle_insurer": lc_insurer,
                "lifecycle_product_name": lc_product_name,
                "lifecycle_product_type": lc_product_type,
                "normalized_insurer": normalized_folder_insurer,
                "match_status": match_status,
                "match_confidence": match_confidence,
                "plan_match_score": round(score, 4),
                "verification_notes": verification_notes,
                "triage_flags": triage_flags,
            }
        )

    total = len(active_entries)
    unmatched = sum(1 for r in results if r["match_status"] == MATCH_STATUS_UNMATCHED)
    summary = {
        "total_entries": total,
        "verified": matched_count,
        "conflict": conflict_count,
        "special_case": special_count,
        "unmatched": unmatched,
        "plan_name_matched": plan_matched_count,
        "verified_pct": round(matched_count / total * 100, 1) if total else 0.0,
        "verified_or_special_pct": round((matched_count + special_count) / total * 100, 1)
        if total
        else 0.0,
    }
    return results, summary


def generate_report(
    active_path: str,
    lifecycle_path: str,
    output_path: str,
    triage_output_path: str,
) -> Dict[str, Any]:
    with open(active_path) as f:
        active_entries = json.load(f)
    with open(lifecycle_path) as f:
        lifecycle_data = json.load(f)

    lifecycle_products = lifecycle_data.get("products", {})
    mapping_check = validate_all_mappings(active_entries)

    results, summary = match_entries(active_entries, lifecycle_products)

    report = {
        "report_type": "uin_match_report",
        "generated_at": datetime.now().isoformat(),
        "source_active_manifest": active_path,
        "source_lifecycle": lifecycle_path,
        "summary": summary,
        "insurer_mapping_coverage": {fi: info for fi, info in mapping_check.items()},
        "results": results,
    }

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    triage_entries = [
        r
        for r in results
        if r["match_status"]
        in (MATCH_STATUS_CONFLICT, MATCH_STATUS_UNMATCHED, MATCH_STATUS_SPECIAL)
        or r.get("triage_flags")
    ]

    if triage_entries:
        fieldnames = [
            "document_id",
            "filename",
            "folder_insurer",
            "uin",
            "uin_base",
            "lifecycle_insurer",
            "lifecycle_product_name",
            "match_status",
            "match_confidence",
            "verification_notes",
            "triage_flags",
        ]
        with open(triage_output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for te in triage_entries:
                row = {k: te.get(k, "") for k in fieldnames}
                if isinstance(row.get("triage_flags"), list):
                    row["triage_flags"] = "; ".join(row["triage_flags"])
                writer.writerow(row)
    else:
        with open(triage_output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["No triage entries found"])

    return report
