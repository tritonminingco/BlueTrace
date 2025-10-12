"""Sea surface temperature service."""
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_common import DatasetSST


async def get_sst_data(
    db: AsyncSession,
    lat: float,
    lon: float,
    start: datetime,
    end: datetime,
    radius: float = 0.5,
    limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Fetch SST data near a location within a time range.
    
    Args:
        db: Database session
        lat: Latitude
        lon: Longitude
        start: Start datetime
        end: End datetime
        radius: Search radius in degrees
        limit: Maximum number of records
        
    Returns:
        List of SST records
    """
    query = (
        select(DatasetSST)
        .where(
            DatasetSST.lat >= lat - radius,
            DatasetSST.lat <= lat + radius,
            DatasetSST.lon >= lon - radius,
            DatasetSST.lon <= lon + radius,
            DatasetSST.time >= start,
            DatasetSST.time <= end
        )
        .order_by(DatasetSST.time)
        .limit(limit)
    )
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return [
        {
            "lat": record.lat,
            "lon": record.lon,
            "time": record.time.isoformat(),
            "sst_c": record.sst_c,
        }
        for record in records
    ]

