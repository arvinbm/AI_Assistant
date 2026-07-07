"""Tests for the document storage layer (local filesystem / mounted volume)."""
import pytest

from app.services import storage


def test_store_document_writes_file(monkeypatch, tmp_path):
    """A document is written under the storage dir and its path is returned."""
    monkeypatch.setattr(storage, "UPLOAD_DIR", tmp_path)

    ref = storage.store_document(b"hello world", "sub/manual.pdf")

    written = tmp_path / "sub" / "manual.pdf"
    assert written.read_bytes() == b"hello world"  # bytes stored correctly
    assert ref == str(written)                      # returns the file path


def test_load_document_round_trip(monkeypatch, tmp_path):
    """A stored document can be read back byte-for-byte."""
    monkeypatch.setattr(storage, "UPLOAD_DIR", tmp_path)

    storage.store_document(b"hello", "sub/a.txt")

    assert storage.load_document("sub/a.txt") == b"hello"


def test_load_document_missing_raises_filenotfound(monkeypatch, tmp_path):
    """A missing file raises FileNotFoundError."""
    monkeypatch.setattr(storage, "UPLOAD_DIR", tmp_path)

    with pytest.raises(FileNotFoundError):
        storage.load_document("nope.txt")
