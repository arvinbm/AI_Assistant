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

    # AWS Bedrock model IDs
    bedrock_embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    bedrock_generation_model_id: str = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
