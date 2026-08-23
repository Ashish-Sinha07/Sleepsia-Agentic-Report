def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_readiness_check(client):
    """Test readiness check endpoint."""
    response = client.get("/ready")
    assert response.status_code in [200, 503]  # Either healthy or service unavailable if DB is down
    data = response.json()
    assert "ready" in data or "error" in data
