"""Text extraction from documents.

Extracts plain text from in-memory document bytes.

PDFs are parsed with PyMuPDF (fitz); scanned / image-only pages have no text
layer and yield nothing, so a document with no extractable text is reported as
empty and skipped by the caller. Plain ``.txt`` content is decoded directly.
"""
from pathlib import Path

import fitz  # PyMuPDF

# Documents with fewer than this many non-whitespace characters are treated as empty.
MIN_TEXT_CHARS = 50


def extract_text(content: bytes, filename: str) -> str:
    """Extract plain text from a document's raw bytes.

    Args:
        content: The raw bytes of the document.
        filename: The original filename, used to detect the type (.pdf / .txt).

    Returns:
        The combined text of the document, or an empty string if it has no extractable text.

    Raises:
        ValueError: If the file type is not supported.
    """
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        text = _extract_pdf(content)
    elif suffix == ".txt":
        text = content.decode("utf-8", errors="replace")
    else:
        raise ValueError(f"Unsupported file type: '{suffix}'")

    # Treat near-empty extractions as empty so the caller can skip them.
    if len("".join(text.split())) < MIN_TEXT_CHARS:
        return ""
    return text


def _extract_pdf(content: bytes) -> str:
    """Parse PDF bytes with PyMuPDF and concatenate the text of every page."""
    doc = fitz.open(stream=content, filetype="pdf")
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()
