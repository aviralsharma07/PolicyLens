import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

FOLDER_TO_LIFECYCLE: Dict[str, str] = {
    "New_India_Assurance": "New India Assurance",
    "Star_Health": "Star Health",
    "Care_Health": "Care Health",
    "ICICI_Lombard": "ICICI Lombard",
    "Niva_Bupa": "Niva Bupa",
    "United_India": "United India Insurance",
    "Oriental_Insurance": "Oriental Insurance",
    "Bajaj_Allianz": "Bajaj Allianz General Insurance",
    "HDFC_ERGO": "HDFC ERGO",
    "Tata_AIG": "Tata AIG General Insurance",
    "Aditya_Birla": "Aditya Birla Health Insurance",
    "IFFCO_Tokio": "IFFCO Tokio General Insurance",
    "Future_Generali": "Future Generali India Insurance",
    "Universal_Sompo": "Universal Sompo General Insurance",
    "Magma_HDI": "Magma HDI General Insurance",
    "Kotak_Mahindra": "Kotak Mahindra General Insurance",
    "Reliance": "Reliance General Insurance",
    "Cholamandalam": "Cholamandalam MS General Insurance",
    "Liberty": "Liberty General Insurance",
    "SBI_General": "SBI General Insurance",
    "Royal_Sundaram": "Royal Sundaram General Insurance",
    "Edelweiss": "Edelweiss General Insurance",
    "Raheja_QBE": "Raheja QBE General Insurance",
}

LIFECYCLE_TO_FOLDER: Dict[str, str] = {v: k for k, v in FOLDER_TO_LIFECYCLE.items()}

FOLDER_ABBREVIATIONS: Dict[str, List[str]] = {
    "New_India_Assurance": ["NewIndia", "New_India"],
    "Star_Health": ["Star"],
    "Care_Health": ["Care"],
    "ICICI_Lombard": ["ICICI"],
    "Niva_Bupa": ["Niva", "NivaBupa"],
    "United_India": ["United", "UnitedIndia"],
    "Oriental_Insurance": ["Oriental"],
    "Bajaj_Allianz": ["Bajaj"],
    "HDFC_ERGO": ["HDFC", "HDFCERGO"],
    "Tata_AIG": ["Tata"],
    "Aditya_Birla": ["Aditya"],
    "IFFCO_Tokio": ["IFFCO"],
    "Future_Generali": ["Future"],
    "Universal_Sompo": ["Universal"],
    "Magma_HDI": ["Magma"],
    "Kotak_Mahindra": ["Kotak"],
    "Reliance": ["Reliance"],
    "Cholamandalam": ["Cholamandalam"],
    "Liberty": ["Liberty"],
    "SBI_General": ["SBI"],
    "Royal_Sundaram": ["Royal"],
    "Edelweiss": ["Edelweiss"],
    "Raheja_QBE": ["Raheja"],
}


def normalize(folder_insurer: str) -> Optional[str]:
    if folder_insurer in FOLDER_TO_LIFECYCLE:
        return FOLDER_TO_LIFECYCLE[folder_insurer]
    return None


def reverse_normalize(lifecycle_insurer: str) -> Optional[str]:
    if lifecycle_insurer in LIFECYCLE_TO_FOLDER:
        return LIFECYCLE_TO_FOLDER[lifecycle_insurer]
    for k, v in FOLDER_TO_LIFECYCLE.items():
        if v.lower() == lifecycle_insurer.lower():
            return k
    for k, v in FOLDER_TO_LIFECYCLE.items():
        if lifecycle_insurer.lower() in v.lower() or v.lower() in lifecycle_insurer.lower():
            return k
    return None


def get_abbreviations(folder_insurer: str) -> List[str]:
    return FOLDER_ABBREVIATIONS.get(folder_insurer, [])


def validate_all_mappings(entries: List[dict]) -> dict:
    folder_insurers = sorted(set(e["insurer"] for e in entries))
    results = {}
    for fi in folder_insurers:
        lc = normalize(fi)
        results[fi] = {
            "folder_insurer": fi,
            "lifecycle_insurer": lc,
            "has_mapping": lc is not None,
        }
        if lc is None:
            logger.warning("No lifecycle mapping for folder insurer: %s", fi)
    return results
