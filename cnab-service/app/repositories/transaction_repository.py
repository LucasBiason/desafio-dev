"""Repository for Transaction and TransactionType models."""

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.transaction_type import TransactionType
from cnab_shared import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Handles database operations for transactions and transaction types."""

    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model_class=Transaction)

    def get_all_types(self) -> list[TransactionType]:
        """Returns all 9 CNAB transaction types ordered by code."""
        return self.db.query(TransactionType).order_by(TransactionType.code).all()

    def get_type_by_code(self, code: int) -> TransactionType | None:
        """Returns a transaction type by its CNAB numeric code."""
        return self.db.query(TransactionType).filter(TransactionType.code == code).first()

    def list_by_store(
        self,
        store_id: str,
        page: int = 1,
        page_size: int = 20,
        type_code: int | None = None,
        nature: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[dict], int]:
        """Returns paginated transactions for a given store with optional filters.

        Returns (rows, total_count) where each row is a dict with transaction fields.
        """
        where_clauses = ["t.store_id = CAST(:store_id AS UUID)"]
        params: dict = {"store_id": store_id}

        if type_code is not None:
            where_clauses.append("tt.code = :type_code")
            params["type_code"] = type_code

        if nature:
            where_clauses.append("tt.nature = :nature")
            params["nature"] = nature

        if date_from:
            where_clauses.append("t.occurred_at >= :date_from")
            params["date_from"] = date_from

        if date_to:
            where_clauses.append("t.occurred_at <= :date_to")
            params["date_to"] = date_to

        where_sql = " AND ".join(where_clauses)

        count_sql = f"""
            SELECT COUNT(*) AS total
            FROM cnab_transaction t
            JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id
            WHERE {where_sql}
        """
        count_row = self.query_one(count_sql, params)
        total = int(count_row["total"]) if count_row else 0

        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        data_sql = f"""
            SELECT
                CAST(t.id AS TEXT) AS id,
                t.amount,
                t.card,
                CAST(t.occurred_at AS TEXT) AS occurred_at,
                CAST(t.occurred_time AS TEXT) AS occurred_time,
                CAST(tt.id AS TEXT) AS transaction_type_id,
                tt.code AS transaction_type_code,
                tt.description AS transaction_type_description,
                tt.nature AS transaction_type_nature,
                tt.sign AS transaction_type_sign,
                CAST(s.id AS TEXT) AS store_id,
                s.name AS store_name,
                s.owner_name AS store_owner_name,
                s.owner_cpf AS store_owner_cpf
            FROM cnab_transaction t
            JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id
            JOIN cnab_store s ON s.id = t.store_id
            WHERE {where_sql}
            ORDER BY t.occurred_at DESC, t.occurred_time DESC
            LIMIT :limit OFFSET :offset
        """
        rows = self.query_list(data_sql, params)
        return rows, total

    def bulk_create(self, transactions: list[Transaction]) -> int:
        """Inserts a list of Transaction instances in bulk and returns the count inserted."""
        for transaction in transactions:
            self.db.add(transaction)
        self.db.flush()
        return len(transactions)
