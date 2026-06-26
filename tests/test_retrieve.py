"""Tests for the retrieval orchestration (embed/rerank/store/keyword mocked)."""
import unittest.mock as mock

from app.services import retrieve


def _fake_store(candidates):
    """A store whose search returns the given candidate metadata dicts."""
    store = mock.MagicMock()
    store.search.return_value = [(c, 0.0) for c in candidates]
    return store


def _fake_keyword_index(search_results=None, distinctive_results=None):
    """A keyword index returning the given hits for search / search_distinctive."""
    index = mock.MagicMock()
    index.search.return_value = [(c, 1.0) for c in (search_results or [])]
    index.search_distinctive.return_value = [(c, 2.0) for c in (distinctive_results or [])]
    return index


def test_retrieve_keeps_only_chunks_above_threshold(monkeypatch):
    store = _fake_store([{"text": "A", "source": "a"}])
    keyword = _fake_keyword_index([])
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

    result = retrieve.retrieve("belt?", store, keyword)

    # C (0.30) is below the rerank threshold and there are no keyword hits to rescue it.
    assert [m["text"] for m, _ in result] == ["B", "A"]


def test_retrieve_rescues_strong_keyword_match(monkeypatch):
    # Exact-entity case: reranker underrates everything, but a keyword hit is kept.
    entity = {"text": "8M-1200 invoice line", "source": "inv.pdf"}
    store = _fake_store([{"text": "noise", "source": "n.pdf"}])
    keyword = _fake_keyword_index(search_results=[entity])
    monkeypatch.setattr(retrieve, "embed_text", lambda *_: [0.0] * 1024)
    monkeypatch.setattr(retrieve, "rerank", lambda q, c, top_k: [(m, 0.1) for m in c])

    result = retrieve.retrieve("8M-1200", store, keyword)

    # Nothing clears 0.5, but the strong keyword match is rescued.
    assert any(m["source"] == "inv.pdf" for m, _ in result)


def test_retrieve_merges_and_dedupes_vector_and_keyword(monkeypatch):
    shared = {"text": "8M-1200 belt", "source": "inv.pdf"}
    store = _fake_store([shared, {"text": "other", "source": "x.pdf"}])
    keyword = _fake_keyword_index(search_results=[shared])  # duplicate of a vector hit
    monkeypatch.setattr(retrieve, "embed_text", lambda *_: [0.0] * 1024)

    captured = {}

    def fake_rerank(query, candidates, top_k):
        captured["candidates"] = candidates
        return [(candidates[0], 0.9)]

    monkeypatch.setattr(retrieve, "rerank", fake_rerank)
    retrieve.retrieve("8M-1200", store, keyword)

    # 2 vector + 1 keyword, but the shared chunk is deduped -> 2 unique candidates.
    assert len(captured["candidates"]) == 2


def test_retrieve_off_topic_returns_empty(monkeypatch):
    store = _fake_store([{"text": "X", "source": "x"}])
    keyword = _fake_keyword_index([])  # no keyword matches for off-topic
    monkeypatch.setattr(retrieve, "embed_text", lambda *_: [0.0] * 1024)
    monkeypatch.setattr(retrieve, "rerank", lambda *a, **k: [({"text": "X", "source": "x"}, 0.39)])

    assert retrieve.retrieve("capital of France?", store, keyword) == []


def test_retrieve_empty_query_short_circuits():
    store = mock.MagicMock()
    keyword = mock.MagicMock()
    assert retrieve.retrieve("   ", store, keyword) == []
    store.search.assert_not_called()
    keyword.search.assert_not_called()
