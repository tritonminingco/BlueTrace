"""Demo turbidity data generator."""
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.base import BaseIngester
from app.models.dataset_common import DatasetTurbidity


class TurbidityDemoIngester(BaseIngester):
    """Generate demo turbidity data with seeded randomness."""

    def __init__(self):
        """Initialize demo ingester."""
        super().__init__("turbidity_demo")
        random.seed(42)  # Predictable data for testing

    async def fetch_data(self) -> Dict[str, Any]:
        """Generate demo data (no external fetch)."""
        return {"demo": True}

    async def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Generate demo turbidity records."""
        records = []
        
        # Generate data for coastal areas
        # Chesapeake Bay region
        base_time = datetime(2024, 1, 1, 0, 0, 0)
        
        for day in range(7):
            for lat in range(36, 40):
                for lon in range(-77, -74):
                    time = base_time + timedelta(days=day, hours=12)
                    
                    # Generate turbidity with some variation
                    base_ntu = 5.0 + random.uniform(-2, 3)
                    
                    records.append({
                        "lat": lat + random.uniform(0, 0.9),
                        "lon": lon + random.uniform(0, 0.9),
                        "time": time,
                        "ntu": max(0.1, base_ntu)
                    })
        
        return records

    async def upsert(self, db: AsyncSession, records: List[Dict[str, Any]]) -> int:
        """Upsert turbidity records."""
        if not records:
            return 0
        
        stmt = pg_insert(DatasetTurbidity).values(records)
        stmt = stmt.on_conflict_do_nothing()
        
        await db.execute(stmt)
        return len(records)

