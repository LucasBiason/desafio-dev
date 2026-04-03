"""Controller for store listing and transaction queries."""

from sqlalchemy.orm import Session

from app.repositories.store_repository import StoreRepository
from app.repositories.transaction_repository import TransactionRepository


class StoreController:
    """Coordinates queries for stores and their transactions."""

    def __init__(self, db: Session) -> None:
        self._store_repo = StoreRepository(db=db)
        self._transaction_repo = TransactionRepository(db=db)

    def list_stores(
        self,
        page: int = 1,
        page_size: int = 20,
        name: str | None = None,
        owner_name: str | None = None,
    ) -> tuple[list[dict], int]:
        """Returns paginated stores with balance aggregations and optional filters."""
        return self._store_repo.list_with_balance(
            page=page,
            page_size=page_size,
            name_filter=name,
            owner_filter=owner_name,
        )

    def get_store_transactions(
        self,
        store_id: str,
        page: int = 1,
        page_size: int = 20,
        type_code: int | None = None,
        nature: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[dict], int]:
        """Returns paginated transactions for a given store with optional filters."""
        return self._transaction_repo.list_by_store(
            store_id=store_id,
            page=page,
            page_size=page_size,
            type_code=type_code,
            nature=nature,
            date_from=date_from,
            date_to=date_to,
        )
