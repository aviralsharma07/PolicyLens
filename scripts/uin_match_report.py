#!/usr/bin/env python3
"""
DSE-002: UIN Match Verification Report

Reads the active policy wordings manifest and uin_lifecycle.json,
cross-verifies UIN-insurer assignments, and generates:
  - data/manifests/uin_match_report_v1.json
  - data/manifests/unmatched_triage_report_v1.csv

Usage:
    python scripts/uin_match_report.py
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from identity.uin_matcher import generate_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("uin_match_report")

BASE_DIR = Path(__file__).resolve().parent.parent
ACTIVE_MANIFEST = BASE_DIR / "data" / "manifests" / "active_policy_wordings_v1.json"
LIFECYCLE_DATA = BASE_DIR.parent / "insurance-agent" / "data" / "uin_lifecycle.json"
OUTPUT_REPORT = BASE_DIR / "data" / "manifests" / "uin_match_report_v1.json"
TRIAGE_OUTPUT = BASE_DIR / "data" / "manifests" / "unmatched_triage_report_v1.csv"


def main():
    logger.info("DSE-002: UIN Match Verification Report")
    logger.info("Active manifest: %s", ACTIVE_MANIFEST)
    logger.info("Lifecycle data: %s", LIFECYCLE_DATA)

    if not ACTIVE_MANIFEST.exists():
        logger.error("Active manifest not found: %s", ACTIVE_MANIFEST)
        sys.exit(1)
    if not LIFECYCLE_DATA.exists():
        logger.error("Lifecycle data not found: %s", LIFECYCLE_DATA)
        sys.exit(1)

    report = generate_report(
        active_path=str(ACTIVE_MANIFEST),
        lifecycle_path=str(LIFECYCLE_DATA),
        output_path=str(OUTPUT_REPORT),
        triage_output_path=str(TRIAGE_OUTPUT),
    )

    summary = report["summary"]
    print()
    print("=" * 60)
    print("UIN MATCH REPORT - SUMMARY")
    print("=" * 60)
    print(f"  Total entries:        {summary['total_entries']}")
    print(f"  Verified:             {summary['verified']} ({summary['verified_pct']}%)")
    print(f"  Plan name matched:    {summary['plan_name_matched']}")
    print(f"  Conflict:             {summary['conflict']}")
    print(f"  Special case:         {summary['special_case']}")
    print(f"  Unmatched:            {summary['unmatched']}")
    print(f"  Verified + special:   {summary['verified_or_special_pct']}%")
    print()
    print(f"  Full report:     {OUTPUT_REPORT}")
    print(f"  Triage CSV:      {TRIAGE_OUTPUT}")
    print("=" * 60)

    conflict_entries = [r for r in report["results"] if r["match_status"] == "conflict"]
    if conflict_entries:
        print()
        print("CONFLICTS:")
        for c in conflict_entries:
            print(f"  - {c['filename']}: {c['verification_notes']}")

    special_entries = [r for r in report["results"] if r["match_status"] == "special_case"]
    if special_entries:
        print()
        print("SPECIAL CASES:")
        for s in special_entries:
            print(f"  - {s['filename']}: {s['verification_notes']}")

    summary_path = BASE_DIR / "data" / "manifests" / "uin_match_summary_v1.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info("Summary saved to %s", summary_path)

    return 0 if summary["conflict"] == 0 and summary["unmatched"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
