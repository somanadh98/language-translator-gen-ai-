from langdetect import detect, DetectorFactory
from .lang_map import iso_to_nllb
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """Returns an NLLB-style language code when possible, or None.
    Uses langdetect to get an ISO-639-1 code then maps via lang_map.iso_to_nllb.
    """
    try:
        iso = detect(text)
        nllb = iso_to_nllb(iso)
        return nllb
    except Exception:
        return None
