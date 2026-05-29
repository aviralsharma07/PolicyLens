## 2026-05-30 — ADR-0012: Stack-Based Section Tree Builder With Synthetic Body-Numbered Sections

**Status:** accepted

**Decision:** Build the DSE-006 section tree using a stack-based algorithm over DSE-005 heading candidates sorted by reading order. Detect additional sub-sections from compact numbered body lines and selected structural all-caps body headings inside leaf sections as synthetic nodes.

**Context:** DSE-005 produces visual heading candidates (e.g., "3. Definitions") but correctly rejects long definition entries (e.g., "3.1. Accident means...") as body text. DSE-006 must build a complete section hierarchy that includes these sub-entries so that extractors can operate at the right granularity.

**Options considered:**
1. Recursive descent parser over numbering patterns.
2. ML classifier for section boundaries.
3. Stack-based tree builder + body-numbered detection (chosen).

**Reasoning:** Insurance policy numbering is not always well-formed (gaps, mixed styles, irregular nesting, compact no-space prefixes such as `2.1.1Accident`). A stack-based algorithm handles irregular hierarchies gracefully by relying on relative level changes rather than absolute numbering. Body-numbered detection recovers definition entries that DSE-005 correctly excluded.

**Consequences:**
- Positive: Handles irregular hierarchies (gaps, mixed styles).
- Positive: Recovers definition sub-entries without weakening DSE-005 heading precision.
- Positive: Synthetic nodes carry `heading_type = "synthetic_body_numbered"` for downstream awareness.
- Positive: Deterministic section IDs make generated artifacts diffable between runs.
- Negative: TOC duplicates must be deduplicated manually by preferring content-page vs TOC-page position.
- Negative: Synthetic node detection may introduce false sub-sections in policies with many numbered body lines.
- Negative: Clause boundary F1 remains a proxy until gold clauses carry physical line/span IDs.

**Revisit when:** Synthetic body-numbered detection produces >20% false positives on 20-policy gold corpus. Consider switching to a scoring approach for body-numbered candidates.
