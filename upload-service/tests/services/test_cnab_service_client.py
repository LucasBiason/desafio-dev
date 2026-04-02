"""Tests for CnabServiceClient."""

import os
import pytest
from cryptography.fernet import Fernet

from app.services.cnab_service_client import CnabServiceClient


@pytest.fixture
def fernet_key():
    """Generates a valid Fernet key for testing."""
    return Fernet.generate_key().decode()


class TestCnabServiceClient:
    """Tests for CnabServiceClient token generation and transaction stub."""

    def test_generate_token_returns_string(self, fernet_key):
        """_generate_token returns a non-empty string token."""
        os.environ["SERVICE_SECRET_KEY"] = fernet_key
        client = CnabServiceClient()
        token = client._generate_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_transactions_stub_returns_dict(self):
        """create_transactions returns a dict with expected keys."""
        client = CnabServiceClient()
        transactions = [{"type_code": 1, "amount": "10.00"}]
        result = client.create_transactions("upload-uuid-123", transactions)
        assert isinstance(result, dict)
        assert result["upload_id"] == "upload-uuid-123"
        assert result["total_inserted"] == 1
        assert "stores_created" in result
