"""NOAA CO-OPS tides ingester."""
from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.base import BaseIngester
from app.models.dataset_common import DatasetTides


class TidesNOAAIngester(BaseIngester):
    """Ingester for NOAA CO-OPS tides data."""

    DEMO_STATIONS = ["8454000", "8518750", "8574680"]  # Providence, NY, Wilmington

    def __init__(self):
        """Initialize tides ingester."""
        super().__init__("tides_noaa")

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch tides data from NOAA CO-OPS API."""
        all_data = []
        
        # Fetch data for demo stations
        for station_id in self.DEMO_STATIONS:
            try:
                # Get last 7 days of data
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=7)
                
                url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
                params = {
                    "station": station_id,
                    "begin_date": start_date.strftime("%Y%m%d"),
                    "end_date": end_date.strftime("%Y%m%d"),
                    "product": "water_level",
                    "datum": "MLLW",
                    "units": "metric",
                    "time_zone": "gmt",
                    "format": "json",
                    "application": "bluetrace"
                }
                
                data = await self.fetch_page(url, params)
                all_data.append({"station_id": station_id, "data": data})
                
            except Exception as e:
                self.logger.warning(f"Failed to fetch data for station {station_id}: {str(e)}")
        
        return all_data

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform NOAA tides data."""
        records = []
        
        for station_data in raw_data:
            station_id = station_data["station_id"]
            data = station_data["data"]
            
            if "data" not in data:
                continue
            
            for record in data["data"]:
                try:
                    records.append({
                        "station_id": station_id,
                        "time": datetime.strptime(record["t"], "%Y-%m-%d %H:%M"),
                        "water_level_m": float(record["v"])
                    })
                except (KeyError, ValueError) as e:
                    self.logger.warning(f"Skipping invalid record: {e}")
        
        return records

    async def upsert(self, db: AsyncSession, records: List[Dict[str, Any]]) -> int:
        """Upsert tides records."""
        if not records:
            return 0
        
        # Use PostgreSQL INSERT ... ON CONFLICT DO NOTHING for idempotency
        stmt = pg_insert(DatasetTides).values(records)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["station_id", "time"]
        )
        
        await db.execute(stmt)
        return len(records)

