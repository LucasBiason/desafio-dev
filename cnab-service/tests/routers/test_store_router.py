"""Tests for store_router endpoints."""

import uuid
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

USER_DATA = {"id": 1, "email": "user@test.com"}


@pytest.fixture
def auth_client():
    """Returns a TestClient with JWT auth bypassed."""
    with patch("app.dependencies.UserService") as mock_user_service:
        mock_user_service.return_value.validate_token.return_value = USER_DATA
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


def _store_row(name: str = "Loja A") -> dict:
    """Returns a minimal store row dict matching StoreResponse fields."""
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "owner_name": "Joao",
        "owner_cpf": "12345678901",
        "balance": Decimal("1000.00"),
        "total_income": Decimal("1500.00"),
        "total_expense": Decimal("500.00"),
        "transaction_count": 5,
    }


def _transaction_row() -> dict:
    """Returns a minimal transaction row dict matching the SQL query output."""
    return {
        "id": str(uuid.uuid4()),
        "amount": Decimal("100.00"),
        "card": "1234****5678",
        "occurred_at": "2024-01-15",
        "occurred_time": "10:30:00",
        "transaction_type_id": str(uuid.uuid4()),
        "transaction_type_code": 1,
        "transaction_type_description": "Debito",
        "transaction_type_nature": "Entrada",
        "transaction_type_sign": "+",
        "store_id": str(uuid.uuid4()),
        "store_name": "Loja A",
        "store_owner_name": "Joao",
        "store_owner_cpf": "12345678901",
    }


class TestStoreRouter:
    """Tests for GET /stores/ and GET /stores/{id}/transactions/."""

    def test_list_stores_returns_200(self, auth_client):
        """GET /stores/ returns 200 with count and results."""
        rows = [_store_row()]
        with patch("app.routers.store_router.StoreController") as mock_ctrl:
            mock_ctrl.return_value.list_stores.return_value = (rows, 1)
            response = auth_client.get("/stores/", headers={"Authorization": "Bearer token"})

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "Loja A"

    def test_list_stores_with_filters(self, auth_client):
        """GET /stores/?name=X passes name filter to controller."""
        with patch("app.routers.store_router.StoreController") as mock_ctrl:
            mock_ctrl.return_value.list_stores.return_value = ([], 0)
            response = auth_client.get(
                "/stores/?name=Loja&owner_name=Joao",
                headers={"Authorization": "Bearer token"},
            )

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.list_stores.call_args[1]
        assert call_kwargs.get("name") == "Loja"
        assert call_kwargs.get("owner_name") == "Joao"

    def test_list_stores_empty(self, auth_client):
        """GET /stores/ returns count=0 and empty results when no stores exist."""
        with patch("app.routers.store_router.StoreController") as mock_ctrl:
            mock_ctrl.return_value.list_stores.return_value = ([], 0)
            response = auth_client.get("/stores/", headers={"Authorization": "Bearer token"})

        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_list_stores_requires_auth(self, client):
        """GET /stores/ returns 401 when Authorization header is missing."""
        response = client.get("/stores/")
        assert response.status_code == 401

    def test_list_store_transactions_returns_200(self, auth_client):
        """GET /stores/{id}/transactions/ returns 200 with paginated transactions."""
        store_id = str(uuid.uuid4())
        rows = [_transaction_row()]
        with patch("app.routers.store_router.StoreController") as mock_ctrl:
            mock_ctrl.return_value.get_store_transactions.return_value = (rows, 1)
            response = auth_client.get(
                f"/stores/{store_id}/transactions/",
                headers={"Authorization": "Bearer token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["results"]) == 1

    def test_list_store_transactions_with_filters(self, auth_client):
        """GET /stores/{id}/transactions/ passes filters to controller."""
        store_id = str(uuid.uuid4())
        with patch("app.routers.store_router.StoreController") as mock_ctrl:
            mock_ctrl.return_value.get_store_transactions.return_value = ([], 0)
            response = auth_client.get(
                f"/stores/{store_id}/transactions/?type_code=1&nature=Entrada&date_from=2024-01-01&date_to=2024-12-31",
                headers={"Authorization": "Bearer token"},
            )

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.get_store_transactions.call_args[1]
        assert call_kwargs.get("type_code") == 1
        assert call_kwargs.get("nature") == "Entrada"

    def test_list_store_transactions_requires_auth(self, client):
        """GET /stores/{id}/transactions/ returns 401 without auth."""
        response = client.get(f"/stores/{uuid.uuid4()}/transactions/")
        assert response.status_code == 401
