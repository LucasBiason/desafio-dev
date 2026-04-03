"""Pydantic schemas for internal (service-to-service) transaction ingestion."""

from pydantic import BaseModel


class TransactionInput(BaseModel):
    """Single transaction record sent by upload-service."""

    type_code: int
    date: str
    amount: str
    cpf: str
    card: str
    time: str
    store_owner: str
    store_name: str


class BulkTransactionRequest(BaseModel):
    """Payload for bulk transaction ingestion from upload-service."""

    upload_id: str
    transactions: list[TransactionInput]


class BulkTransactionResponse(BaseModel):
    """Summary returned after bulk ingestion."""

    upload_id: str
    total_inserted: int
    stores_created: int
