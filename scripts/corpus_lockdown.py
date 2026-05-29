import csv
import hashlib
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("corpus_lockdown")

POLICY_INDEX = Path("/Users/aviralsharma/Personal Projects/insurance-agent/data/policy_index.json")
CLASSIFICATION_REPORT = Path(
    "/Users/aviralsharma/Personal Projects/insurance-agent/data/classification_report.json"
)
POLICY_DATA_BASE = Path("/Users/aviralsharma/Personal Projects/policy_data")
OUTPUT_DIR = Path("data/manifests")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def classify_entry(entry: dict) -> tuple:
    category = entry["category"]
    status = entry.get("status")
    document_type = category.replace("_", " ")
    document_type = {"policy_wording": "policy_wording", "non_health": "non_health"}.get(
        category, category
    )

    if status == "active":
        corpus_status = "active"
        exclusion_reason = None
        triage_flags = []
        if category == "brochure":
            triage_flags.append("document_type_brochure")
        return corpus_status, exclusion_reason, triage_flags

    if category == "policy_wording" and status is None:
        corpus_status = "needs_review"
        exclusion_reason = None
        triage_flags = ["status_unset"]
        return corpus_status, exclusion_reason, triage_flags

    corpus_status = "excluded"
    triage_flags = []

    if category == "corrupt":
        exclusion_reason = "file_corrupt"
    elif category == "brochure":
        exclusion_reason = "category_not_policy_wording"
        triage_flags.append("document_type_brochure")
    elif category == "circular":
        exclusion_reason = "category_not_policy_wording"
    elif category == "non_health":
        exclusion_reason = "category_not_policy_wording"
    elif category == "reference_data":
        exclusion_reason = "category_not_policy_wording"
    elif status == "superseded":
        exclusion_reason = "policy_superseded"
    else:
        exclusion_reason = "unclassified"

    return corpus_status, exclusion_reason, triage_flags


def build_entry(
    entry: dict,
    corpus_status: str,
    exclusion_reason,
    triage_flags: list,
    file_hash=None,
) -> dict:
    path_raw = entry.get("path", f"{entry['folder']}/{entry['filename']}")
    return {
        "document_id": file_hash or f"pending_hash:{entry['filename']}",
        "filename": entry["filename"],
        "file_path": path_raw,
        "file_hash": file_hash,
        "size_bytes": entry.get("size_bytes"),
        "page_count": entry.get("pages"),
        "document_type": entry["category"],
        "corpus_status": corpus_status,
        "exclusion_reason": exclusion_reason,
        "insurer": entry["folder"].split("_", 1)[1] if "_" in entry["folder"] else entry["folder"],
        "source_domain": entry.get("source"),
        "uin": entry.get("uin") or None,
        "match_status": "pending" if corpus_status == "active" else None,
        "triage_flags": triage_flags,
    }


def main():
    logger.info("Reading policy index...")
    with open(POLICY_INDEX) as f:
        records = json.load(f)
    logger.info("Loaded %d records", len(records))

    logger.info("Reading classification report for validation...")
    with open(CLASSIFICATION_REPORT) as f:
        class_report = json.load(f)
    logger.info(
        "Classification report: %d total, %d active, %d policy_wording",
        class_report["total_files"],
        class_report["statuses"]["active"],
        class_report["categories"]["policy_wording"],
    )

    active = []
    needs_review = []
    excluded = []
    issues = []

    for entry in records:
        corpus_status, exclusion_reason, triage_flags = classify_entry(entry)

        if corpus_status == "active":
            pdf_path = POLICY_DATA_BASE / entry["folder"] / entry["filename"]
            if not pdf_path.exists():
                issues.append(
                    {
                        "filename": entry["filename"],
                        "issue_type": "file_not_found",
                        "description": f"PDF not found at {pdf_path}",
                    }
                )
                file_hash = None
            else:
                try:
                    file_hash = sha256_file(pdf_path)
                except Exception as e:
                    issues.append(
                        {
                            "filename": entry["filename"],
                            "issue_type": "hash_failed",
                            "description": str(e),
                        }
                    )
                    file_hash = None
            result = build_entry(
                entry, corpus_status, exclusion_reason, triage_flags, file_hash=file_hash
            )
            result["is_canonical"] = entry.get("is_canonical", False)
            active.append(result)

        elif corpus_status == "needs_review":
            result = build_entry(entry, corpus_status, exclusion_reason, triage_flags)
            needs_review.append(result)

        else:
            result = build_entry(entry, corpus_status, exclusion_reason, triage_flags)
            excluded.append(result)

    logger.info("Classification results:")
    logger.info("  ACTIVE:       %d", len(active))
    logger.info("  NEEDS_REVIEW: %d", len(needs_review))
    logger.info("  EXCLUDED:     %d", len(excluded))
    logger.info("  TOTAL:        %d", len(active) + len(needs_review) + len(excluded))

    total = len(active) + len(needs_review) + len(excluded)
    if total != len(records):
        logger.error(
            "INVARIANT FAILURE: %d + %d + %d = %d != %d",
            len(active),
            len(needs_review),
            len(excluded),
            total,
            len(records),
        )
        sys.exit(1)
    logger.info("Invariant passed: all %d records accounted for", total)

    hash_to_entries = {}
    for e in active:
        h = e.get("file_hash")
        if h:
            hash_to_entries.setdefault(h, []).append(e)

    dup_groups = {h: entries for h, entries in hash_to_entries.items() if len(entries) > 1}
    if dup_groups:
        logger.info("Duplicate content groups found: %d", len(dup_groups))
        for h, entries in sorted(dup_groups.items()):
            canonical = [e for e in entries if e.get("is_canonical")]
            non_canonical = [e for e in entries if not e.get("is_canonical")]
            for e in non_canonical:
                e["triage_flags"].append("possible_duplicate")
            logger.info(
                "  hash=%s... canon=%d non_canon=%d files=%s",
                h[:12],
                len(canonical),
                len(non_canonical),
                [e["filename"] for e in entries],
            )
        dup_flagged = sum(1 for e in active if "possible_duplicate" in e["triage_flags"])
        logger.info("Flagged %d entries with possible_duplicate triage flag", dup_flagged)

    # Clean up temporary is_canonical field
    for e in active:
        e.pop("is_canonical", None)

    active_metadata_fields = [
        "file_hash",
        "document_type",
        "corpus_status",
        "insurer",
        "source_domain",
        "match_status",
    ]
    for field in active_metadata_fields:
        missing = [e["filename"] for e in active if e.get(field) is None]
        if missing:
            logger.warning("Active entries missing %s: %d entries", field, len(missing))
    logger.info("Active metadata check complete")

    brochure_flagged = [e for e in active if "document_type_brochure" in e["triage_flags"]]
    logger.info("Active brochures flagged with triage_flags: %d", len(brochure_flagged))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    active_path = OUTPUT_DIR / "active_policy_wordings_v1.json"
    with open(active_path, "w") as f:
        json.dump(active, f, indent=2)
    logger.info("Wrote %s (%d entries)", active_path, len(active))

    excluded_path = OUTPUT_DIR / "excluded_documents_v1.json"
    with open(excluded_path, "w") as f:
        json.dump(excluded, f, indent=2)
    logger.info("Wrote %s (%d entries)", excluded_path, len(excluded))

    if issues:
        issues_path = OUTPUT_DIR / "corpus_lockdown_issues_v1.json"
        with open(issues_path, "w") as f:
            json.dump(issues, f, indent=2)
        logger.info("Wrote %s (%d issues)", issues_path, len(issues))

    review_csv_path = OUTPUT_DIR / "status_unset_review_v1.csv"
    with open(review_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "document_id",
                "filename",
                "insurer",
                "plan_name",
                "source_url",
                "uin_match",
                "confidence",
                "review_status",
                "notes",
            ]
        )
        for entry in needs_review:
            writer.writerow(
                [
                    entry["document_id"],
                    entry["filename"],
                    entry["insurer"],
                    "",
                    entry["source_domain"],
                    entry["uin"] or "",
                    "",
                    "",
                    "status_unset",
                ]
            )
    logger.info("Wrote %s (%d rows)", review_csv_path, len(needs_review))

    logger.info("Corpus lockdown complete.")


if __name__ == "__main__":
    main()
