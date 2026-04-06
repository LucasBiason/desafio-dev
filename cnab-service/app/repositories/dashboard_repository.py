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

    @staticmethod
    def _build_join_filter(year: int | None, month: int | None) -> tuple[str, dict]:
        """Builds extra JOIN conditions and params for filtering transactions by date.

        Returns an AND-prefixed clause string (suitable for appending to a JOIN ON clause)
        and the corresponding bind params dict.
        """
        clauses: list[str] = []
        params: dict = {}
        if year is not None:
            clauses.append("EXTRACT(YEAR FROM t.occurred_at) = :year")
            params["year"] = year
        if year is not None and month is not None:
            clauses.append("EXTRACT(MONTH FROM t.occurred_at) = :month")
            params["month"] = month
        join_filter = (" AND " + " AND ".join(clauses)) if clauses else ""
        return join_filter, params

    @staticmethod
    def _build_where_filter(year: int | None, month: int | None) -> tuple[str, dict]:
        """Builds a WHERE clause and params for filtering transactions by date."""
        clauses: list[str] = []
        params: dict = {}
        if year is not None:
            clauses.append("EXTRACT(YEAR FROM t.occurred_at) = :year")
            params["year"] = year
        if year is not None and month is not None:
            clauses.append("EXTRACT(MONTH FROM t.occurred_at) = :month")
            params["month"] = month
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        return where, params

    def get_summary(
        self,
        year: int | None = None,
        month: int | None = None,
    ) -> dict[str, Any]:
        """Returns overall counts and financial totals across all stores."""
        join_filter, params = self._build_join_filter(year, month)
        sql = f"""
            SELECT
                COUNT(DISTINCT CASE WHEN t.id IS NOT NULL THEN s.id END) AS total_stores,
                COUNT(t.id) AS total_transactions,
                COALESCE(SUM(CASE WHEN tt.sign = '+' THEN t.amount ELSE 0 END), 0)
                    AS total_income,
                COALESCE(SUM(CASE WHEN tt.sign = '-' THEN t.amount ELSE 0 END), 0)
                    AS total_expense,
                COALESCE(SUM(CASE WHEN tt.sign = '+' THEN t.amount ELSE -t.amount END), 0)
                    AS overall_balance
            FROM cnab_store s
            LEFT JOIN cnab_transaction t ON t.store_id = s.id{join_filter}
            LEFT JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id
        """
        row = self._execute_one(sql, params)
        if row is None:
            return {
                "total_stores": 0,
                "total_transactions": 0,
                "total_income": Decimal("0.00"),
                "total_expense": Decimal("0.00"),
                "overall_balance": Decimal("0.00"),
            }
        return row

    def get_balance_by_store(
        self,
        year: int | None = None,
        month: int | None = None,
    ) -> list[dict[str, Any]]:
        """Returns store names and their computed balance, ordered by store name."""
        join_filter, params = self._build_join_filter(year, month)
        sql = f"""
            SELECT
                s.name AS store_name,
                COALESCE(SUM(CASE WHEN tt.sign = '+' THEN t.amount ELSE -t.amount END), 0)
                    AS balance
            FROM cnab_store s
            LEFT JOIN cnab_transaction t ON t.store_id = s.id{join_filter}
            LEFT JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id
            GROUP BY s.id, s.name
            ORDER BY s.name
        """
        return self._execute_list(sql, params)

    def get_transactions_by_type(
        self,
        year: int | None = None,
        month: int | None = None,
    ) -> list[dict[str, Any]]:
        """Returns transaction count per type along with type description, ordered by code."""
        join_filter, params = self._build_join_filter(year, month)
        sql = f"""
            SELECT
                tt.description AS type_description,
                COUNT(t.id) AS transaction_count
            FROM cnab_transaction_type tt
            LEFT JOIN cnab_transaction t ON t.transaction_type_id = tt.id{join_filter}
            GROUP BY tt.id, tt.code, tt.description
            ORDER BY tt.code
        """
        return self._execute_list(sql, params)

    def get_transactions_timeline(
        self,
        year: int | None = None,
        month: int | None = None,
    ) -> list[dict[str, Any]]:
        """Returns transaction count grouped by occurred_at date, ordered chronologically."""
        where, params = self._build_where_filter(year, month)
        sql = f"""
            SELECT
                t.occurred_at AS transaction_date,
                COUNT(t.id) AS transaction_count
            FROM cnab_transaction t{where}
            GROUP BY t.occurred_at
            ORDER BY t.occurred_at
        """
        return self._execute_list(sql, params)
