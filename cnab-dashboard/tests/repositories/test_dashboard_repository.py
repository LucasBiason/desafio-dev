"""Tests for DashboardRepository."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

from app.repositories.dashboard_repository import DashboardRepository


def _make_row(**kwargs):
    """Creates a mock SQLAlchemy Row with _mapping returning the given kwargs."""
    row = MagicMock()
    row._mapping = kwargs
    return row


def _make_db(fetchone_result=None, fetchall_result=None):
    """Returns a mocked Session whose execute() chain returns controlled data."""
    db = MagicMock()
    execute_result = MagicMock()
    execute_result.fetchone.return_value = fetchone_result
    execute_result.fetchall.return_value = fetchall_result or []
    db.execute.return_value = execute_result
    return db


# ---------------------------------------------------------------------------
# Static helper: _build_filters
# ---------------------------------------------------------------------------


class TestBuildFilters:
    """Tests for DashboardRepository._build_filters."""

    def test_no_params_returns_empty_clauses_and_params(self):
        """_build_filters with all None args returns empty list and empty dict."""
        clauses, params = DashboardRepository._build_filters(None, None, None, None)
        assert clauses == []
        assert params == {}

    def test_store_id_adds_uuid_cast_clause(self):
        """_build_filters with store_id adds a CAST AS UUID condition."""
        clauses, params = DashboardRepository._build_filters("abc-123", None, None, None)
        assert any("CAST(:store_id AS UUID)" in c for c in clauses)
        assert params["store_id"] == "abc-123"

    def test_owner_name_adds_ilike_clause(self):
        """_build_filters with owner_name adds an ILIKE condition with wildcards."""
        clauses, params = DashboardRepository._build_filters(None, "Maria", None, None)
        assert any("ILIKE :owner_pattern" in c for c in clauses)
        assert params["owner_pattern"] == "%Maria%"

    def test_date_from_adds_gte_clause(self):
        """_build_filters with date_from adds a >= condition."""
        clauses, params = DashboardRepository._build_filters(None, None, "2024-01-01", None)
        assert any(">= :date_from" in c for c in clauses)
        assert params["date_from"] == "2024-01-01"

    def test_date_to_adds_lte_clause(self):
        """_build_filters with date_to adds a <= condition."""
        clauses, params = DashboardRepository._build_filters(None, None, None, "2024-12-31")
        assert any("<= :date_to" in c for c in clauses)
        assert params["date_to"] == "2024-12-31"

    def test_all_params_returns_four_clauses(self):
        """_build_filters with all params returns exactly four clauses."""
        clauses, params = DashboardRepository._build_filters(
            "store-uuid", "Pedro", "2024-01-01", "2024-12-31"
        )
        assert len(clauses) == 4
        assert "store_id" in params
        assert "owner_pattern" in params
        assert "date_from" in params
        assert "date_to" in params

    def test_custom_table_prefix_is_applied(self):
        """_build_filters uses the given table_prefix for date conditions."""
        clauses, _ = DashboardRepository._build_filters(
            None, None, "2024-01-01", None, table_prefix="tx"
        )
        assert any("tx.occurred_at" in c for c in clauses)

    def test_custom_store_alias_is_applied(self):
        """_build_filters uses the given store_alias for store conditions."""
        clauses, _ = DashboardRepository._build_filters(
            "some-id", None, None, None, store_alias="store"
        )
        assert any("store.id = CAST" in c for c in clauses)

    def test_store_id_only_returns_one_clause(self):
        """_build_filters with only store_id returns a single clause."""
        clauses, params = DashboardRepository._build_filters("uuid-only", None, None, None)
        assert len(clauses) == 1
        assert "store_id" in params
        assert "owner_pattern" not in params

    def test_dates_only_returns_two_clauses(self):
        """_build_filters with only date range returns two clauses."""
        clauses, params = DashboardRepository._build_filters(None, None, "2024-03-01", "2024-03-31")
        assert len(clauses) == 2
        assert "date_from" in params
        assert "date_to" in params
        assert "store_id" not in params


# ---------------------------------------------------------------------------
# Static helper: _join_conditions
# ---------------------------------------------------------------------------


class TestJoinConditions:
    """Tests for DashboardRepository._join_conditions."""

    def test_empty_list_returns_empty_string(self):
        """_join_conditions with no conditions returns an empty string."""
        result = DashboardRepository._join_conditions([])
        assert result == ""

    def test_single_condition_prefixed_with_and(self):
        """_join_conditions with one condition returns ' AND <condition>'."""
        result = DashboardRepository._join_conditions(["s.id = :x"])
        assert result == " AND s.id = :x"

    def test_multiple_conditions_joined_with_and(self):
        """_join_conditions with multiple conditions joins them all with AND."""
        result = DashboardRepository._join_conditions(["a = :a", "b = :b"])
        assert result == " AND a = :a AND b = :b"

    def test_custom_prefix_is_used(self):
        """_join_conditions respects a custom prefix argument."""
        result = DashboardRepository._join_conditions(["x = :x"], prefix=" OR ")
        assert result.startswith(" OR ")

    def test_two_conditions_with_custom_prefix(self):
        """_join_conditions with custom prefix still joins internal conditions with AND."""
        result = DashboardRepository._join_conditions(["x = :x", "y = :y"], prefix=" OR ")
        assert result == " OR x = :x AND y = :y"


# ---------------------------------------------------------------------------
# Static helper: _where_clause
# ---------------------------------------------------------------------------


class TestWhereClause:
    """Tests for DashboardRepository._where_clause."""

    def test_empty_list_returns_empty_string(self):
        """_where_clause with no conditions returns an empty string."""
        result = DashboardRepository._where_clause([])
        assert result == ""

    def test_single_condition_produces_where_clause(self):
        """_where_clause with one condition returns ' WHERE <condition>'."""
        result = DashboardRepository._where_clause(["t.id IS NOT NULL"])
        assert result == " WHERE t.id IS NOT NULL"

    def test_multiple_conditions_joined_with_and(self):
        """_where_clause joins multiple conditions with AND inside WHERE."""
        result = DashboardRepository._where_clause(["a = :a", "b = :b"])
        assert result == " WHERE a = :a AND b = :b"


# ---------------------------------------------------------------------------
# get_summary
# ---------------------------------------------------------------------------


class TestGetSummary:
    """Tests for DashboardRepository.get_summary."""

    def test_returns_row_data_when_result_exists(self):
        """get_summary returns the row dict when the query returns data."""
        row = _make_row(
            total_stores=3,
            total_transactions=10,
            total_income=Decimal("500.00"),
            total_expense=Decimal("200.00"),
            overall_balance=Decimal("300.00"),
        )
        db = _make_db(fetchone_result=row)
        repo = DashboardRepository(db=db)

        result = repo.get_summary()

        assert result["total_stores"] == 3
        assert result["total_transactions"] == 10
        assert result["total_income"] == Decimal("500.00")
        assert result["overall_balance"] == Decimal("300.00")

    def test_returns_default_zeros_when_execute_returns_none(self):
        """get_summary returns zeroed defaults when no row is returned."""
        db = _make_db(fetchone_result=None)
        repo = DashboardRepository(db=db)

        result = repo.get_summary()

        assert result["total_stores"] == 0
        assert result["total_transactions"] == 0
        assert result["total_income"] == Decimal("0.00")
        assert result["total_expense"] == Decimal("0.00")
        assert result["overall_balance"] == Decimal("0.00")

    def test_passes_filter_params_to_execute(self):
        """get_summary forwards filter arguments to the underlying execute call."""
        row = _make_row(
            total_stores=1,
            total_transactions=2,
            total_income=Decimal("100.00"),
            total_expense=Decimal("50.00"),
            overall_balance=Decimal("50.00"),
        )
        db = _make_db(fetchone_result=row)
        repo = DashboardRepository(db=db)

        repo.get_summary(store_id="some-uuid", date_from="2024-01-01")

        db.execute.assert_called_once()
        _, call_params = db.execute.call_args[0]
        assert call_params["store_id"] == "some-uuid"
        assert call_params["date_from"] == "2024-01-01"


# ---------------------------------------------------------------------------
# get_balance_by_store
# ---------------------------------------------------------------------------


class TestGetBalanceByStore:
    """Tests for DashboardRepository.get_balance_by_store."""

    def test_returns_list_of_store_balance_dicts(self):
        """get_balance_by_store returns one dict per store with name and balance."""
        rows = [
            _make_row(store_name="Loja A", balance=Decimal("100.00")),
            _make_row(store_name="Loja B", balance=Decimal("-50.00")),
        ]
        db = _make_db(fetchall_result=rows)
        repo = DashboardRepository(db=db)

        result = repo.get_balance_by_store()

        assert len(result) == 2
        assert result[0]["store_name"] == "Loja A"
        assert result[1]["balance"] == Decimal("-50.00")

    def test_returns_empty_list_when_no_stores(self):
        """get_balance_by_store returns an empty list when no rows are returned."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        result = repo.get_balance_by_store()

        assert result == []

    def test_with_owner_name_filter(self):
        """get_balance_by_store passes owner_name filter to execute."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        repo.get_balance_by_store(owner_name="Carlos")

        _, call_params = db.execute.call_args[0]
        assert "owner_pattern" in call_params
        assert "Carlos" in call_params["owner_pattern"]


# ---------------------------------------------------------------------------
# get_transactions_by_type
# ---------------------------------------------------------------------------


class TestGetTransactionsByType:
    """Tests for DashboardRepository.get_transactions_by_type."""

    def test_returns_list_of_type_dicts(self):
        """get_transactions_by_type returns a list with description and count per type."""
        rows = [
            _make_row(type_description="Debito", transaction_count=5),
            _make_row(type_description="Credito", transaction_count=3),
        ]
        db = _make_db(fetchall_result=rows)
        repo = DashboardRepository(db=db)

        result = repo.get_transactions_by_type()

        assert len(result) == 2
        assert result[0]["type_description"] == "Debito"
        assert result[0]["transaction_count"] == 5

    def test_returns_empty_list_when_no_types(self):
        """get_transactions_by_type returns an empty list when no data exists."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        result = repo.get_transactions_by_type()

        assert result == []

    def test_with_date_filters(self):
        """get_transactions_by_type forwards date filters to execute."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        repo.get_transactions_by_type(date_from="2024-06-01", date_to="2024-06-30")

        _, call_params = db.execute.call_args[0]
        assert call_params["date_from"] == "2024-06-01"
        assert call_params["date_to"] == "2024-06-30"


# ---------------------------------------------------------------------------
# get_transactions_timeline
# ---------------------------------------------------------------------------


class TestGetTransactionsTimeline:
    """Tests for DashboardRepository.get_transactions_timeline."""

    def test_returns_list_of_date_count_dicts(self):
        """get_transactions_timeline returns rows with transaction_date and count."""
        rows = [
            _make_row(transaction_date="2024-01-10", transaction_count=4),
            _make_row(transaction_date="2024-01-11", transaction_count=2),
        ]
        db = _make_db(fetchall_result=rows)
        repo = DashboardRepository(db=db)

        result = repo.get_transactions_timeline()

        assert len(result) == 2
        assert result[0]["transaction_date"] == "2024-01-10"
        assert result[1]["transaction_count"] == 2

    def test_with_store_id_includes_store_join_in_sql(self):
        """get_transactions_timeline includes store JOIN when store_id is provided."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        repo.get_transactions_timeline(store_id="some-uuid")

        sql_text = str(db.execute.call_args[0][0])
        assert "cnab_store" in sql_text

    def test_with_owner_name_includes_store_join_in_sql(self):
        """get_transactions_timeline includes store JOIN when owner_name is provided."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        repo.get_transactions_timeline(owner_name="Ana")

        sql_text = str(db.execute.call_args[0][0])
        assert "cnab_store" in sql_text

    def test_without_store_filters_no_store_join(self):
        """get_transactions_timeline omits store JOIN when no store filters are given."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        repo.get_transactions_timeline(date_from="2024-01-01", date_to="2024-01-31")

        sql_text = str(db.execute.call_args[0][0])
        assert "JOIN cnab_store" not in sql_text

    def test_date_filters_without_store_filters_pass_params(self):
        """get_transactions_timeline passes date params when no store filters are given."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        repo.get_transactions_timeline(date_from="2024-05-01", date_to="2024-05-31")

        _, call_params = db.execute.call_args[0]
        assert call_params.get("date_from") == "2024-05-01"
        assert call_params.get("date_to") == "2024-05-31"

    def test_no_filters_returns_all_dates(self):
        """get_transactions_timeline with no filters returns all date rows."""
        rows = [_make_row(transaction_date="2024-03-01", transaction_count=1)]
        db = _make_db(fetchall_result=rows)
        repo = DashboardRepository(db=db)

        result = repo.get_transactions_timeline()

        assert len(result) == 1


# ---------------------------------------------------------------------------
# get_advanced_kpis
# ---------------------------------------------------------------------------


class TestGetAdvancedKpis:
    """Tests for DashboardRepository.get_advanced_kpis."""

    def test_returns_dict_with_kpi_and_max_expense(self):
        """get_advanced_kpis returns both kpi and max_expense when data exists."""
        kpi_row = _make_row(
            cash_flow=Decimal("300.00"),
            avg_ticket=Decimal("150.00"),
            total_transactions=4,
        )
        expense_row = _make_row(
            amount=Decimal("200.00"),
            store_name="Loja X",
            type_description="Boleto",
            occurred_at="2024-03-15",
        )

        db = MagicMock()
        execute_result_kpi = MagicMock()
        execute_result_kpi.fetchone.return_value = kpi_row
        execute_result_expense = MagicMock()
        execute_result_expense.fetchone.return_value = expense_row
        db.execute.side_effect = [execute_result_kpi, execute_result_expense]

        repo = DashboardRepository(db=db)
        result = repo.get_advanced_kpis()

        assert result["kpi"]["cash_flow"] == Decimal("300.00")
        assert result["max_expense"]["store_name"] == "Loja X"

    def test_returns_none_max_expense_when_no_expenses(self):
        """get_advanced_kpis returns max_expense=None when no expense row exists."""
        kpi_row = _make_row(
            cash_flow=Decimal("0.00"),
            avg_ticket=Decimal("0.00"),
            total_transactions=0,
        )

        db = MagicMock()
        execute_result_kpi = MagicMock()
        execute_result_kpi.fetchone.return_value = kpi_row
        execute_result_expense = MagicMock()
        execute_result_expense.fetchone.return_value = None
        db.execute.side_effect = [execute_result_kpi, execute_result_expense]

        repo = DashboardRepository(db=db)
        result = repo.get_advanced_kpis()

        assert result["max_expense"] is None

    def test_returns_none_kpi_when_no_kpi_row(self):
        """get_advanced_kpis returns kpi=None when the KPI query returns nothing."""
        db = MagicMock()
        execute_result_kpi = MagicMock()
        execute_result_kpi.fetchone.return_value = None
        execute_result_expense = MagicMock()
        execute_result_expense.fetchone.return_value = None
        db.execute.side_effect = [execute_result_kpi, execute_result_expense]

        repo = DashboardRepository(db=db)
        result = repo.get_advanced_kpis()

        assert result["kpi"] is None
        assert result["max_expense"] is None

    def test_executes_two_queries(self):
        """get_advanced_kpis issues exactly two SQL execute calls."""
        kpi_row = _make_row(cash_flow=Decimal("0"), avg_ticket=Decimal("0"), total_transactions=0)

        db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = kpi_row
        mock_result_expense = MagicMock()
        mock_result_expense.fetchone.return_value = None
        db.execute.side_effect = [mock_result, mock_result_expense]

        repo = DashboardRepository(db=db)
        repo.get_advanced_kpis()

        assert db.execute.call_count == 2


# ---------------------------------------------------------------------------
# get_transactions_by_hour
# ---------------------------------------------------------------------------


class TestGetTransactionsByHour:
    """Tests for DashboardRepository.get_transactions_by_hour."""

    def test_returns_list_of_hour_count_dicts(self):
        """get_transactions_by_hour returns rows with hour and count."""
        rows = [
            _make_row(hour=9, transaction_count=3),
            _make_row(hour=14, transaction_count=7),
        ]
        db = _make_db(fetchall_result=rows)
        repo = DashboardRepository(db=db)

        result = repo.get_transactions_by_hour()

        assert len(result) == 2
        assert result[0]["hour"] == 9
        assert result[1]["transaction_count"] == 7

    def test_returns_empty_list_when_no_transactions(self):
        """get_transactions_by_hour returns an empty list when no rows exist."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        result = repo.get_transactions_by_hour()

        assert result == []

    def test_with_store_id_includes_store_join(self):
        """get_transactions_by_hour includes store JOIN when store_id is given."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        repo.get_transactions_by_hour(store_id="some-uuid")

        sql_text = str(db.execute.call_args[0][0])
        assert "cnab_store" in sql_text

    def test_without_store_filters_no_store_join(self):
        """get_transactions_by_hour omits store JOIN when no store filter is given."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        repo.get_transactions_by_hour(date_from="2024-01-01")

        sql_text = str(db.execute.call_args[0][0])
        assert "JOIN cnab_store" not in sql_text

    def test_date_filter_without_store_passes_params(self):
        """get_transactions_by_hour passes date params when no store filters are given."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        repo.get_transactions_by_hour(date_from="2024-09-01", date_to="2024-09-30")

        _, call_params = db.execute.call_args[0]
        assert call_params.get("date_from") == "2024-09-01"
        assert call_params.get("date_to") == "2024-09-30"

    def test_sql_uses_extract_hour(self):
        """get_transactions_by_hour uses EXTRACT(HOUR FROM ...) in the query."""
        db = _make_db(fetchall_result=[])
        repo = DashboardRepository(db=db)

        repo.get_transactions_by_hour()

        sql_text = str(db.execute.call_args[0][0])
        assert "EXTRACT" in sql_text
        assert "HOUR" in sql_text


# ---------------------------------------------------------------------------
# get_transactions_detail
# ---------------------------------------------------------------------------


class TestGetTransactionsDetail:
    """Tests for DashboardRepository.get_transactions_detail."""

    def test_returns_dict_with_count_and_rows(self):
        """get_transactions_detail returns a dict with total count and row list."""
        count_row = _make_row(total=5)
        detail_rows = [
            _make_row(
                id="tx-1",
                occurred_at="2024-01-10",
                occurred_time="10:00:00",
                type_description="Debito",
                nature="saida",
                sign="-",
                amount=Decimal("50.00"),
                card="1234****",
                store_name="Loja A",
                owner_name="Joao",
                cpf="12345678901",
            )
        ]

        db = MagicMock()
        count_execute = MagicMock()
        count_execute.fetchone.return_value = count_row
        rows_execute = MagicMock()
        rows_execute.fetchall.return_value = detail_rows
        db.execute.side_effect = [count_execute, rows_execute]

        repo = DashboardRepository(db=db)
        result = repo.get_transactions_detail()

        assert result["count"] == 5
        assert len(result["rows"]) == 1
        assert result["rows"][0]["id"] == "tx-1"

    def test_page_and_page_size_affect_offset(self):
        """get_transactions_detail computes the correct OFFSET for page > 1."""
        count_row = _make_row(total=100)

        db = MagicMock()
        count_execute = MagicMock()
        count_execute.fetchone.return_value = count_row
        rows_execute = MagicMock()
        rows_execute.fetchall.return_value = []
        db.execute.side_effect = [count_execute, rows_execute]

        repo = DashboardRepository(db=db)
        repo.get_transactions_detail(page=3, page_size=10)

        rows_call_params = db.execute.call_args_list[1][0][1]
        assert rows_call_params["offset"] == 20
        assert rows_call_params["limit"] == 10

    def test_first_page_offset_is_zero(self):
        """get_transactions_detail uses offset=0 for page=1."""
        count_row = _make_row(total=0)

        db = MagicMock()
        count_execute = MagicMock()
        count_execute.fetchone.return_value = count_row
        rows_execute = MagicMock()
        rows_execute.fetchall.return_value = []
        db.execute.side_effect = [count_execute, rows_execute]

        repo = DashboardRepository(db=db)
        repo.get_transactions_detail(page=1, page_size=20)

        rows_call_params = db.execute.call_args_list[1][0][1]
        assert rows_call_params["offset"] == 0

    def test_count_zero_when_count_row_is_none(self):
        """get_transactions_detail returns count=0 when the count query returns None."""
        db = MagicMock()
        count_execute = MagicMock()
        count_execute.fetchone.return_value = None
        rows_execute = MagicMock()
        rows_execute.fetchall.return_value = []
        db.execute.side_effect = [count_execute, rows_execute]

        repo = DashboardRepository(db=db)
        result = repo.get_transactions_detail()

        assert result["count"] == 0
        assert result["rows"] == []

    def test_count_query_excludes_limit_and_offset_params(self):
        """get_transactions_detail does not pass limit/offset to the count query."""
        count_row = _make_row(total=0)

        db = MagicMock()
        count_execute = MagicMock()
        count_execute.fetchone.return_value = count_row
        rows_execute = MagicMock()
        rows_execute.fetchall.return_value = []
        db.execute.side_effect = [count_execute, rows_execute]

        repo = DashboardRepository(db=db)
        repo.get_transactions_detail(store_id="uuid", page=2, page_size=5)

        count_call_params = db.execute.call_args_list[0][0][1]
        assert "limit" not in count_call_params
        assert "offset" not in count_call_params


# ---------------------------------------------------------------------------
# get_available_filters
# ---------------------------------------------------------------------------


class TestGetAvailableFilters:
    """Tests for DashboardRepository.get_available_filters."""

    def test_returns_stores_owners_and_date_range(self):
        """get_available_filters returns all three keys with correct structure."""
        store_rows = [
            _make_row(id="uuid-1", name="Loja A", owner_name="Joao"),
            _make_row(id="uuid-2", name="Loja B", owner_name="Maria"),
        ]
        owner_rows = [
            _make_row(owner_name="Joao"),
            _make_row(owner_name="Maria"),
        ]
        date_row = _make_row(min_date=date(2024, 1, 1), max_date=date(2024, 12, 31))

        db = MagicMock()
        stores_exec = MagicMock()
        stores_exec.fetchall.return_value = store_rows
        owners_exec = MagicMock()
        owners_exec.fetchall.return_value = owner_rows
        date_exec = MagicMock()
        date_exec.fetchone.return_value = date_row
        db.execute.side_effect = [stores_exec, owners_exec, date_exec]

        repo = DashboardRepository(db=db)
        result = repo.get_available_filters()

        assert len(result["stores"]) == 2
        assert result["owners"] == ["Joao", "Maria"]
        assert "date_range" in result

    def test_date_range_formatted_from_date_objects(self):
        """get_available_filters formats date objects as YYYY-MM-DD strings."""
        store_rows = []
        owner_rows = []
        date_row = _make_row(min_date=date(2024, 3, 15), max_date=date(2024, 11, 20))

        db = MagicMock()
        stores_exec = MagicMock()
        stores_exec.fetchall.return_value = store_rows
        owners_exec = MagicMock()
        owners_exec.fetchall.return_value = owner_rows
        date_exec = MagicMock()
        date_exec.fetchone.return_value = date_row
        db.execute.side_effect = [stores_exec, owners_exec, date_exec]

        repo = DashboardRepository(db=db)
        result = repo.get_available_filters()

        assert result["date_range"]["min_date"] == "2024-03-15"
        assert result["date_range"]["max_date"] == "2024-11-20"

    def test_date_range_formatted_from_datetime_objects(self):
        """get_available_filters formats datetime objects as YYYY-MM-DD strings."""
        store_rows = []
        owner_rows = []
        date_row = _make_row(
            min_date=datetime(2024, 2, 5, 8, 30, 0),
            max_date=datetime(2024, 10, 22, 18, 0, 0),
        )

        db = MagicMock()
        stores_exec = MagicMock()
        stores_exec.fetchall.return_value = store_rows
        owners_exec = MagicMock()
        owners_exec.fetchall.return_value = owner_rows
        date_exec = MagicMock()
        date_exec.fetchone.return_value = date_row
        db.execute.side_effect = [stores_exec, owners_exec, date_exec]

        repo = DashboardRepository(db=db)
        result = repo.get_available_filters()

        assert result["date_range"]["min_date"] == "2024-02-05"
        assert result["date_range"]["max_date"] == "2024-10-22"

    def test_date_range_none_when_no_date_row(self):
        """get_available_filters returns None dates when no transactions exist."""
        store_rows = []
        owner_rows = []

        db = MagicMock()
        stores_exec = MagicMock()
        stores_exec.fetchall.return_value = store_rows
        owners_exec = MagicMock()
        owners_exec.fetchall.return_value = owner_rows
        date_exec = MagicMock()
        date_exec.fetchone.return_value = None
        db.execute.side_effect = [stores_exec, owners_exec, date_exec]

        repo = DashboardRepository(db=db)
        result = repo.get_available_filters()

        assert result["date_range"]["min_date"] is None
        assert result["date_range"]["max_date"] is None

    def test_date_range_none_values_stay_none(self):
        """get_available_filters keeps dates as None when the row contains None values."""
        store_rows = []
        owner_rows = []
        date_row = _make_row(min_date=None, max_date=None)

        db = MagicMock()
        stores_exec = MagicMock()
        stores_exec.fetchall.return_value = store_rows
        owners_exec = MagicMock()
        owners_exec.fetchall.return_value = owner_rows
        date_exec = MagicMock()
        date_exec.fetchone.return_value = date_row
        db.execute.side_effect = [stores_exec, owners_exec, date_exec]

        repo = DashboardRepository(db=db)
        result = repo.get_available_filters()

        assert result["date_range"]["min_date"] is None
        assert result["date_range"]["max_date"] is None

    def test_owners_extracted_as_flat_list(self):
        """get_available_filters extracts owner_name values into a flat list."""
        store_rows = []
        owner_rows = [
            _make_row(owner_name="Alice"),
            _make_row(owner_name="Bob"),
            _make_row(owner_name="Carol"),
        ]
        date_row = _make_row(min_date=None, max_date=None)

        db = MagicMock()
        stores_exec = MagicMock()
        stores_exec.fetchall.return_value = store_rows
        owners_exec = MagicMock()
        owners_exec.fetchall.return_value = owner_rows
        date_exec = MagicMock()
        date_exec.fetchone.return_value = date_row
        db.execute.side_effect = [stores_exec, owners_exec, date_exec]

        repo = DashboardRepository(db=db)
        result = repo.get_available_filters()

        assert result["owners"] == ["Alice", "Bob", "Carol"]

    def test_executes_exactly_three_queries(self):
        """get_available_filters issues exactly three SQL execute calls."""
        store_rows = []
        owner_rows = []
        date_row = _make_row(min_date=None, max_date=None)

        db = MagicMock()
        stores_exec = MagicMock()
        stores_exec.fetchall.return_value = store_rows
        owners_exec = MagicMock()
        owners_exec.fetchall.return_value = owner_rows
        date_exec = MagicMock()
        date_exec.fetchone.return_value = date_row
        db.execute.side_effect = [stores_exec, owners_exec, date_exec]

        repo = DashboardRepository(db=db)
        repo.get_available_filters()

        assert db.execute.call_count == 3
