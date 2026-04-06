"""Tests for health check endpoint."""


class TestHealthCheck:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client):
        """GET /health returns 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy(self, client):
        """GET /health returns status healthy."""
        data = response = client.get("/health").json()
        assert data["status"] == "healthy"
