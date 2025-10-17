"""Seed script to create admin key and demo data."""

import asyncio
import random
import sys
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import generate_api_key
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.session import AsyncSessionLocal
from app.ingestion.turbidity_demo import TurbidityDemoIngester
from app.models.api_key import APIKey
from app.models.dataset_common import DatasetCurrents, DatasetSST, DatasetTides

setup_logging()
logger = get_logger(__name__)


async def create_admin_key(db: AsyncSession) -> str:
    """Create admin API key."""
    logger.info("Creating admin API key...")

    # Generate key
    full_key, prefix, key_hash = generate_api_key()

    # Create record
    admin_key = APIKey(
        name="Admin Key",
        key_hash=key_hash,
        prefix=prefix,
        owner_email=settings.ADMIN_SEED_EMAIL,
        plan="enterprise",
    )

    db.add(admin_key)
    await db.commit()

    logger.info(f"✓ Admin key created with prefix: {prefix}")
    return full_key


async def seed_demo_tides(db: AsyncSession) -> None:
    """Seed demo tides data."""
    logger.info("Seeding demo tides data...")

    base_time = datetime.utcnow() - timedelta(days=3)
    stations = ["DEMO001", "DEMO002", "DEMO003"]

    records = []
    for station_id in stations:
        for hour in range(72):  # 3 days
            time = base_time + timedelta(hours=hour)
            # Simulate tidal pattern
            water_level = 1.5 + 0.8 * random.sin(hour * 0.5)

            records.append(
                DatasetTides(station_id=station_id, time=time, water_level_m=water_level)
            )

    db.add_all(records)
    await db.commit()
    logger.info(f"✓ Seeded {len(records)} tide records")


async def seed_demo_sst(db: AsyncSession) -> None:
    """Seed demo SST data."""
    logger.info("Seeding demo SST data...")

    base_time = datetime.utcnow() - timedelta(days=3)

    records = []
    for day in range(3):
        for lat in range(35, 42):
            for lon in range(-76, -70):
                time = base_time + timedelta(days=day, hours=12)
                sst_c = 18.0 + random.uniform(-2, 2)

                records.append(
                    DatasetSST(
                        lat=float(lat) + random.uniform(0, 0.5),
                        lon=float(lon) + random.uniform(0, 0.5),
                        time=time,
                        sst_c=sst_c,
                    )
                )

    db.add_all(records)
    await db.commit()
    logger.info(f"✓ Seeded {len(records)} SST records")


async def seed_demo_currents(db: AsyncSession) -> None:
    """Seed demo currents data."""
    logger.info("Seeding demo currents data...")

    time = datetime.utcnow() - timedelta(hours=1)

    records = []
    for lat in range(36, 40):
        for lon in range(-76, -73):
            u = random.uniform(-0.5, 0.5)
            v = random.uniform(-0.3, 0.3)

            records.append(
                DatasetCurrents(
                    lat=float(lat) + random.uniform(0, 0.5),
                    lon=float(lon) + random.uniform(0, 0.5),
                    time=time,
                    u=u,
                    v=v,
                )
            )

    db.add_all(records)
    await db.commit()
    logger.info(f"✓ Seeded {len(records)} currents records")


async def seed_demo_turbidity(db: AsyncSession) -> None:
    """Seed demo turbidity data."""
    logger.info("Seeding demo turbidity data via ingester...")

    ingester = TurbidityDemoIngester()
    raw_data = await ingester.fetch_data()
    records_data = await ingester.transform(raw_data)
    count = await ingester.upsert(db, records_data)
    await db.commit()

    logger.info(f"✓ Seeded {count} turbidity records")


async def main() -> None:
    """Main seed function."""
    logger.info("=" * 60)
    logger.info("BlueTrace Seed Script")
    logger.info("=" * 60)

    async with AsyncSessionLocal() as db:
        try:
            # Create admin key
            admin_key = await create_admin_key(db)

            # Seed demo data
            await seed_demo_tides(db)
            await seed_demo_sst(db)
            await seed_demo_currents(db)
            await seed_demo_turbidity(db)

            logger.info("=" * 60)
            logger.info("✓ Seeding completed successfully!")
            logger.info("=" * 60)
            logger.info("")
            logger.info("Your Admin API Key (SAVE THIS - shown only once):")
            logger.info("")
            logger.info(f"  {admin_key}")
            logger.info("")
            logger.info("Test the API with:")
            logger.info("")
            logger.info(f'  curl -H "X-Api-Key: {admin_key}" \\')
            logger.info("    http://localhost:8080/v1/health")
            logger.info("")
            logger.info(f'  curl -H "X-Api-Key: {admin_key}" \\')
            logger.info(
                '    "http://localhost:8080/v1/tides?station_id=DEMO001&start=2024-01-01T00:00:00Z&end=2024-12-31T23:59:59Z"'
            )
            logger.info("")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Seeding failed: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
