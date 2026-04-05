"""Pydantic schemas for dashboard statistics responses."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


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
