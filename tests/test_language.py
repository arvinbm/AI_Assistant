"""Tests for language detection."""
from app.services.language import detect_language


def test_pure_persian_is_fa():
    assert detect_language("این یک کتاب است") == "fa"


def test_pure_english_is_en():
    assert detect_language("this is a book") == "en"


def test_mixed_text_is_mixed():
    assert detect_language("این belt است PVC مدل dryer") == "mixed"


def test_mostly_persian_with_one_english_letter_stays_fa():
    # A long Persian sentence with a single English letter stays 'fa' (>=90% Persian).
    assert detect_language("این تسمه نقاله صنعتی بسیار مقاوم و بادوام است x") == "fa"


def test_digits_only_is_unknown():
    # Persian digits live in the Arabic block but must NOT count as letters.
    assert detect_language("۲۰۱۵ 2015 ۳۴۵") == "unknown"


def test_punctuation_and_symbols_only_is_unknown():
    assert detect_language("!!! ... --- ###") == "unknown"


def test_empty_is_unknown():
    assert detect_language("") == "unknown"


def test_part_numbers_are_english():
    assert detect_language("PVC-20G 8M-1200 belt") == "en"
