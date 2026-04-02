"""Validation rules for CNAB file uploads."""

import os

ALLOWED_EXTENSIONS = {".txt", ".cnab"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class UploadValidator:
    """Validates uploaded CNAB files before processing."""

    @staticmethod
    def validate_file(filename: str, content: bytes) -> dict:
        """Validates file extension, size, and content.

        Returns dict with 'valid' (bool) and 'error' (str or None).
        """
        if not filename:
            return {"valid": False, "error": "Filename is required."}

        ext = os.path.splitext(filename)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return {
                "valid": False,
                "error": f"Invalid extension '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            }

        if len(content) == 0:
            return {"valid": False, "error": "File is empty."}

        if len(content) > MAX_FILE_SIZE:
            return {"valid": False, "error": f"File exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit."}

        return {"valid": True, "error": None}
