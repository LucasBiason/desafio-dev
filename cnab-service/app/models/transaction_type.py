"""Transaction type reference model (9 fixed CNAB types)."""

from sqlalchemy import Column, SmallInteger, String, UniqueConstraint

from cnab_shared import BaseModel


class TransactionType(BaseModel):
    """CNAB transaction type (seed table with 9 fixed records)."""

    __tablename__ = "cnab_transaction_type"

    code = Column(SmallInteger, unique=True, nullable=False)
    description = Column(String(50), nullable=False)
    nature = Column(String(10), nullable=False)
    sign = Column(String(1), nullable=False)

    __table_args__ = (
        UniqueConstraint("code", name="uq_transaction_type_code"),
    )

    def __repr__(self) -> str:
        return f"<TransactionType {self.code}: {self.description}>"
