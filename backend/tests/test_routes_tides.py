"""Tests for tides endpoints."""
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_common import DatasetTides


@pytest.mark.asyncio
async def test_get_tides_with_data(client: AsyncClient, db_session: AsyncSession, test_api_key):
    """Test getting tides data when data exists."""
    full_key, _ = test_api_key
    
    # Insert test data
    base_time = datetime(2024, 1, 1, 0, 0, 0)
    for hour in range(24):
        tide = DatasetTides(
            station_id="TEST001",
            time=base_time + timedelta(hours=hour),
            water_level_m=1.5 + 0.5 * hour
        )
        db_session.add(tide)
    await db_session.commit()
    
    # Query tides
    response = await client.get(
        "/v1/tides",
        params={
            "station_id": "TEST001",
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-02T00:00:00Z"
        },
        headers={"X-Api-Key": full_key}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "data" in data
    assert "meta" in data
    assert len(data["data"]) == 24
    assert data["meta"]["count"] == 24
    assert data["meta"]["query"]["station_id"] == "TEST001"


@pytest.mark.asyncio
async def test_get_tides_empty_result(client: AsyncClient, test_api_key):
    """Test getting tides data when no data exists."""
    full_key, _ = test_api_key
    
    response = await client.get(
        "/v1/tides",
        params={
            "station_id": "NONEXISTENT",
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-02T00:00:00Z"
        },
        headers={"X-Api-Key": full_key}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["data"] == []
    assert data["meta"]["count"] == 0


@pytest.mark.asyncio
async def test_get_tides_invalid_dates(client: AsyncClient, test_api_key):
    """Test tides endpoint with invalid date format."""
    full_key, _ = test_api_key
    
    response = await client.get(
        "/v1/tides",
        params={
            "station_id": "TEST",
            "start": "invalid-date",
            "end": "2024-01-02T00:00:00Z"
        },
        headers={"X-Api-Key": full_key}
    )
    
    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.asyncio
async def test_get_tides_end_before_start(client: AsyncClient, test_api_key):
    """Test tides endpoint with end date before start date."""
    full_key, _ = test_api_key
    
    response = await client.get(
        "/v1/tides",
        params={
            "station_id": "TEST",
            "start": "2024-01-02T00:00:00Z",
            "end": "2024-01-01T00:00:00Z"
        },
        headers={"X-Api-Key": full_key}
    )
    
    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.asyncio
async def test_get_tides_response_structure(client: AsyncClient, test_api_key):
    """Test that tides response has correct structure."""
    full_key, _ = test_api_key
    
    response = await client.get(
        "/v1/tides",
        params={
            "station_id": "TEST",
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-02T00:00:00Z"
        },
        headers={"X-Api-Key": full_key}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check envelope structure
    assert "data" in data
    assert "meta" in data
    assert "query" in data["meta"]
    assert "source" in data["meta"]
    assert "credits" in data["meta"]
    assert "next" in data["meta"]

