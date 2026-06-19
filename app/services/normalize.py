"""Persian (Farsi) text normalization.

Persian text appears in inconsistent character forms — Arabic vs Persian yeh/kaf,
Arabic-Indic vs Persian digits, optional ZWNJ, diacritics, tatweel. The *same*
word written two ways produces different tokens/embeddings and silently fails to
match at search time.

Normalizing all text to one canonical form — applied to BOTH documents (at
ingestion) and queries (at search time) — removes these mismatches. It is the
cheapest, deterministic retrieval-quality win for a Persian/mixed corpus.

ASCII content (English words, part numbers like "PVC-20G", Western digits) is
left untouched, so the high-value structured data is unaffected.
"""
import re
import unicodedata

# Arabic letter forms -> their Persian equivalents.
_CHAR_MAP = {
    "ي": "ی",  # Arabic yeh     -> Persian yeh
    "ى": "ی",  # alef maksura   -> Persian yeh
    "ك": "ک",  # Arabic kaf     -> Persian keheh
    "ة": "ه",  # teh marbuta    -> heh
    "أ": "ا",  # alef + hamza   -> bare alef
    "إ": "ا",
    "ٱ": "ا",
}

# Arabic-Indic digits (U+0660-0669) -> Persian digits (U+06F0-06F9).
_DIGIT_MAP = {chr(0x0660 + i): chr(0x06F0 + i) for i in range(10)}

# Characters dropped entirely: tatweel/kashida and zero-width marks (incl. ZWNJ).
_REMOVE = ["ـ", "‌", "‍", "​", "﻿"]

# Build one translation table: char swaps + digit swaps + deletions.
_TRANSLATION = {ord(k): v for k, v in {**_CHAR_MAP, **_DIGIT_MAP}.items()}
_TRANSLATION.update({ord(c): None for c in _REMOVE})

# Arabic diacritics / harakat (fatha, kasra, damma, sukun, superscript alef, ...).
_DIACRITICS = re.compile("[ً-ْٰ]")


def normalize(text: str) -> str:
    """Return a canonical form of Persian/mixed text for consistent matching."""
    if not text:
        return text
    # NFKC also folds Arabic presentation-form glyphs back to base letters.
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_TRANSLATION)   # letters, digits, removals in one pass
    text = _DIACRITICS.sub("", text)      # strip harakat
    text = re.sub(r"[ \t]+", " ", text)   # collapse runs of horizontal whitespace
    return text.strip()
