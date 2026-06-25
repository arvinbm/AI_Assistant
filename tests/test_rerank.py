"""Tests for the cross-encoder reranking module (mocked model)."""
import unittest.mock as mock

import numpy as np

from app.services import rerank


def _fake_model(scores):
    model = mock.MagicMock()
    model.predict.return_value = np.array(scores)
    return model


def test_rerank_sorts_by_score_and_truncates(monkeypatch):
    monkeypatch.setattr(rerank, "_reranker_model", _fake_model([0.2, 0.9, 0.5]))
    candidates = [
        {"text": "A", "source": "a.pdf", "lang": "en"},
        {"text": "B", "source": "b.pdf", "lang": "fa"},
        {"text": "C", "source": "c.pdf", "lang": "mixed"},
    ]

    result = rerank.rerank("belt", candidates, top_k=2)

    assert [m["text"] for m, _ in result] == ["B", "C"]   # highest score first
    assert len(result) == 2                                # truncated to top_k
    assert result[0][1] == 0.9                             # returns the score


def test_rerank_pairs_query_with_each_candidate(monkeypatch):
    fake = _fake_model([0.1, 0.2])
    monkeypatch.setattr(rerank, "_reranker_model", fake)

    rerank.rerank("q", [{"text": "x"}, {"text": "y"}])

    assert fake.predict.call_args.args[0] == [("q", "x"), ("q", "y")]


def test_rerank_empty_returns_empty():
    assert rerank.rerank("q", [], top_k=5) == []
