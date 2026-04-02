"""CNAB file upload history model."""

from sqlalchemy import Column, Integer, String, Text

from cnab_shared import BaseModel


class UploadHistory(BaseModel):
    """Tracks each CNAB file upload and its processing state."""

    __tablename__ = "cnab_upload_history"

    user_id = Column(Integer, nullable=True)  # Cross-reference to user-service (no FK)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    total_transactions = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<UploadHistory {self.id}: {self.original_filename} [{self.status}]>"
