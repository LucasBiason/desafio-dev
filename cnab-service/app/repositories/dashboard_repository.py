"""Repository for dashboard aggregation queries."""

from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


# Consistent color palette based on green tones for chart types
_TYPE_COLORS = [
    "#02BE3B",
    "#00A832",
    "#008C2A",
    "#007022",
    "#00541A",
    "#38D468",
    "#6EE395",
    "#A4F1BF",
    "#D0F8E3",
]


class DashboardRepository:
    """Executes raw SQL aggregation queries for dashboard endpoints."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _execute_one(self, sql: str, params: dict | None = None) -> dict[str, Any] | None:
        """Runs a query and returns the first row as dict, or None."""
        result = self._db.execute(text(sql), params or {}).fetchone()
        if result is None:
            return None
        return dict(result._mapping)

    def _execute_list(self, sql: str, params: dict | None = None) -> list[dict[str, Any]]:
        """Runs a query and returns all rows as a list of dicts."""
        results = self._db.execute(text(sql), params or {}).fetchall()
        return [dict(row._mapping) for row in results]

    def get_summary(self) -> dict[str, Any]:
        """Returns overall counts and financial totals across all stores."""
        sql = """
            SELECT
                COUNT(DISTINCT s.id) AS total_stores,
                COUNT(t.id) AS total_transactions,
                COALESCE(SUM(CASE WHEN tt.sign = '+' THEN t.amount ELSE 0 END), 0)
                    AS total_income,
                COALESCE(SUM(CASE WHEN tt.sign = '-' THEN t.amount ELSE 0 END), 0)
                    AS total_expense,
                COALESCE(SUM(CASE WHEN tt.sign = '+' THEN t.amount ELSE -t.amount END), 0)
                    AS overall_balance
            FROM cnab_store s
            LEFT JOIN cnab_transaction t ON t.store_id = s.id
            LEFT JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id
        """
        row = self._execute_one(sql)
        if row is None:
            return {
                "total_stores": 0,
                "total_transactions": 0,
                "total_income": Decimal("0.00"),
                "total_expense": Decimal("0.00"),
                "overall_balance": Decimal("0.00"),
            }
        return row

    def get_balance_by_store(self) -> list[dict[str, Any]]:
        """Returns store names and their computed balance, ordered by store name."""
        sql = """
            SELECT
                s.name AS store_name,
                COALESCE(SUM(CASE WHEN tt.sign = '+' THEN t.amount ELSE -t.amount END), 0)
                    AS balance
            FROM cnab_store s
            LEFT JOIN cnab_transaction t ON t.store_id = s.id
            LEFT JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id
            GROUP BY s.id, s.name
            ORDER BY s.name
        """
        return self._execute_list(sql)

    def get_transactions_by_type(self) -> list[dict[str, Any]]:
        """Returns transaction count per type along with type description, ordered by code."""
        sql = """
            SELECT
                tt.description AS type_description,
                COUNT(t.id) AS transaction_count
            FROM cnab_transaction_type tt
            LEFT JOIN cnab_transaction t ON t.transaction_type_id = tt.id
            GROUP BY tt.id, tt.code, tt.description
            ORDER BY tt.code
        """
        return self._execute_list(sql)

    def get_transactions_timeline(self) -> list[dict[str, Any]]:
        """Returns transaction count grouped by occurred_at date, ordered chronologically."""
        sql = """
            SELECT
                t.occurred_at AS transaction_date,
                COUNT(t.id) AS transaction_count
            FROM cnab_transaction t
            GROUP BY t.occurred_at
            ORDER BY t.occurred_at
        """
        return self._execute_list(sql)
