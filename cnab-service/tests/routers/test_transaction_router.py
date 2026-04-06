"""Tests for transaction_router endpoints."""

import uuid
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.transaction_schema import (
    TransactionListResponse,
    TransactionResponse,
    TransactionTypeResponse,
)

USER_DATA = {"id": 1, "email": "user@test.com"}


@pytest.fixture
def auth_client():
    """Returns a TestClient with JWT auth bypassed."""
    with patch("cnab_shared.dependencies.require_jwt.UserService") as mock_user_service:
        mock_user_service.return_value.validate_token.return_value = USER_DATA
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


def _transaction_response() -> TransactionResponse:
    """Returns a TransactionResponse instance with sensible defaults."""
    transaction_type = TransactionTypeResponse(
        id=str(uuid.uuid4()),
        code=1,
        description="Debito",
        nature="Entrada",
        sign="+",
    )
    return TransactionResponse(
        id=str(uuid.uuid4()),
        transaction_type=transaction_type,
        amount=Decimal("100.00"),
        card="1234****5678",
        occurred_at="2024-01-15",
        occurred_time="10:30:00",
        store={
            "id": str(uuid.uuid4()),
            "name": "Loja A",
            "owner_name": "Joao",
            "owner_cpf": "12345678901",
        },
    )


class TestTransactionRouter:
    """Tests for GET /transactions/ and GET /transactions/{transaction_id}."""

    def test_list_transactions_returns_200_with_count_and_results(self, auth_client):
        """GET /transactions/?store_id=... returns 200 with serialized count and results."""
        store_id = str(uuid.uuid4())
        transaction = _transaction_response()
        list_response = TransactionListResponse(count=1, results=[transaction])
        with patch("app.routers.transaction_router.TransactionController") as mock_ctrl:
            mock_ctrl.return_value.list_by_store.return_value = list_response
            response = auth_client.get(
                f"/transactions/?store_id={store_id}",
                headers={"Authorization": "Bearer token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["card"] == "1234****5678"

    def test_list_transactions_passes_filters_to_controller(self, auth_client):
        """GET /transactions/ forwards filter parameters to the controller."""
        store_id = str(uuid.uuid4())
        list_response = TransactionListResponse(count=0, results=[])
        with patch("app.routers.transaction_router.TransactionController") as mock_ctrl:
            mock_ctrl.return_value.list_by_store.return_value = list_response
            response = auth_client.get(
                f"/transactions/?store_id={store_id}&type_codes=1,3&nature=Entrada"
                f"&date_from=2024-01-01&date_to=2024-12-31",
                headers={"Authorization": "Bearer token"},
            )

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.list_by_store.call_args[1]
        assert call_kwargs.get("store_id") == store_id
        assert call_kwargs.get("type_codes") == [1, 3]
        assert call_kwargs.get("nature") == "Entrada"
        assert call_kwargs.get("date_from") == "2024-01-01"
        assert call_kwargs.get("date_to") == "2024-12-31"

    def test_list_transactions_requires_auth(self, client):
        """GET /transactions/ returns 401 when Authorization header is missing."""
        response = client.get(f"/transactions/?store_id={uuid.uuid4()}")
        assert response.status_code == 401

    def test_get_transaction_returns_200_with_transaction_data(self, auth_client):
        """GET /transactions/{transaction_id} returns 200 with the transaction payload."""
        transaction = _transaction_response()
        with patch("app.routers.transaction_router.TransactionController") as mock_ctrl:
            mock_ctrl.return_value.get_transaction.return_value = transaction
            response = auth_client.get(
                f"/transactions/{transaction.id}",
                headers={"Authorization": "Bearer token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["card"] == "1234****5678"
        assert data["occurred_at"] == "2024-01-15"

    def test_get_transaction_returns_404_when_not_found(self, auth_client):
        """GET /transactions/{transaction_id} returns 404 when the controller returns None."""
        transaction_id = str(uuid.uuid4())
        with patch("app.routers.transaction_router.TransactionController") as mock_ctrl:
            mock_ctrl.return_value.get_transaction.return_value = None
            response = auth_client.get(
                f"/transactions/{transaction_id}",
                headers={"Authorization": "Bearer token"},
            )

        assert response.status_code == 404

    def test_get_transaction_requires_auth(self, client):
        """GET /transactions/{transaction_id} returns 401 when Authorization header is missing."""
        response = client.get(f"/transactions/{uuid.uuid4()}")
        assert response.status_code == 401
