"""Abstract base model with audit fields and soft delete support."""

import uuid

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from ..database.database import Base


class BaseModel(Base):
    """Abstract base with UUID primary key, soft delete, and timestamp fields."""

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    inactivated_at = Column(DateTime(timezone=True), nullable=True)

    def soft_delete(self) -> None:
        """Marks the record as inactive without removing it from the database."""
        self.is_active = False
        self.inactivated_at = func.now()

    def restore(self) -> None:
        """Reactivates a previously inactivated record."""
        self.is_active = True
        self.inactivated_at = None

    def to_dict(self) -> dict:
        """Returns all table column values as a dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
