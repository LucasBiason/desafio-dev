"""Tests for UploadValidator."""

import pytest
from unittest.mock import patch

from app.validators.upload_validator import UploadValidator


class TestUploadValidator:
    """Tests for UploadValidator.validate_file."""

    def test_valid_txt_file(self):
        """Valid .txt file passes validation."""
        result = UploadValidator.validate_file("transactions.txt", b"some content")
        assert result["valid"] is True
        assert result["error"] is None

    def test_valid_cnab_file(self):
        """Valid .cnab file passes validation."""
        result = UploadValidator.validate_file("transactions.cnab", b"some content")
        assert result["valid"] is True
        assert result["error"] is None

    def test_invalid_extension(self):
        """File with disallowed extension fails validation."""
        result = UploadValidator.validate_file("malware.exe", b"some content")
        assert result["valid"] is False
        assert "Invalid extension" in result["error"]

    def test_empty_file(self):
        """Empty file content fails validation."""
        result = UploadValidator.validate_file("transactions.txt", b"")
        assert result["valid"] is False
        assert "empty" in result["error"].lower()

    def test_empty_filename(self):
        """Empty filename fails validation."""
        result = UploadValidator.validate_file("", b"some content")
        assert result["valid"] is False
        assert "required" in result["error"].lower()

    def test_file_too_large(self):
        """File exceeding MAX_FILE_SIZE limit fails validation."""
        with patch("app.validators.upload_validator.MAX_FILE_SIZE", 10):
            result = UploadValidator.validate_file("transactions.txt", b"x" * 11)
        assert result["valid"] is False
        assert "exceeds" in result["error"].lower()
