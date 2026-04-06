"""Store model extracted from CNAB files."""

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.orm import relationship

from cnab_shared import BaseModel


class Store(BaseModel):
    """Store identified from CNAB transaction data."""

    __tablename__ = "cnab_store"

    name = Column(String(50), nullable=False)
    owner_name = Column(String(50), nullable=False)
    owner_cpf = Column(String(11), nullable=False)

    transactions = relationship("Transaction", back_populates="store")

    __table_args__ = (UniqueConstraint("name", "owner_cpf", name="uq_store_name_cpf"),)

    def __repr__(self) -> str:
        return f"<Store {self.name} ({self.owner_name})>"
