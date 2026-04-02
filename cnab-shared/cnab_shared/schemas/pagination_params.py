"""Pagination query parameters for listing endpoints."""

from pydantic import BaseModel, ConfigDict, Field


class PaginationParams(BaseModel):
    """Standard pagination parameters for listing routes."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    page: int = Field(default=1, ge=1, description="Page number, starting at 1.")
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (maximum 100).",
    )
