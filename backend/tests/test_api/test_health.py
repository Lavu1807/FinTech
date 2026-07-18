from fastapi.testclient import TestClient
from backend.config.settings import settings

def test_health_check(client: TestClient):
    """Test the primary health check endpoint."""
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == settings.PROJECT_NAME
    assert "llm_available" in data
    assert "exports_dir_writable" in data

def test_liveness_probe(client: TestClient):
    """Test the liveness probe endpoint."""
    response = client.get(f"{settings.API_V1_STR}/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_readiness_probe(client: TestClient):
    """Test the readiness probe endpoint."""
    response = client.get(f"{settings.API_V1_STR}/health/ready")
    assert response.status_code in [200, 503] # Depending on if the directory is writable
