"""
Insurer registry — DSE-015

Canonical insurer records for all 32 lifecycle insurers.
ADR-0032: Registry is the single source of truth for insurer identity.

Subsumes FOLDER_TO_LIFECYCLE from DSE-002 insurer_normalizer.py.
Old API preserved for backward compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# InsurerRecord
# ---------------------------------------------------------------------------


@dataclass
class InsurerRecord:
    canonical_name: str  # Official short name used in lifecycle data
    legal_name: str  # Full legal entity name
    display_name: str  # For Product B UI (usually == canonical_name)
    folder_aliases: List[str]  # Corpus folder names that map to this insurer
    irdai_prefix: str = ""  # 3-char IRDAI insurer code from UIN (e.g., "CHI", "HDF")


# ---------------------------------------------------------------------------
# The 32-insurer registry
# ---------------------------------------------------------------------------

_REGISTRY_LIST: List[InsurerRecord] = [
    InsurerRecord("Acko General Insurance", "Acko General Insurance Limited", "Acko", [], "ACK"),
    InsurerRecord(
        "Aditya Birla Health Insurance",
        "Aditya Birla Health Insurance Co. Limited",
        "Aditya Birla",
        ["Aditya_Birla"],
        "ABI",
    ),
    InsurerRecord(
        "Apollo Munich Health Insurance",
        "Apollo Munich Health Insurance Co. Limited",
        "Apollo Munich",
        [],
        "APO",
    ),
    InsurerRecord(
        "Bajaj Allianz General Insurance",
        "Bajaj Allianz General Insurance Co. Limited",
        "Bajaj Allianz",
        ["Bajaj_Allianz"],
        "BAJ",
    ),
    InsurerRecord(
        "Bharti AXA General Insurance",
        "Bharti AXA General Insurance Co. Limited",
        "Bharti AXA",
        [],
        "BHA",
    ),
    InsurerRecord(
        "CIGNA TTK Health Insurance",
        "CIGNA TTK Health Insurance Co. Limited",
        "CIGNA TTK",
        [],
        "CIG",
    ),
    InsurerRecord(
        "Care Health", "Care Health Insurance Limited", "Care Health", ["Care_Health"], "CHI"
    ),
    InsurerRecord(
        "Cholamandalam MS General Insurance",
        "Cholamandalam MS General Insurance Co. Limited",
        "Cholamandalam",
        ["Cholamandalam"],
        "CHO",
    ),
    InsurerRecord("DHFL General Insurance", "DHFL General Insurance Limited", "DHFL", [], "DHF"),
    InsurerRecord(
        "Edelweiss General Insurance",
        "Edelweiss General Insurance Co. Limited",
        "Edelweiss",
        ["Edelweiss"],
        "EDL",
    ),
    InsurerRecord(
        "Future Generali India Insurance",
        "Future Generali India Insurance Co. Limited",
        "Future Generali",
        ["Future_Generali"],
        "FGI",
    ),
    InsurerRecord(
        "Go Digit General Insurance", "Go Digit General Insurance Limited", "Go Digit", [], "GDG"
    ),
    InsurerRecord(
        "HDFC ERGO", "HDFC ERGO General Insurance Co. Limited", "HDFC ERGO", ["HDFC_ERGO"], "HDF"
    ),
    InsurerRecord(
        "ICICI Lombard",
        "ICICI Lombard General Insurance Co. Limited",
        "ICICI Lombard",
        ["ICICI_Lombard"],
        "ICI",
    ),
    InsurerRecord(
        "IFFCO Tokio General Insurance",
        "IFFCO Tokio General Insurance Co. Limited",
        "IFFCO Tokio",
        ["IFFCO_Tokio"],
        "IFF",
    ),
    InsurerRecord(
        "Kotak Mahindra General Insurance",
        "Kotak Mahindra General Insurance Co. Limited",
        "Kotak Mahindra",
        ["Kotak_Mahindra"],
        "KOT",
    ),
    InsurerRecord(
        "Liberty General Insurance",
        "Liberty General Insurance Limited",
        "Liberty",
        ["Liberty"],
        "LIB",
    ),
    InsurerRecord(
        "Magma HDI General Insurance",
        "Magma HDI General Insurance Co. Limited",
        "Magma HDI",
        ["Magma_HDI"],
        "MAG",
    ),
    InsurerRecord(
        "National Insurance", "National Insurance Co. Limited", "National Insurance", [], "NAT"
    ),
    InsurerRecord("Navi General Insurance", "Navi General Insurance Limited", "Navi", [], "NAV"),
    InsurerRecord(
        "New India Assurance",
        "The New India Assurance Co. Limited",
        "New India",
        ["New_India_Assurance"],
        "NIA",
    ),
    InsurerRecord(
        "Niva Bupa", "Niva Bupa Health Insurance Co. Limited", "Niva Bupa", ["Niva_Bupa"], "NIV"
    ),
    InsurerRecord(
        "Oriental Insurance",
        "The Oriental Insurance Co. Limited",
        "Oriental",
        ["Oriental_Insurance"],
        "ORI",
    ),
    InsurerRecord(
        "Raheja QBE General Insurance",
        "Raheja QBE General Insurance Co. Limited",
        "Raheja QBE",
        ["Raheja_QBE"],
        "RAH",
    ),
    InsurerRecord(
        "Reliance General Insurance",
        "Reliance General Insurance Co. Limited",
        "Reliance",
        ["Reliance"],
        "REL",
    ),
    InsurerRecord(
        "Royal Sundaram General Insurance",
        "Royal Sundaram General Insurance Co. Limited",
        "Royal Sundaram",
        ["Royal_Sundaram"],
        "ROY",
    ),
    InsurerRecord(
        "SBI General Insurance",
        "SBI General Insurance Co. Limited",
        "SBI General",
        ["SBI_General"],
        "SBI",
    ),
    InsurerRecord(
        "Shriram General Insurance", "Shriram General Insurance Co. Limited", "Shriram", [], "SHR"
    ),
    InsurerRecord(
        "Star Health",
        "Star Health and Allied Insurance Co. Limited",
        "Star Health",
        ["Star_Health"],
        "SHA",
    ),
    InsurerRecord(
        "Tata AIG General Insurance",
        "Tata AIG General Insurance Co. Limited",
        "Tata AIG",
        ["Tata_AIG"],
        "TAT",
    ),
    InsurerRecord(
        "United India Insurance",
        "United India Insurance Co. Limited",
        "United India",
        ["United_India"],
        "UNI",
    ),
    InsurerRecord(
        "Universal Sompo General Insurance",
        "Universal Sompo General Insurance Co. Limited",
        "Universal Sompo",
        ["Universal_Sompo"],
        "UNS",
    ),
]

# ---------------------------------------------------------------------------
# Lookup indexes (built once at import time)
# ---------------------------------------------------------------------------

INSURER_REGISTRY: Dict[str, InsurerRecord] = {r.canonical_name: r for r in _REGISTRY_LIST}

_BY_FOLDER: Dict[str, InsurerRecord] = {}
for _rec in _REGISTRY_LIST:
    for _alias in _rec.folder_aliases:
        _BY_FOLDER[_alias] = _rec

_BY_DISPLAY: Dict[str, InsurerRecord] = {r.display_name.lower(): r for r in _REGISTRY_LIST}

_BY_PREFIX: Dict[str, InsurerRecord] = {r.irdai_prefix: r for r in _REGISTRY_LIST if r.irdai_prefix}

# Collect all known insurer name variants for plan-name stripping
ALL_INSURER_NAMES: List[str] = sorted(
    set(
        [r.canonical_name for r in _REGISTRY_LIST]
        + [r.display_name for r in _REGISTRY_LIST]
        + [r.legal_name for r in _REGISTRY_LIST]
        + [alias for r in _REGISTRY_LIST for alias in r.folder_aliases]
    ),
    key=len,
    reverse=True,  # longest first for greedy matching
)


# ---------------------------------------------------------------------------
# Lookup functions
# ---------------------------------------------------------------------------


def lookup_by_canonical(name: str) -> Optional[InsurerRecord]:
    """Lookup by canonical lifecycle name (exact match)."""
    return INSURER_REGISTRY.get(name)


def lookup_by_folder(folder_name: str) -> Optional[InsurerRecord]:
    """Lookup by corpus folder name (e.g., 'HDFC_ERGO')."""
    return _BY_FOLDER.get(folder_name)


def lookup_by_irdai_prefix(prefix: str) -> Optional[InsurerRecord]:
    """Lookup by 3-char IRDAI prefix from UIN (e.g., 'HDF')."""
    return _BY_PREFIX.get(prefix.upper()[:3])


def get_display_name(canonical_or_folder: str) -> str:
    """Get display name for an insurer. Returns input if not found."""
    rec = lookup_by_canonical(canonical_or_folder) or lookup_by_folder(canonical_or_folder)
    return rec.display_name if rec else canonical_or_folder


def get_all_name_variants(canonical_name: str) -> List[str]:
    """Get all known name variants for plan-name stripping."""
    rec = lookup_by_canonical(canonical_name)
    if not rec:
        return [canonical_name]
    return sorted(
        set([rec.canonical_name, rec.display_name, rec.legal_name] + rec.folder_aliases),
        key=len,
        reverse=True,
    )
