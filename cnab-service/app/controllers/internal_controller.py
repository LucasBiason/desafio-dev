"""Controller for internal transaction ingestion from upload-service."""

import logging
from datetime import date, time
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.store_repository import StoreRepository
from app.repositories.transaction_repository import TransactionRepository

logger = logging.getLogger(__name__)


class InternalController:
    """Processes bulk transaction payloads sent by the upload-service."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._store_repo = StoreRepository(db=db)
        self._transaction_repo = TransactionRepository(db=db)

    def process_bulk_transactions(
        self,
        upload_id: str,
        transactions: list[dict],
    ) -> dict:
        """Ingests a list of parsed transactions and returns a summary.

        For each transaction: resolves or creates the store, looks up the
        transaction type, and creates a Transaction record. Returns a dict
        with upload_id, total_inserted, and stores_created.
        """
        stores_created = 0
        records: list[Transaction] = []

        for item in transactions:
            store, created = self._store_repo.get_or_create(
                name=item["store_name"],
                owner_name=item["store_owner"],
                owner_cpf=item["cpf"],
            )
            if created:
                stores_created += 1

            transaction_type = self._transaction_repo.get_type_by_code(item["type_code"])
            if transaction_type is None:
                logger.warning("Unknown transaction type code: %s — skipping.", item["type_code"])
                continue

            transaction = Transaction()
            transaction.transaction_type_id = transaction_type.id
            transaction.store_id = store.id
            transaction.upload_id = upload_id
            transaction.amount = Decimal(item["amount"])
            transaction.card = item["card"]
            transaction.occurred_at = date.fromisoformat(item["date"])
            transaction.occurred_time = time.fromisoformat(item["time"])

            records.append(transaction)

        total_inserted = self._transaction_repo.bulk_create(records)
        self._db.commit()

        return {
            "upload_id": upload_id,
            "total_inserted": total_inserted,
            "stores_created": stores_created,
        }
