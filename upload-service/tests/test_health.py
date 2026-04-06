"""Health check tests for the Upload Service."""

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("TESTING", "true")

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    """Returns a test client for the Upload Service."""
    return TestClient(app)


class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_returns_200(self, client):
        """Verifies that the health check returns HTTP status 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy(self, client):
        """Verifies that the health check returns the correct body."""
        response = client.get("/health")
        assert response.json() == {"status": "healthy"}
