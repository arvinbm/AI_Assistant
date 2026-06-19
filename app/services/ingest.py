"""Document ingestion pipeline.

Chains the building blocks to ingest a single document into the knowledge base:

    extract -> (skip if empty) -> store raw -> normalize -> chunk -> embed -> add to index

The caller passes in a VectorStore and owns loading/saving it, so bulk ingestion
can add many documents and persist once (instead of saving after every file).
Scanned / empty documents are skipped (no OCR), and reported as such.
"""
from app.services import storage
from app.services.chunk import chunk_text
from app.services.embeddings import embed_texts
from app.services.extract import extract_text
from app.services.normalize import normalize
from app.services.vector_store import VectorStore


def ingest_document(content: bytes, filename: str, store: VectorStore) -> dict:
    """Ingest one document's bytes into the given vector store.

    Args:
        content: The raw bytes of the document.
        filename: The original filename (used as the storage key and source).
        store: The VectorStore to add the document's chunks to (mutated in place).

    Returns:
        A small result dict, e.g.
        {"status": "ingested", "filename": ..., "chunks": 7} or
        {"status": "skipped", "filename": ..., "reason": "no extractable text"}.
    """
    text = extract_text(content, filename)
    if not text:
        # Scanned / image-only / empty document -> not added to the index.
        return {"status": "skipped", "filename": filename, "reason": "no extractable text"}

    # Preserve the raw file (S3 or local) before indexing it.
    storage.store_document(content, filename)

    # Canonicalize Persian/mixed text so chunks and queries match consistently.
    text = normalize(text)
    chunks = chunk_text(text)
    vectors = embed_texts(chunks)
    store.add(vectors, chunks, source=filename)

    return {"status": "ingested", "filename": filename, "chunks": len(chunks)}
