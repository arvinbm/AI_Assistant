"""Tests for answer generation (mocked Bedrock)."""
import json
import unittest.mock as mock

import pytest
from botocore.exceptions import ClientError

from app.services import generate
from app.services.generate import generate_answer

CHUNKS = [
    ({"text": "2P120 belt, oil resistant", "source": "spec.pdf", "lang": "en"}, 0.97),
    ({"text": "تسمه مقاوم در برابر روغن", "source": "cat.txt", "lang": "fa"}, 0.80),
]


def _fake_client(answer_text):
    """A mock bedrock-runtime client whose invoke_model returns `answer_text`."""
    body = mock.MagicMock()
    body.read.return_value = json.dumps({"content": [{"text": answer_text}]}).encode("utf-8")
    client = mock.MagicMock()
    client.invoke_model.return_value = {"body": body}
    return client


def test_generate_returns_answer_text(monkeypatch):
    fake = _fake_client("It is oil resistant (source: spec.pdf).")
    monkeypatch.setattr(generate.boto3, "client", lambda *a, **k: fake)

    answer = generate_answer("Is it oil resistant?", CHUNKS)

    assert answer == "It is oil resistant (source: spec.pdf)."


def test_generate_sends_grounded_prompt_with_context(monkeypatch):
    fake = _fake_client("ok")
    monkeypatch.setattr(generate.boto3, "client", lambda *a, **k: fake)

    generate_answer("Is it oil resistant?", CHUNKS)

    kwargs = fake.invoke_model.call_args.kwargs
    assert kwargs["modelId"] == generate.settings.bedrock_generation_model_id
    sent = json.loads(kwargs["body"])
    assert sent["system"]                                       # grounding instructions present
    user_msg = sent["messages"][0]["content"]
    assert "spec.pdf" in user_msg and "cat.txt" in user_msg    # both sources in context
    assert "oil resistant" in user_msg                         # the question is included


def test_generate_error_becomes_runtime_error(monkeypatch):
    fake = mock.MagicMock()
    fake.invoke_model.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "no"}}, "InvokeModel"
    )
    monkeypatch.setattr(generate.boto3, "client", lambda *a, **k: fake)

    with pytest.raises(RuntimeError, match="Bedrock generation failed"):
        generate_answer("q", CHUNKS)
