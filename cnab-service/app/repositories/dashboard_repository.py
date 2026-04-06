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
    def _build_filters(
        store_id: str | None,
        owner_name: str | None,
        date_from: str | None,
        date_to: str | None,
        table_prefix: str = "t",
        store_alias: str = "s",
    ) -> tuple[list[str], dict]:
        """Builds WHERE clause conditions and bind params for the given filters.

        Returns a list of condition strings and the corresponding params dict.
        Caller is responsible for joining conditions with AND and prefixing with WHERE.
        """
        clauses: list[str] = []
        params: dict = {}

        if store_id is not None:
            clauses.append(f"{store_alias}.id = CAST(:store_id AS UUID)")
            params["store_id"] = store_id

        if owner_name is not None:
            clauses.append(f"{store_alias}.owner_name ILIKE :owner_pattern")
            params["owner_pattern"] = f"%{owner_name}%"

        if date_from is not None:
            clauses.append(f"{table_prefix}.occurred_at >= :date_from")
            params["date_from"] = date_from

        if date_to is not None:
            clauses.append(f"{table_prefix}.occurred_at <= :date_to")
            params["date_to"] = date_to

        return clauses, params

    @staticmethod
    def _join_conditions(clauses: list[str], prefix: str = " AND ") -> str:
        """Returns a joined condition string with the given prefix, or empty string."""
        if not clauses:
            return ""
        return prefix + (" AND ".join(clauses))

    @staticmethod
    def _where_clause(clauses: list[str]) -> str:
        """Returns a WHERE clause string from conditions, or empty string."""
        if not clauses:
            return ""
        return " WHERE " + " AND ".join(clauses)

    def get_summary(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any]:
        """Returns overall counts and financial totals across all stores."""
        clauses, params = self._build_filters(store_id, owner_name, date_from, date_to)
        join_filter = self._join_conditions(clauses)
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
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict[str, Any]]:
        """Returns store names and their computed balance, ordered by store name."""
        clauses, params = self._build_filters(store_id, owner_name, date_from, date_to)
        join_filter = self._join_conditions(clauses)
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
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict[str, Any]]:
        """Returns transaction count per type along with type description, ordered by code."""
        clauses, params = self._build_filters(store_id, owner_name, date_from, date_to)
        join_filter = self._join_conditions(clauses)
        sql = f"""
            SELECT
                tt.description AS type_description,
                COUNT(t.id) AS transaction_count
            FROM cnab_transaction_type tt
            LEFT JOIN cnab_transaction t ON t.transaction_type_id = tt.id{join_filter}
            LEFT JOIN cnab_store s ON s.id = t.store_id
            GROUP BY tt.id, tt.code, tt.description
            ORDER BY tt.code
        """
        return self._execute_list(sql, params)

    def get_transactions_timeline(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict[str, Any]]:
        """Returns transaction count grouped by occurred_at date, ordered chronologically."""
        t_clauses, t_params = self._build_filters(store_id, owner_name, date_from, date_to)

        if store_id is not None or owner_name is not None:
            # Need to join cnab_store when filtering by store fields
            store_join = " JOIN cnab_store s ON s.id = t.store_id"
        else:
            store_join = ""

        # Rebuild clauses without store alias for timeline (no store join by default)
        # When store_join is present, store alias 's' is available; otherwise skip store clauses
        if not store_join:
            # Only date filters — no store alias needed
            clauses: list[str] = []
            params: dict = {}
            if date_from is not None:
                clauses.append("t.occurred_at >= :date_from")
                params["date_from"] = date_from
            if date_to is not None:
                clauses.append("t.occurred_at <= :date_to")
                params["date_to"] = date_to
        else:
            clauses = t_clauses
            params = t_params

        where = self._where_clause(clauses)
        sql = f"""
            SELECT
                t.occurred_at AS transaction_date,
                COUNT(t.id) AS transaction_count
            FROM cnab_transaction t{store_join}{where}
            GROUP BY t.occurred_at
            ORDER BY t.occurred_at
        """
        return self._execute_list(sql, params)

    def get_advanced_kpis(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any]:
        """Returns cash flow, average ticket, total transactions and max expense details."""
        clauses, params = self._build_filters(store_id, owner_name, date_from, date_to)
        join_filter = self._join_conditions(clauses)

        kpi_sql = f"""
            SELECT
                COALESCE(SUM(CASE WHEN tt.sign = '+' THEN t.amount ELSE -t.amount END), 0)
                    AS cash_flow,
                COALESCE(AVG(CASE WHEN tt.sign = '+' THEN t.amount END), 0)
                    AS avg_ticket,
                COUNT(t.id) AS total_transactions
            FROM cnab_store s
            LEFT JOIN cnab_transaction t ON t.store_id = s.id{join_filter}
            LEFT JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id
        """
        kpi_row = self._execute_one(kpi_sql, params)

        expense_clauses = list(clauses) + ["tt.sign = '-'"]
        expense_params = dict(params)
        expense_join_filter = " AND ".join(expense_clauses)
        expense_where = (" WHERE " + expense_join_filter) if expense_clauses else ""
        expense_sql = f"""
            SELECT
                t.amount,
                s.name AS store_name,
                tt.description AS type_description,
                t.occurred_at
            FROM cnab_store s
            JOIN cnab_transaction t ON t.store_id = s.id
            JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id{expense_where}
            ORDER BY t.amount DESC
            LIMIT 1
        """
        expense_row = self._execute_one(expense_sql, expense_params)

        return {"kpi": kpi_row, "max_expense": expense_row}

    def get_transactions_by_hour(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict[str, Any]]:
        """Returns transaction count grouped by hour of day (0-23)."""
        clauses, params = self._build_filters(store_id, owner_name, date_from, date_to)

        if store_id is not None or owner_name is not None:
            store_join = " JOIN cnab_store s ON s.id = t.store_id"
        else:
            store_join = ""
            clauses = []
            params = {}
            if date_from is not None:
                clauses.append("t.occurred_at >= :date_from")
                params["date_from"] = date_from
            if date_to is not None:
                clauses.append("t.occurred_at <= :date_to")
                params["date_to"] = date_to

        where = self._where_clause(clauses)
        sql = f"""
            SELECT
                EXTRACT(HOUR FROM t.occurred_time) AS hour,
                COUNT(t.id) AS transaction_count
            FROM cnab_transaction t{store_join}{where}
            GROUP BY hour
            ORDER BY hour
        """
        return self._execute_list(sql, params)

    def get_transactions_detail(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Returns paginated transaction detail rows joined with type and store data."""
        clauses, params = self._build_filters(store_id, owner_name, date_from, date_to)
        where = self._where_clause(clauses)
        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        count_sql = f"""
            SELECT COUNT(t.id) AS total
            FROM cnab_transaction t
            JOIN cnab_store s ON s.id = t.store_id
            JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id{where}
        """
        count_row = self._execute_one(count_sql, {k: v for k, v in params.items() if k not in ("limit", "offset")})
        total = int(count_row["total"]) if count_row else 0

        rows_sql = f"""
            SELECT
                CAST(t.id AS TEXT) AS id,
                t.occurred_at,
                t.occurred_time,
                tt.description AS type_description,
                CASE WHEN tt.sign = '+' THEN 'entrada' ELSE 'saida' END AS nature,
                tt.sign,
                t.amount,
                t.card,
                s.name AS store_name,
                s.owner_name,
                s.owner_cpf AS cpf
            FROM cnab_transaction t
            JOIN cnab_store s ON s.id = t.store_id
            JOIN cnab_transaction_type tt ON tt.id = t.transaction_type_id{where}
            ORDER BY t.occurred_at DESC, t.occurred_time DESC
            LIMIT :limit OFFSET :offset
        """
        rows = self._execute_list(rows_sql, params)
        return {"count": total, "rows": rows}

    def get_available_filters(self) -> dict[str, Any]:
        """Returns all stores, distinct owner names, and the overall date range."""
        stores_sql = """
            SELECT
                CAST(id AS TEXT) AS id,
                name,
                owner_name
            FROM cnab_store
            ORDER BY name
        """
        owners_sql = """
            SELECT DISTINCT owner_name
            FROM cnab_store
            ORDER BY owner_name
        """
        date_range_sql = """
            SELECT
                MIN(occurred_at) AS min_date,
                MAX(occurred_at) AS max_date
            FROM cnab_transaction
        """
        stores = self._execute_list(stores_sql)
        owner_rows = self._execute_list(owners_sql)
        date_range_row = self._execute_one(date_range_sql)

        owners = [row["owner_name"] for row in owner_rows]

        min_date: str | None = None
        max_date: str | None = None
        if date_range_row:
            raw_min = date_range_row.get("min_date")
            raw_max = date_range_row.get("max_date")
            if raw_min is not None:
                min_date = raw_min.strftime("%Y-%m-%d") if hasattr(raw_min, "strftime") else str(raw_min)[:10]
            if raw_max is not None:
                max_date = raw_max.strftime("%Y-%m-%d") if hasattr(raw_max, "strftime") else str(raw_max)[:10]

        return {
            "stores": stores,
            "owners": owners,
            "date_range": {"min_date": min_date, "max_date": max_date},
        }
