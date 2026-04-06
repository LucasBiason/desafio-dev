"""Shared fixtures for cnab-dashboard tests."""

import os

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SERVICE_SECRET_KEY"] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Returns a TestClient for the Dashboard Service."""
    from app.main import app
    return TestClient(app)
