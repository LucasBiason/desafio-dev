"""Generic paginated response schema for listing endpoints."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Wraps a list of results with pagination metadata."""

    model_config = ConfigDict(from_attributes=True)

    count: int = Field(description="Total number of available records.")
    next: str | None = Field(default=None, description="URL of the next page.")
    previous: str | None = Field(default=None, description="URL of the previous page.")
    results: list[T] = Field(description="List of items on the current page.")
