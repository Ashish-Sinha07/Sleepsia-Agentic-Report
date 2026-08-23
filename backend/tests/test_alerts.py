def test_get_alerts(client):
    """Test getting alerts."""
    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert "total" in data
    assert "critical_count" in data
    assert "high_count" in data
    assert isinstance(data["alerts"], list)


def test_get_alerts_by_priority(client):
    """Test getting alerts by priority."""
    response = client.get(
        "/api/alerts",
        params={"priority": "Critical"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
