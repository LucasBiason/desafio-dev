"""Tests for transaction_type_router endpoints."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.transaction_type import TransactionType

USER_DATA = {"id": 1, "email": "user@test.com"}


@pytest.fixture
def auth_client():
    """Returns a TestClient with JWT auth bypassed."""
    with patch("app.dependencies.UserService") as mock_user_service:
        mock_user_service.return_value.validate_token.return_value = USER_DATA
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


def _make_mock_type(code: int = 1) -> MagicMock:
    """Creates a mock TransactionType for router tests."""
    tt = MagicMock(spec=TransactionType)
    tt.id = str(uuid.uuid4())
    tt.code = code
    tt.description = f"Type {code}"
    tt.nature = "Entrada"
    tt.sign = "+"
    return tt


class TestTransactionTypeRouter:
    """Tests for GET /transaction-types/."""

    def test_list_types_returns_200(self, auth_client):
        """GET /transaction-types/ returns 200 with a list of types."""
        mock_types = [_make_mock_type(code=i) for i in range(1, 4)]
        with patch("app.routers.transaction_type_router.TransactionRepository") as mock_repo:
            mock_repo.return_value.get_all_types.return_value = mock_types
            response = auth_client.get(
                "/transaction-types/",
                headers={"Authorization": "Bearer token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_list_types_structure(self, auth_client):
        """GET /transaction-types/ returns objects with id, code, description, nature, sign."""
        mock_type = _make_mock_type(code=1)
        with patch("app.routers.transaction_type_router.TransactionRepository") as mock_repo:
            mock_repo.return_value.get_all_types.return_value = [mock_type]
            response = auth_client.get(
                "/transaction-types/",
                headers={"Authorization": "Bearer token"},
            )

        data = response.json()
        assert len(data) == 1
        item = data[0]
        assert "id" in item
        assert "code" in item
        assert "description" in item
        assert "nature" in item
        assert "sign" in item

    def test_list_types_empty(self, auth_client):
        """GET /transaction-types/ returns an empty list when no types are seeded."""
        with patch("app.routers.transaction_type_router.TransactionRepository") as mock_repo:
            mock_repo.return_value.get_all_types.return_value = []
            response = auth_client.get(
                "/transaction-types/",
                headers={"Authorization": "Bearer token"},
            )

        assert response.status_code == 200
        assert response.json() == []

    def test_list_types_requires_auth(self, client):
        """GET /transaction-types/ returns 401 without Authorization header."""
        response = client.get("/transaction-types/")
        assert response.status_code == 401
