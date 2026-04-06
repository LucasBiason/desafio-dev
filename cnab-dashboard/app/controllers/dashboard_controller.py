"""Controller for dashboard statistics aggregation."""

from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository, _TYPE_COLORS
from app.schemas.dashboard_schema import (
    AdvancedKPIsResponse,
    AvailableFiltersResponse,
    BalanceByStoreResponse,
    DashboardSummaryResponse,
    MaxExpenseDetail,
    TransactionDetailItem,
    TransactionDetailResponse,
    TransactionsByHourResponse,
    TransactionsByTypeResponse,
    UploadsTimelineResponse,
)


class DashboardController:
    """Orchestrates dashboard data retrieval and response assembly."""

    def __init__(self, db: Session) -> None:
        self._repo = DashboardRepository(db=db)

    def get_summary(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> DashboardSummaryResponse:
        """Returns overall counts and financial totals."""
        row = self._repo.get_summary(
            store_id=store_id,
            owner_name=owner_name,
            date_from=date_from,
            date_to=date_to,
        )
        return DashboardSummaryResponse(
            total_stores=int(row["total_stores"]),
            total_transactions=int(row["total_transactions"]),
            total_income=Decimal(str(row["total_income"])),
            total_expense=Decimal(str(row["total_expense"])),
            overall_balance=Decimal(str(row["overall_balance"])),
        )

    def get_balance_by_store(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> BalanceByStoreResponse:
        """Returns store names and balances for bar chart."""
        rows = self._repo.get_balance_by_store(
            store_id=store_id,
            owner_name=owner_name,
            date_from=date_from,
            date_to=date_to,
        )
        labels = [row["store_name"] for row in rows]
        data = [Decimal(str(row["balance"])) for row in rows]
        return BalanceByStoreResponse(labels=labels, data=data)

    def get_transactions_by_type(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> TransactionsByTypeResponse:
        """Returns transaction counts per type with colors for pie chart."""
        rows = self._repo.get_transactions_by_type(
            store_id=store_id,
            owner_name=owner_name,
            date_from=date_from,
            date_to=date_to,
        )
        labels = [row["type_description"] for row in rows]
        data = [int(row["transaction_count"]) for row in rows]
        colors = [_TYPE_COLORS[i % len(_TYPE_COLORS)] for i in range(len(rows))]
        return TransactionsByTypeResponse(labels=labels, data=data, colors=colors)

    def get_transactions_timeline(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> UploadsTimelineResponse:
        """Returns transaction counts grouped by date for line chart."""
        rows = self._repo.get_transactions_timeline(
            store_id=store_id,
            owner_name=owner_name,
            date_from=date_from,
            date_to=date_to,
        )
        labels = []
        for row in rows:
            date_val = row["transaction_date"]
            # Format date as DD/MM/YYYY regardless of type returned by the DB
            if hasattr(date_val, "strftime"):
                labels.append(date_val.strftime("%d/%m/%Y"))
            else:
                # Handle string dates in YYYY-MM-DD format
                parts = str(date_val).split("-")
                if len(parts) == 3:
                    labels.append(f"{parts[2]}/{parts[1]}/{parts[0]}")
                else:
                    labels.append(str(date_val))
        data = [int(row["transaction_count"]) for row in rows]
        return UploadsTimelineResponse(labels=labels, data=data)

    def get_advanced_kpis(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> AdvancedKPIsResponse:
        """Returns advanced KPI metrics: cash flow, avg ticket, total transactions and max expense."""
        result = self._repo.get_advanced_kpis(
            store_id=store_id,
            owner_name=owner_name,
            date_from=date_from,
            date_to=date_to,
        )
        kpi = result["kpi"] or {}
        expense_row = result["max_expense"]

        max_expense: MaxExpenseDetail | None = None
        if expense_row:
            raw_date = expense_row.get("occurred_at")
            if raw_date is not None:
                if hasattr(raw_date, "strftime"):
                    occurred_at_str = raw_date.strftime("%Y-%m-%d")
                else:
                    occurred_at_str = str(raw_date)[:10]
            else:
                occurred_at_str = None
            max_expense = MaxExpenseDetail(
                amount=Decimal(str(expense_row["amount"])),
                store_name=expense_row.get("store_name"),
                type_description=expense_row.get("type_description"),
                occurred_at=occurred_at_str,
            )

        return AdvancedKPIsResponse(
            cash_flow=Decimal(str(kpi.get("cash_flow", "0"))),
            avg_ticket=Decimal(str(kpi.get("avg_ticket", "0"))),
            total_transactions=int(kpi.get("total_transactions", 0)),
            max_expense=max_expense,
        )

    def get_transactions_by_hour(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> TransactionsByHourResponse:
        """Returns transaction counts for each of the 24 hours, filling missing hours with 0."""
        rows = self._repo.get_transactions_by_hour(
            store_id=store_id,
            owner_name=owner_name,
            date_from=date_from,
            date_to=date_to,
        )
        hour_map = {int(row["hour"]): int(row["transaction_count"]) for row in rows}
        labels = [f"{h:02d}:00" for h in range(24)]
        data = [hour_map.get(h, 0) for h in range(24)]
        return TransactionsByHourResponse(labels=labels, data=data)

    def get_transactions_detail(
        self,
        store_id: str | None = None,
        owner_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        nature: str | None = None,
        ordering: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> TransactionDetailResponse:
        """Returns a paginated list of transaction detail rows."""
        result = self._repo.get_transactions_detail(
            store_id=store_id,
            owner_name=owner_name,
            date_from=date_from,
            date_to=date_to,
            nature=nature,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )
        items: list[TransactionDetailItem] = []
        for row in result["rows"]:
            raw_date = row.get("occurred_at")
            if raw_date is not None:
                if hasattr(raw_date, "strftime"):
                    occurred_at_str = raw_date.strftime("%Y-%m-%d")
                else:
                    occurred_at_str = str(raw_date)[:10]
            else:
                occurred_at_str = ""

            raw_time = row.get("occurred_time")
            if raw_time is not None:
                if hasattr(raw_time, "strftime"):
                    occurred_time_str = raw_time.strftime("%H:%M:%S")
                else:
                    occurred_time_str = str(raw_time)[:8]
            else:
                occurred_time_str = ""

            items.append(
                TransactionDetailItem(
                    id=str(row["id"]),
                    occurred_at=occurred_at_str,
                    occurred_time=occurred_time_str,
                    type_description=str(row["type_description"]),
                    nature=str(row["nature"]),
                    sign=str(row["sign"]),
                    amount=Decimal(str(row["amount"])),
                    card=row.get("card"),
                    store_name=str(row["store_name"]),
                    owner_name=str(row["owner_name"]),
                    cpf=row.get("cpf"),
                )
            )
        return TransactionDetailResponse(count=result["count"], results=items)

    def get_available_filters(self) -> AvailableFiltersResponse:
        """Returns stores, owner names and date range for filter dropdowns."""
        result: dict[str, Any] = self._repo.get_available_filters()
        stores = [
            {"id": row["id"], "name": row["name"], "owner_name": row["owner_name"]}
            for row in result["stores"]
        ]
        return AvailableFiltersResponse(
            stores=stores,
            owners=result["owners"],
            date_range=result["date_range"],
        )
