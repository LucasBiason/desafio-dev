"""HTTP client for communicating with cnab-service."""

import json
import logging
import os
from datetime import datetime, timezone

import httpx
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class CnabServiceClient:
    def __init__(self) -> None:
        self.cnab_service_url = os.environ.get("CNAB_SERVICE_URL", "http://cnab-service:8002")
        self.secret_key = os.environ.get("SERVICE_SECRET_KEY", "")

    def _generate_token(self) -> str:
        """Creates a Fernet-encrypted token identifying this service."""
        fernet = Fernet(self.secret_key.encode())
        payload = json.dumps({
            "service": "upload-service",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }).encode()
        return fernet.encrypt(payload).decode()

    def create_transactions(self, upload_id: str, transactions: list[dict]) -> dict:
        """Sends parsed transactions to cnab-service via Fernet-authenticated POST."""
        token = self._generate_token()
        response = httpx.post(
            f"{self.cnab_service_url}/internal/transactions/",
            json={"upload_id": upload_id, "transactions": transactions},
            headers={"X-Service-Token": token},
            timeout=30.0,
        )

        if response.status_code == 201:
            return response.json()

        logger.error(
            "cnab-service returned %d: %s",
            response.status_code,
            response.text[:500],
        )
        raise RuntimeError(f"cnab-service error: {response.status_code}")
