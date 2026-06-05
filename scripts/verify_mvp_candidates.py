"""Generate DSE-027 verified MVP candidate manifest and latest-version audit."""

from __future__ import annotations

import argparse
from pathlib import Path

from source_bundles.mvp import (
    build_latest_audit,
    build_verified_candidates,
    load_json,
    render_latest_audit_markdown,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidates",
        default="data/manifests/mvp_product_candidates_v1.json",
        help="Input DSE-026 candidate manifest.",
    )
    parser.add_argument(
        "--manual-verification",
        default="data/manifests/mvp_product_candidate_verification_manual_v1.json",
        help="Manual latest-version verification input.",
    )
    parser.add_argument(
        "--verified-output",
        default="data/manifests/mvp_product_candidates_verified_v1.json",
        help="Output verified manifest path.",
    )
    parser.add_argument(
        "--audit-json-output",
        default="data/reports/dse027_mvp_candidate_latest_audit_v1.json",
        help="Output audit JSON path.",
    )
    parser.add_argument(
        "--audit-md-output",
        default="data/reports/dse027_mvp_candidate_latest_audit_v1.md",
        help="Output audit Markdown path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates_manifest = load_json(Path(args.candidates))
    manual_doc = load_json(Path(args.manual_verification))

    verified_manifest = build_verified_candidates(candidates_manifest, manual_doc)
    audit_doc = build_latest_audit(verified_manifest)
    audit_md = render_latest_audit_markdown(verified_manifest, audit_doc)

    write_json(Path(args.verified_output), verified_manifest)
    write_json(Path(args.audit_json_output), audit_doc)
    Path(args.audit_md_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.audit_md_output).write_text(audit_md, encoding="utf-8")


if __name__ == "__main__":
    main()
