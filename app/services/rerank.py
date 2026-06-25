"""Cross-encoder reranking of retrieved chunks.

Vector search (a bi-encoder) is fast but coarse: it embeds the query and each
chunk separately. A cross-encoder reranker scores the query and a candidate chunk
*together*, giving sharper relevance. So we retrieve a wider set from FAISS
(e.g. top-30), rerank it here, and keep only the best few (e.g. top-8).

Uses BGE-reranker-v2-m3 (multilingual, pairs with the BGE-m3 embeddings). The
model is loaded lazily so the heavy dependency (sentence-transformers) is only
needed when reranking is actually used.
"""
from app.config import get_settings

settings = get_settings()

# Default number of chunks to keep after reranking.
DEFAULT_TOP_K = 8

# Lazily-loaded cross-encoder model (loaded once, reused after).
_reranker_model = None


def _get_reranker_model():
    """Load (once) and return the cross-encoder reranker model."""
    global _reranker_model
    if _reranker_model is None:
        try:
            from sentence_transformers import CrossEncoder
        except ImportError as exc:
            raise RuntimeError(
                "Reranking requires sentence-transformers. "
                "Install it with: pip install -r requirements-ml.txt"
            ) from exc
        _reranker_model = CrossEncoder(settings.reranker_model_id)
    return _reranker_model


def rerank(query: str, candidates: list[dict], top_k: int = DEFAULT_TOP_K) -> list[tuple[dict, float]]:
    """Re-score candidate chunks against the query and return the top_k.

    Args:
        query: The (already normalized) user query.
        candidates: Chunk metadata dicts, each containing a "text" field.
        top_k: How many of the best-scoring chunks to return.

    Returns:
        A list of (metadata, score) pairs sorted by relevance, highest first.
        Higher score = more relevant. Empty input -> [].
    """
    if not candidates:
        return []

    model = _get_reranker_model()
    pairs = [(query, candidate["text"]) for candidate in candidates]
    scores = model.predict(pairs)

    ranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)
    return [(meta, float(score)) for meta, score in ranked[:top_k]]
