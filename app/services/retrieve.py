"""Retrieval orchestration for the RAG query path.

Given a user question, returns the most relevant chunks to ground an answer via
**hybrid search**:

    normalize -> ┌─ vector search (BGE-m3 -> FAISS) ─┐
                 └─ keyword search (BM25) ───────────┘ -> merge -> rerank -> top-k

Vector search captures meaning; BM25 captures exact tokens (part numbers, model
codes, customer names) that embeddings miss. The merged candidates are reranked,
and a relevance threshold drops off-topic results so the caller can say
"I don't have information on that" instead of forcing an answer.
"""
from app.services.embeddings import embed_text
from app.services.keyword_search import KeywordIndex
from app.services.normalize import normalize
from app.services.rerank import rerank
from app.services.vector_store import VectorStore

# How many candidates each retriever contributes before reranking.
CANDIDATE_COUNT = 15
# How many reranked chunks to keep at most.
TOP_K = 8
# Minimum reranker score (0-1) for a chunk to count as relevant.
RELEVANCE_THRESHOLD = 0.5


def retrieve(
    query: str, store: VectorStore, keyword_index: KeywordIndex
) -> list[tuple[dict, float]]:
    """Return the relevant (metadata, score) chunks for a query, best first.

    An empty list means nothing cleared the relevance threshold — i.e. the
    question is off-topic or unanswerable from the corpus.
    """
    normalized = normalize(query)
    if not normalized:
        return []

    # Two retrievers: semantic (vector) and exact-token (keyword).
    vector_hits = store.search(embed_text(normalized), k=CANDIDATE_COUNT)
    keyword_hits = keyword_index.search(normalized, top_k=CANDIDATE_COUNT)

    candidates = _merge_candidates(
        [meta for meta, _ in vector_hits] + [meta for meta, _ in keyword_hits]
    )

    ranked = rerank(normalized, candidates, top_k=TOP_K)
    return [(meta, score) for meta, score in ranked if score >= RELEVANCE_THRESHOLD]


def _merge_candidates(metadatas: list[dict]) -> list[dict]:
    """Deduplicate chunks (by source + text), preserving first-seen order."""
    seen: set[tuple[str, str]] = set()
    unique: list[dict] = []
    for meta in metadatas:
        key = (meta["source"], meta["text"])
        if key not in seen:
            seen.add(key)
            unique.append(meta)
    return unique
