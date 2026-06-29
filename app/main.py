"""FastAPI application entrypoint for the AI Assistant backend."""
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config import get_settings
from app.services.embeddings import embed_text
from app.services.generate import generate_answer, generate_answer_stream
from app.services.ingest import ingest_document
from app.services.keyword_search import KeywordIndex
from app.services.rerank import rerank
from app.services.retrieve import retrieve
from app.services.vector_store import VectorStore

settings = get_settings()

# The knowledge base, loaded once and shared across requests.
_store: VectorStore | None = None
_keyword_index: KeywordIndex | None = None


def get_FAISS_index() -> VectorStore:
    """Return the shared VectorStore, loading it from storage on first use."""
    global _store
    if _store is None:
        _store = VectorStore.load()
    return _store


def get_BM25_index() -> KeywordIndex:
    """Return the shared BM25 index, building it from the store on first use."""
    global _keyword_index
    if _keyword_index is None:
        _keyword_index = KeywordIndex(get_FAISS_index().metadata)
    return _keyword_index


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Load the index and warm up the models once at startup."""
    get_FAISS_index()
    get_BM25_index()
    try:
        # Pre-load the embedding + reranker models so the first query is fast.
        embed_text("warm up")
        rerank("warm up", [{"text": "warm up"}], top_k=1)
    except Exception:
        pass  # models load lazily on first request if warm-up isn't possible
    yield


app = FastAPI(
    title=settings.app_name,
    description="Production-ready RAG assistant built with FastAPI and AWS Bedrock.",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow the local Vite dev frontend to call the API from the browser.
# In production the frontend is served from the same origin (Step 9), so CORS
# is only needed during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


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
    """Ingest an uploaded document into the knowledge base."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    content = await file.read()
    store = get_FAISS_index()
    try:
        result = ingest_document(content, file.filename, store)
    except ValueError as exc:  # unsupported file type
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result["status"] == "ingested":
        store.save()
        global _keyword_index
        _keyword_index = None  # rebuild on next query to include the new chunks
    return result


@app.post("/chat", tags=["chat"])
def chat(request: ChatRequest) -> dict:
    """Answer a question from the knowledge base (retrieve -> rerank -> generate)."""
    chunks = retrieve(request.question, get_FAISS_index(), get_BM25_index())
    if not chunks:
        return {
            "answer": "I don't have information about that in the available documents.",
            "sources": [],
        }
    answer = generate_answer(request.question, chunks)
    # Unique source documents, preserving order.
    sources = list(dict.fromkeys(meta["source"] for meta, _score in chunks))
    return {"answer": answer, "sources": sources}


@app.post("/chat/stream", tags=["chat"])
def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Like /chat, but stream the answer as it is generated.

    Emits newline-delimited JSON (NDJSON): first a `sources` line, then a
    `token` line for each piece of text as Claude produces it.
    """
    chunks = retrieve(request.question, get_FAISS_index(), get_BM25_index())

    def event_stream():
        if not chunks:
            yield json.dumps({"type": "sources", "sources": []}) + "\n"
            yield json.dumps(
                {
                    "type": "token",
                    "text": "I don't have information about that in the "
                    "available documents.",
                }
            ) + "\n"
            return

        sources = list(dict.fromkeys(meta["source"] for meta, _score in chunks))
        yield json.dumps({"type": "sources", "sources": sources}) + "\n"
        for piece in generate_answer_stream(request.question, chunks):
            yield json.dumps({"type": "token", "text": piece}) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")
