"""FastAPI application entrypoint for the AI Assistant backend."""
from fastapi import FastAPI

from app.config import get_settings

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
