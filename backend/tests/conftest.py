import pytest
from fastapi.testclient import TestClient
from datetime import date
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.database import SessionLocal, get_db


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Database session for tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_date_range():
    """Sample date range for tests."""
    return {
        "start_date": "2026-08-01",
        "end_date": "2026-08-21",
    }
