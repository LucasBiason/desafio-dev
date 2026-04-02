"""Pydantic schemas for upload request/response serialization."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    """Serializes a single upload history record for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    original_filename: str
    file_path: str | None
    status: str
    total_transactions: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class UploadListResponse(BaseModel):
    """Paginated list of upload records."""

    count: int
    results: list[UploadResponse]
