"""Tests for store_router endpoints."""

import uuid
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.store_schema import StoreResponse

USER_DATA = {"id": 1, "email": "user@test.com"}


@pytest.fixture
def auth_client():
    """Returns a TestClient with JWT auth bypassed."""
    with patch("cnab_shared.dependencies.require_jwt.UserService") as mock_user_service:
        mock_user_service.return_value.validate_token.return_value = USER_DATA
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


def _store_response(name: str = "Loja A") -> StoreResponse:
    """Returns a StoreResponse instance with sensible defaults."""
    return StoreResponse(
        id=str(uuid.uuid4()),
        name=name,
        owner_name="Joao",
        owner_cpf="12345678901",
        balance=Decimal("1000.00"),
        total_income=Decimal("1500.00"),
        total_expense=Decimal("500.00"),
        transaction_count=5,
    )


class TestStoreRouter:
    """Tests for GET /stores/ and GET /stores/{store_id}."""

    def test_list_stores_returns_200_with_count_and_results(self, auth_client):
        """GET /stores/ returns 200 with serialized count and results."""
        store = _store_response()
        with patch("app.routers.store_router.StoreController") as mock_ctrl:
            mock_ctrl.return_value.list_stores.return_value = ([store], 1)
            response = auth_client.get("/stores/", headers={"Authorization": "Bearer token"})

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "Loja A"

    def test_list_stores_passes_filters_to_controller(self, auth_client):
        """GET /stores/?name=X&owner_name=Y forwards filters to the controller."""
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

    def test_list_stores_empty_returns_count_zero(self, auth_client):
        """GET /stores/ returns count=0 and empty results list when no stores exist."""
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

    def test_get_store_returns_200_with_store_data(self, auth_client):
        """GET /stores/{store_id} returns 200 with the store payload."""
        store_id = str(uuid.uuid4())
        store = _store_response()
        with patch("app.routers.store_router.StoreController") as mock_ctrl:
            mock_ctrl.return_value.get_store.return_value = store
            response = auth_client.get(
                f"/stores/{store_id}",
                headers={"Authorization": "Bearer token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Loja A"
        assert data["owner_name"] == "Joao"

    def test_get_store_returns_404_when_not_found(self, auth_client):
        """GET /stores/{store_id} returns 404 when the controller returns None."""
        store_id = str(uuid.uuid4())
        with patch("app.routers.store_router.StoreController") as mock_ctrl:
            mock_ctrl.return_value.get_store.return_value = None
            response = auth_client.get(
                f"/stores/{store_id}",
                headers={"Authorization": "Bearer token"},
            )

        assert response.status_code == 404

    def test_get_store_requires_auth(self, client):
        """GET /stores/{store_id} returns 401 when Authorization header is missing."""
        response = client.get(f"/stores/{uuid.uuid4()}")
        assert response.status_code == 401
