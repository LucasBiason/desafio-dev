"""Tests for upload_router endpoints."""

import json
import os
import uuid
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from app.main import app

_TEST_KEY = Fernet.generate_key()


def _make_fernet_token(key: bytes = _TEST_KEY) -> str:
    """Creates a fresh valid Fernet service token."""
    fernet = Fernet(key)
    payload = json.dumps({"service": "upload-service", "timestamp": datetime.now(tz=UTC).isoformat()}).encode()
    return fernet.encrypt(payload).decode()


@pytest.fixture
def upload_client():
    """Returns a TestClient with SERVICE_SECRET_KEY set for Fernet auth."""
    with patch.dict(os.environ, {"SERVICE_SECRET_KEY": _TEST_KEY.decode()}):
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


def _bulk_payload(upload_id: str | None = None, count: int = 1) -> dict:
    """Returns a minimal BulkTransactionRequest payload."""
    return {
        "upload_id": upload_id or str(uuid.uuid4()),
        "transactions": [
            {
                "type_code": 1,
                "date": "2024-01-15",
                "amount": "150.00",
                "cpf": "12345678901",
                "card": "1234****5678",
                "time": "10:30:00",
                "store_owner": "Joao",
                "store_name": "Loja A",
            }
        ]
        * count,
    }


class TestUploadRouter:
    """Tests for POST /transactions/upload/."""

    def test_valid_request_returns_201(self, upload_client):
        """POST /transactions/upload/ returns 201 with summary."""
        upload_id = str(uuid.uuid4())
        payload = _bulk_payload(upload_id=upload_id)
        token = _make_fernet_token()

        with patch("app.routers.upload_router.UploadController") as mock_ctrl:
            mock_ctrl.return_value.process_bulk_transactions.return_value = {
                "upload_id": upload_id,
                "total_inserted": 1,
                "stores_created": 0,
            }
            response = upload_client.post(
                "/transactions/upload/",
                json=payload,
                headers={"X-Service-Token": token},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["upload_id"] == upload_id
        assert data["total_inserted"] == 1

    def test_missing_service_token_returns_422(self, upload_client):
        """POST /transactions/upload/ returns 422 when X-Service-Token header is absent."""
        response = upload_client.post(
            "/transactions/upload/",
            json=_bulk_payload(),
        )
        assert response.status_code == 422

    def test_invalid_service_token_returns_401(self, upload_client):
        """POST /transactions/upload/ returns 401 for an invalid token."""
        response = upload_client.post(
            "/transactions/upload/",
            json=_bulk_payload(),
            headers={"X-Service-Token": "not-valid-fernet"},
        )
        assert response.status_code == 401

    def test_empty_transactions_list(self, upload_client):
        """POST /transactions/upload/ returns 201 with zeros for empty list."""
        upload_id = str(uuid.uuid4())
        payload = {"upload_id": upload_id, "transactions": []}
        token = _make_fernet_token()

        with patch("app.routers.upload_router.UploadController") as mock_ctrl:
            mock_ctrl.return_value.process_bulk_transactions.return_value = {
                "upload_id": upload_id,
                "total_inserted": 0,
                "stores_created": 0,
            }
            response = upload_client.post(
                "/transactions/upload/",
                json=payload,
                headers={"X-Service-Token": token},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["total_inserted"] == 0
        assert data["stores_created"] == 0

    def test_wrong_key_returns_401(self):
        """POST /transactions/upload/ returns 401 when token was signed with a different key."""
        other_key = Fernet.generate_key()
        token = _make_fernet_token(key=other_key)

        with patch.dict(os.environ, {"SERVICE_SECRET_KEY": _TEST_KEY.decode()}):
            with TestClient(app, raise_server_exceptions=False) as client:
                response = client.post(
                    "/transactions/upload/",
                    json=_bulk_payload(),
                    headers={"X-Service-Token": token},
                )

        assert response.status_code == 401
