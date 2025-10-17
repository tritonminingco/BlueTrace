"""Water turbidity API endpoints."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_api_key
from app.core.errors import ValidationError
from app.db.session import get_db
from app.models.api_key import APIKey
from app.services.turbidity import get_turbidity_data

router = APIRouter()


@router.get("/turbidity")
async def get_turbidity(
    bbox: str = Query(..., description="Bounding box: minLon,minLat,maxLon,maxLat"),
    start: str = Query(..., description="Start datetime (ISO format)"),
    end: str = Query(..., description="End datetime (ISO format)"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum records"),
    db: AsyncSession = Depends(get_db),
    api_key: APIKey = Depends(get_current_api_key),
) -> dict[str, Any]:
    """
    Get water turbidity data within a bounding box.

    Returns turbidity measurements (NTU) within the specified area and time range.
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
            hint="Use format: minLon,minLat,maxLon,maxLat (e.g., -75,38,-74,39)",
        )

    # Parse datetimes
    try:
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
    except ValueError:
        raise ValidationError(
            message="Invalid datetime format",
            hint="Use ISO 8601 format (e.g., 2024-01-01T00:00:00Z)",
        )

    # Validate time range
    if end_dt <= start_dt:
        raise ValidationError(message="End time must be after start time")

    # Fetch data
    data = await get_turbidity_data(db, min_lon, min_lat, max_lon, max_lat, start_dt, end_dt, limit)

    return {
        "data": data,
        "meta": {
            "query": {"bbox": bbox, "start": start, "end": end, "limit": limit},
            "count": len(data),
            "source": "Demo Dataset",
            "credits": "Demonstration data for BlueTrace MVP",
            "next": None,
        },
    }
