"""Pydantic schemas for store responses."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class StoreResponse(BaseModel):
    """Serializes a store with computed balance fields."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    owner_name: str
    owner_cpf: str
    balance: Decimal = Decimal("0.00")
    total_income: Decimal = Decimal("0.00")
    total_expense: Decimal = Decimal("0.00")
    transaction_count: int = 0


class StoreListResponse(BaseModel):
    """Paginated list of stores with balances."""

    count: int
    results: list[StoreResponse]
