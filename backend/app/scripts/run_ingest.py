"""Run ingestion workers once."""

import asyncio

from app.core.logging import get_logger, setup_logging
from app.ingestion.turbidity_demo import TurbidityDemoIngester

setup_logging()
logger = get_logger(__name__)


async def main() -> None:
    """Run all ingesters."""
    logger.info("Starting manual ingestion...")

    # Run turbidity ingester (demo data)
    logger.info("Running turbidity ingester...")
    turbidity = TurbidityDemoIngester()
    await turbidity.run()

    logger.info("✓ Ingestion completed")


if __name__ == "__main__":
    asyncio.run(main())
