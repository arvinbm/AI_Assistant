"""BM25 keyword search over chunk text.

Complements vector search: BM25 matches *exact tokens* — part numbers, model
codes, customer names (e.g. ``8M-1200``) — that dense embeddings miss. It is
built over the same normalized chunk text used for embeddings, so Persian and
English tokens line up at query time.

Only chunks with a positive BM25 score (an actual term overlap) are returned, so
a query that matches just two chunks returns two — never padded with non-matches.
"""
import re

from rank_bm25 import BM25Okapi

# Max number of keyword matches to return.
DEFAULT_TOP_K = 15

# Tokens are word/code runs; the hyphen is kept so "8M-1200" stays one token.
_TOKEN_RE = re.compile(r"[\w-]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Split text into lowercase tokens, keeping hyphens (for codes like 8M-1200)."""
    return [t for t in _TOKEN_RE.findall(text.lower()) if any(c.isalnum() for c in t)]


class KeywordIndex:
    """A BM25 index over chunk metadata dicts (each has a ``text`` field)."""

    def __init__(self, metadatas: list[dict]):
        self.metadatas = metadatas
        self._bm25 = (
            BM25Okapi([tokenize(m["text"]) for m in metadatas]) if metadatas else None
        )

    def search(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[tuple[dict, float]]:
        """Return up to ``top_k`` chunks with a positive BM25 score, best first."""
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(tokenize(query))
        ranked = sorted(
            (
                (self.metadatas[i], float(score))
                for i, score in enumerate(scores)
                if score > 0
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return ranked[:top_k]
