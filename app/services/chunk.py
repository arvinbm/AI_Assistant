"""Split extracted text into overlapping chunks for embedding.

A whole document is too large and too unfocused to embed as one vector, so its
text is split into fixed-size, slightly overlapping passages. The overlap keeps
context that would otherwise be cut across a chunk boundary. """

# Target size of each chunk, in characters.
CHUNK_SIZE = 800
# Characters each chunk shares with the previous one.
CHUNK_OVERLAP = 100


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split ``text`` into overlapping chunks of approx ``chunk_size`` characters.

    Args:
        text: The full document text.
        chunk_size: Target number of characters per chunk.
        overlap: Number of characters shared between consecutive chunks.

    Returns:
        A list of non-empty chunks, in document order. Empty input -> [].

    Raises:
        ValueError: If ``overlap`` is not smaller than ``chunk_size``.
    """
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    # Remove whitespaces from the beginning and the end
    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap
    start = 0
    while start < len(text):
        chunk = text[start : start + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
        start += step

    return chunks
