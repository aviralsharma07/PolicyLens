"""
UIN parsing utilities — DSE-015

Correct UIN base extraction using the V-delimiter, not fixed-length slicing.
ADR-0030: UIN base extraction uses V-delimiter.

IRDAI UIN format: {INSURER_CODE}{PRODUCT_CODE}V{VERSION_DIGITS}{FISCAL_YEAR_DIGITS}
Example: CHIHLIP22047V012122
  base   = CHIHLIP22047  (12 chars — everything before first V followed by digits)
  version = 01
  year    = 2122
"""

from __future__ import annotations

import re
from typing import Optional

# Pattern: letters+digits, then V followed by digits
_UIN_PATTERN = re.compile(r"^([A-Z]{3,}[A-Z0-9]+?)(V\d+)$", re.IGNORECASE)
_UIN_STRICT = re.compile(r"^[A-Z]{3}[A-Z]{2}[A-Z]{2,3}\d{5}V\d{6,8}$")


def extract_uin_base(full_uin: str) -> str:
    """
    Extract UIN base from a full IRDAI UIN.

    Uses the V-delimiter: everything before the first 'V' followed by digits.
    Falls back to the full string if no V-delimiter found.

    Examples:
      CHIHLIP22047V012122 → CHIHLIP22047
      HDFHLIP20175V011920 → HDFHLIP20175
      SHAHLIP18029V031718 → SHAHLIP18029
    """
    if not full_uin:
        return full_uin or ""

    m = _UIN_PATTERN.match(full_uin.strip())
    if m:
        return m.group(1)

    # Fallback: find the rightmost V preceded by alphanums
    idx = full_uin.rfind("V")
    if idx > 0 and idx < len(full_uin) - 1 and full_uin[idx + 1 :].isdigit():
        return full_uin[:idx]

    return full_uin


def extract_version_number(full_uin: str) -> Optional[int]:
    """
    Extract version number from a full IRDAI UIN.

    CHIHLIP22047V012122 → 1
    ICIHLIP22092V032122 → 3
    """
    if not full_uin:
        return None

    m = _UIN_PATTERN.match(full_uin.strip())
    if m:
        version_part = m.group(2)  # e.g., "V012122"
        # Version digits are the first 2 digits after V (before fiscal year)
        digits = version_part[1:]  # "012122"
        if len(digits) >= 2:
            try:
                return int(digits[:2])
            except ValueError:
                return None
    return None


def validate_uin_format(full_uin: str) -> bool:
    """
    Validate that a UIN matches the IRDAI format.

    Strict pattern: 3 letters insurer + 2 letters line + 2-3 letters sub + 5 digits + V + 6-8 digits
    """
    if not full_uin:
        return False
    return bool(_UIN_STRICT.match(full_uin.strip()))
