"""Water turbidity service."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_common import DatasetTurbidity


async def get_turbidity_data(
    db: AsyncSession,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    start: datetime,
    end: datetime,
    limit: int = 1000,
) -> list[dict[str, Any]]:
    """
    Fetch turbidity data within a bounding box and time range.

    Args:
        db: Database session
        min_lon: Minimum longitude
        min_lat: Minimum latitude
        max_lon: Maximum longitude
        max_lat: Maximum latitude
        start: Start datetime
        end: End datetime
        limit: Maximum number of records

    Returns:
        List of turbidity records
    """
    query = (
        select(DatasetTurbidity)
        .where(
            DatasetTurbidity.lon >= min_lon,
            DatasetTurbidity.lon <= max_lon,
            DatasetTurbidity.lat >= min_lat,
            DatasetTurbidity.lat <= max_lat,
            DatasetTurbidity.time >= start,
            DatasetTurbidity.time <= end,
        )
        .order_by(DatasetTurbidity.time)
        .limit(limit)
    )

    result = await db.execute(query)
    records = result.scalars().all()

    return [
        {
            "lat": record.lat,
            "lon": record.lon,
            "time": record.time.isoformat(),
            "ntu": record.ntu,
        }
        for record in records
    ]
