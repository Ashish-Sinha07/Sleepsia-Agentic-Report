def test_get_kpis(client, sample_date_range):
    """Test getting KPIs endpoint."""
    response = client.get(
        "/api/kpis",
        params=sample_date_range,
    )
    assert response.status_code == 200
    data = response.json()
    assert "period" in data
    assert "kpis" in data
    assert data["period"]["start_date"] == sample_date_range["start_date"]
    assert data["period"]["end_date"] == sample_date_range["end_date"]


def test_get_kpis_by_date(client, sample_date_range):
    """Test getting daily KPIs endpoint."""
    response = client.get(
        "/api/kpis/by-date",
        params=sample_date_range,
    )
    assert response.status_code == 200
    data = response.json()
    assert "period" in data
    assert "daily_data" in data
    assert "total_days" in data
    assert isinstance(data["daily_data"], list)


def test_get_kpis_invalid_date_range(client):
    """Test invalid date range."""
    response = client.get(
        "/api/kpis",
        params={
            "start_date": "2026-08-21",
            "end_date": "2026-08-01",  # end before start
        },
    )
    assert response.status_code == 400
