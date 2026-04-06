"""HTTP client for communicating with cnab-service."""

import json
import logging
import os
from datetime import UTC, datetime

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
            "timestamp": datetime.now(tz=UTC).isoformat(),
        }).encode()
        return fernet.encrypt(payload).decode()

    def _send_batch(self, upload_id: str, transactions: list[dict]) -> dict:
        """Sends a single batch of transactions to cnab-service."""
        token = self._generate_token()
        response = httpx.post(
            f"{self.cnab_service_url}/transactions/upload/",
            json={"upload_id": upload_id, "transactions": transactions},
            headers={"X-Service-Token": token},
            timeout=60.0,
        )

        if response.status_code == 201:
            return response.json()

        logger.error(
            "cnab-service returned %d: %s",
            response.status_code,
            response.text[:500],
        )
        raise RuntimeError(f"cnab-service error: {response.status_code}")

    def create_transactions(self, upload_id: str, transactions: list[dict]) -> dict:
        """Sends parsed transactions to cnab-service in batches of 1000."""
        batch_size = 1000
        total_inserted = 0
        stores_created = 0
        last_result: dict = {}

        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            logger.info(
                "Sending batch %d/%d (%d transactions) for upload %s",
                (i // batch_size) + 1,
                (len(transactions) + batch_size - 1) // batch_size,
                len(batch),
                upload_id,
            )
            result = self._send_batch(upload_id, batch)
            total_inserted += result.get("total_inserted", 0)
            stores_created += result.get("stores_created", 0)
            last_result = result

        last_result["total_inserted"] = total_inserted
        last_result["stores_created"] = stores_created
        return last_result
