"""Text embeddings.

Turns text chunks into fixed-length vectors. When Bedrock is enabled, uses
Amazon Titan Text Embeddings; otherwise falls back to a deterministic local
pseudo-embedding so the ingestion pipeline can run and be tested without AWS.

"""
import hashlib
import json

import boto3
import numpy as np
from botocore.exceptions import BotoCoreError, ClientError

from app.config import get_settings

settings = get_settings()

# Vector dimension.
EMBEDDING_DIM = 1024


def embed_text(text: str) -> list[float]:
    """Return an embedding vector for a single piece of text."""
    if settings.use_bedrock:
        return _embed_bedrock(text)
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
