"""Tests for CnabServiceClient."""

import os
from unittest.mock import MagicMock, patch

import pytest
from cryptography.fernet import Fernet

from app.services.cnab_service_client import CnabServiceClient


@pytest.fixture
def fernet_key():
    """Generates a valid Fernet key for testing."""
    return Fernet.generate_key().decode()


class TestCnabServiceClient:

    def test_generate_token_returns_string(self, fernet_key):
        """Token is a non-empty encrypted string."""
        os.environ["SERVICE_SECRET_KEY"] = fernet_key
        client = CnabServiceClient()
        token = client._generate_token()
        assert isinstance(token, str)
        assert len(token) > 0

    @patch("app.services.cnab_service_client.httpx.post")
    def test_create_transactions_success(self, mock_post, fernet_key):
        """Returns cnab-service response on 201."""
        os.environ["SERVICE_SECRET_KEY"] = fernet_key
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "upload_id": "test-uuid",
            "total_inserted": 2,
            "stores_created": 1,
        }
        mock_post.return_value = mock_response

        client = CnabServiceClient()
        result = client.create_transactions("test-uuid", [{"type_code": 1}, {"type_code": 2}])

        assert result["upload_id"] == "test-uuid"
        assert result["total_inserted"] == 2
        mock_post.assert_called_once()

    @patch("app.services.cnab_service_client.httpx.post")
    def test_create_transactions_batching(self, mock_post, fernet_key):
        """Sends multiple batches when transactions exceed batch size."""
        os.environ["SERVICE_SECRET_KEY"] = fernet_key
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "upload_id": "test-uuid",
            "total_inserted": 1000,
            "stores_created": 0,
        }
        mock_post.return_value = mock_response

        client = CnabServiceClient()
        transactions = [{"type_code": 1}] * 2500
        result = client.create_transactions("test-uuid", transactions)

        assert mock_post.call_count == 3
        assert result["total_inserted"] == 3000
        assert result["stores_created"] == 0

    @patch("app.services.cnab_service_client.httpx.post")
    def test_create_transactions_failure_raises(self, mock_post, fernet_key):
        """Raises RuntimeError on non-201 response."""
        os.environ["SERVICE_SECRET_KEY"] = fernet_key
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        client = CnabServiceClient()
        with pytest.raises(RuntimeError, match="cnab-service error: 500"):
            client.create_transactions("test-uuid", [{"type_code": 1}])
