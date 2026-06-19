"""Tests for the embeddings layer."""
import json
import numpy as np
import unittest.mock as mock

import pytest
from botocore.exceptions import ClientError

from app.services import embeddings
from app.services.embeddings import EMBEDDING_DIM, embed_text, embed_texts


# --- Local fallback (no AWS) ---

def test_local_embedding_has_correct_dimension(monkeypatch):
    monkeypatch.setattr(embeddings.settings, "embedding_backend", "local")
    assert len(embed_text("industrial belt")) == EMBEDDING_DIM


def test_local_embedding_is_deterministic(monkeypatch):
    monkeypatch.setattr(embeddings.settings, "embedding_backend", "local")
    assert embed_text("belt") == embed_text("belt")


def test_local_embedding_differs_by_text(monkeypatch):
    monkeypatch.setattr(embeddings.settings, "embedding_backend", "local")
    assert embed_text("belt") != embed_text("pulley")


def test_embed_texts_returns_one_vector_per_input(monkeypatch):
    monkeypatch.setattr(embeddings.settings, "embedding_backend", "local")
    vectors = embed_texts(["a", "b", "c"])
    assert len(vectors) == 3
    assert all(len(v) == EMBEDDING_DIM for v in vectors)


# --- Bedrock path (mocked) ---

def _fake_bedrock_client(embedding):
    """A mock bedrock-runtime client whose invoke_model returns `embedding`."""
    body = mock.MagicMock()
    body.read.return_value = json.dumps(
        {"embedding": embedding, "inputTextTokenCount": 3}
    ).encode("utf-8")
    client = mock.MagicMock()
    client.invoke_model.return_value = {"body": body}
    return client


def test_bedrock_embedding_parses_vector_and_sends_text(monkeypatch):
    monkeypatch.setattr(embeddings.settings, "embedding_backend", "bedrock")
    fake = _fake_bedrock_client([0.1, 0.2, 0.3])
    monkeypatch.setattr(embeddings.boto3, "client", lambda *a, **k: fake)

    result = embed_text("belt")

    assert result == [0.1, 0.2, 0.3]                      # parsed from response
    kwargs = fake.invoke_model.call_args.kwargs
    assert kwargs["modelId"] == embeddings.settings.bedrock_embedding_model_id
    assert json.loads(kwargs["body"]) == {"inputText": "belt"}   # sent the text


def test_bedrock_error_becomes_runtime_error(monkeypatch):
    monkeypatch.setattr(embeddings.settings, "embedding_backend", "bedrock")
    fake = mock.MagicMock()
    fake.invoke_model.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "no"}}, "InvokeModel"
    )
    monkeypatch.setattr(embeddings.boto3, "client", lambda *a, **k: fake)

    with pytest.raises(RuntimeError, match="Bedrock embedding failed"):
        embed_text("belt")


# --- Multilingual path (mocked, no heavy dependency) ---

def test_multilingual_backend_uses_local_model(monkeypatch):
    """The multilingual backend encodes via the loaded sentence-transformers model."""
    monkeypatch.setattr(embeddings.settings, "embedding_backend", "multilingual")
    fake_model = mock.MagicMock()
    fake_model.encode.return_value = np.array([0.1, 0.2, 0.3])
    # Pre-seed the cached model so no real import/download happens.
    monkeypatch.setattr(embeddings, "_multilingual_model", fake_model)

    result = embed_text("کتاب")

    assert result == [0.1, 0.2, 0.3]
    fake_model.encode.assert_called_once()
