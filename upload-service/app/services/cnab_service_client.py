"""HTTP client for communicating with cnab-service."""

import json
import os
from datetime import datetime, timezone

from cryptography.fernet import Fernet


class CnabServiceClient:
    """Sends parsed transaction data to cnab-service using a Fernet service token."""

    def __init__(self) -> None:
        self.cnab_service_url = os.environ.get("CNAB_SERVICE_URL", "http://cnab-service:8002")
        self.secret_key = os.environ.get("SERVICE_SECRET_KEY", "")

    def _generate_token(self) -> str:
        """Creates a Fernet-encrypted token identifying this service."""
        fernet = Fernet(self.secret_key.encode())
        payload = json.dumps(
            {
                "service": "upload-service",
                "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            }
        ).encode()
        return fernet.encrypt(payload).decode()

    def create_transactions(self, upload_id: str, transactions: list[dict]) -> dict:
        """Sends parsed transactions to cnab-service for storage.

        TODO: Replace stub with actual HTTP call to cnab-service.
              Use httpx to POST to {self.cnab_service_url}/transactions/bulk/
              with Authorization header: Bearer {self._generate_token()}
        """
        return {
            "upload_id": upload_id,
            "total_inserted": len(transactions),
            "stores_created": 0,
        }
