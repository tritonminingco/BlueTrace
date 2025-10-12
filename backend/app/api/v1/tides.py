"""Tides API endpoints."""
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_api_key
from app.core.errors import ValidationError
from app.db.session import get_db
from app.models.api_key import APIKey
from app.services.tides import get_tides_data

router = APIRouter()


@router.get("/tides")
async def get_tides(
    station_id: str = Query(..., description="Station identifier"),
    start: str = Query(..., description="Start datetime (ISO format)"),
    end: str = Query(..., description="End datetime (ISO format)"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum records"),
    db: AsyncSession = Depends(get_db),
    api_key: APIKey = Depends(get_current_api_key)
) -> Dict[str, Any]:
    """
    Get tides and water level data for a station.
    
    Returns water level measurements within the specified time range.
    """
    # Parse datetimes
    try:
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValidationError(
            message="Invalid datetime format",
            hint="Use ISO 8601 format (e.g., 2024-01-01T00:00:00Z)"
        )
    
    # Validate time range
    if end_dt <= start_dt:
        raise ValidationError(
            message="End time must be after start time"
        )
    
    # Fetch data
    data = await get_tides_data(db, station_id, start_dt, end_dt, limit)
    
    return {
        "data": data,
        "meta": {
            "query": {
                "station_id": station_id,
                "start": start,
                "end": end,
                "limit": limit
            },
            "count": len(data),
            "source": "NOAA CO-OPS",
            "credits": "Data provided by NOAA Center for Operational Oceanographic Products and Services",
            "next": None
        }
    }

