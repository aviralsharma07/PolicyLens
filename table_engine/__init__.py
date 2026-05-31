"""
table_engine — DSE-009 Table Engine v1

Two-tier table detection:
  Primary:  pdfplumber lattice (visible grid lines) → pdfplumber_lattice
  Fallback: text alignment heuristics (borderless) → text_alignment_candidate

Extraction method is always recorded. Uncertain cells are never silently flattened.
"""
