"""Bathymetry tile API endpoints."""
from fastapi import APIRouter, Depends, Path
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_api_key
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models.api_key import APIKey
from app.services.bathy import get_bathy_tile

router = APIRouter()


@router.get("/bathy/tiles/{z}/{x}/{y}.png")
async def get_bathy_tile_endpoint(
    z: int = Path(..., ge=0, le=10, description="Zoom level"),
    x: int = Path(..., ge=0, description="Tile X coordinate"),
    y: int = Path(..., ge=0, description="Tile Y coordinate"),
    db: AsyncSession = Depends(get_db),
    api_key: APIKey = Depends(get_current_api_key)
) -> Response:
    """
    Get a bathymetry tile image.
    
    Returns a PNG tile for the specified coordinates.
    """
    # Fetch tile
    tile_data = await get_bathy_tile(db, z, x, y)
    
    if not tile_data:
        raise NotFoundError(
            message=f"Tile not found: {z}/{x}/{y}",
            hint="Check tile coordinates or request tile generation"
        )
    
    return Response(
        content=tile_data,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Tile-Z": str(z),
            "X-Tile-X": str(x),
            "X-Tile-Y": str(y),
        }
    )

