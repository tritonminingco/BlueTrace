"""Tests for offline ingestion with demo data."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.turbidity_demo import TurbidityDemoIngester
from app.models.dataset_common import DatasetTurbidity


class TestTurbidityIngester:
    """Test turbidity demo ingester."""

    @pytest.mark.asyncio
    async def test_turbidity_ingester_generates_data(self, db_session: AsyncSession):
        """Test that turbidity ingester generates data."""
        ingester = TurbidityDemoIngester()

        # Run ingestion
        raw_data = await ingester.fetch_data()
        records = await ingester.transform(raw_data)

        assert len(records) > 0
        assert all("lat" in r for r in records)
        assert all("lon" in r for r in records)
        assert all("time" in r for r in records)
        assert all("ntu" in r for r in records)

    @pytest.mark.asyncio
    async def test_turbidity_ingester_upsert(self, db_session: AsyncSession):
        """Test that turbidity ingester can upsert to database."""
        ingester = TurbidityDemoIngester()

        # Generate and insert data
        raw_data = await ingester.fetch_data()
        records = await ingester.transform(raw_data)
        count = await ingester.upsert(db_session, records)
        await db_session.commit()

        assert count > 0

        # Verify data in database
        result = await db_session.execute(select(DatasetTurbidity))
        db_records = result.scalars().all()

        assert len(db_records) > 0

    @pytest.mark.asyncio
    async def test_turbidity_ingester_idempotent(self, db_session: AsyncSession):
        """Test that turbidity ingester is idempotent."""
        ingester = TurbidityDemoIngester()

        # Run ingestion twice
        raw_data = await ingester.fetch_data()
        records = await ingester.transform(raw_data)

        count1 = await ingester.upsert(db_session, records)
        await db_session.commit()

        count2 = await ingester.upsert(db_session, records)
        await db_session.commit()

        # Count should be the same (idempotent)
        assert count1 == count2

        # Verify no duplicates
        result = await db_session.execute(select(DatasetTurbidity))
        db_records = result.scalars().all()

        # Should still be same count (no duplicates)
        assert len(db_records) <= count1
