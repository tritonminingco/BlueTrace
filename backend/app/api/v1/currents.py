"""Ocean currents API endpoints."""
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_api_key
from app.core.errors import ValidationError
from app.db.session import get_db
from app.models.api_key import APIKey
from app.services.currents import get_currents_data

router = APIRouter()


@router.get("/currents")
async def get_currents(
    bbox: str = Query(..., description="Bounding box: minLon,minLat,maxLon,maxLat"),
    time: str = Query(..., description="Target datetime (ISO format)"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum records"),
    db: AsyncSession = Depends(get_db),
    api_key: APIKey = Depends(get_current_api_key)
) -> Dict[str, Any]:
    """
    Get ocean currents data within a bounding box.
    
    Returns current velocity (u, v components) at the specified time.
    """
    # Parse bbox
    try:
        coords = [float(c) for c in bbox.split(",")]
        if len(coords) != 4:
            raise ValueError("Expected 4 coordinates")
        min_lon, min_lat, max_lon, max_lat = coords
    except ValueError:
        raise ValidationError(
            message="Invalid bounding box format",
            hint="Use format: minLon,minLat,maxLon,maxLat (e.g., -75,38,-74,39)"
        )
    
    # Parse datetime
    try:
        time_dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
    except ValueError:
        raise ValidationError(
            message="Invalid datetime format",
            hint="Use ISO 8601 format (e.g., 2024-01-01T12:00:00Z)"
        )
    
    # Fetch data
    data = await get_currents_data(db, min_lon, min_lat, max_lon, max_lat, time_dt, limit)
    
    return {
        "data": data,
        "meta": {
            "query": {
                "bbox": bbox,
                "time": time,
                "limit": limit
            },
            "count": len(data),
            "source": "Demo Dataset",
            "credits": "Demonstration data for BlueTrace MVP",
            "next": None
        }
    }

