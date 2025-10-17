"""Health check endpoint."""

from typing import Any

import redis.asyncio as redis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Health check endpoint.

    Returns system status, version, and connectivity checks for dependencies.
    """
    status_data: dict[str, Any] = {
        "status": "ok",
        "version": "0.1.0",
        "service": settings.OTEL_SERVICE_NAME,
    }

    # Check database connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        status_data["database"] = "connected"
    except Exception as e:
        status_data["database"] = f"error: {str(e)}"
        status_data["status"] = "degraded"

    # Check Redis connectivity
    try:
        redis_client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        await redis_client.ping()
        await redis_client.close()
        status_data["redis"] = "connected"
    except Exception as e:
        status_data["redis"] = f"error: {str(e)}"
        status_data["status"] = "degraded"

    return status_data
