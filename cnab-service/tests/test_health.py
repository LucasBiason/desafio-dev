"""Health check tests for the CNAB Service."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Returns a test client for the CNAB Service."""
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
