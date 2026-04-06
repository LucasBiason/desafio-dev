"""Pydantic schemas for dashboard statistics responses."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MaxExpenseDetail(BaseModel):
    """Details of the single largest expense transaction."""

    model_config = ConfigDict(from_attributes=True)

    amount: Decimal
    store_name: str | None
    type_description: str | None
    occurred_at: str | None


class AdvancedKPIsResponse(BaseModel):
    """Advanced KPI metrics for the analytics dashboard."""

    model_config = ConfigDict(from_attributes=True)

    cash_flow: Decimal
    avg_ticket: Decimal
    total_transactions: int
    max_expense: MaxExpenseDetail | None


class TransactionsByHourResponse(BaseModel):
    """Transaction count grouped by hour of day for heatmap/area chart."""

    model_config = ConfigDict(from_attributes=True)

    labels: list[str]
    data: list[int]


class TransactionDetailItem(BaseModel):
    """A single transaction row for the drill-down table."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    occurred_at: str
    occurred_time: str
    type_description: str
    nature: str
    sign: str
    amount: Decimal
    card: str | None
    store_name: str
    owner_name: str
    cpf: str | None


class TransactionDetailResponse(BaseModel):
    """Paginated transaction detail list."""

    model_config = ConfigDict(from_attributes=True)

    count: int
    results: list[TransactionDetailItem]


class DashboardSummaryResponse(BaseModel):
    """Overall summary statistics across all stores and transactions."""

    model_config = ConfigDict(from_attributes=True)

    total_stores: int
    total_transactions: int
    total_income: Decimal
    total_expense: Decimal
    overall_balance: Decimal


class BalanceByStoreResponse(BaseModel):
    """Per-store balance data for bar chart rendering."""

    model_config = ConfigDict(from_attributes=True)

    labels: list[str]
    data: list[Decimal]


class TransactionsByTypeResponse(BaseModel):
    """Transaction count per type for pie/donut chart rendering."""

    model_config = ConfigDict(from_attributes=True)

    labels: list[str]
    data: list[int]
    colors: list[str]


class UploadsTimelineResponse(BaseModel):
    """Transaction count grouped by date for line chart rendering."""

    model_config = ConfigDict(from_attributes=True)

    labels: list[str]
    data: list[int]


class StoreFilterItem(BaseModel):
    """A single store entry for the available-filters response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    owner_name: str


class DateRangeFilter(BaseModel):
    """Min and max transaction dates available in the dataset."""

    model_config = ConfigDict(from_attributes=True)

    min_date: str | None
    max_date: str | None


class AvailableFiltersResponse(BaseModel):
    """Available filter options for frontend dropdowns."""

    model_config = ConfigDict(from_attributes=True)

    stores: list[StoreFilterItem]
    owners: list[str]
    date_range: DateRangeFilter
