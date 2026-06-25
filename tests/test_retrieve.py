"""Tests for the retrieval orchestration (embed/rerank/store mocked)."""
import unittest.mock as mock

from app.services import retrieve


def _fake_store(candidates):
    """A store whose search returns the given candidate metadata dicts."""
    store = mock.MagicMock()
    store.search.return_value = [(c, 0.0) for c in candidates]
    return store


def test_retrieve_keeps_only_chunks_above_threshold(monkeypatch):
    store = _fake_store([{"text": "A"}, {"text": "B"}, {"text": "C"}])
    monkeypatch.setattr(retrieve, "embed_text", lambda *_: [0.0] * 1024)
    monkeypatch.setattr(
        retrieve,
        "rerank",
        lambda *a, **k: [
            ({"text": "B", "source": "b", "lang": "fa"}, 0.97),
            ({"text": "A", "source": "a", "lang": "en"}, 0.62),
            ({"text": "C", "source": "c", "lang": "mixed"}, 0.30),
        ],
    )

    result = retrieve.retrieve("belt?", store)

    # C (0.30) is below RELEVANCE_THRESHOLD and is dropped.
    assert [m["text"] for m, _ in result] == ["B", "A"]


def test_retrieve_off_topic_returns_empty(monkeypatch):
    store = _fake_store([{"text": "X"}])
    monkeypatch.setattr(retrieve, "embed_text", lambda *_: [0.0] * 1024)
    monkeypatch.setattr(retrieve, "rerank", lambda *a, **k: [({"text": "X"}, 0.39)])

    assert retrieve.retrieve("capital of France?", store) == []


def test_retrieve_empty_query_short_circuits():
    store = mock.MagicMock()
    assert retrieve.retrieve("   ", store) == []
    store.search.assert_not_called()   # no embedding/search work for an empty query
