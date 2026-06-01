"""
Run Fact Scoring — DSE-011

Batch ingest: read fact_candidates.json + facts_resolved/accepted_facts.json,
compute composite scores, insert into extracted_fact_candidates + extracted_facts,
detect and record conflicts in fact_conflicts.

Requires data/engine.sqlite to already have DSE-010 data (run run_clause_store.py first).

Usage:
  PYTHONPATH=. python scripts/run_fact_scoring.py \\
    --gold-corpus gold_corpus \\
    --candidates-root data/interim/facts \\
    --resolved-root data/interim/facts_resolved \\
    --db data/engine.sqlite

Exit 0 if all 5 policies processed. Exit 1 if parity check fails.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import sys
import time
from typing import Any, Dict, List, Optional

from clause_store.models import (
    ExtractedFact,
    ExtractedFactCandidate,
    FactConflict,
    PipelineRun,
)
from clause_store.repository import (
    count_dangling_fks,
    get_table_counts,
    init_db,
    insert_extracted_facts,
    insert_fact_candidates,
    insert_fact_conflicts,
    insert_pipeline_run,
    update_pipeline_run_finished,
)
from extractors.conflict_detector import detect_conflicts, resolve_conflict
from extractors.scoring import compute_composite_score, score_candidates

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("run_fact_scoring")

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_json_opt(path: str) -> Optional[Any]:
    return _load_json(path) if os.path.isfile(path) else None


def _write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _uid(document_id: str, source_id: str) -> str:
    """Global UID from document-local ID (ADR-0022)."""
    return f"{document_id}:{source_id}"


def _json_str(obj: Any) -> Optional[str]:
    """Convert a dict/list to a JSON string, or return None."""
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    return json.dumps(obj, ensure_ascii=False)


def _build_resolved_span_lookup(resolved_facts: List[dict]) -> Dict[str, dict]:
    """Build {source_candidate_id → resolved_fact} for present resolved facts."""
    lookup = {}
    for fact in resolved_facts:
        cid = fact.get("candidate_id")
        if cid and fact.get("evidence_resolution_status") == "resolved":
            lookup[cid] = fact
    return lookup


def process_policy(
    slug: str,
    gold_corpus: str,
    candidates_root: str,
    resolved_root: str,
    conn,
    pipeline_run_id: str,
) -> dict:
    """Ingest candidates + facts for one policy."""
    logger.info("Processing %s", slug)

    # Load metadata for document_id
    meta = _load_json(os.path.join(gold_corpus, "policies", slug, "metadata.json"))
    physical_path = os.path.join("data/interim/physical", slug, "document_physical.json")
    physical = _load_json(physical_path)
    document_id = physical["document_id"]
    policy_id = meta.get("policy_id", slug)

    # Load source artifacts
    candidates_path = os.path.join(candidates_root, slug, "fact_candidates.json")
    resolved_path = os.path.join(resolved_root, slug, "accepted_facts.json")

    raw_candidates = _load_json_opt(candidates_path) or []
    resolved_facts = _load_json_opt(resolved_path) or []

    # Build resolved span lookup for evidence_span_id resolution
    resolved_lookup = _build_resolved_span_lookup(resolved_facts)

    # Score all candidates
    scored = score_candidates(list(raw_candidates))

    # Build ExtractedFactCandidate records
    db_candidates: List[ExtractedFactCandidate] = []
    for cand in scored:
        source_candidate_id = cand.get("candidate_id", "")
        source_clause_id = cand.get("evidence_clause_id") or ""

        # Resolve evidence_span_id: use resolved span for accepted candidates
        evidence_span_id = None
        resolved_fact = resolved_lookup.get(source_candidate_id)
        if resolved_fact and cand.get("accepted"):
            evidence_span_id = resolved_fact.get("evidence_span_id")

        db_candidates.append(
            ExtractedFactCandidate(
                id=_uid(document_id, source_candidate_id),
                source_candidate_id=source_candidate_id,
                clause_id=_uid(document_id, source_clause_id),
                source_clause_id=source_clause_id,
                document_id=document_id,
                concept=cand.get("concept", ""),
                extractor_name=cand.get("extractor_name", ""),
                pipeline_run_id=pipeline_run_id,
                confidence=float(cand.get("confidence", 0.0)),
                score=float(cand.get("score", 0.0)),
                accepted=bool(cand.get("accepted", False)),
                candidate_value_json=_json_str(cand.get("value_json")),
                normalized_value_json=_json_str(cand.get("normalized_value_json")),
                fact_status=cand.get("fact_status", "present"),
                scope_json=_json_str(cand.get("scope_json")),
                condition_json=_json_str(cand.get("condition_json")),
                evidence_span_id=evidence_span_id,
                evidence_text=cand.get("evidence_text"),
                evidence_page=cand.get("evidence_page"),
                extractor_version=cand.get("extractor_version"),
                pattern_id=cand.get("pattern_id"),
                rejection_reason=cand.get("rejection_reason"),
            )
        )

    insert_fact_candidates(conn, db_candidates)
    logger.info("  %s: %d candidates inserted", slug, len(db_candidates))

    # Build ExtractedFact records (only present facts with clause evidence)
    db_facts: List[ExtractedFact] = []
    for fact in resolved_facts:
        if fact.get("fact_status") not in ("present", "explicitly_not_covered"):
            continue
        source_candidate_id = fact.get("candidate_id")
        source_clause_id = fact.get("evidence_clause_id")
        if not source_candidate_id or not source_clause_id:
            continue

        db_facts.append(
            ExtractedFact(
                id=_uid(document_id, source_candidate_id),
                source_candidate_id=source_candidate_id,
                clause_id=_uid(document_id, source_clause_id),
                source_clause_id=source_clause_id,
                document_id=document_id,
                concept=fact.get("concept", ""),
                extraction_method=fact.get("extraction_method", "deterministic"),
                pipeline_run_id=pipeline_run_id,
                fact_status=fact.get("fact_status", "present"),
                confidence=float(fact.get("confidence", 0.0)),
                value_json=_json_str(fact.get("value_json")),
                normalized_value_json=_json_str(fact.get("normalized_value_json")),
                scope_json=_json_str(fact.get("scope_json")),
                condition_json=_json_str(fact.get("condition_json")),
                evidence_span_id=fact.get("evidence_span_id"),
            )
        )

    insert_extracted_facts(conn, db_facts)
    logger.info("  %s: %d extracted facts inserted", slug, len(db_facts))

    # Detect conflicts
    # Build candidate dicts with global UIDs for conflict detection
    conflict_input = [
        {
            "id": c.id,
            "concept": c.concept,
            "accepted": c.accepted,
            "normalized_value_json": c.normalized_value_json,
            "fact_status": c.fact_status,
            "scope_json": c.scope_json,
            "score": c.score,
        }
        for c in db_candidates
    ]
    conflicts = detect_conflicts(conflict_input, document_id, pipeline_run_id)

    # Resolve any conflicts
    if conflicts:
        by_id = {c["id"]: c for c in conflict_input}
        resolved_conflicts = [resolve_conflict(c, by_id, "higher_score_wins") for c in conflicts]
        insert_fact_conflicts(conn, resolved_conflicts)
        logger.info("  %s: %d conflicts detected and resolved", slug, len(resolved_conflicts))
    else:
        resolved_conflicts = []

    conn.commit()

    # Parity checks
    db_cand_count = conn.execute(
        "SELECT COUNT(*) FROM extracted_fact_candidates WHERE document_id = ?",
        (document_id,),
    ).fetchone()[0]
    db_fact_count = conn.execute(
        "SELECT COUNT(*) FROM extracted_facts WHERE document_id = ?",
        (document_id,),
    ).fetchone()[0]

    json_cand_count = len(raw_candidates)
    json_present_count = sum(
        1
        for f in resolved_facts
        if f.get("fact_status") in ("present", "explicitly_not_covered")
        and f.get("candidate_id")
        and f.get("evidence_clause_id")
    )

    cand_parity = db_cand_count == json_cand_count
    fact_parity = db_fact_count == json_present_count

    if not cand_parity:
        logger.error(
            "  %s: PARITY FAIL candidates: JSON=%d SQLite=%d",
            slug,
            json_cand_count,
            db_cand_count,
        )
    if not fact_parity:
        logger.error(
            "  %s: PARITY FAIL facts: resolved_present=%d SQLite=%d",
            slug,
            json_present_count,
            db_fact_count,
        )

    return {
        "slug": slug,
        "document_id": document_id,
        "status": "ok" if (cand_parity and fact_parity) else "parity_failed",
        "json_candidates": json_cand_count,
        "db_candidates": db_cand_count,
        "candidate_parity": cand_parity,
        "json_present_facts": json_present_count,
        "db_facts": db_fact_count,
        "fact_parity": fact_parity,
        "conflicts_detected": len(resolved_conflicts),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fact Scoring Ingest — DSE-011")
    parser.add_argument("--gold-corpus", default="gold_corpus")
    parser.add_argument("--candidates-root", default="data/interim/facts")
    parser.add_argument("--resolved-root", default="data/interim/facts_resolved")
    parser.add_argument("--db", default="data/engine.sqlite")
    parser.add_argument("--pipeline-run-id")
    args = parser.parse_args()

    if not os.path.isfile(args.db):
        logger.error("Database not found: %s — run run_clause_store.py first", args.db)
        return 1

    pipeline_run_id = args.pipeline_run_id or f"dse011_v1_{int(time.time())}"
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S")

    conn = init_db(args.db)
    insert_pipeline_run(conn, PipelineRun(id=pipeline_run_id, started_at=started_at))

    policies_dir = os.path.join(args.gold_corpus, "policies")
    slugs = sorted(
        s
        for s in os.listdir(policies_dir)
        if os.path.isfile(os.path.join(policies_dir, s, "metadata.json"))
    )

    results = []
    had_failure = False

    for slug in slugs:
        try:
            result = process_policy(
                slug,
                args.gold_corpus,
                args.candidates_root,
                args.resolved_root,
                conn,
                pipeline_run_id,
            )
            results.append(result)
            if result["status"] != "ok":
                had_failure = True
        except Exception as exc:
            logger.exception("FATAL error processing %s: %s", slug, exc)
            results.append({"slug": slug, "status": "fatal_error", "error": str(exc)})
            had_failure = True

    finished_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    success_count = sum(1 for r in results if r["status"] == "ok")
    update_pipeline_run_finished(
        conn,
        pipeline_run_id,
        "completed" if not had_failure else "partial_failure",
        finished_at,
        success_count,
        len(slugs) - success_count,
    )

    fk_violations = count_dangling_fks(conn)
    table_counts = get_table_counts(conn)
    conn.close()

    summary = {
        "pipeline_run_id": pipeline_run_id,
        "date": time.strftime("%Y-%m-%d"),
        "policies_processed": len(results),
        "policies_ok": success_count,
        "fk_violations": fk_violations,
        "table_row_counts": table_counts,
        "policy_results": results,
    }
    summary_path = "data/reports/dse011_fact_scoring_summary.json"
    _write_json(summary_path, summary)
    logger.info("Summary written to %s", summary_path)

    total_cands = sum(r.get("db_candidates", 0) for r in results if r.get("status") == "ok")
    total_facts = sum(r.get("db_facts", 0) for r in results if r.get("status") == "ok")
    total_conflicts = sum(
        r.get("conflicts_detected", 0) for r in results if r.get("status") == "ok"
    )
    logger.info(
        "Done: %d/%d policies | %d candidates | %d facts | %d conflicts | %d FK violations",
        success_count,
        len(slugs),
        total_cands,
        total_facts,
        total_conflicts,
        fk_violations,
    )

    return 1 if had_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
