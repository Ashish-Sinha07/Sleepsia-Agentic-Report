def test_get_inventory(client):
    """Test getting inventory."""
    response = client.get("/api/inventory")
    assert response.status_code == 200
    data = response.json()
    assert "inventory" in data
    assert "total" in data
    assert isinstance(data["inventory"], list)


def test_get_low_stock(client):
    """Test getting low stock items."""
    response = client.get("/api/inventory/low-stock")
    assert response.status_code == 200
    data = response.json()
    assert "inventory" in data


def test_get_stockouts(client):
    """Test getting stockout items."""
    response = client.get("/api/inventory/stockouts")
    assert response.status_code == 200
    data = response.json()
    assert "inventory" in data


def test_inventory_pagination(client):
    """Test inventory pagination."""
    response = client.get(
        "/api/inventory",
        params={"skip": 0, "limit": 50},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0
