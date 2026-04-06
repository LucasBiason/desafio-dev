"""Generic base repository with CRUD operations and raw SQL support."""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic CRUD repository to be inherited by domain repositories."""

    def __init__(self, db: Session, model_class: type[T]) -> None:
        self.db = db
        self.model_class = model_class

    def create(self, instance: T) -> T:
        """Persists a new model instance and returns it with database-generated fields."""
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get_by_id(self, id: UUID) -> T | None:
        """Returns a record by UUID, or None if not found."""
        return self.db.query(self.model_class).filter(self.model_class.id == id).first()

    def list_all(
        self,
        filters: dict | None = None,
        order_by: str | None = None,
    ) -> list[T]:
        """
        Returns all records matching the given filters.

        Args:
            filters: Optional dict of {field: value} equality filters.
            order_by: Optional column name for sorting.

        Returns:
            List of matching model instances.
        """
        query = self.db.query(self.model_class)

        if filters:
            for field, value in filters.items():
                column = getattr(self.model_class, field, None)
                if column is not None:
                    query = query.filter(column == value)

        if order_by:
            order_column = getattr(self.model_class, order_by, None)
            if order_column is not None:
                query = query.order_by(order_column)

        return query.all()

    def update(self, instance: T) -> T:
        """Commits changes to an existing instance and returns the refreshed record."""
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def soft_delete(self, instance: T) -> T:
        """Calls soft_delete() on the instance and persists the change."""
        instance.soft_delete()
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def hard_delete(self, instance: T) -> None:
        """Permanently removes the record from the database."""
        self.db.delete(instance)
        self.db.commit()

    def query_one(
        self,
        sql: str,
        params: dict | None = None,
    ) -> dict[str, Any] | None:
        """
        Executes a parameterized SQL query and returns a single row.

        Args:
            sql: SQL string with named parameters in :name format.
            params: Dictionary of parameter values.

        Returns:
            First row as a dict, or None if no results.
        """
        result = self.db.execute(text(sql), params or {}).fetchone()
        if result is None:
            return None
        return dict(result._mapping)

    def query_list(
        self,
        sql: str,
        params: dict | None = None,
    ) -> list[dict[str, Any]]:
        """
        Executes a parameterized SQL query and returns all rows.

        Args:
            sql: SQL string with named parameters in :name format.
            params: Dictionary of parameter values.

        Returns:
            List of rows, each as a dict.
        """
        results = self.db.execute(text(sql), params or {}).fetchall()
        return [dict(row._mapping) for row in results]
