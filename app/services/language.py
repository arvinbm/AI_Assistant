"""Lightweight language tagging for chunks.

The corpus is specifically Persian + English, so instead of a general-purpose
(probabilistic) language detector we use a simple, deterministic script-based
heuristic: count Persian/Arabic-script letters vs Latin letters and compare the
ratio. Digits, punctuation, and whitespace are ignored.

The result ("fa" / "en" / "mixed" / "unknown") is stored as chunk metadata for
debugging and optional weighting — NOT as a hard retrieval filter, since mixed
chunks would otherwise be wrongly excluded.
"""

# A chunk is "fa" if at least this fraction of its letters are Persian-script,
# "en" if at most (1 - this) are, and "mixed" in between.
FA_THRESHOLD = 0.9
EN_THRESHOLD = 0.1


def _script(ch: str) -> str | None:
    """Classify a single character as 'fa', 'en', or None (ignored).

    Only letters are counted; digits (incl. Persian/Arabic-Indic, which live in
    the Arabic block), punctuation, and whitespace are ignored.
    """
    if not ch.isalpha():
        return None
    code = ord(ch)
    if 0x0600 <= code <= 0x06FF or 0x0750 <= code <= 0x077F or 0xFB50 <= code <= 0xFEFF:
        return "fa"   # Arabic/Persian script blocks (incl. presentation forms)
    if "a" <= ch <= "z" or "A" <= ch <= "Z":
        return "en"
    return None       # other scripts -> not counted


def detect_language(text: str) -> str:
    """Return the dominant language of text: 'fa', 'en', 'mixed', or 'unknown'."""
    fa = en = 0
    for ch in text:
        script = _script(ch)
        if script == "fa":
            fa += 1
        elif script == "en":
            en += 1

    total = fa + en
    if total == 0:
        return "unknown"   # no letters (e.g. only digits/symbols)

    fa_ratio = fa / total
    if fa_ratio >= FA_THRESHOLD:
        return "fa"
    if fa_ratio <= EN_THRESHOLD:
        return "en"
    return "mixed"
