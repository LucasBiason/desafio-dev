"""Tests for process_pending_uploads task."""

import uuid
from unittest.mock import MagicMock, patch

from app.tasks.process_upload import process_pending_uploads


def _make_pending_upload():
    """Creates a mock pending upload."""
    upload = MagicMock()
    upload.id = uuid.uuid4()
    upload.status = "pending"
    return upload


class TestProcessPendingUploads:
    """Tests for the process_pending_uploads background task."""

    def test_process_pending_uploads_with_data(self):
        """Calls controller.process_upload for each pending record found."""
        db = MagicMock()
        pending = [_make_pending_upload(), _make_pending_upload()]

        with (
            patch("app.tasks.process_upload.UploadHistoryRepository") as MockRepo,
            patch("app.tasks.process_upload.UploadController") as MockController,
        ):
            MockRepo.return_value.get_pending.return_value = pending
            process_pending_uploads(db)

        assert MockController.return_value.process_upload.call_count == 2

    def test_process_pending_uploads_empty(self):
        """Returns without calling controller when no pending uploads exist."""
        db = MagicMock()

        with (
            patch("app.tasks.process_upload.UploadHistoryRepository") as MockRepo,
            patch("app.tasks.process_upload.UploadController") as MockController,
        ):
            MockRepo.return_value.get_pending.return_value = []
            process_pending_uploads(db)

        MockController.return_value.process_upload.assert_not_called()
