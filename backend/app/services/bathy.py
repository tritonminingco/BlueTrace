"""Bathymetry service."""


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_common import DatasetBathyTiles


async def get_bathy_tile(db: AsyncSession, z: int, x: int, y: int) -> bytes | None:
    """
    Fetch a bathymetry tile.

    Args:
        db: Database session
        z: Zoom level
        x: Tile X coordinate
        y: Tile Y coordinate

    Returns:
        Tile image bytes or None if not found
    """
    query = select(DatasetBathyTiles).where(
        DatasetBathyTiles.tile_z == z, DatasetBathyTiles.tile_x == x, DatasetBathyTiles.tile_y == y
    )

    result = await db.execute(query)
    record = result.scalar_one_or_none()

    if record:
        return record.blob

    return None
