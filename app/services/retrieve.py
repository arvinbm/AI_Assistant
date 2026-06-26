"""Retrieval orchestration for the RAG query path.

Hybrid retrieval with hybrid *scoring*:

    normalize -> ┌─ vector search (BGE-m3 -> FAISS) ─┐
                 ├─ keyword search (BM25, all tokens)─┤ -> merge -> rerank
                 └─ keyword search (distinctive tokens)┘
                 -> keep (reranker-relevant) OR (strong keyword match)

Vector + reranker handle *semantic* questions. But the cross-encoder reranker
scores exact-entity lookups (part numbers, customer names) as low as off-topic
junk, so we can't rely on it alone there. Instead we also *rescue* strong keyword
matches: a chunk is returned if it clears the rerank threshold OR it is a top
keyword hit. Off-topic queries match no keywords and score low, so they still
yield nothing.
"""
from app.services.embeddings import embed_text
from app.services.keyword_search import KeywordIndex
from app.services.normalize import normalize
from app.services.rerank import rerank
from app.services.vector_store import VectorStore

# How many candidates each retriever contributes.
CANDIDATE_COUNT = 15
# How many chunks to return at most.
TOP_K = 8
# Minimum reranker score (0-1) for a chunk to count as semantically relevant.
RERANK_THRESHOLD = 0.5
# Max exact-keyword matches to rescue even if the reranker underrates them.
KEYWORD_RESCUE = 5


def retrieve(
    query: str, store: VectorStore, keyword_index: KeywordIndex
) -> list[tuple[dict, float]]:
    """Return the relevant (metadata, score) chunks for a query, best first.

    Empty list means nothing was relevant (off-topic / not in the corpus).
    """
    normalized = normalize(query)
    if not normalized:
        return []

    vector_hits = store.search(embed_text(normalized), k=CANDIDATE_COUNT)
    # Distinctive-token hits first so exact codes outrank common-word noise.
    keyword_hits = _merge_scored(
        keyword_index.search_distinctive(normalized, top_k=KEYWORD_RESCUE)
        + keyword_index.search(normalized, top_k=CANDIDATE_COUNT)
    )

    candidates = _merge_candidates(
        [meta for meta, _ in vector_hits] + [meta for meta, _ in keyword_hits]
    )
    if not candidates:
        return []

    ranked = rerank(normalized, candidates, top_k=len(candidates))

    # 1) Semantically relevant chunks (reranker cleared the threshold).
    result = [(meta, score) for meta, score in ranked if score >= RERANK_THRESHOLD]
    chosen = {(m["source"], m["text"]) for m, _ in result}

    # 2) Rescue strong keyword matches the reranker underrates (exact lookups).
    for meta, kw_score in keyword_hits:
        if len(result) >= TOP_K:
            break
        key = (meta["source"], meta["text"])
        if key not in chosen:
            result.append((meta, kw_score))
            chosen.add(key)

    return result[:TOP_K]


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


def _merge_scored(scored: list[tuple[dict, float]]) -> list[tuple[dict, float]]:
    """Deduplicate (metadata, score) pairs by chunk, keeping the first (best) seen."""
    seen: set[tuple[str, str]] = set()
    unique: list[tuple[dict, float]] = []
    for meta, score in scored:
        key = (meta["source"], meta["text"])
        if key not in seen:
            seen.add(key)
            unique.append((meta, score))
    return unique
