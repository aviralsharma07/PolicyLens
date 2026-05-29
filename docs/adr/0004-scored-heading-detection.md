## 2026-05-29 — ADR-0004: Scored Heading Detection Over Binary Classification

**Status:** accepted

**Decision:** Use scored heading detection instead of binary. Each candidate line gets a score based on numbering pattern (+0.3), font above body mean (+0.25), bold/italic (+0.15), spacing (+0.1), heading dictionary match (+0.1), TOC match (+0.1), with penalties for sentence-like text (-0.3), too long (-0.2), footer/header position (-0.3), and all-caps false positives (-0.2). Default acceptance threshold: 0.5.

**Context:** Insurance PDFs use wildly different heading styles (numbered, SECTION X, all-caps, bold without numbering — 6+ distinct patterns across 5 test PDFs). Binary heading detection fails on any style it wasn't explicitly configured for, requiring per-insurer configuration.

**Options considered:**
1. Binary regex-only heading detection
2. ML classifier for heading detection
3. Scored heading detection with heuristics (chosen)

**Reasoning:** Scored detection works across different heading styles without per-insurer configuration. The score threshold is tunable per phase (lower for candidate generation, higher for final tree). Feature breakdown helps debugging. ML is overkill — scored heuristics + small gold corpus will match or beat ML with far less complexity. Binary regex is too brittle.

**Consequences:**
- Positive: Works across heading styles without per-insurer config.
- Positive: Score threshold tunable per phase.
- Positive: Feature breakdown aids debugging.
- Negative: Requires font-size distribution calculation per document.
- Negative: Threshold tuning needs gold corpus validation.

**Revisit when:** Heading precision < 90% or recall < 80% on gold corpus after tuning. Consider ML classifier if heuristics fail to reach targets across 20+ diverse insurers.
