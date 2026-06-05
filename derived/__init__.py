"""
derived — DSE-013/DSE-023: Product B JSON Export

Builds Product B consumable JSON from SQLite engine data.
Produces three files per policy:
  policy_features.json         — 20-concept derived feature view
  policy_fact_sources.json     — full evidence provenance per concept
  policy_clauses_minimal.json  — lightweight clause context
"""
