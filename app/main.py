"""FastAPI application entrypoint for the AI Assistant backend."""
from fastapi import FastAPI, HTTPException, UploadFile

from app.config import get_settings
from app.services.ingest import ingest_document
from app.services.vector_store import VectorStore

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Production-ready RAG assistant built with FastAPI and AWS Bedrock.",
    version="0.1.0",
)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    """Basic service banner."""
    return {"service": settings.app_name, "version": app.version}


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Health check endpoint used by Docker and CI."""
    return {"status": "ok", "environment": settings.environment}


@app.post("/upload", tags=["documents"])
async def upload(file: UploadFile) -> dict:
    """Ingest an uploaded document into the knowledge base.

    Loads the existing index, runs the ingestion pipeline on the file, and
    (if it had usable text) saves the updated index. Scanned/empty files are
    reported as skipped.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    content = await file.read()
    store = VectorStore.load()
    try:
        result = ingest_document(content, file.filename, store)
    except ValueError as exc:  # unsupported file type
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result["status"] == "ingested":
        store.save()
    return result
