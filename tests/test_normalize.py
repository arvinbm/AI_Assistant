"""Tests for Persian text normalization."""
from app.services.normalize import normalize


def test_arabic_letters_become_persian():
    assert normalize("كتاب") == "کتاب"   # Arabic kaf -> Persian kaf
    assert normalize("يك") == "یک"        # Arabic yeh + kaf -> Persian


def test_arabic_digits_become_persian():
    assert normalize("٢٠١٥") == "۲۰۱۵"    # Arabic-Indic -> Persian digits


def test_zwnj_is_removed():
    assert normalize("می‌رود") == "میرود"   # zero-width non-joiner stripped


def test_tatweel_is_removed():
    assert normalize("كــــتاب") == "کتاب"  # kashida/tatweel stretching removed


def test_diacritics_are_removed():
    assert normalize("مُحَمَّد") == "محمد"      # harakat stripped


def test_ascii_is_left_untouched():
    # English words, part numbers, and Western digits must pass through unchanged.
    assert normalize("PVC-20G belt") == "PVC-20G belt"


def test_whitespace_is_collapsed_and_trimmed():
    assert normalize("  عرض   20    میل  ") == "عرض 20 میل"


def test_normalization_is_idempotent():
    text = "كتاب می‌رود ٢٠"
    assert normalize(normalize(text)) == normalize(text)


def test_match_is_restored_between_forms():
    # The whole point: the same word in Arabic vs Persian forms now matches.
    assert normalize("يك كتاب") == normalize("یک کتاب")


def test_empty_input_returns_empty():
    assert normalize("") == ""
