"""EF-4 — evaluate multilingual retrieval quality on a sample of the real corpus.

Builds a small in-memory index from a sample of Farsi / English / mixed documents
using the *multilingual* embedding backend (BGE-m3 by default), then runs a set of
Farsi, English, and mixed queries and prints the top matches for inspection.

Run from the project root (after `pip install -r requirements-ml.txt`):

    python scripts/eval_retrieval.py
"""
import os
import sys

# Force the multilingual backend BEFORE importing app code (settings is cached).
os.environ["EMBEDDING_BACKEND"] = "multilingual"
# Make the project root importable when run as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import glob  # noqa: E402
from pathlib import Path  # noqa: E402

from app.services.chunk import chunk_text  # noqa: E402
from app.services.embeddings import embed_text, embed_texts  # noqa: E402
from app.services.extract import extract_text  # noqa: E402
from app.services.normalize import normalize  # noqa: E402
from app.services.vector_store import VectorStore  # noqa: E402

BASE = Path("data/base_docs")
FILES_PER_CATEGORY = 12   # sample size per folder (keeps CPU embedding time bounded)
CHUNK_CAP = 400           # stop after this many chunks total
TOP_K = 4

# (label, query) pairs spanning the three retrieval paths.
QUERIES = [
    ("fa   ", "تسمه نقاله صنعتی"),        # "industrial conveyor belt" in Farsi
    ("en   ", "industrial conveyor belt"),
    ("fa   ", "تسمه تایمینگ و وی بلت"),    # "timing & V-belt"
    ("en   ", "timing belt"),
    ("mixed", "PVC تسمه belt"),
]


def build_sample_index() -> VectorStore:
    """Extract -> normalize -> chunk -> embed a sample of the corpus into a store."""
    store = VectorStore()
    total = 0
    for folder in ("data_sheets", "customers", "catalog"):
        files = sorted(glob.glob(str(BASE / folder / "*")))[:FILES_PER_CATEGORY]
        for fp in files:
            if total >= CHUNK_CAP:
                break
            content = Path(fp).read_bytes()
            text = extract_text(content, os.path.basename(fp))
            if not text:
                continue
            chunks = chunk_text(normalize(text))[: CHUNK_CAP - total]
            if not chunks:
                continue
            store.add(embed_texts(chunks), chunks, source=os.path.basename(fp))
            total += len(chunks)
        print(f"  {folder}: indexed (running total {total} chunks)")
    print(f"Indexed {store.index.ntotal} chunks total.\n")
    return store


def run_queries(store: VectorStore) -> None:
    for label, query in QUERIES:
        print(f"=== [{label}] {query}")
        results = store.search(embed_text(normalize(query)), k=TOP_K)
        for meta, dist in results:
            snippet = " ".join(meta["text"].split())[:70]
            print(f"   {dist:7.3f} | {meta['lang']:6} | {meta['source'][:28]:28} | {snippet}")
        print()


if __name__ == "__main__":
    print("Building sample index with the multilingual backend (first run downloads BGE-m3)...\n")
    store = build_sample_index()
    run_queries(store)
