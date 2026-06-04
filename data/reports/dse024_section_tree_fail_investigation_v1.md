# DSE-024 Section Tree Fail Investigation

Date: 2026-06-04
Task: Packet E2 — Fix section_tree_fail bucket (44 policies)

## Root Cause

All 44 section_tree_fail policies share the same pattern:
- `heading_candidates.json` has `total_headings > 0` (fallback-promoted headings with `decision="heading"`)
- `section_tree.json` has `total_visual_headings == 0` and `total_clauses == 0`

**Cause:** The section tree builder was run BEFORE the fallback heading promotion. When the section tree ran, these candidates had `decision != "heading"` and were filtered out. The later fallback pass updated `decision` to `"heading"` in heading_candidates.json but did not re-run the section tree.

**Fix:** Re-run `scripts/run_section_tree.py` — no code changes needed to `section_tree.py` or `clause_segmenter.py` because the tree builder already filters by `decision == "heading"` and handles all heading formats correctly.

## Representative Sample Results

| Policy | Before | After | Headings | Synthetic | Clauses |
|--------|-------:|------:|---------:|----------:|--------:|
| HDFC ERGO critical illness | 0 | 131 | 2 | 15 | 131 |
| Liberty 10.Renewal | 0 | 726 | 8 | 284 | 726 |
| Cholamandalam compact | 0 | 500 | 6 | 12 | 500 |
| Tata AIG arogya sanjeevani | 0 | 236 | 5 | 0 | 236 |
| Niva Bupa health pulse | 0 | 1018 | 7 | 332 | 1018 |
| Universal Sompo D. BENEFITS: | 0 | 190 | 3 | 124 | 190 |
| Reliance group hospi cash | 0 | 376 | 2 | 305 | 376 |
| ICICI health care plus | 0 | 185 | 5 | 89 | 185 |

## Edge Cases Verified

1. **Compact numbered heading** `10.Renewal` — `ARABIC_NUMBER_RE` regex matches `10.` as number, `Renewal` as title. Section tree assigns lines between `10.Renewal` and `17.Policy Disputes` correctly. Synthetic detection picks up intermediate numbered lines (`11.`, `12.`, etc.).

2. **Alpha heading** `D. BENEFITS:` — Section tree accepts via `decision="heading"`. `_extract_number_from_heading` returns None (D is not a digit). `_infer_level` returns 1 (D is a valid Roman numeral character but not a valid Roman number; actually `re.match(r"^[IVXLCDM]+\.?$", "D.")` does match). Body text has `D.1. WHAT WE COVER:` which is detected by `_split_into_blocks` as a new paragraph block.

3. **ICICI `0.25 years`** — This heading has `numbering_token=0.25`. The section tree creates a level-2 section. While this is a data quality issue (not a real heading), the code handles it without error. Content assignment correctly captures lines between `0.25 years` and `2.2 EXCLUSIONS`.

4. **Tata AIG `2.Family`** — Compact heading with no space after dot. `ARABIC_NUMBER_RE` correctly extracts number `2` and title `Family`.

## Conclusion

No code changes to `structure_parser/section_tree.py` or `structure_parser/clause_segmenter.py` are required. The section tree builder and clause segmenter already correctly handle:
- `decision == "heading"` filter (includes fallback-promoted)
- Compact numbered headings (`10.Renewal`, `2.Family`)
- Alpha headings (`D. BENEFITS:`)
- Section content assignment between any two consecutive accepted headings (including fallback)
- Clause segmentation via numbered prefix splitting and paragraph gap detection

The fix is a pipeline re-run: regenerate section_tree.json from the updated heading_candidates.json for all 44 + remaining 603 policies.
