"""
Run Clause Store — DSE-010

Batch ingest all 5 gold-policy interim JSON outputs into SQLite (data/engine.sqlite).
Also builds source_spans, resolves provisional evidence IDs, and writes
data/interim/facts_resolved/{slug}/accepted_facts.json.

Usage:
  PYTHONPATH=. python scripts/run_clause_store.py \\
    --gold-corpus gold_corpus \\
    --physical-root data/interim/physical \\
    --logical-root data/interim/logical \\
    --tables-root data/interim/tables \\
    --facts-root data/interim/facts \\
    --output-db data/engine.sqlite \\
    --output-facts-resolved data/interim/facts_resolved

Exit 0 if all 5 policies processed.
Exit 1 if any policy fails a critical check (unverifiable evidence, FK violation).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

from clause_store.fact_resolver import resolve_facts
from clause_store.models import (
    DocumentBlock,
    DocumentIssue,
    DocumentLine,
    DocumentPage,
    DocumentSection,
    DocumentTable,
    DocumentTableCell,
    PolicyClause,
    PipelineRun,
    Product,
    ProductVersion,
    SourceDocument,
)
from clause_store.repository import (
    backfill_table_parent_clauses,
    get_db_size_bytes,
    get_table_counts,
    init_db,
    insert_blocks,
    insert_clauses,
    insert_issues,
    insert_lines,
    insert_pages,
    insert_pipeline_run,
    insert_product,
    insert_product_version,
    insert_sections,
    insert_source_document,
    insert_source_spans,
    insert_table_cells,
    insert_tables,
    update_pipeline_run_finished,
)
from clause_store.span_builder import (
    build_clause_spans,
    build_fact_evidence_spans,
    build_line_index,
    build_table_cell_spans,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("run_clause_store")

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(_PROJECT_ROOT),
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_json_opt(path: str) -> Optional[Any]:
    if os.path.isfile(path):
        return _load_json(path)
    return None


def _write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _make_page_id(document_id: str, page_number: int) -> str:
    return f"{document_id}_p{page_number}"


def _uid(document_id: str, source_id: str) -> str:
    """Convert a document-local artifact ID into a globally unique SQLite UID."""
    return f"{document_id}:{source_id}"


# ---------------------------------------------------------------------------
# Per-policy ingestion
# ---------------------------------------------------------------------------


def ingest_policy(
    slug: str,
    gold_corpus: str,
    physical_root: str,
    logical_root: str,
    tables_root: str,
    facts_root: str,
    output_facts_resolved: str,
    conn,
    pipeline_run_id: str,
) -> dict:
    """
    Ingest one policy's interim JSON outputs into SQLite.
    Returns a summary dict for the run report.
    Raises on critical failures (unverifiable evidence, FK violation).
    """
    issues: List[DocumentIssue] = []
    logger.info("Ingesting %s", slug)

    # -----------------------------------------------------------------------
    # 1. Load metadata + physical
    # -----------------------------------------------------------------------
    meta = _load_json(os.path.join(gold_corpus, "policies", slug, "metadata.json"))
    physical_path = os.path.join(physical_root, slug, "document_physical.json")
    physical_doc = _load_json(physical_path)

    policy_id = meta.get("policy_id", slug)
    document_id = physical_doc["document_id"]
    file_hash = physical_doc["file_hash"]
    full_uin = meta.get("uin", "")

    # DSE-015: Use canonical identity library for UIN parsing, insurer/plan normalization
    from identity.uin_utils import extract_uin_base, extract_version_number
    from identity.insurer_registry import get_display_name, lookup_by_canonical
    from identity.plan_normalizer import clean_plan_name, make_display_name, make_short_name

    # Correct UIN base via V-delimiter (fixes DSE-010 [:11] truncation bug — ADR-0030)
    uin_base = meta.get("uin_base") or extract_uin_base(full_uin) or policy_id

    raw_insurer = meta.get("insurer", "")
    raw_plan = meta.get("plan_name", "")
    canonical_plan = clean_plan_name(raw_plan, raw_insurer)
    insurer_display = get_display_name(raw_insurer)
    display_name = make_display_name(canonical_plan, insurer_display)
    short_name = make_short_name(canonical_plan)

    # Match confidence and method from gold metadata
    match_confidence = meta.get("match_confidence", "none")
    match_method = (
        "uin_insurer_plan_verified" if meta.get("match_status") == "verified" else "uin_only"
    )

    # Products / versions / source_documents
    product = Product(
        product_id=policy_id,
        uin_base=uin_base,
        normalized_insurer=raw_insurer,
        normalized_plan_name=canonical_plan,
        display_name=display_name,
        short_name=short_name,
        match_confidence=match_confidence,
        match_method=match_method,
    )
    insert_product(conn, product)

    # Version info from lifecycle data if available
    version_number = extract_version_number(full_uin)
    # Lifecycle approval_date and financial_year from UIN lifecycle registry.
    # Enrichment is optional but failures must be recorded (AGENTS.md: no silent failure).
    lifecycle_approval_date = None
    lifecycle_financial_year = None
    try:
        lifecycle_path = os.path.join(
            str(_PROJECT_ROOT.parent / "insurance-agent" / "data" / "uin_lifecycle.json")
        )
        if os.path.isfile(lifecycle_path):
            lifecycle_data = _load_json(lifecycle_path)
            lifecycle_product = lifecycle_data.get("products", {}).get(uin_base)

            # Fallback: if primary key lookup fails, scan all products for matching full_uin.
            # Handles malformed lifecycle keys where the base doesn't match extract_uin_base().
            if lifecycle_product is None and full_uin:
                for _base, _prod in lifecycle_data.get("products", {}).items():
                    for _v in _prod.get("versions", []):
                        if _v.get("uin") == full_uin:
                            lifecycle_product = _prod
                            logger.info(
                                "  %s: lifecycle fallback matched uin_base=%s via full_uin scan",
                                slug,
                                _base,
                            )
                            break
                    if lifecycle_product:
                        break

            if lifecycle_product:
                for v in lifecycle_product.get("versions", []):
                    if v.get("uin") == full_uin:
                        lifecycle_approval_date = v.get("approval_date")
                        lifecycle_financial_year = v.get("financial_year")
                        break
        else:
            logger.info(
                "  %s: lifecycle file not found at %s — skipping enrichment", slug, lifecycle_path
            )
    except Exception as exc:
        logger.warning("  %s: lifecycle enrichment failed: %s", slug, exc)
        issues.append(
            DocumentIssue(
                document_id=document_id,
                pipeline_run_id=pipeline_run_id,
                issue_type="lifecycle_enrichment_failed",
                severity="warning",
                description=f"Could not enrich product identity from lifecycle data: {exc}",
            )
        )

    version = ProductVersion(
        version_id=f"{policy_id}_v1",
        product_id=policy_id,
        full_uin=full_uin,
        version_number=version_number,
        approval_date=lifecycle_approval_date,
        financial_year=lifecycle_financial_year,
    )
    insert_product_version(conn, version)

    source_doc = SourceDocument(
        document_id=document_id,
        policy_id=policy_id,
        source_pdf_path=meta.get("source_pdf_path", ""),
        file_hash=file_hash,
        page_count=physical_doc.get("page_count", 0),
        version_id=f"{policy_id}_v1",
    )
    insert_source_document(conn, source_doc)

    # -----------------------------------------------------------------------
    # 2. Physical layer: pages, blocks, lines
    # -----------------------------------------------------------------------
    pages_to_insert: List[DocumentPage] = []
    blocks_to_insert: List[DocumentBlock] = []
    lines_to_insert: List[DocumentLine] = []

    for page_data in physical_doc.get("pages", []):
        pnum = page_data["page_number"]
        page_id = _make_page_id(document_id, pnum)

        pages_to_insert.append(
            DocumentPage(
                page_id=page_id,
                document_id=document_id,
                page_number=pnum,
                width=page_data.get("width", 595.0),
                height=page_data.get("height", 842.0),
                rotation=page_data.get("rotation", 0),
            )
        )

        # One block per page (physical parser limitation)
        for bidx, block_data in enumerate(page_data.get("blocks", []), start=1):
            block_id = block_data.get("block_id") or f"{document_id}_p{pnum}_b{bidx}"
            raw_bbox = block_data.get("bbox") or block_data.get("bbox_json")
            bbox_json = json.dumps(raw_bbox) if raw_bbox and isinstance(raw_bbox, list) else None
            blocks_to_insert.append(
                DocumentBlock(
                    block_id=block_id,
                    page_id=page_id,
                    document_id=document_id,
                    block_type=block_data.get("block_type", "text"),
                    bbox_json=bbox_json,
                    reading_order=bidx,
                )
            )

        # Lines — must have a block FK
        default_block_id = (
            blocks_to_insert[-1].block_id
            if blocks_to_insert and blocks_to_insert[-1].page_id == page_id
            else f"{document_id}_p{pnum}_b1"
        )
        for ln in page_data.get("lines", []):
            source_line_id = ln.get("line_id")
            if not source_line_id:
                continue
            raw_bbox = ln.get("bbox", [])
            lines_to_insert.append(
                DocumentLine(
                    line_id=_uid(document_id, source_line_id),
                    source_line_id=source_line_id,
                    block_id=default_block_id,
                    document_id=document_id,
                    page_number=pnum,
                    bbox_json=json.dumps(raw_bbox) if raw_bbox else "[]",
                    text=ln.get("text", ""),
                    region=ln.get("region", "body"),
                    is_header_candidate=bool(ln.get("is_header_candidate", False)),
                    is_footer_candidate=bool(ln.get("is_footer_candidate", False)),
                )
            )

    insert_pages(conn, pages_to_insert)
    insert_blocks(conn, blocks_to_insert)
    insert_lines(conn, lines_to_insert)
    logger.info(
        "  %s: %d pages, %d blocks, %d lines",
        slug,
        len(pages_to_insert),
        len(blocks_to_insert),
        len(lines_to_insert),
    )

    # Log deferred document_text_spans (ADR-0017)
    issues.append(
        DocumentIssue(
            document_id=document_id,
            pipeline_run_id=pipeline_run_id,
            issue_type="document_text_spans_deferred",
            severity="info",
            description="Character-level text spans not persisted per ADR-0017. Physical JSON is source of truth.",
        )
    )

    # -----------------------------------------------------------------------
    # 3. Build line index (needed for span construction)
    # -----------------------------------------------------------------------
    line_index = build_line_index(physical_doc)
    for source_line_id, info in line_index.items():
        info["line_uid"] = _uid(document_id, source_line_id)

    # -----------------------------------------------------------------------
    # 4. Section tree: sections + clauses
    # -----------------------------------------------------------------------
    logical_path = os.path.join(logical_root, slug, "section_tree.json")
    section_tree = _load_json(logical_path)

    raw_sections = section_tree.get("sections", [])
    raw_clauses = section_tree.get("clauses", [])
    enriched_clauses = []
    for c in raw_clauses:
        enriched = dict(c)
        enriched["clause_uid"] = _uid(document_id, c["clause_id"])
        enriched["section_uid"] = _uid(document_id, c.get("section_id", ""))
        enriched["line_uids"] = [_uid(document_id, lid) for lid in c.get("line_ids", [])]
        enriched_clauses.append(enriched)
    # Always use the DSE-010 pipeline_run_id for SQLite rows.
    # The source artifact's own pipeline_run_id (e.g. "physical_v1_fixed") is stored
    # in the JSON file but is not a FK in the store.
    tree_pipeline_run_id = pipeline_run_id

    sections_to_insert: List[DocumentSection] = []
    # Sort parent-before-child to respect self-referential FK
    section_by_id: Dict[str, dict] = {s["section_id"]: s for s in raw_sections}
    ordered_sections: List[dict] = []
    visited = set()

    def _visit_section(sec_id: str):
        if sec_id in visited:
            return
        sec = section_by_id.get(sec_id)
        if not sec:
            return
        parent_id = sec.get("parent_id")
        if parent_id and parent_id not in visited:
            _visit_section(parent_id)
        ordered_sections.append(sec)
        visited.add(sec_id)

    for s in raw_sections:
        _visit_section(s["section_id"])

    for sec in ordered_sections:
        source_section_id = sec["section_id"]
        parent_source_id = sec.get("parent_id")
        sections_to_insert.append(
            DocumentSection(
                section_id=_uid(document_id, source_section_id),
                source_section_id=source_section_id,
                document_id=document_id,
                pipeline_run_id=tree_pipeline_run_id,
                parent_id=_uid(document_id, parent_source_id) if parent_source_id else None,
                section_number=sec.get("number"),
                title=sec.get("title"),
                normalized_title=sec.get("normalized_title"),
                level=sec.get("level", 0),
                heading_type=sec.get("heading_type", "root"),
                heading_score=sec.get("heading_score"),
                heading_line_id=sec.get("heading_line_id"),
                page_start=sec.get("page_start", 0),
                page_end=sec.get("page_end", 0),
            )
        )

    clauses_to_insert: List[PolicyClause] = []
    for clause in raw_clauses:
        source_clause_id = clause["clause_id"]
        source_line_ids = clause.get("line_ids", [])
        clauses_to_insert.append(
            PolicyClause(
                clause_id=_uid(document_id, source_clause_id),
                source_clause_id=source_clause_id,
                document_id=document_id,
                section_id=_uid(document_id, clause.get("section_id", "")),
                pipeline_run_id=tree_pipeline_run_id,
                clause_number=clause.get("clause_number"),
                title=clause.get("title"),
                raw_text=clause.get("text", ""),
                page_start=clause.get("page_start", 0),
                page_end=clause.get("page_end", 0),
                line_ids_json=json.dumps([_uid(document_id, lid) for lid in source_line_ids]),
                source_line_ids_json=json.dumps(source_line_ids),
                segmentation_method=clause.get("segmentation_method"),
                confidence=clause.get("confidence"),
            )
        )

    insert_sections(conn, sections_to_insert)
    insert_clauses(conn, clauses_to_insert)
    logger.info(
        "  %s: %d sections, %d clauses", slug, len(sections_to_insert), len(clauses_to_insert)
    )

    # -----------------------------------------------------------------------
    # 5. Build clause source_spans
    # -----------------------------------------------------------------------
    clause_spans = build_clause_spans(
        enriched_clauses, line_index, policy_id, document_id, pipeline_run_id, issues
    )
    insert_source_spans(conn, clause_spans)
    logger.info("  %s: %d clause_body source_spans", slug, len(clause_spans))

    # -----------------------------------------------------------------------
    # 6. Tables + cells (provisional parent_clause_id from JSON)
    # -----------------------------------------------------------------------
    tables_path = os.path.join(tables_root, slug, "document_tables.json")
    cells_path = os.path.join(tables_root, slug, "document_table_cells.json")
    tables_doc = _load_json_opt(tables_path) or {"tables": []}
    flat_cells = _load_json_opt(cells_path) or []

    tables_to_insert: List[DocumentTable] = []
    for t in tables_doc.get("tables", []):
        raw_bbox = t.get("bbox")
        source_parent_clause_id = t.get("parent_clause_id")
        tables_to_insert.append(
            DocumentTable(
                table_id=t["table_id"],
                document_id=document_id,
                page=t.get("page", 0),
                extraction_method=t.get("extraction_method"),
                table_type=t.get("table_type"),
                table_type_confidence=t.get("table_type_confidence"),
                row_count=t.get("row_count", 0),
                col_count=t.get("col_count", 0),
                has_header_row=bool(t.get("has_header_row", False)),
                bbox_json=json.dumps(raw_bbox) if raw_bbox else None,
                # Provisional — will be overwritten by backfill_table_parent_clauses()
                parent_clause_id=_uid(document_id, source_parent_clause_id)
                if source_parent_clause_id
                else None,
                parent_clause_confidence=t.get("parent_clause_confidence"),
                issues_json=json.dumps(t.get("issues", [])) if t.get("issues") else None,
            )
        )

    cells_to_insert: List[DocumentTableCell] = []
    for c in flat_cells:
        raw_bbox = c.get("bbox")
        cells_to_insert.append(
            DocumentTableCell(
                cell_id=c["cell_id"],
                table_id=c["table_id"],
                row_index=c.get("row_index", 0),
                col_index=c.get("col_index", 0),
                text=c.get("text", ""),
                bbox_json=json.dumps(raw_bbox) if raw_bbox else None,
                is_header=bool(c.get("is_header", False)),
                column_header_text=c.get("column_header_text"),
                row_header_text=c.get("row_header_text"),
            )
        )

    insert_tables(conn, tables_to_insert)
    insert_table_cells(conn, cells_to_insert)
    logger.info(
        "  %s: %d tables, %d table cells", slug, len(tables_to_insert), len(cells_to_insert)
    )

    # -----------------------------------------------------------------------
    # 7. Table cell source_spans (lattice cells with bbox only)
    # -----------------------------------------------------------------------
    cell_spans = build_table_cell_spans(tables_doc, document_id, policy_id, pipeline_run_id)
    insert_source_spans(conn, cell_spans)
    logger.info("  %s: %d table_cell source_spans", slug, len(cell_spans))

    # -----------------------------------------------------------------------
    # 8. Backfill table parent_clause_id via bbox overlap
    # -----------------------------------------------------------------------
    conn.commit()  # commit before spatial query (reads from DB)
    tables_updated = backfill_table_parent_clauses(conn, document_id)
    logger.info("  %s: %d tables parent_clause_id resolved via bbox overlap", slug, tables_updated)

    # -----------------------------------------------------------------------
    # 9. Fact evidence spans + resolve accepted facts
    # -----------------------------------------------------------------------
    facts_path = os.path.join(facts_root, slug, "accepted_facts.json")
    accepted_facts = _load_json_opt(facts_path) or []

    clause_lookup: Dict[str, dict] = {c["clause_id"]: c for c in enriched_clauses}

    evidence_spans = build_fact_evidence_spans(
        accepted_facts, clause_lookup, line_index, policy_id, document_id, pipeline_run_id, issues
    )
    insert_source_spans(conn, evidence_spans)
    logger.info("  %s: %d fact_evidence source_spans", slug, len(evidence_spans))

    # Map candidate_id → SourceSpan for resolver
    evidence_by_candidate = {
        span.span_id.replace(f"ss_{policy_id}_", "").replace("_evidence", ""): span
        for span in evidence_spans
    }
    # Rebuild correctly: candidate_id is encoded in span_id
    evidence_by_candidate = {}
    for span in evidence_spans:
        # span_id = "ss_{policy_id}_{candidate_id}_evidence"
        prefix = f"ss_{policy_id}_"
        suffix = "_evidence"
        if span.span_id.startswith(prefix) and span.span_id.endswith(suffix):
            candidate_id = span.span_id[len(prefix) : -len(suffix)]
            evidence_by_candidate[candidate_id] = span

    resolved_facts, warnings = resolve_facts(accepted_facts, evidence_by_candidate, policy_id)
    if warnings:
        for w in warnings:
            logger.warning("  %s: %s", slug, w)
            issues.append(
                DocumentIssue(
                    document_id=document_id,
                    pipeline_run_id=pipeline_run_id,
                    issue_type="fact_resolution_warning",
                    severity="warning",
                    description=w,
                )
            )

    # Write resolved facts (ADR-0020: separate artifact, original not mutated)
    resolved_path = os.path.join(output_facts_resolved, slug, "accepted_facts.json")
    _write_json(resolved_path, resolved_facts)
    logger.info("  %s: resolved facts written to %s", slug, resolved_path)

    # -----------------------------------------------------------------------
    # 10. Insert all accumulated issues
    # -----------------------------------------------------------------------
    insert_issues(conn, issues)
    conn.commit()

    present_facts = [f for f in accepted_facts if f.get("fact_status") == "present"]
    resolved_present = [
        f
        for f in resolved_facts
        if f.get("fact_status") == "present" and f.get("evidence_resolution_status") == "resolved"
    ]
    total_spans = len(clause_spans) + len(cell_spans) + len(evidence_spans)

    return {
        "slug": slug,
        "status": "ok",
        "document_id": document_id,
        "pages": len(pages_to_insert),
        "lines": len(lines_to_insert),
        "sections": len(sections_to_insert),
        "clauses": len(clauses_to_insert),
        "clause_body_spans": len(clause_spans),
        "table_cell_spans": len(cell_spans),
        "fact_evidence_spans": len(evidence_spans),
        "total_source_spans": total_spans,
        "tables": len(tables_to_insert),
        "table_cells": len(cells_to_insert),
        "tables_parent_clause_resolved": tables_updated,
        "present_facts": len(present_facts),
        "resolved_present_facts": len(resolved_present),
        "issues_logged": len(issues),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Clause Store Ingest — DSE-010")
    parser.add_argument("--gold-corpus", default="gold_corpus")
    parser.add_argument("--physical-root", default="data/interim/physical")
    parser.add_argument("--logical-root", default="data/interim/logical")
    parser.add_argument("--tables-root", default="data/interim/tables")
    parser.add_argument("--facts-root", default="data/interim/facts")
    parser.add_argument("--output-db", default="data/engine.sqlite")
    parser.add_argument("--output-facts-resolved", default="data/interim/facts_resolved")
    parser.add_argument("--pipeline-run-id")
    args = parser.parse_args()

    pipeline_run_id = args.pipeline_run_id or f"dse010_v1_{int(time.time())}"
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    git_commit = _git_commit()

    os.makedirs(
        os.path.dirname(args.output_db) if os.path.dirname(args.output_db) else ".", exist_ok=True
    )

    logger.info("Initialising database: %s", args.output_db)
    conn = init_db(args.output_db)

    run = PipelineRun(
        id=pipeline_run_id,
        started_at=started_at,
        git_commit=git_commit,
    )
    insert_pipeline_run(conn, run)

    policies_dir = os.path.join(args.gold_corpus, "policies")
    slugs = sorted(
        s
        for s in os.listdir(policies_dir)
        if os.path.isfile(os.path.join(policies_dir, s, "metadata.json"))
    )

    policy_results = []
    had_fatal = False
    success_count = 0

    for slug in slugs:
        try:
            result = ingest_policy(
                slug=slug,
                gold_corpus=args.gold_corpus,
                physical_root=args.physical_root,
                logical_root=args.logical_root,
                tables_root=args.tables_root,
                facts_root=args.facts_root,
                output_facts_resolved=args.output_facts_resolved,
                conn=conn,
                pipeline_run_id=pipeline_run_id,
            )
            policy_results.append(result)
            success_count += 1
            logger.info(
                "  OK %s: %d spans, %d resolved facts",
                slug,
                result["total_source_spans"],
                result["resolved_present_facts"],
            )
        except Exception as exc:
            logger.exception("FATAL error ingesting %s: %s", slug, exc)
            policy_results.append({"slug": slug, "status": "fatal_error", "error": str(exc)})
            had_fatal = True

    finished_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    final_status = "completed" if not had_fatal else "partial_failure"
    update_pipeline_run_finished(
        conn,
        pipeline_run_id,
        final_status,
        finished_at,
        success_count=success_count,
        failure_count=len(slugs) - success_count,
    )
    conn.close()

    # Build summary report (committed artifact)
    counts = {}
    conn2 = init_db(args.output_db)
    counts = get_table_counts(conn2)
    conn2.close()
    db_size = get_db_size_bytes(args.output_db)

    summary = {
        "pipeline_run_id": pipeline_run_id,
        "git_commit": git_commit,
        "date": time.strftime("%Y-%m-%d"),
        "db_path": args.output_db,
        "db_gitignored": True,
        "policies_ingested": success_count,
        "policies_total": len(slugs),
        "db_size_bytes": db_size,
        "db_size_mb": round(db_size / 1024 / 1024, 2),
        "table_row_counts": counts,
        "policy_results": policy_results,
    }
    summary_path = "data/reports/dse010_sqlite_build_summary.json"
    _write_json(summary_path, summary)
    logger.info("Build summary written to %s", summary_path)
    logger.info(
        "Done: %d/%d policies ingested | DB size: %.2f MB",
        success_count,
        len(slugs),
        db_size / 1024 / 1024,
    )

    return 1 if had_fatal else 0


if __name__ == "__main__":
    raise SystemExit(main())
