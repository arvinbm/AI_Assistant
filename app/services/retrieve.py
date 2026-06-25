"""Retrieval orchestration for the RAG query path.

Given a user question, returns the most relevant chunks to ground an answer:

    normalize -> embed (BGE-m3) -> FAISS top-N candidates -> rerank -> top-k

A relevance threshold guards against off-topic questions: chunks scoring below it
are dropped, so an off-topic query yields an empty list and the caller can say
"I don't have information on that" instead of forcing an answer.
"""
from app.services.embeddings import embed_text
from app.services.normalize import normalize
from app.services.rerank import rerank
from app.services.vector_store import VectorStore

# How many candidates to pull from FAISS before reranking.
CANDIDATE_COUNT = 15
# How many reranked chunks to keep at most.
TOP_K = 8
# Minimum reranker score (0-1) for a chunk to count as relevant.
RELEVANCE_THRESHOLD = 0.5


def retrieve(query: str, store: VectorStore) -> list[tuple[dict, float]]:
    """Return the relevant (metadata, score) chunks for a query, best first.

    An empty list means nothing cleared the relevance threshold — i.e. the
    question is off-topic or unanswerable from the corpus.
    """
    normalized = normalize(query)
    if not normalized:
        return []

    query_vector = embed_text(normalized)
    candidates = [meta for meta, _dist in store.search(query_vector, k=CANDIDATE_COUNT)]
    ranked = rerank(normalized, candidates, top_k=TOP_K)

    # Keep only chunks that are actually relevant.
    return [(meta, score) for meta, score in ranked if score >= RELEVANCE_THRESHOLD]
