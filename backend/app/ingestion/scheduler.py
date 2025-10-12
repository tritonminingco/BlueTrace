"""Dramatiq-based task scheduler."""
import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app.core.config import settings
from app.core.logging import get_logger
from app.ingestion.tides_noaa import TidesNOAAIngester
from app.ingestion.turbidity_demo import TurbidityDemoIngester

logger = get_logger(__name__)

# Initialize Dramatiq broker
redis_broker = RedisBroker(url=settings.REDIS_URL)
dramatiq.set_broker(redis_broker)


@dramatiq.actor(max_retries=3)
def ingest_tides_task() -> None:
    """Task to ingest tides data."""
    import asyncio
    
    logger.info("Starting tides ingestion task")
    ingester = TidesNOAAIngester()
    asyncio.run(ingester.run())
    logger.info("Tides ingestion task completed")


@dramatiq.actor(max_retries=3)
def ingest_turbidity_task() -> None:
    """Task to ingest turbidity data."""
    import asyncio
    
    logger.info("Starting turbidity ingestion task")
    ingester = TurbidityDemoIngester()
    asyncio.run(ingester.run())
    logger.info("Turbidity ingestion task completed")


def schedule_all_tasks() -> None:
    """Schedule all ingestion tasks."""
    logger.info("Scheduling ingestion tasks")
    
    # Send tasks to queue
    ingest_tides_task.send()
    ingest_turbidity_task.send()
    
    logger.info("All tasks scheduled")

