import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load .env so settings get the API key before main.py is imported
load_dotenv()

from backend.main import app

@pytest.fixture
def client():
    """Provides a TestClient for FastAPI endpoints."""
    return TestClient(app)
