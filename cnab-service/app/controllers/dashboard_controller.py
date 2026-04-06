"""Controller for dashboard statistics aggregation."""

from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository, _TYPE_COLORS
from app.schemas.dashboard_schema import (
    AvailableFiltersResponse,
    BalanceByStoreResponse,
    DashboardSummaryResponse,
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
