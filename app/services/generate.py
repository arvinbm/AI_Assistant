"""Answer generation with Claude Haiku (AWS Bedrock).

Builds a grounded prompt from the retrieved chunks and the user's question, calls
Claude Haiku via Bedrock, and returns the answer. The model is instructed to
answer ONLY from the provided context (and say so when the answer isn't there),
which keeps responses grounded and avoids hallucination.
"""
import json

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import get_settings

settings = get_settings()

# Max tokens in the generated answer.
MAX_TOKENS = 1000

SYSTEM_PROMPT = (
    "You are an assistant that answers questions about a company's internal "
    "documents. Answer using ONLY the provided context. If the answer is not in "
    "the context, say you don't have that information — do not guess. Reply in "
    "the same language as the question (Persian or English)."
)


def generate_answer(question: str, chunks: list[tuple[dict, float]]) -> str:
    """Generate a grounded answer to `question` from the retrieved `chunks`."""
    body = _build_request(question, chunks)
    client = _bedrock_client()
    try:
        response = client.invoke_model(
            modelId=settings.bedrock_generation_model_id,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        payload = json.loads(response["body"].read())
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Bedrock generation failed: {exc}") from exc

    return payload["content"][0]["text"]


def _build_request(question: str, chunks: list[tuple[dict, float]]) -> str:
    """Build the Bedrock request body (shared by streaming and non-streaming)."""
    context = _build_context(chunks)
    user_message = f"Context:\n{context}\n\nQuestion: {question}"
    return json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": MAX_TOKENS,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_message}],
        }
    )


def _bedrock_client():
    """Create a Bedrock runtime client from the configured AWS credentials."""
    return boto3.client(
        "bedrock-runtime",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def _build_context(chunks: list[tuple[dict, float]]) -> str:
    """Format retrieved chunks into a numbered, source-tagged context block."""
    blocks = [
        f"[{i}] (source: {meta['source']})\n{meta['text']}"
        for i, (meta, _score) in enumerate(chunks, 1)
    ]
    return "\n\n".join(blocks)
