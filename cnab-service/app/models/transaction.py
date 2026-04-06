"""CNAB transaction model."""

from sqlalchemy import Column, Date, ForeignKey, Index, Numeric, String, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from cnab_shared import BaseModel


class Transaction(BaseModel):
    """Single financial transaction parsed from a CNAB file."""

    __tablename__ = "cnab_transaction"

    transaction_type_id = Column(UUID(as_uuid=True), ForeignKey("cnab_transaction_type.id"), nullable=False)
    store_id = Column(UUID(as_uuid=True), ForeignKey("cnab_store.id"), nullable=False)
    upload_id = Column(UUID(as_uuid=True), nullable=False)  # Cross-reference to upload-service (no FK)
    amount = Column(Numeric(10, 2), nullable=False)
    card = Column(String(20), nullable=False)
    occurred_at = Column(Date, nullable=False)
    occurred_time = Column(Time, nullable=False)
    content_hash = Column(String(64), nullable=True, unique=True)

    transaction_type = relationship("TransactionType")
    store = relationship("Store", back_populates="transactions")

    __table_args__ = (
        Index("idx_transaction_store_date", "store_id", "occurred_at"),
        Index("idx_transaction_upload", "upload_id"),
        UniqueConstraint("content_hash", name="uq_transaction_content_hash"),
    )

    def __repr__(self) -> str:
        return f"<Transaction {self.id}: {self.amount} ({self.occurred_at})>"
