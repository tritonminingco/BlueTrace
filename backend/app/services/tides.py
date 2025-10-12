"""Tides data service."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_common import DatasetTides


async def get_tides_data(
    db: AsyncSession,
    station_id: str,
    start: datetime,
    end: datetime,
    limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Fetch tides data for a station within a time range.
    
    Args:
        db: Database session
        station_id: Station identifier
        start: Start datetime
        end: End datetime
        limit: Maximum number of records
        
    Returns:
        List of tide records
    """
    query = (
        select(DatasetTides)
        .where(
            DatasetTides.station_id == station_id,
            DatasetTides.time >= start,
            DatasetTides.time <= end
        )
        .order_by(DatasetTides.time)
        .limit(limit)
    )
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return [
        {
            "station_id": record.station_id,
            "time": record.time.isoformat(),
            "water_level_m": record.water_level_m,
        }
        for record in records
    ]

