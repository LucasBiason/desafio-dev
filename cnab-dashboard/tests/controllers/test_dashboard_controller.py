"""Tests for DashboardController."""

from datetime import date, time
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.controllers.dashboard_controller import DashboardController
from app.schemas.dashboard_schema import (
    AdvancedKPIsResponse,
    AvailableFiltersResponse,
    BalanceByStoreResponse,
    DashboardSummaryResponse,
    TransactionDetailResponse,
    TransactionsByHourResponse,
    TransactionsByTypeResponse,
    UploadsTimelineResponse,
)


def _make_controller() -> DashboardController:
    """Creates a DashboardController with a mock db session."""
    return DashboardController(db=MagicMock())


class TestGetSummary:
    """Tests for DashboardController.get_summary."""

    def test_returns_summary_response_with_correct_values(self):
        """get_summary maps repo row fields to DashboardSummaryResponse."""
        controller = _make_controller()
        repo_row = {
            "total_stores": 3,
            "total_transactions": 120,
            "total_income": Decimal("5000.00"),
            "total_expense": Decimal("1500.00"),
            "overall_balance": Decimal("3500.00"),
        }
        with patch.object(controller._repo, "get_summary", return_value=repo_row):
            result = controller.get_summary()

        assert isinstance(result, DashboardSummaryResponse)
        assert result.total_stores == 3
        assert result.total_transactions == 120
        assert result.total_income == Decimal("5000.00")
        assert result.total_expense == Decimal("1500.00")
        assert result.overall_balance == Decimal("3500.00")

    def test_passes_filter_params_to_repository(self):
        """get_summary forwards all filter arguments to the repository."""
        controller = _make_controller()
        repo_row = {
            "total_stores": 1,
            "total_transactions": 10,
            "total_income": Decimal("100.00"),
            "total_expense": Decimal("50.00"),
            "overall_balance": Decimal("50.00"),
        }
        with patch.object(controller._repo, "get_summary", return_value=repo_row) as mock_get:
            controller.get_summary(
                store_id="store-abc",
                owner_name="Alice",
                date_from="2024-01-01",
                date_to="2024-12-31",
            )

        mock_get.assert_called_once_with(
            store_id="store-abc",
            owner_name="Alice",
            date_from="2024-01-01",
            date_to="2024-12-31",
        )


class TestGetBalanceByStore:
    """Tests for DashboardController.get_balance_by_store."""

    def test_returns_labels_and_data_from_rows(self):
        """get_balance_by_store populates labels and data from repo rows."""
        controller = _make_controller()
        repo_rows = [
            {"store_name": "Store A", "balance": Decimal("200.00")},
            {"store_name": "Store B", "balance": Decimal("-50.00")},
        ]
        with patch.object(controller._repo, "get_balance_by_store", return_value=repo_rows):
            result = controller.get_balance_by_store()

        assert isinstance(result, BalanceByStoreResponse)
        assert result.labels == ["Store A", "Store B"]
        assert result.data == [Decimal("200.00"), Decimal("-50.00")]

    def test_empty_rows_returns_empty_labels_and_data(self):
        """get_balance_by_store returns empty lists when no rows exist."""
        controller = _make_controller()
        with patch.object(controller._repo, "get_balance_by_store", return_value=[]):
            result = controller.get_balance_by_store()

        assert result.labels == []
        assert result.data == []


class TestGetTransactionsByType:
    """Tests for DashboardController.get_transactions_by_type."""

    def test_returns_labels_data_and_colors(self):
        """get_transactions_by_type maps repo rows to labels, data and colors."""
        controller = _make_controller()
        repo_rows = [
            {"type_description": "Debito", "transaction_count": 40},
            {"type_description": "Credito", "transaction_count": 25},
        ]
        with patch.object(controller._repo, "get_transactions_by_type", return_value=repo_rows):
            result = controller.get_transactions_by_type()

        assert isinstance(result, TransactionsByTypeResponse)
        assert result.labels == ["Debito", "Credito"]
        assert result.data == [40, 25]
        assert len(result.colors) == 2

    def test_colors_cycle_through_type_colors(self):
        """Colors are assigned cycling through _TYPE_COLORS for each row."""
        from app.repositories.dashboard_repository import _TYPE_COLORS

        controller = _make_controller()
        # Build enough rows to force color cycling
        num_rows = len(_TYPE_COLORS) + 2
        repo_rows = [{"type_description": f"Type {i}", "transaction_count": i} for i in range(num_rows)]
        with patch.object(controller._repo, "get_transactions_by_type", return_value=repo_rows):
            result = controller.get_transactions_by_type()

        expected_colors = [_TYPE_COLORS[i % len(_TYPE_COLORS)] for i in range(num_rows)]
        assert result.colors == expected_colors


class TestGetTransactionsTimeline:
    """Tests for DashboardController.get_transactions_timeline."""

    def test_formats_labels_as_dd_mm_yyyy(self):
        """get_transactions_timeline returns labels in DD/MM/YYYY format."""
        controller = _make_controller()
        repo_rows = [
            {"transaction_date": "2024-03-15", "transaction_count": 5},
            {"transaction_date": "2024-03-16", "transaction_count": 8},
        ]
        with patch.object(controller._repo, "get_transactions_timeline", return_value=repo_rows):
            result = controller.get_transactions_timeline()

        assert isinstance(result, UploadsTimelineResponse)
        assert result.labels == ["15/03/2024", "16/03/2024"]
        assert result.data == [5, 8]

    def test_handles_datetime_date_objects(self):
        """get_transactions_timeline calls strftime on datetime.date objects."""
        controller = _make_controller()
        repo_rows = [
            {"transaction_date": date(2024, 7, 4), "transaction_count": 3},
        ]
        with patch.object(controller._repo, "get_transactions_timeline", return_value=repo_rows):
            result = controller.get_transactions_timeline()

        assert result.labels == ["04/07/2024"]
        assert result.data == [3]

    def test_handles_string_date_yyyy_mm_dd(self):
        """get_transactions_timeline parses string dates in YYYY-MM-DD format."""
        controller = _make_controller()
        repo_rows = [
            {"transaction_date": "2024-12-01", "transaction_count": 10},
        ]
        with patch.object(controller._repo, "get_transactions_timeline", return_value=repo_rows):
            result = controller.get_transactions_timeline()

        assert result.labels == ["01/12/2024"]

    def test_handles_unexpected_date_format_gracefully(self):
        """get_transactions_timeline falls back to raw string for unexpected formats."""
        controller = _make_controller()
        repo_rows = [
            {"transaction_date": "unexpected", "transaction_count": 1},
        ]
        with patch.object(controller._repo, "get_transactions_timeline", return_value=repo_rows):
            result = controller.get_transactions_timeline()

        assert result.labels == ["unexpected"]


class TestGetAdvancedKpis:
    """Tests for DashboardController.get_advanced_kpis."""

    def test_returns_kpi_response_with_max_expense(self):
        """get_advanced_kpis assembles AdvancedKPIsResponse with max_expense present."""
        controller = _make_controller()
        repo_result = {
            "kpi": {
                "cash_flow": Decimal("3500.00"),
                "avg_ticket": Decimal("87.50"),
                "total_transactions": 40,
            },
            "max_expense": {
                "amount": Decimal("500.00"),
                "store_name": "Store Alpha",
                "type_description": "Boleto",
                "occurred_at": "2024-06-15",
            },
        }
        with patch.object(controller._repo, "get_advanced_kpis", return_value=repo_result):
            result = controller.get_advanced_kpis()

        assert isinstance(result, AdvancedKPIsResponse)
        assert result.cash_flow == Decimal("3500.00")
        assert result.avg_ticket == Decimal("87.50")
        assert result.total_transactions == 40
        assert result.max_expense is not None
        assert result.max_expense.amount == Decimal("500.00")
        assert result.max_expense.store_name == "Store Alpha"
        assert result.max_expense.occurred_at == "2024-06-15"

    def test_returns_kpi_response_with_max_expense_none(self):
        """get_advanced_kpis sets max_expense to None when repo returns no expense."""
        controller = _make_controller()
        repo_result = {
            "kpi": {
                "cash_flow": Decimal("100.00"),
                "avg_ticket": Decimal("20.00"),
                "total_transactions": 5,
            },
            "max_expense": None,
        }
        with patch.object(controller._repo, "get_advanced_kpis", return_value=repo_result):
            result = controller.get_advanced_kpis()

        assert result.max_expense is None

    def test_handles_occurred_at_as_datetime_date(self):
        """get_advanced_kpis formats occurred_at when it is a datetime.date object."""
        controller = _make_controller()
        repo_result = {
            "kpi": {
                "cash_flow": Decimal("0.00"),
                "avg_ticket": Decimal("0.00"),
                "total_transactions": 0,
            },
            "max_expense": {
                "amount": Decimal("250.00"),
                "store_name": "Store Beta",
                "type_description": "DOC",
                "occurred_at": date(2024, 9, 30),
            },
        }
        with patch.object(controller._repo, "get_advanced_kpis", return_value=repo_result):
            result = controller.get_advanced_kpis()

        assert result.max_expense is not None
        assert result.max_expense.occurred_at == "2024-09-30"

    def test_handles_empty_kpi_row_defaults_to_zero(self):
        """get_advanced_kpis defaults numeric KPI fields to 0 when kpi is None."""
        controller = _make_controller()
        repo_result = {
            "kpi": None,
            "max_expense": None,
        }
        with patch.object(controller._repo, "get_advanced_kpis", return_value=repo_result):
            result = controller.get_advanced_kpis()

        assert result.cash_flow == Decimal("0")
        assert result.avg_ticket == Decimal("0")
        assert result.total_transactions == 0


class TestGetTransactionsByHour:
    """Tests for DashboardController.get_transactions_by_hour."""

    def test_returns_24_labels_from_00_to_23(self):
        """get_transactions_by_hour always returns labels for all 24 hours."""
        controller = _make_controller()
        with patch.object(controller._repo, "get_transactions_by_hour", return_value=[]):
            result = controller.get_transactions_by_hour()

        assert isinstance(result, TransactionsByHourResponse)
        assert len(result.labels) == 24
        assert result.labels[0] == "00:00"
        assert result.labels[23] == "23:00"

    def test_fills_missing_hours_with_zero(self):
        """get_transactions_by_hour fills hours absent from the repo with 0."""
        controller = _make_controller()
        repo_rows = [
            {"hour": 9, "transaction_count": 15},
            {"hour": 14, "transaction_count": 30},
        ]
        with patch.object(controller._repo, "get_transactions_by_hour", return_value=repo_rows):
            result = controller.get_transactions_by_hour()

        assert len(result.data) == 24
        assert result.data[9] == 15
        assert result.data[14] == 30
        assert result.data[0] == 0
        assert result.data[23] == 0

    def test_returns_correct_counts_for_present_hours(self):
        """get_transactions_by_hour maps repo counts to the correct hour index."""
        controller = _make_controller()
        repo_rows = [{"hour": h, "transaction_count": h * 2} for h in range(24)]
        with patch.object(controller._repo, "get_transactions_by_hour", return_value=repo_rows):
            result = controller.get_transactions_by_hour()

        for h in range(24):
            assert result.data[h] == h * 2
            assert result.labels[h] == f"{h:02d}:00"


class TestGetTransactionsDetail:
    """Tests for DashboardController.get_transactions_detail."""

    def _build_repo_result(self, rows: list) -> dict:
        """Wraps rows in the repository result structure."""
        return {"count": len(rows), "rows": rows}

    def _sample_row(self, **overrides) -> dict:
        """Returns a complete transaction row dict with sensible defaults."""
        row = {
            "id": "txn-001",
            "occurred_at": "2024-05-10",
            "occurred_time": "14:30:00",
            "type_description": "Credito",
            "nature": "Entrada",
            "sign": "+",
            "amount": Decimal("99.90"),
            "card": "1234****5678",
            "store_name": "My Store",
            "owner_name": "Bob",
            "cpf": "123.456.789-00",
        }
        row.update(overrides)
        return row

    def test_returns_count_and_items(self):
        """get_transactions_detail returns TransactionDetailResponse with count and results."""
        controller = _make_controller()
        rows = [self._sample_row()]
        with patch.object(
            controller._repo,
            "get_transactions_detail",
            return_value=self._build_repo_result(rows),
        ):
            result = controller.get_transactions_detail()

        assert isinstance(result, TransactionDetailResponse)
        assert result.count == 1
        assert len(result.results) == 1
        item = result.results[0]
        assert item.id == "txn-001"
        assert item.occurred_at == "2024-05-10"
        assert item.occurred_time == "14:30:00"
        assert item.amount == Decimal("99.90")

    def test_handles_datetime_date_and_time_objects(self):
        """get_transactions_detail formats date/time objects via strftime."""
        controller = _make_controller()
        rows = [
            self._sample_row(
                occurred_at=date(2024, 1, 15),
                occurred_time=time(8, 45, 0),
            )
        ]
        with patch.object(
            controller._repo,
            "get_transactions_detail",
            return_value=self._build_repo_result(rows),
        ):
            result = controller.get_transactions_detail()

        item = result.results[0]
        assert item.occurred_at == "2024-01-15"
        assert item.occurred_time == "08:45:00"

    def test_handles_string_dates_and_times(self):
        """get_transactions_detail keeps string dates and times as-is."""
        controller = _make_controller()
        rows = [self._sample_row(occurred_at="2024-08-20", occurred_time="22:00:00")]
        with patch.object(
            controller._repo,
            "get_transactions_detail",
            return_value=self._build_repo_result(rows),
        ):
            result = controller.get_transactions_detail()

        item = result.results[0]
        assert item.occurred_at == "2024-08-20"
        assert item.occurred_time == "22:00:00"

    def test_empty_rows_returns_zero_count_and_empty_results(self):
        """get_transactions_detail returns count=0 and empty results for no rows."""
        controller = _make_controller()
        with patch.object(
            controller._repo,
            "get_transactions_detail",
            return_value={"count": 0, "rows": []},
        ):
            result = controller.get_transactions_detail()

        assert result.count == 0
        assert result.results == []


class TestGetAvailableFilters:
    """Tests for DashboardController.get_available_filters."""

    def test_returns_available_filters_response(self):
        """get_available_filters assembles AvailableFiltersResponse from repo data."""
        controller = _make_controller()
        repo_result = {
            "stores": [
                {"id": "store-1", "name": "Alpha Store", "owner_name": "Carol"},
                {"id": "store-2", "name": "Beta Store", "owner_name": "Dave"},
            ],
            "owners": ["Carol", "Dave"],
            "date_range": {"min_date": "2024-01-01", "max_date": "2024-12-31"},
        }
        with patch.object(controller._repo, "get_available_filters", return_value=repo_result):
            result = controller.get_available_filters()

        assert isinstance(result, AvailableFiltersResponse)
        assert len(result.stores) == 2
        assert result.stores[0].id == "store-1"
        assert result.stores[0].name == "Alpha Store"
        assert result.stores[0].owner_name == "Carol"
        assert result.owners == ["Carol", "Dave"]
        assert result.date_range.min_date == "2024-01-01"
        assert result.date_range.max_date == "2024-12-31"

    def test_returns_none_date_range_when_no_data(self):
        """get_available_filters handles None min/max dates in the date_range."""
        controller = _make_controller()
        repo_result = {
            "stores": [],
            "owners": [],
            "date_range": {"min_date": None, "max_date": None},
        }
        with patch.object(controller._repo, "get_available_filters", return_value=repo_result):
            result = controller.get_available_filters()

        assert result.stores == []
        assert result.owners == []
        assert result.date_range.min_date is None
        assert result.date_range.max_date is None
