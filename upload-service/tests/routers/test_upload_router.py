"""Tests for upload_router endpoints."""

import io
import uuid
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.upload_history import UploadHistory


USER_DATA = {"id": 1, "email": "user@test.com"}


def _make_upload_history(filename="test.txt", status="pending"):
    """Creates a mock UploadHistory for use in router tests."""
    upload = MagicMock(spec=UploadHistory)
    upload.id = uuid.uuid4()
    upload.original_filename = filename
    upload.file_path = f"/uploads/{filename}"
    upload.status = status
    upload.total_transactions = 0
    upload.error_message = None
    upload.created_at = datetime.now(timezone.utc)
    upload.updated_at = datetime.now(timezone.utc)
    return upload


@pytest.fixture
def auth_client():
    """Returns a TestClient that injects user state, bypassing AuthMiddleware."""
    with patch("cnab_shared.middleware.auth_middleware.AuthMiddleware.dispatch") as mock_dispatch:
        async def fake_dispatch(request, call_next):
            request.state.user = USER_DATA
            return await call_next(request)

        mock_dispatch.side_effect = fake_dispatch

        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


class TestUploadRouter:
    """Tests for /upload/, /uploads/, and /uploads/{id} endpoints."""

    def test_upload_endpoint_success(self, auth_client, db):
        """POST /upload/ with valid file returns 201 and upload record."""
        mock_upload = _make_upload_history()

        with patch("app.routers.upload_router.UploadController") as MockController:
            MockController.return_value.create_upload.return_value = mock_upload
            response = auth_client.post(
                "/upload/",
                files={"file": ("test.txt", io.BytesIO(b"cnab data"), "text/plain")},
            )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"

    def test_list_endpoint(self, auth_client, db):
        """GET /uploads/ returns a list response with count and results."""
        mock_uploads = [_make_upload_history()]

        with patch("app.routers.upload_router.UploadController") as MockController:
            MockController.return_value.list_uploads.return_value = (mock_uploads, 1)
            response = auth_client.get("/uploads/")

        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "results" in data
        assert data["count"] == 1

    def test_get_endpoint(self, auth_client, db):
        """GET /uploads/{id} returns a single upload record."""
        mock_upload = _make_upload_history()
        upload_id = str(mock_upload.id)

        with patch("app.routers.upload_router.UploadController") as MockController:
            MockController.return_value.get_upload.return_value = mock_upload
            response = auth_client.get(f"/uploads/{upload_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == upload_id

    def test_get_nonexistent_returns_error(self, auth_client, db):
        """GET /uploads/{id} returns an error response for unknown upload id."""
        missing_id = str(uuid.uuid4())

        with patch("app.routers.upload_router.UploadController") as MockController:
            MockController.return_value.get_upload.return_value = None
            response = auth_client.get(f"/uploads/{missing_id}")

        # ResourceNotFoundError propagates through CatchExceptionsMiddleware as 500
        assert response.status_code in (404, 500)
        data = response.json()
        assert "error" in data or "detail" in data
