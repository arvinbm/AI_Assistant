"""Text embeddings.

Pluggable embedding backends, selected by ``settings.embedding_backend``:
  - "local"        : deterministic pseudo-embedding (no deps/AWS) for plumbing/tests
  - "bedrock"      : Amazon Titan Text Embeddings via AWS Bedrock
  - "multilingual" : a local sentence-transformers model (good for Farsi/mixed)

All backends return a ``list[float]`` of length ``EMBEDDING_DIM`` so the FAISS
index dimension stays consistent. (Switching backends produces vectors in a
different semantic space, so the index must be rebuilt after a switch.)
"""
import hashlib
import json

import boto3
import numpy as np
from botocore.exceptions import BotoCoreError, ClientError

from app.config import get_settings

settings = get_settings()

# Vector dimension (Titan v2 and BGE-m3 both produce 1024-dim vectors).
EMBEDDING_DIM = 1024

# Lazily-loaded multilingual model (kept module-level so it loads only once).
_multilingual_model = None


def embed_text(text: str) -> list[float]:
    """Return an embedding vector for a single piece of text."""
    backend = settings.embedding_backend
    if backend == "bedrock":
        return _embed_bedrock(text)
    if backend == "multilingual":
        return _embed_multilingual(text)
    return _embed_local(text)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts, returning one vector per input."""
    return [embed_text(text) for text in texts]


def _embed_bedrock(text: str) -> list[float]:
    """Call Amazon Titan Embeddings via Bedrock and return the vector."""
    client = boto3.client(
        "bedrock-runtime",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )

    try:
        response = client.invoke_model(
            modelId=settings.bedrock_embedding_model_id,
            body=json.dumps({"inputText": text}),
            contentType="application/json",
            accept="application/json",
        )
        # Extract the embeddings & the token count
        payload = json.loads(response["body"].read())

    # Amazon Titan refused to embed the text chunk or the connection was not established
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Bedrock embedding failed: {exc}") from exc
    
    # Only return the embedded vector
    return payload["embedding"]


def _embed_multilingual(text: str) -> list[float]:
    """Embed with a local multilingual sentence-transformers model (e.g. BGE-m3).

    Imported lazily so the heavy dependency (sentence-transformers / torch) is
    only needed when this backend is actually selected.
    """
    global _multilingual_model
    if _multilingual_model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "The 'multilingual' embedding backend requires sentence-transformers. "
                "Install it with: pip install -r requirements-ml.txt"
            ) from exc
        _multilingual_model = SentenceTransformer(settings.multilingual_model_id)
    vector = _multilingual_model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def _embed_local(text: str) -> list[float]:
    """Deterministic local pseudo-embedding (no AWS).

    Seeds a random generator from a hash of the text, so the same text always
    yields the same vector. For running/testing the pipeline only.
    """
    # seed must be deterministic: same text -> same vector
    seed = int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")
    rng = np.random.default_rng(seed)
    # produces 1024 random floats drawn from a standard normal distribution
    return rng.standard_normal(EMBEDDING_DIM).tolist() 
