"""Application configuration loaded from environment variables."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings sourced from the environment / .env file."""

    app_name: str = "AI Assistant"
    environment: str = "dev"

    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    # Document storage
    s3_bucket: str | None = None
    # Set True only when real AWS credentials + bucket are configured;
    # otherwise files are saved to the local uploads/ folder.
    use_s3: bool = False

    # AWS Bedrock model IDs
    bedrock_embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    bedrock_generation_model_id: str = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

    # Which embedding backend to use:
    #   "local"        - deterministic pseudo-embedding (no deps/AWS), for plumbing/tests
    #   "bedrock"      - Amazon Titan Text Embeddings (needs AWS credentials)
    #   "multilingual" - local sentence-transformers model (good for Farsi/mixed)
    embedding_backend: str = "local"
    # Multilingual model id (1024-dim, matches EMBEDDING_DIM). Requires
    # `pip install -r requirements-ml.txt` when embedding_backend == "multilingual".
    multilingual_model_id: str = "BAAI/bge-m3"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
