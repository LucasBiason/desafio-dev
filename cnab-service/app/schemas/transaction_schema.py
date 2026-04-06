"""Pydantic schemas for transaction and transaction type responses."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionTypeResponse(BaseModel):
    """Serializes a CNAB transaction type."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: int
    description: str
    nature: str
    sign: str


class TransactionResponse(BaseModel):
    """Serializes a single transaction with its type and store."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    transaction_type: TransactionTypeResponse
    amount: Decimal
    card: str
    occurred_at: str
    occurred_time: str
    store: dict | None = None


class TransactionListResponse(BaseModel):
    """Paginated list of transactions."""

    count: int
    results: list[TransactionResponse]
