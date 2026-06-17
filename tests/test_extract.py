"""Tests for the text extraction layer."""
import fitz  # PyMuPDF
import pytest

from app.services.extract import extract_text


def _make_pdf(text: str) -> bytes:
    """Build a one-page PDF containing ``text`` and return its raw bytes."""
    doc = fitz.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def test_extract_pdf_returns_text():
    """A PDF with a real text layer yields its text."""
    content = _make_pdf("Industrial conveyor belt specification sheet for testing.")
    result = extract_text(content, "spec.pdf")
    assert "conveyor belt" in result.lower()


def test_extract_txt_decodes_bytes():
    """A .txt file's bytes are decoded as UTF-8 text."""
    content = (
        "Payvand industrial conveyor belts catalogue line item entry for testing."
    ).encode("utf-8")
    result = extract_text(content, "notes.txt")
    assert "Payvand" in result


def test_empty_pdf_returns_empty_string():
    """A PDF with no text layer (e.g. scanned) is reported as empty."""
    content = _make_pdf("")  # blank page, no text
    assert extract_text(content, "blank.pdf") == ""


def test_below_threshold_returns_empty_string():
    """Text shorter than MIN_TEXT_CHARS is treated as empty."""
    content = b"hi"  # far fewer than 50 characters
    assert extract_text(content, "tiny.txt") == ""


def test_unsupported_type_raises():
    """An unsupported extension raises a clear ValueError."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(b"data", "image.png")
