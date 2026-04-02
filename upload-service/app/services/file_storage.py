"""File storage service for CNAB uploads."""

import os
import uuid
from pathlib import Path


class FileStorage:
    UPLOAD_DIR: Path = Path(os.environ.get("UPLOAD_DIR", "/app/uploads"))

    def save(self, filename: str, content: bytes) -> str:
        """Saves file content to disk with a UUID prefix. Returns the stored file path."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        unique_name = f"{uuid.uuid4()}_{filename}"
        file_path = self.UPLOAD_DIR / unique_name
        file_path.write_bytes(content)
        return str(file_path)

    def read(self, file_path: str) -> bytes:
        return Path(file_path).read_bytes()

    def delete(self, file_path: str) -> None:
        """Removes the file at the given path if it exists."""
        path = Path(file_path)
        if path.exists():
            path.unlink()
