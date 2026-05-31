-- DSE-010: Clause Store + Source Spans
-- SQLite DDL — all 19 tables.
-- Tables marked DEFERRED are defined here but not populated until DSE-011/DSE-013.
-- FK enforcement requires: PRAGMA foreign_keys = ON (set in init_db).
--
-- Build order respects FK dependency tiers:
--   Tier 0: pipeline_runs, products
--   Tier 1: product_versions, source_documents
--   Tier 2: document_pages
--   Tier 3: document_blocks
--   Tier 4: document_lines
--   Tier 5: document_text_spans           [DEFERRED — ADR-0017]
--   Tier 6: document_sections
--   Tier 7: policy_clauses
--   Tier 8: document_tables, document_table_cells
--   Tier 9: source_spans
--   Tier 10: document_issues
--   Tier 11: extracted_fact_candidates    [DEFERRED — DSE-011]
--   Tier 12: extracted_facts              [DEFERRED — DSE-011]
--   Tier 13: fact_conflicts               [DEFERRED — DSE-011]
--   Tier 14: validation_labels            [DEFERRED — DSE-011/013]
--   Tier 15: derived_policy_features      [DEFERRED — DSE-013]

-- ============================================================
-- Tier 0: no FK dependencies
-- ============================================================

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id                TEXT PRIMARY KEY,
    git_commit        TEXT,
    parser_version    TEXT,
    extractor_version TEXT,
    started_at        TEXT NOT NULL,
    finished_at       TEXT,
    status            TEXT NOT NULL DEFAULT 'running',
    input_count       INTEGER DEFAULT 0,
    success_count     INTEGER DEFAULT 0,
    failure_count     INTEGER DEFAULT 0,
    notes             TEXT
);

CREATE TABLE IF NOT EXISTS products (
    product_id            TEXT PRIMARY KEY,
    uin_base              TEXT NOT NULL,
    normalized_insurer    TEXT NOT NULL,
    normalized_plan_name  TEXT NOT NULL,
    product_type          TEXT NOT NULL DEFAULT 'health',
    insurance_type        TEXT NOT NULL DEFAULT 'individual'
);

-- ============================================================
-- Tier 1
-- ============================================================

CREATE TABLE IF NOT EXISTS product_versions (
    version_id      TEXT PRIMARY KEY,
    product_id      TEXT NOT NULL,
    full_uin        TEXT NOT NULL,
    version_label   TEXT,
    active_status   TEXT NOT NULL DEFAULT 'active',
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS source_documents (
    document_id     TEXT PRIMARY KEY,  -- equals file_hash (sha256:...)
    version_id      TEXT,
    policy_id       TEXT NOT NULL,
    document_type   TEXT NOT NULL DEFAULT 'policy_wording',
    source_pdf_path TEXT NOT NULL,
    file_hash       TEXT NOT NULL,
    page_count      INTEGER NOT NULL,
    parser_status   TEXT NOT NULL DEFAULT 'parsed',
    FOREIGN KEY(version_id) REFERENCES product_versions(version_id)
);

-- ============================================================
-- Tier 2
-- ============================================================

CREATE TABLE IF NOT EXISTS document_pages (
    page_id       TEXT PRIMARY KEY,   -- "{document_id}_p{page_number}"
    document_id   TEXT NOT NULL,
    page_number   INTEGER NOT NULL,
    width         REAL,
    height        REAL,
    rotation      INTEGER DEFAULT 0,
    FOREIGN KEY(document_id) REFERENCES source_documents(document_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_pages_doc_page
    ON document_pages(document_id, page_number);

-- ============================================================
-- Tier 3
-- ============================================================

CREATE TABLE IF NOT EXISTS document_blocks (
    block_id      TEXT PRIMARY KEY,
    page_id       TEXT NOT NULL,
    document_id   TEXT NOT NULL,
    block_type    TEXT,
    bbox_json     TEXT,
    reading_order INTEGER,
    FOREIGN KEY(page_id)     REFERENCES document_pages(page_id),
    FOREIGN KEY(document_id) REFERENCES source_documents(document_id)
);

-- ============================================================
-- Tier 4
-- ============================================================

CREATE TABLE IF NOT EXISTS document_lines (
    line_id               TEXT PRIMARY KEY,
    block_id              TEXT NOT NULL,
    document_id           TEXT NOT NULL,
    page_number           INTEGER NOT NULL,
    bbox_json             TEXT NOT NULL,
    text                  TEXT NOT NULL,
    region                TEXT,
    is_header_candidate   INTEGER NOT NULL DEFAULT 0,
    is_footer_candidate   INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(block_id)    REFERENCES document_blocks(block_id),
    FOREIGN KEY(document_id) REFERENCES source_documents(document_id)
);
CREATE INDEX IF NOT EXISTS idx_lines_doc_page
    ON document_lines(document_id, page_number);

-- ============================================================
-- Tier 5: DEFERRED — ADR-0017 (character-level spans not persisted)
-- 617K char-level spans stay in physical JSON. DB size stays bounded.
-- ============================================================

CREATE TABLE IF NOT EXISTS document_text_spans (
    span_id     TEXT PRIMARY KEY,
    line_id     TEXT NOT NULL,
    bbox_json   TEXT,
    text        TEXT,
    font_size   REAL,
    font_name   TEXT,
    is_bold     INTEGER DEFAULT 0,
    is_italic   INTEGER DEFAULT 0,
    FOREIGN KEY(line_id) REFERENCES document_lines(line_id)
);

-- ============================================================
-- Tier 6
-- ============================================================

-- heading_score and heading_type stored here per ADR-0021 (resolves OQ-001).
-- No separate heading_candidates table.
CREATE TABLE IF NOT EXISTS document_sections (
    section_id          TEXT PRIMARY KEY,
    document_id         TEXT NOT NULL,
    parent_id           TEXT,
    section_number      TEXT,
    title               TEXT,
    normalized_title    TEXT,
    level               INTEGER NOT NULL DEFAULT 0,
    heading_type        TEXT,    -- root|visual|synthetic_body_numbered|synthetic_body_heading
    heading_score       REAL,
    heading_line_id     TEXT,
    page_start          INTEGER NOT NULL DEFAULT 0,
    page_end            INTEGER NOT NULL DEFAULT 0,
    pipeline_run_id     TEXT NOT NULL,
    FOREIGN KEY(document_id)     REFERENCES source_documents(document_id),
    FOREIGN KEY(parent_id)       REFERENCES document_sections(section_id),
    FOREIGN KEY(pipeline_run_id) REFERENCES pipeline_runs(id)
);
CREATE INDEX IF NOT EXISTS idx_sections_doc
    ON document_sections(document_id);

-- ============================================================
-- Tier 7
-- ============================================================

CREATE TABLE IF NOT EXISTS policy_clauses (
    clause_id           TEXT PRIMARY KEY,
    document_id         TEXT NOT NULL,
    section_id          TEXT NOT NULL,
    clause_number       TEXT,
    title               TEXT,
    raw_text            TEXT NOT NULL,   -- full clause text, never truncated
    page_start          INTEGER NOT NULL,
    page_end            INTEGER NOT NULL,
    line_ids_json       TEXT NOT NULL,   -- JSON array of line IDs
    segmentation_method TEXT,
    confidence          REAL,
    pipeline_run_id     TEXT NOT NULL,
    FOREIGN KEY(document_id)     REFERENCES source_documents(document_id),
    FOREIGN KEY(section_id)      REFERENCES document_sections(section_id),
    FOREIGN KEY(pipeline_run_id) REFERENCES pipeline_runs(id)
);
CREATE INDEX IF NOT EXISTS idx_clauses_doc_page
    ON policy_clauses(document_id, page_start, page_end);

-- ============================================================
-- Tier 8
-- ============================================================

CREATE TABLE IF NOT EXISTS document_tables (
    table_id                 TEXT PRIMARY KEY,
    document_id              TEXT NOT NULL,
    page                     INTEGER NOT NULL,
    bbox_json                TEXT,
    parent_clause_id         TEXT,
    parent_clause_confidence REAL,
    extraction_method        TEXT,
    table_type               TEXT,
    table_type_confidence    REAL,
    row_count                INTEGER DEFAULT 0,
    col_count                INTEGER DEFAULT 0,
    has_header_row           INTEGER DEFAULT 0,
    issues_json              TEXT,
    FOREIGN KEY(document_id)      REFERENCES source_documents(document_id),
    FOREIGN KEY(parent_clause_id) REFERENCES policy_clauses(clause_id)
);
CREATE INDEX IF NOT EXISTS idx_tables_doc_page
    ON document_tables(document_id, page);

CREATE TABLE IF NOT EXISTS document_table_cells (
    cell_id             TEXT PRIMARY KEY,
    table_id            TEXT NOT NULL,
    row_index           INTEGER NOT NULL DEFAULT 0,
    col_index           INTEGER NOT NULL DEFAULT 0,
    text                TEXT NOT NULL DEFAULT '',
    bbox_json           TEXT,
    is_header           INTEGER NOT NULL DEFAULT 0,
    column_header_text  TEXT,
    row_header_text     TEXT,
    FOREIGN KEY(table_id) REFERENCES document_tables(table_id)
);
CREATE INDEX IF NOT EXISTS idx_cells_table
    ON document_table_cells(table_id);

-- ============================================================
-- Tier 9: source_spans — THE KEY TABLE
-- ADR-0018: page_regions_json handles cross-page spans
-- ADR-0019: char_start/char_end are clause-text offsets
-- ============================================================

CREATE TABLE IF NOT EXISTS source_spans (
    span_id             TEXT PRIMARY KEY,
    document_id         TEXT NOT NULL,
    clause_id           TEXT,
    table_cell_id       TEXT,
    span_type           TEXT NOT NULL
        CHECK(span_type IN ('clause_body','fact_evidence','table_cell','heading')),
    text                TEXT NOT NULL,
    char_start          INTEGER,
    char_end            INTEGER,
    -- JSON array: [{page: int, bbox: [x0,top,x1,bottom], line_ids: [...]}]
    page_regions_json   TEXT NOT NULL,
    pipeline_run_id     TEXT NOT NULL,
    FOREIGN KEY(document_id)     REFERENCES source_documents(document_id),
    FOREIGN KEY(clause_id)       REFERENCES policy_clauses(clause_id),
    FOREIGN KEY(pipeline_run_id) REFERENCES pipeline_runs(id)
);
CREATE INDEX IF NOT EXISTS idx_spans_clause
    ON source_spans(clause_id);
CREATE INDEX IF NOT EXISTS idx_spans_doc_type
    ON source_spans(document_id, span_type);

-- ============================================================
-- Tier 10
-- ============================================================

CREATE TABLE IF NOT EXISTS document_issues (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id     TEXT,
    pipeline_run_id TEXT NOT NULL,
    issue_type      TEXT NOT NULL,
    severity        TEXT NOT NULL DEFAULT 'warning'
        CHECK(severity IN ('error','warning','info')),
    page_number     INTEGER,
    description     TEXT NOT NULL,
    raw_context     TEXT,
    resolved        INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(document_id)     REFERENCES source_documents(document_id),
    FOREIGN KEY(pipeline_run_id) REFERENCES pipeline_runs(id)
);

-- ============================================================
-- Tiers 11–15: DEFERRED — DSE-011 / DSE-013
-- DDL exists for schema completeness; not populated by DSE-010.
-- ============================================================

CREATE TABLE IF NOT EXISTS extracted_fact_candidates (
    id               TEXT PRIMARY KEY,
    clause_id        TEXT NOT NULL,
    document_id      TEXT NOT NULL,
    concept          TEXT NOT NULL,
    candidate_value_json TEXT,
    evidence_span_id TEXT,
    extractor_name   TEXT,
    extractor_version TEXT,
    pattern_id       TEXT,
    normalizer_version TEXT,
    score            REAL DEFAULT 0.0,
    accepted         INTEGER DEFAULT 0,
    rejection_reason TEXT,
    pipeline_run_id  TEXT NOT NULL,
    FOREIGN KEY(clause_id)       REFERENCES policy_clauses(clause_id),
    FOREIGN KEY(evidence_span_id) REFERENCES source_spans(span_id),
    FOREIGN KEY(pipeline_run_id) REFERENCES pipeline_runs(id)
);

CREATE TABLE IF NOT EXISTS extracted_facts (
    id                    TEXT PRIMARY KEY,
    clause_id             TEXT NOT NULL,
    document_id           TEXT NOT NULL,
    concept               TEXT NOT NULL,
    value_json            TEXT,
    normalized_value_json TEXT,
    value_type            TEXT,
    scope_json            TEXT,
    condition_json        TEXT,
    extraction_method     TEXT,
    confidence            REAL DEFAULT 0.0,
    evidence_span_id      TEXT,
    pipeline_run_id       TEXT NOT NULL,
    fact_status           TEXT NOT NULL DEFAULT 'not_found',
    validated             INTEGER DEFAULT 0,
    validator             TEXT,
    FOREIGN KEY(clause_id)        REFERENCES policy_clauses(clause_id),
    FOREIGN KEY(evidence_span_id) REFERENCES source_spans(span_id),
    FOREIGN KEY(pipeline_run_id)  REFERENCES pipeline_runs(id)
);

CREATE TABLE IF NOT EXISTS fact_conflicts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    fact_a_id     TEXT NOT NULL,
    fact_b_id     TEXT NOT NULL,
    conflict_type TEXT,
    resolution    TEXT DEFAULT 'unresolved',
    resolved_by   TEXT,
    resolution_notes TEXT,
    FOREIGN KEY(fact_a_id) REFERENCES extracted_facts(id),
    FOREIGN KEY(fact_b_id) REFERENCES extracted_facts(id)
);

CREATE TABLE IF NOT EXISTS validation_labels (
    id                   TEXT PRIMARY KEY,
    document_id          TEXT NOT NULL,
    pipeline_run_id      TEXT NOT NULL,
    label_type           TEXT,
    concept              TEXT,
    expected_value_json  TEXT,
    expected_source_span TEXT,
    expected_page        INTEGER,
    annotator            TEXT,
    reviewed_by          TEXT,
    label_status         TEXT DEFAULT 'draft',
    notes                TEXT,
    FOREIGN KEY(document_id)     REFERENCES source_documents(document_id),
    FOREIGN KEY(pipeline_run_id) REFERENCES pipeline_runs(id)
);

CREATE TABLE IF NOT EXISTS derived_policy_features (
    id                     TEXT PRIMARY KEY,
    document_id            TEXT NOT NULL,
    pipeline_run_id        TEXT NOT NULL,
    feature_json           TEXT,
    feature_schema_version TEXT,
    created_at             TEXT,
    export_status          TEXT DEFAULT 'pending',
    FOREIGN KEY(document_id)     REFERENCES source_documents(document_id),
    FOREIGN KEY(pipeline_run_id) REFERENCES pipeline_runs(id)
);
