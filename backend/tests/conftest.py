"""
Test configuration and fixtures for backend tests.
Uses SQLite in-memory database for fast, isolated testing.
"""

import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app

# Test database configuration - use async SQLite for compatibility with app
test_database_url = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    test_database_url,
    connect_args={"check_same_thread": False},
    poolclass=None,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Override the get_db dependency for testing
async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def setup_database():
    """Set up the test database"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database):
    """Create a test database session"""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            try:
                await session.rollback()
            except Exception:
                pass
            finally:
                await session.close()


@pytest.fixture
def client(setup_database):
    """Create a test client with test database setup"""
    return TestClient(app)
