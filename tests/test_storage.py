"""Tests for the document storage layer."""
import unittest.mock as mock

import pytest
from botocore.exceptions import ClientError

from app.services import storage


def test_local_fallback_writes_file(monkeypatch, tmp_path):
    """When S3 is disabled, the file is written to the local uploads folder."""
    monkeypatch.setattr(storage, "LOCAL_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage.settings, "use_s3", False)

    ref = storage.store_document(b"hello world", "sub/manual.pdf")

    written = tmp_path / "sub" / "manual.pdf"
    assert written.read_bytes() == b"hello world"   # bytes stored correctly
    assert ref == str(written)                        # returns the local path


def test_s3_upload_calls_put_object(monkeypatch):
    """When S3 is enabled, put_object is called and an s3:// URI is returned."""
    monkeypatch.setattr(storage.settings, "use_s3", True)
    monkeypatch.setattr(storage.settings, "s3_bucket", "test-bucket")

    fake_client = mock.MagicMock()
    monkeypatch.setattr(storage.boto3, "client", lambda *a, **k: fake_client)

    ref = storage.store_document(b"data", "manual.pdf")

    fake_client.put_object.assert_called_once_with(
        Bucket="test-bucket", Key="manual.pdf", Body=b"data"
    )
    assert ref == "s3://test-bucket/manual.pdf"


def test_s3_error_becomes_runtime_error(monkeypatch):
    """AWS ClientError is wrapped in a clear RuntimeError."""
    monkeypatch.setattr(storage.settings, "use_s3", True)
    monkeypatch.setattr(storage.settings, "s3_bucket", "test-bucket")

    fake_client = mock.MagicMock()
    fake_client.put_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "nope"}}, "PutObject"
    )
    monkeypatch.setattr(storage.boto3, "client", lambda *a, **k: fake_client)

    with pytest.raises(RuntimeError, match="Failed to upload"):
        storage.store_document(b"data", "manual.pdf")
