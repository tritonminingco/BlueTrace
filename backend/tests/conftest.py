"""Pytest configuration and fixtures."""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.auth import generate_api_key
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.api_key import APIKey


# Test database URL
TEST_DATABASE_URL = settings.POSTGRES_DSN.replace("bluetrace", "bluetrace_test")
TEST_DATABASE_URL = TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_api_key(db_session: AsyncSession) -> tuple[str, APIKey]:
    """Create test API key."""
    full_key, prefix, key_hash = generate_api_key()
    
    api_key = APIKey(
        name="Test Key",
        key_hash=key_hash,
        prefix=prefix,
        owner_email="test@example.com",
        plan="free",
    )
    
    db_session.add(api_key)
    await db_session.commit()
    await db_session.refresh(api_key)
    
    return full_key, api_key


@pytest_asyncio.fixture
async def admin_api_key(db_session: AsyncSession) -> tuple[str, APIKey]:
    """Create admin API key."""
    full_key, prefix, key_hash = generate_api_key()
    
    api_key = APIKey(
        name="Admin Key",
        key_hash=key_hash,
        prefix=prefix,
        owner_email=settings.ADMIN_SEED_EMAIL,
        plan="enterprise",
    )
    
    db_session.add(api_key)
    await db_session.commit()
    await db_session.refresh(api_key)
    
    return full_key, api_key


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

