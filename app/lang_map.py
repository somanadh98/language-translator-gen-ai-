# Simple mapping from ISO-639-1 codes to NLLB-style codes (not exhaustive).
# Extend this map as needed for other languages.
COMMON_MAP = {
    'en': 'eng_Latn',
    'fr': 'fra_Latn',
    'de': 'deu_Latn',
    'es': 'spa_Latn',
    'pt': 'por_Latn',
    'hi': 'hin_Deva',
    'bn': 'ben_Beng',
    'ta': 'tam_Taml',
    'te': 'tel_Telu',
    'ml': 'mal_Mlym',
    'kn': 'kan_Knda',
    'mr': 'mar_Deva',
    'ur': 'urd_Arab',
    'ar': 'arb_Arab',
    'ru': 'rus_Cyrl',
    'ja': 'jpn_Jpan',
    'ko': 'kor_Hang',
    'zh': 'zho_Hans',  # simplified chinese; NLLB uses zho_Hans / zho_Hant
    'vi': 'vie_Latn',
    'id': 'ind_Latn',
    'nl': 'nld_Latn',
    'it': 'ita_Latn',
    'tr': 'tur_Latn'
}

def iso_to_nllb(iso_code: str) -> str | None:
    """Map a 2-letter ISO code to an NLLB-style code when possible.
    Returns None if mapping is unknown.
    """
    if not iso_code:
        return None
    iso = iso_code.lower()
    if iso in COMMON_MAP:
        return COMMON_MAP[iso]
    # Generic fallback: append _Latn for many latin-script languages
    if len(iso) == 2 and iso.isalpha():
        return f"{iso}_Latn"
    return None
