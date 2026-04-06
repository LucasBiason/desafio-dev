"""Controller for store listing and detail."""

from sqlalchemy.orm import Session

from app.repositories.store_repository import StoreRepository
from app.schemas.store_schema import StoreResponse


class StoreController:
    """Coordinates queries for stores."""

    def __init__(self, db: Session) -> None:
        self._store_repo = StoreRepository(db=db)

    def list_stores(
        self,
        page: int = 1,
        page_size: int = 20,
        name: str | None = None,
        owner_name: str | None = None,
    ) -> tuple[list[StoreResponse], int]:
        """Returns paginated stores with balance aggregations and optional filters."""
        rows, total = self._store_repo.list_with_balance(
            page=page,
            page_size=page_size,
            name_filter=name,
            owner_filter=owner_name,
        )
        results = [StoreResponse(**row) for row in rows]
        return results, total

    def get_store(self, store_id: str) -> StoreResponse | None:
        """Returns a single store by UUID with balance data, or None if not found."""
        row = self._store_repo.get_with_balance(store_id)
        if row is None:
            return None
        return StoreResponse(**row)
