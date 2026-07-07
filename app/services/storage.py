"""Document and index storage on the filesystem.

Files are written under ``settings.upload_dir`` (``./uploads`` locally). In
production an **Azure Files** share is mounted at that path, so uploaded
documents and the FAISS index persist across container restarts. Because a
mounted file share behaves like an ordinary directory, this module just uses
normal file I/O — no cloud SDK is involved.
"""
from pathlib import Path

from app.config import get_settings

settings = get_settings()

# Storage root: a plain folder locally, an Azure Files mount in production.
UPLOAD_DIR = Path(settings.upload_dir)


def store_document(content: bytes, key: str) -> str:
    """Write `content` under `key` (a relative path) and return the file path.

    `key` can include subfolders, e.g. "manual.pdf" or "index/index.faiss";
    parent directories are created as needed.
    """
    dest = UPLOAD_DIR / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    return str(dest)


def load_document(key: str) -> bytes:
    """Read and return the bytes stored under `key`.

    Raises:
        FileNotFoundError: if no file exists at `key`.
    """
    return (UPLOAD_DIR / key).read_bytes()
