"""Base ingester class."""

from abc import ABC, abstractmethod
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal

logger = get_logger(__name__)


class BaseIngester(ABC):
    """Base class for data ingesters."""

    def __init__(self, source_name: str):
        """
        Initialize ingester.

        Args:
            source_name: Name of the data source
        """
        self.source_name = source_name
        self.logger = get_logger(f"ingestion.{source_name}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def fetch_page(self, url: str, params: dict[str, Any] | None = None) -> Any:
        """
        Fetch data from external source with retry logic.

        Args:
            url: Source URL
            params: Query parameters

        Returns:
            Response data
        """
        self.logger.info(f"Fetching data from {url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    @abstractmethod
    async def transform(self, raw_data: Any) -> list[dict[str, Any]]:
        """
        Transform raw data into database-ready format.

        Args:
            raw_data: Raw data from source

        Returns:
            List of records ready for insertion
        """
        pass

    @abstractmethod
    async def upsert(self, db: AsyncSession, records: list[dict[str, Any]]) -> int:
        """
        Insert or update records in database.

        Args:
            db: Database session
            records: Records to upsert

        Returns:
            Number of records processed
        """
        pass

    async def run(self) -> None:
        """Run the ingestion process."""
        self.logger.info(f"Starting ingestion for {self.source_name}")

        try:
            # Fetch data
            raw_data = await self.fetch_data()

            # Transform
            records = await self.transform(raw_data)
            self.logger.info(f"Transformed {len(records)} records")

            # Upsert to database
            async with AsyncSessionLocal() as db:
                count = await self.upsert(db, records)
                await db.commit()

            self.logger.info(f"Successfully ingested {count} records from {self.source_name}")

        except Exception as e:
            self.logger.error(f"Ingestion failed for {self.source_name}: {str(e)}")
            raise

    @abstractmethod
    async def fetch_data(self) -> Any:
        """
        Fetch data from source.

        Returns:
            Raw data from source
        """
        pass
