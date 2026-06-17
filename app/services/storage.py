"""Raw document storage.

Saves uploaded/ingested files to Amazon S3 when AWS is configured, and falls
back to a local ``uploads/`` folder otherwise so the pipeline is runnable
without AWS credentials during development.
"""
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import get_settings

settings = get_settings()

# Local fallback directory (gitignored) used when AWS is not configured.
LOCAL_UPLOAD_DIR = Path("uploads")


def _use_s3() -> bool:
    """Return True when S3 storage is explicitly enabled and a bucket is set."""
    return settings.use_s3 and bool(settings.s3_bucket)


def store_document(content: bytes, key: str) -> str:
    """Store a raw document and return a reference to where it was saved.

    Args:
        content: The raw bytes of the file.
        key: The object key / relative path to store it under (e.g. "manual.pdf").

    Returns:
        An ``s3://bucket/key`` URI when stored in S3, or the local file path
        when using the local fallback.
    """
    if _use_s3():
        return _store_s3(content, key)
    return _store_local(content, key)


def _store_s3(content: bytes, key: str) -> str:
    """Upload bytes to the configured S3 bucket."""
    client = boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    try:
        client.put_object(Bucket=settings.s3_bucket, Key=key, Body=content)
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to upload '{key}' to S3: {exc}") from exc
    return f"s3://{settings.s3_bucket}/{key}"


def _store_local(content: bytes, key: str) -> str:
    """Write bytes to the local uploads/ folder, creating parents as needed."""
    dest = LOCAL_UPLOAD_DIR / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    return str(dest)
