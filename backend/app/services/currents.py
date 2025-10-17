"""Ocean currents service."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_common import DatasetCurrents


async def get_currents_data(
    db: AsyncSession,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    time: datetime,
    limit: int = 1000,
) -> list[dict[str, Any]]:
    """
    Fetch currents data within a bounding box at a specific time.

    Args:
        db: Database session
        min_lon: Minimum longitude
        min_lat: Minimum latitude
        max_lon: Maximum longitude
        max_lat: Maximum latitude
        time: Target datetime
        limit: Maximum number of records

    Returns:
        List of currents records
    """
    query = (
        select(DatasetCurrents)
        .where(
            DatasetCurrents.lon >= min_lon,
            DatasetCurrents.lon <= max_lon,
            DatasetCurrents.lat >= min_lat,
            DatasetCurrents.lat <= max_lat,
            DatasetCurrents.time == time,
        )
        .limit(limit)
    )

    result = await db.execute(query)
    records = result.scalars().all()

    return [
        {
            "lat": record.lat,
            "lon": record.lon,
            "time": record.time.isoformat(),
            "u": record.u,
            "v": record.v,
        }
        for record in records
    ]
