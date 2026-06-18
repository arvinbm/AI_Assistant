"""Tests for the text chunking layer."""
import pytest

from app.services.chunk import chunk_text


def test_overlap_not_smaller_than_chunk_size_raises():
    """overlap must be strictly smaller than chunk_size."""
    with pytest.raises(ValueError, match="overlap must be smaller"):
        chunk_text("abcdef", chunk_size=5, overlap=10)   # overlap > size
    with pytest.raises(ValueError, match="overlap must be smaller"):
        chunk_text("abcdef", chunk_size=5, overlap=5)    # overlap == size


def test_empty_text_returns_empty_list():
    """Empty or whitespace-only input yields no chunks."""
    assert chunk_text("") == []
    assert chunk_text("   \n\t ") == []


def test_short_text_returns_single_chunk():
    """Text shorter than chunk_size becomes one chunk equal to the text."""
    assert chunk_text("hello", chunk_size=10, overlap=3) == ["hello"]


def test_chunk_boundaries_and_leftover():
    """Chunks are sliced at the right offsets, last chunk is the leftover."""
    text = "abcdefghijklmnopqrstuvwxy"
    chunks = chunk_text(text, chunk_size=10, overlap=3)   # step = 7

    assert chunks == [
        "abcdefghij",   # [0:10]
        "hijklmnopq",   # [7:17]
        "opqrstuvwx",   # [14:24]
        "vwxy",         # [21:25] -> leftover, shorter than chunk_size
    ]
    assert [len(chunk) for chunk in chunks] == [10, 10, 10, 4]


def test_overlap_is_preserved_between_chunks():
    """Each chunk's tail equals the next chunk's head by `overlap` chars."""
    text = "abcdefghijklmnopqrstuvwxy"
    overlap = 3
    chunks = chunk_text(text, chunk_size=10, overlap=overlap)

    for current, nxt in zip(chunks, chunks[1:]):
        assert current[-overlap:] == nxt[:overlap]
