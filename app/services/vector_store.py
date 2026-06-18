"""FAISS vector store with text/source metadata, persisted via the storage layer.

Holds the embedding vectors in a FAISS index plus a parallel list of metadata
({text, source}) so search results can be turned back into readable text and
cited. 

Supports load -> append -> save, so user uploads add to the existing
index rather than replacing it. The index and metadata are persisted to S3
(or the local folder) so they survive without the original corpus.

Uses a class VectorStore to keep the state of operations while the index and metadata
grow and searched.
"""
import json

import faiss
import numpy as np

from app.services import storage
from app.services.embeddings import EMBEDDING_DIM

# Keys the index and its metadata are persisted under.
# Used by both local and S3 storage
INDEX_KEY = "index/index.faiss"
META_KEY = "index/chunks.json"


class VectorStore:
    """An in-memory FAISS index plus aligned chunk metadata."""

    def __init__(self, index: faiss.Index | None = None, metadata: list[dict] | None = None):
        # IndexFlatL2 = exact nearest-neighbor search by L2 (Euclidean) distance.
        # index = the vectors + the machinery to find nearest neighbors among them.
        if index is not None:
            self.index = index
        else:
            self.index = faiss.IndexFlatL2(EMBEDDING_DIM)

        if metadata is not None:
            self.metadata: list[dict] = metadata
        else:
            self.metadata = []

    def add(self, vectors: list[list[float]], chunks: list[str], source: str) -> None:
        """Add chunk vectors and their text/source to the index (aligned by order)."""
        if not vectors:
            return
        
        # Add the vectors
        self.index.add(np.array(vectors, dtype="float32"))

        # Add the metadata
        for text in chunks:
            self.metadata.append({"text": text, "source": source})

    def search(self, query_vector: list[float], k: int = 5) -> list[tuple[dict, float]]:
        """Return up to k nearest chunks as (metadata, distance) pairs.

        Lower distance = closer match. The distance lets callers apply a
        relevance threshold (e.g. ignore results that are too far away).
        """
        if self.index.ntotal == 0:
            # No vectors stored
            return []
        
        # Search for the nearest neighbors 
        query = np.array([query_vector], dtype="float32")
        distances, indices = self.index.search(query, min(k, self.index.ntotal))

        return [
            (self.metadata[idx], float(dist)) for dist, idx in zip(distances[0], indices[0])
        ]

    def save(self) -> None:
        """Persist the index and metadata via the storage layer (S3 or local)."""
        # Store the index
        index_bytes = faiss.serialize_index(self.index).tobytes()
        storage.store_document(index_bytes, INDEX_KEY)

        # Store the metadata
        meta_bytes = json.dumps(self.metadata, ensure_ascii=False).encode("utf-8")
        storage.store_document(meta_bytes, META_KEY)

    @classmethod
    def load(cls) -> "VectorStore":
        """Load a persisted store, or return an empty one if none exists yet."""
        try:
            index_bytes = storage.load_document(INDEX_KEY)
            meta_bytes = storage.load_document(META_KEY)
        except FileNotFoundError:
            # Nothing persisted yet -> start with an empty index
            # Calls VectorStore's constructor
            return cls()
        
        index = faiss.deserialize_index(np.frombuffer(index_bytes, dtype="uint8"))
        metadata = json.loads(meta_bytes.decode("utf-8"))
        return cls(index=index, metadata=metadata)
