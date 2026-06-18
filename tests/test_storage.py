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
    assert ref == str(written)                      # returns the local path


def test_s3_upload_calls_put_object(monkeypatch):
    """When S3 is enabled, put_object is called and an s3:// URI is returned."""
    # Temporarily change a value for this test.
    monkeypatch.setattr(storage.settings, "use_s3", True)
    monkeypatch.setattr(storage.settings, "s3_bucket", "test-bucket")

    fake_client = mock.MagicMock() # A fake object that records how its called
    monkeypatch.setattr(storage.boto3, "client", lambda *a, **k: fake_client) # Swap AWS for the fake

    ref = storage.store_document(b"data", "manual.pdf")

    # Verify the mock was called once, with exact args
    fake_client.put_object.assert_called_once_with(
        Bucket="test-bucket", Key="manual.pdf", Body=b"data"
    )
    assert ref == "s3://test-bucket/manual.pdf" # Verify the function's return value


def test_s3_error_becomes_runtime_error(monkeypatch):
    """AWS ClientError is wrapped in a clear RuntimeError."""
    monkeypatch.setattr(storage.settings, "use_s3", True)
    monkeypatch.setattr(storage.settings, "s3_bucket", "test-bucket")

    fake_client = mock.MagicMock()
    # Make the fake client fail 
    fake_client.put_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "nope"}}, "PutObject"
    )
    monkeypatch.setattr(storage.boto3, "client", lambda *a, **k: fake_client)

    # Assert that the block raises exception. This test expects failure.
    with pytest.raises(RuntimeError, match="Failed to upload"):
        storage.store_document(b"data", "manual.pdf")


# --- load_document (read path) ---

def test_load_document_local_round_trip(monkeypatch, tmp_path):
    """A locally stored document can be read back byte-for-byte."""
    monkeypatch.setattr(storage, "LOCAL_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage.settings, "use_s3", False)
    storage.store_document(b"hello", "sub/a.txt")
    assert storage.load_document("sub/a.txt") == b"hello"


def test_load_document_missing_raises_filenotfound(monkeypatch, tmp_path):
    """A missing local file raises FileNotFoundError."""
    monkeypatch.setattr(storage, "LOCAL_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage.settings, "use_s3", False)
    with pytest.raises(FileNotFoundError):
        storage.load_document("nope.txt")


def test_load_document_s3_get(monkeypatch):
    """When S3 is enabled, get_object is called and its body is returned."""
    monkeypatch.setattr(storage.settings, "use_s3", True)
    monkeypatch.setattr(storage.settings, "s3_bucket", "test-bucket")
    body = mock.MagicMock()
    body.read.return_value = b"s3 data"
    fake = mock.MagicMock()
    fake.get_object.return_value = {"Body": body}
    monkeypatch.setattr(storage.boto3, "client", lambda *a, **k: fake)

    assert storage.load_document("k.txt") == b"s3 data"
    fake.get_object.assert_called_once_with(Bucket="test-bucket", Key="k.txt")


def test_load_document_s3_missing_raises_filenotfound(monkeypatch):
    """A NoSuchKey error from S3 is converted to FileNotFoundError."""
    monkeypatch.setattr(storage.settings, "use_s3", True)
    monkeypatch.setattr(storage.settings, "s3_bucket", "test-bucket")
    fake = mock.MagicMock()
    fake.get_object.side_effect = ClientError(
        {"Error": {"Code": "NoSuchKey", "Message": "missing"}}, "GetObject"
    )
    monkeypatch.setattr(storage.boto3, "client", lambda *a, **k: fake)

    with pytest.raises(FileNotFoundError):
        storage.load_document("k.txt")
