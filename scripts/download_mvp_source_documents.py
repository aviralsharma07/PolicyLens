"""Download current official MVP source documents and emit a hash/page-count index."""

from __future__ import annotations

import argparse
import os
import time
import urllib.request
from urllib.parse import quote, urlsplit, urlunsplit
from pathlib import Path

from source_bundles.mvp import load_json, page_count_for_pdf, sha256_for_file, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verified-candidates",
        default="data/manifests/mvp_product_candidates_verified_v1.json",
    )
    parser.add_argument(
        "--output-root",
        default="data/processed/source_documents_mvp_v1",
    )
    parser.add_argument(
        "--index-output",
        default="data/reports/dse027_source_download_index_v1.json",
    )
    return parser.parse_args()


def candidate_urls(row: dict[str, object]) -> list[tuple[str, str]]:
    fields = [
        ("policy_wording", row.get("official_wording_url")),
        ("cis", row.get("official_cis_url")),
        ("brochure", row.get("official_brochure_or_prospectus_url")),
        ("product_benefit_table", row.get("official_pbt_or_table_url")),
    ]
    output: list[tuple[str, str]] = []
    for doc_type, maybe_url in fields:
        if isinstance(maybe_url, str) and maybe_url:
            output.append((doc_type, maybe_url))
    return output


def normalize_url(source_url: str) -> str:
    parts = urlsplit(source_url)
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            quote(parts.path, safe="/:%._-()"),
            parts.query,
            parts.fragment,
        )
    )


def main() -> None:
    args = parse_args()
    verified_manifest = load_json(Path(args.verified_candidates))
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    index_rows: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    for row in verified_manifest["candidates"]:
        candidate_id = row["candidate_id"]
        for document_type, source_url in candidate_urls(row):
            filename = os.path.basename(source_url.split("?", 1)[0]) or f"{document_type}.pdf"
            target = output_root / candidate_id / document_type / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                if not target.exists():
                    request = urllib.request.Request(
                        normalize_url(source_url),
                        headers={
                            "User-Agent": "Mozilla/5.0 (compatible; PolicyLens-DSE027/1.0)",
                            "Accept": "application/pdf,application/octet-stream,*/*",
                        },
                    )
                    with urllib.request.urlopen(request, timeout=60) as response, target.open("wb") as out:
                        out.write(response.read())
                file_hash = sha256_for_file(target)
                index_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "document_type": document_type,
                        "source_url": source_url,
                        "filename": filename,
                        "file_path": str(target),
                        "file_hash": file_hash,
                        "document_id": file_hash,
                        "page_count": page_count_for_pdf(target),
                        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                failures.append(
                    {
                        "candidate_id": candidate_id,
                        "document_type": document_type,
                        "source_url": source_url,
                        "error": str(exc),
                    }
                )

    write_json(
        Path(args.index_output),
        {
            "schema_version": "dse027_source_download_index.v1",
            "task_id": "DSE-027",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "document_count": len(index_rows),
            "failure_count": len(failures),
            "documents": index_rows,
            "failures": failures,
        },
    )


if __name__ == "__main__":
    main()
