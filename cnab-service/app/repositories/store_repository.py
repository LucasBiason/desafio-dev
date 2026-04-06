"""Repository for Store model with balance aggregation queries."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.store import Store
from cnab_shared import BaseRepository


class StoreRepository(BaseRepository[Store]):
    """Handles all database operations for stores, including balance aggregation."""

    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model_class=Store)

    def list_with_balance(
        self,
        page: int = 1,
        page_size: int = 20,
        name_filter: str | None = None,
        owner_filter: str | None = None,
    ) -> tuple[list[dict], int]:
        """Returns paginated stores with aggregated balance fields.

        Applies optional name and owner_name filters. Returns (rows, total_count).
        """
        where_clauses = ["1=1"]
        params: dict = {}

        if name_filter:
            where_clauses.append("LOWER(s.name) LIKE LOWER(:name_filter)")
            params["name_filter"] = f"%{name_filter}%"

        if owner_filter:
            where_clauses.append("LOWER(s.owner_name) LIKE LOWER(:owner_filter)")
            params["owner_filter"] = f"%{owner_filter}%"

        where_sql = " AND ".join(where_clauses)

        count_sql = f"""
            SELECT COUNT(*) AS total
            FROM cnab_store s
            WHERE {where_sql}
        """
        count_row = self.query_one(count_sql, params)
        total = int(count_row["total"]) if count_row else 0

        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        data_sql = f"""
            SELECT
                CAST(s.id AS TEXT) AS id,
                s.name,
                s.owner_name,
                s.owner_cpf,
                COALESCE(SUM(CASE WHEN tt.sign = '+' THEN t.amount ELSE -t.amount END), 0) AS balance,
                COALESCE(SUM(CASE WHEN tt.sign = '+' THEN t.amount ELSE 0 END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN tt.sign = '-' THEN t.amount ELSE 0 END), 0) AS total_expense,
                COUNT(t.id) AS transaction_count
            FROM cnab_store s
            LEFT JOIN cnab_transaction t ON t.store_id = s.id
            LEFT JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id
            WHERE {where_sql}
            GROUP BY s.id, s.name, s.owner_name, s.owner_cpf
            ORDER BY s.name
            LIMIT :limit OFFSET :offset
        """
        rows = self.query_list(data_sql, params)
        return rows, total

    def get_with_balance(self, store_id: str) -> dict | None:
        """Returns a single store by UUID with aggregated balance fields, or None."""
        sql = """
            SELECT
                CAST(s.id AS TEXT) AS id,
                s.name,
                s.owner_name,
                s.owner_cpf,
                COALESCE(SUM(CASE WHEN tt.sign = '+' THEN t.amount ELSE -t.amount END), 0) AS balance,
                COALESCE(SUM(CASE WHEN tt.sign = '+' THEN t.amount ELSE 0 END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN tt.sign = '-' THEN t.amount ELSE 0 END), 0) AS total_expense,
                COUNT(t.id) AS transaction_count
            FROM cnab_store s
            LEFT JOIN cnab_transaction t ON t.store_id = s.id
            LEFT JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id
            WHERE s.id = CAST(:store_id AS UUID)
            GROUP BY s.id, s.name, s.owner_name, s.owner_cpf
        """
        return self.query_one(sql, {"store_id": store_id})

    def get_or_create(
        self,
        name: str,
        owner_name: str,
        owner_cpf: str,
    ) -> tuple[Store, bool]:
        """Finds a store by (name, owner_cpf) or creates a new one.

        Returns (store, created) where created is True when a new record was inserted.
        """
        existing = self.db.query(Store).filter(Store.name == name, Store.owner_cpf == owner_cpf).first()
        if existing:
            return existing, False

        store = Store()
        store.name = name
        store.owner_name = owner_name
        store.owner_cpf = owner_cpf

        self.db.add(store)
        self.db.flush()
        return store, True

    def get_by_id(self, id: UUID) -> Store | None:
        """Returns a single store by UUID, or None if not found."""
        return self.db.query(Store).filter(Store.id == id).first()
