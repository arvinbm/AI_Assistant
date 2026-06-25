"""Inspect real reranker scores to choose a relevance threshold (Phase 3).

Loads the real FAISS index and, for both relevant and deliberately off-topic
queries, runs the full retrieval path (BGE-m3 search top-15 -> BGE reranker ->
top-k) and PRINTS the reranker scores. Read the gap between the lowest "relevant"
score and the highest "off-topic" score to choose a minimum-score threshold.

Run from the project root (needs the built index + requirements-ml.txt):
    python scripts/eval_rerank.py
"""
import os
import sys

os.environ["EMBEDDING_BACKEND"] = "multilingual"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embeddings import embed_text  # noqa: E402
from app.services.normalize import normalize  # noqa: E402
from app.services.rerank import rerank  # noqa: E402
from app.services.vector_store import VectorStore  # noqa: E402

RELEVANT = [
    ("fa", "تسمه نقاله صنعتی"),          # industrial conveyor belt
    ("en", "oil resistant conveyor belt"),
    ("en", "timing belt PVC"),
    ("fa", "تسمه تایمینگ"),              # timing belt
]
OFF_TOPIC = [
    ("en", "what is the capital of France"),
    ("en", "best chocolate cake recipe"),
    ("fa", "آب و هوای امروز تهران"),      # today's weather in Tehran
]


def show(store: VectorStore, label: str, queries: list[tuple[str, str]]) -> None:
    print(f"\n===== {label} =====")
    for lang, query in queries:
        nq = normalize(query)
        candidates = [meta for meta, _dist in store.search(embed_text(nq), k=15)]
        top = rerank(nq, candidates, top_k=3)
        best = top[0][1] if top else float("nan")
        print(f"[{lang}] {query}   -> best rerank score: {best:.3f}")
        for meta, score in top:
            snippet = " ".join(meta["text"].split())[:48]
            print(f"     {score:8.3f} | {meta['source'][:22]:22} | {snippet}")


if __name__ == "__main__":
    print("Loading index...")
    store = VectorStore.load()
    print(f"{store.index.ntotal} vectors loaded.")
    show(store, "RELEVANT queries (expect HIGH scores)", RELEVANT)
    show(store, "OFF-TOPIC queries (expect LOW scores)", OFF_TOPIC)
    print(
        "\nChoose a threshold between the LOWEST relevant best-score "
        "and the HIGHEST off-topic best-score."
    )
