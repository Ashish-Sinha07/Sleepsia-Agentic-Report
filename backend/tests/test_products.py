def test_get_product_performance(client, sample_date_range):
    """Test getting product performance."""
    response = client.get(
        "/api/product-performance",
        params=sample_date_range,
    )
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total" in data
    assert isinstance(data["products"], list)


def test_get_top_products(client, sample_date_range):
    """Test getting top products."""
    response = client.get(
        "/api/product-performance/top",
        params={
            **sample_date_range,
            "limit": 10,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total" in data
    assert data["limit"] == 10


def test_get_bottom_products(client, sample_date_range):
    """Test getting bottom products."""
    response = client.get(
        "/api/product-performance/bottom",
        params={
            **sample_date_range,
            "limit": 10,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total" in data
