"""Tests for UploadController."""

import uuid
import pytest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.controllers.upload_controller import UploadController
from app.models.upload_history import UploadHistory


def _make_mock_upload(status="pending"):
    """Creates a mock UploadHistory object."""
    upload = MagicMock(spec=UploadHistory)
    upload.id = uuid.uuid4()
    upload.original_filename = "test.txt"
    upload.file_path = "/uploads/test.txt"
    upload.status = status
    upload.total_transactions = 0
    upload.error_message = None
    return upload


class TestUploadController:
    """Tests for UploadController business logic methods."""

    def _make_controller(self, db=None):
        """Creates an UploadController with mock db and user_data."""
        if db is None:
            db = MagicMock()
        user_data = {"id": 1, "email": "user@test.com"}
        return UploadController(db=db, user_data=user_data)

    def test_create_upload_valid(self):
        """create_upload returns a pending UploadHistory record on valid input."""
        controller = self._make_controller()
        mock_upload = _make_mock_upload()

        with (
            patch("app.controllers.upload_controller.UploadValidator.validate_file", return_value={"valid": True, "error": None}),
            patch("app.controllers.upload_controller.FileStorage") as MockStorage,
            patch.object(controller.repository, "create", return_value=mock_upload),
        ):
            MockStorage.return_value.save.return_value = "/uploads/uuid_test.txt"
            result = controller.create_upload("test.txt", b"content")

        assert result is mock_upload

    def test_create_upload_invalid_extension(self):
        """create_upload raises HTTPException 422 for invalid file extension."""
        controller = self._make_controller()

        with patch(
            "app.controllers.upload_controller.UploadValidator.validate_file",
            return_value={"valid": False, "error": "Invalid extension '.exe'."},
        ):
            with pytest.raises(HTTPException) as exc_info:
                controller.create_upload("malware.exe", b"content")

        assert exc_info.value.status_code == 422

    def test_create_upload_empty_file(self):
        """create_upload raises HTTPException 422 for empty file content."""
        controller = self._make_controller()

        with patch(
            "app.controllers.upload_controller.UploadValidator.validate_file",
            return_value={"valid": False, "error": "File is empty."},
        ):
            with pytest.raises(HTTPException) as exc_info:
                controller.create_upload("empty.txt", b"")

        assert exc_info.value.status_code == 422

    def test_list_uploads(self):
        """list_uploads delegates to repository with correct user_id."""
        controller = self._make_controller()
        mock_uploads = [_make_mock_upload()]

        with patch.object(controller.repository, "list_filtered", return_value=(mock_uploads, 1)) as mock_list:
            records, total = controller.list_uploads(page=1, page_size=10)

        mock_list.assert_called_once()
        assert total == 1
        assert len(records) == 1

    def test_get_upload(self):
        """get_upload delegates to repository.get_by_id with a UUID."""
        controller = self._make_controller()
        upload_id = str(uuid.uuid4())
        mock_upload = _make_mock_upload()

        with patch.object(controller.repository, "get_by_id", return_value=mock_upload) as mock_get:
            result = controller.get_upload(upload_id)

        mock_get.assert_called_once()
        assert result is mock_upload

    def test_process_upload_success(self):
        """process_upload sets status to completed after successful pipeline."""
        controller = self._make_controller()
        mock_upload = _make_mock_upload(status="pending")
        transactions = [{"type_code": 1}]

        with (
            patch.object(controller.repository, "get_by_id", return_value=mock_upload),
            patch.object(controller.repository, "update_status") as mock_update,
            patch("app.controllers.upload_controller.FileStorage") as MockStorage,
            patch("app.controllers.upload_controller.CnabParser") as MockParser,
            patch("app.controllers.upload_controller.CnabServiceClient") as MockClient,
        ):
            MockStorage.return_value.read.return_value = b"data"
            MockParser.return_value.parse.return_value = transactions
            MockClient.return_value.create_transactions.return_value = {}

            controller.process_upload(str(mock_upload.id))

        calls = [call[0] for call in mock_update.call_args_list]
        statuses = [c[1] for c in calls]
        assert "processing" in statuses
        assert "completed" in statuses

    def test_process_upload_failure(self):
        """process_upload sets status to failed when an exception is raised."""
        controller = self._make_controller()
        mock_upload = _make_mock_upload(status="pending")

        with (
            patch.object(controller.repository, "get_by_id", return_value=mock_upload),
            patch.object(controller.repository, "update_status") as mock_update,
            patch("app.controllers.upload_controller.FileStorage") as MockStorage,
        ):
            MockStorage.return_value.read.side_effect = OSError("disk error")
            controller.process_upload(str(mock_upload.id))

        calls = [call[0] for call in mock_update.call_args_list]
        statuses = [c[1] for c in calls]
        assert "failed" in statuses

    def test_process_upload_not_found(self):
        """process_upload returns early without error when upload_id not found."""
        controller = self._make_controller()

        with patch.object(controller.repository, "get_by_id", return_value=None):
            controller.process_upload(str(uuid.uuid4()))
