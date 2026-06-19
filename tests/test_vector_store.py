"""Tests for the FAISS vector store."""
import numpy as np
import pytest

from app.services import storage
from app.services.embeddings import EMBEDDING_DIM
from app.services.vector_store import VectorStore


def _vec(seed: int) -> list[float]:
    """A deterministic vector of the right dimension (same seed -> same vector)."""
    return np.random.default_rng(seed).standard_normal(EMBEDDING_DIM).tolist()


def test_add_grows_index_and_metadata():
    store = VectorStore()
    store.add([_vec(1), _vec(2)], ["chunk A", "chunk B"], source="doc.pdf")

    assert store.index.ntotal == 2
    assert store.metadata == [
        {"text": "chunk A", "source": "doc.pdf", "lang": "en"},
        {"text": "chunk B", "source": "doc.pdf", "lang": "en"},
    ]


def test_add_empty_is_noop():
    store = VectorStore()
    store.add([], [], source="doc.pdf")
    assert store.index.ntotal == 0
    assert store.metadata == []


def test_search_returns_nearest_with_metadata_and_distance():
    store = VectorStore()
    store.add([_vec(1), _vec(2), _vec(3)], ["A", "B", "C"], source="doc.pdf")

    # Querying with an exact stored vector returns it, at distance ~0.
    results = store.search(_vec(2), k=1)

    assert len(results) == 1
    meta, dist = results[0]
    assert meta == {"text": "B", "source": "doc.pdf", "lang": "en"}
    assert dist == pytest.approx(0.0, abs=1e-3)


def test_search_empty_store_returns_empty_list():
    assert VectorStore().search(_vec(1)) == []


def test_save_and_load_round_trip(monkeypatch, tmp_path):
    # Persist to a temp local folder, not the real uploads/ or S3.
    monkeypatch.setattr(storage.settings, "use_s3", False)
    monkeypatch.setattr(storage, "LOCAL_UPLOAD_DIR", tmp_path)

    store = VectorStore()
    store.add([_vec(1), _vec(2)], ["A", "B"], source="doc.pdf")
    store.save()

    reloaded = VectorStore.load()
    assert reloaded.index.ntotal == 2
    assert reloaded.metadata == store.metadata
    # Search still works after reload.
    meta, _ = reloaded.search(_vec(1), k=1)[0]
    assert meta == {"text": "A", "source": "doc.pdf", "lang": "en"}


def test_load_with_nothing_persisted_returns_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(storage.settings, "use_s3", False)
    monkeypatch.setattr(storage, "LOCAL_UPLOAD_DIR", tmp_path)  # empty dir, no files

    store = VectorStore.load()
    assert store.index.ntotal == 0
    assert store.metadata == []
