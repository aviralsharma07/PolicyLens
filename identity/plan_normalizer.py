"""
Plan name normalizer — DSE-015

Cleans raw plan names from lifecycle data / gold metadata:
  - Strips insurer suffixes: ", HDFC ERGO"
  - Strips generic boilerplate: "Insurance Policy", "Policy"
  - Produces display_name and short_name for Product B UI

ADR-0031: Plan name normalization strips insurer suffix and generic boilerplate.
"""

from __future__ import annotations

import re
from typing import List, Optional

from identity.insurer_registry import ALL_INSURER_NAMES

# ---------------------------------------------------------------------------
# Boilerplate patterns to strip (order matters — longest first)
# ---------------------------------------------------------------------------

_BOILERPLATE_SUFFIXES = [
    r"\s+Insurance\s+Policy\s*$",
    r"\s+Policy\s+Document\s*$",
    r"\s+Policy\s+Wording\s*$",
    r"\s+Policy\s*$",
    r"\s+Individual\s*$",
    r"\s+Group\s*$",
    r"\s+Retail\s*$",
    r"\s+Plan\s*$",
]

_SHORT_NAME_MAX = 35


def _build_insurer_suffix_patterns() -> List[re.Pattern]:
    """Build regex patterns to strip insurer names from plan names."""
    patterns = []
    for name in ALL_INSURER_NAMES:
        if len(name) < 3:
            continue
        escaped = re.escape(name)
        # Match as suffix: ", HDFC ERGO" or " - Star Health" or " HDFC ERGO" at end
        patterns.append(re.compile(r"[,\s\-]+\s*" + escaped + r"\s*$", re.IGNORECASE))
        # Match as prefix: "HDFC ERGO " or "New India " at start
        patterns.append(re.compile(r"^" + escaped + r"\s+", re.IGNORECASE))
    return patterns


_INSURER_PATTERNS = _build_insurer_suffix_patterns()


def clean_plan_name(raw_name: str, insurer_canonical: Optional[str] = None) -> str:
    """
    Clean a raw plan name by stripping insurer references and boilerplate.

    Examples:
      "Arogya Sanjeevani Policy, HDFC ERGO" → "Arogya Sanjeevani"
      "Medi Classic Accident Care Individual Insurance Policy" → "Medi Classic Accident Care"
      "New India Floater Mediclaim Policy" → "Floater Mediclaim"
      "Care Plus" → "Care Plus"  (already clean)
      "Family Shield" → "Family Shield"  (already clean)
    """
    if not raw_name:
        return raw_name or ""

    name = raw_name.strip()

    # Normalize non-breaking spaces and collapse whitespace
    name = name.replace("\xa0", " ")
    name = re.sub(r"\s+", " ", name).strip()

    # If a specific insurer is provided, strip it first (most precise)
    if insurer_canonical:
        from identity.insurer_registry import get_all_name_variants

        variants = get_all_name_variants(insurer_canonical)
        for variant in variants:
            if len(variant) < 3:
                continue
            # Strip as suffix
            pattern = re.compile(r"[,\s\-]+\s*" + re.escape(variant) + r"\s*$", re.IGNORECASE)
            name = pattern.sub("", name)
            # Strip as prefix
            pattern = re.compile(r"^" + re.escape(variant) + r"\s+", re.IGNORECASE)
            name = pattern.sub("", name)

    # Strip broad insurer legal entity suffixes:
    # ", TATA AIG General Insurance Company Limited" etc.
    name = re.sub(
        r"[,\s]+[A-Z][A-Za-z\s]*(?:Company|Co\.)\s+Limited\s*$", "", name, flags=re.IGNORECASE
    )

    # Strip generic boilerplate suffixes
    for pattern_str in _BOILERPLATE_SUFFIXES:
        name = re.sub(pattern_str, "", name, flags=re.IGNORECASE)

    # Apply general insurer suffix patterns if no specific insurer given
    if not insurer_canonical:
        for pattern in _INSURER_PATTERNS:
            name = pattern.sub("", name)

    return name.strip(" ,\t-")


def make_display_name(canonical_plan_name: str, insurer_display: str) -> str:
    """
    Create display name: "{insurer_display} {canonical_plan_name}"
    For Product B comparison UI where insurer context is needed.

    "Arogya Sanjeevani" + "HDFC ERGO" → "HDFC ERGO Arogya Sanjeevani"
    """
    if not canonical_plan_name:
        return insurer_display or ""
    if not insurer_display:
        return canonical_plan_name
    return f"{insurer_display} {canonical_plan_name}"


def make_short_name(canonical_plan_name: str) -> str:
    """
    Short name for compact UI. Max 35 chars.
    Truncates at word boundary if too long.
    """
    if not canonical_plan_name:
        return ""
    if len(canonical_plan_name) <= _SHORT_NAME_MAX:
        return canonical_plan_name
    # Truncate at word boundary
    truncated = canonical_plan_name[:_SHORT_NAME_MAX]
    last_space = truncated.rfind(" ")
    if last_space > 15:
        truncated = truncated[:last_space]
    return truncated.rstrip(" ,\t-")
