def test_get_platform_performance(client, sample_date_range):
    """Test getting platform performance."""
    response = client.get(
        "/api/platform-performance",
        params=sample_date_range,
    )
    assert response.status_code == 200
    data = response.json()
    assert "platforms" in data
    assert "total" in data
    assert isinstance(data["platforms"], list)


def test_get_platform_performance_by_platform(client, sample_date_range):
    """Test getting specific platform performance."""
    response = client.get(
        "/api/platform-performance",
        params={
            **sample_date_range,
            "platform_id": "AMZ",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "platforms" in data
