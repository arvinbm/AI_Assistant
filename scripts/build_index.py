"""Bulk-build the FAISS index from the local base corpus (one-time).

Runs the ingestion pipeline over every document in data/base_docs/ and saves the
resulting index + metadata. This is a FULL REBUILD: it starts from an empty store,
so re-running overwrites cleanly (unlike /upload, which appends).

Usage (from the project root):
    python scripts/build_index.py
"""
import os
import sys

# Make the project root importable when run as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import glob  # noqa: E402
from pathlib import Path  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.services.ingest import ingest_document  # noqa: E402
from app.services.vector_store import VectorStore  # noqa: E402

BASE = Path("data/base_docs")
FOLDERS = ("data_sheets", "customers", "catalog")
SKIP_LOG = Path("uploads/index/skipped_ingest.txt")


def gather_files() -> list[str]:
    """Collect all corpus file paths across the base-doc folders."""
    files: list[str] = []
    for folder in FOLDERS:
        files.extend(sorted(glob.glob(str(BASE / folder / "*"))))
    return files


def main() -> None:
    print(f"Embedding backend: {get_settings().embedding_backend}")
    files = gather_files()
    print(f"Building index from {len(files)} file(s)...\n")

    store = VectorStore()
    ingested = skipped = errors = 0
    skipped_files: list[str] = []

    for i, fp in enumerate(files, 1):
        name = os.path.basename(fp)
        try:
            result = ingest_document(Path(fp).read_bytes(), name, store)
            if result["status"] == "ingested":
                ingested += 1
                print(f"[{i}/{len(files)}] ingested  {name}  ({result['chunks']} chunks)")
            else:
                skipped += 1
                skipped_files.append(name)
                print(f"[{i}/{len(files)}] skipped   {name}  ({result['reason']})")
        except Exception as exc:
            errors += 1
            skipped_files.append(f"{name}\tERROR: {exc}")
            print(f"[{i}/{len(files)}] ERROR     {name}  ({exc})")

    store.save()
    SKIP_LOG.parent.mkdir(parents=True, exist_ok=True)
    SKIP_LOG.write_text("\n".join(skipped_files), encoding="utf-8")

    print(f"\nDone. ingested={ingested} skipped={skipped} errors={errors}")
    print(f"Index now holds {store.index.ntotal} vectors / {len(store.metadata)} chunks.")
    print(f"Saved to uploads/index/ (skip log: {SKIP_LOG})")


if __name__ == "__main__":
    main()
