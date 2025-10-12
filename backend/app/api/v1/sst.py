"""Sea surface temperature API endpoints."""
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_api_key
from app.core.errors import ValidationError
from app.db.session import get_db
from app.models.api_key import APIKey
from app.services.sst import get_sst_data

router = APIRouter()


@router.get("/sst")
async def get_sst(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    start: str = Query(..., description="Start datetime (ISO format)"),
    end: str = Query(..., description="End datetime (ISO format)"),
    radius: float = Query(0.5, ge=0.1, le=5.0, description="Search radius in degrees"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum records"),
    db: AsyncSession = Depends(get_db),
    api_key: APIKey = Depends(get_current_api_key)
) -> Dict[str, Any]:
    """
    Get sea surface temperature data near a location.
    
    Returns SST measurements within the specified location and time range.
    """
    # Parse datetimes
    try:
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
    except ValueError:
        raise ValidationError(
            message="Invalid datetime format",
            hint="Use ISO 8601 format (e.g., 2024-01-01T00:00:00Z)"
        )
    
    # Validate time range
    if end_dt <= start_dt:
        raise ValidationError(message="End time must be after start time")
    
    # Fetch data
    data = await get_sst_data(db, lat, lon, start_dt, end_dt, radius, limit)
    
    return {
        "data": data,
        "meta": {
            "query": {
                "lat": lat,
                "lon": lon,
                "start": start,
                "end": end,
                "radius": radius,
                "limit": limit
            },
            "count": len(data),
            "source": "NOAA ERDDAP",
            "credits": "Data provided by NOAA Environmental Research Division Data Access Program",
            "next": None
        }
    }

