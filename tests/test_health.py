"""Tests for the health and root endpoints."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_returns_service_banner():
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()
