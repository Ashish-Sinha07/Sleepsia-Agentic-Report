def test_get_warehouses(client):
    """Test getting warehouses."""
    response = client.get("/api/warehouses")
    assert response.status_code == 200
    data = response.json()
    assert "warehouses" in data
    assert "total" in data
    assert isinstance(data["warehouses"], list)


def test_get_warehouses_by_region(client):
    """Test getting warehouses by region."""
    response = client.get(
        "/api/warehouses",
        params={"region": "Delhi NCR"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "warehouses" in data
