"""Controller for transaction listing and detail."""

from sqlalchemy.orm import Session

from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction_schema import (
    TransactionListResponse,
    TransactionResponse,
    TransactionTypeResponse,
)


class TransactionController:
    """Coordinates queries for transactions."""

    def __init__(self, db: Session) -> None:
        self._transaction_repo = TransactionRepository(db=db)

    @staticmethod
    def _build_response(row: dict) -> TransactionResponse:
        """Converts a raw SQL result row into a TransactionResponse."""
        transaction_type = TransactionTypeResponse(
            id=row["transaction_type_id"],
            code=row["transaction_type_code"],
            description=row["transaction_type_description"],
            nature=row["transaction_type_nature"],
            sign=row["transaction_type_sign"],
        )
        store_dict = {
            "id": row["store_id"],
            "name": row["store_name"],
            "owner_name": row["store_owner_name"],
            "owner_cpf": row["store_owner_cpf"],
        }
        return TransactionResponse(
            id=row["id"],
            transaction_type=transaction_type,
            amount=row["amount"],
            card=row["card"],
            occurred_at=str(row["occurred_at"]),
            occurred_time=str(row["occurred_time"]),
            store=store_dict,
        )

    def list_by_store(
        self,
        store_id: str,
        page: int = 1,
        page_size: int = 20,
        type_codes: list[int] | None = None,
        nature: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> TransactionListResponse:
        """Returns paginated transactions for a given store with optional filters."""
        rows, total = self._transaction_repo.list_by_store(
            store_id=store_id,
            page=page,
            page_size=page_size,
            type_codes=type_codes,
            nature=nature,
            date_from=date_from,
            date_to=date_to,
        )
        results = [self._build_response(row) for row in rows]
        return TransactionListResponse(count=total, results=results)

    def get_transaction(self, transaction_id: str) -> TransactionResponse | None:
        """Returns a single transaction by UUID, or None if not found."""
        row = self._transaction_repo.get_detail(transaction_id)
        if row is None:
            return None
        return self._build_response(row)
