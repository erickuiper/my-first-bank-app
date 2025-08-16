"""
Test configuration and fixtures for backend tests.
Uses SQLite in-memory database for fast, isolated testing.
"""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for tests
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Create test session factory
TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None, None]:
    """Set up test database schema."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()


@pytest.fixture
async def db_session(setup_database) -> AsyncSession:
    """Create a fresh database session for each test."""
    async with TestingSessionLocal() as session:
        yield session
        # Clean up any pending changes and close the session properly
        try:
            await session.rollback()
        except Exception:  # nosec B110
            # If rollback fails, just close the session
            pass
        finally:
            await session.close()

    # Clear the database between tests to ensure isolation
    from sqlalchemy import text

    async with test_engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DELETE FROM transactions")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DELETE FROM accounts")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DELETE FROM children")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DELETE FROM users")))


@pytest.fixture
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Create a test client with in-memory database."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_user() -> dict:
    """Mock user data for testing."""
    return {
        "id": 1,
        "email": "test@example.com",
        "hashed_password": "hashed_password_123",
        "is_active": True,
    }


@pytest.fixture
def mock_child() -> dict:
    """Mock child data for testing."""
    return {
        "id": 1,
        "name": "Test Child",
        "birthdate": "2015-01-01",
        "parent_id": 1,
    }


@pytest.fixture
def mock_account() -> dict:
    """Mock account data for testing."""
    return {
        "id": 1,
        "account_type": "checking",
        "balance_cents": 0,
        "child_id": 1,
    }


@pytest.fixture
def mock_transaction() -> dict:
    """Mock transaction data for testing."""
    return {
        "id": 1,
        "amount_cents": 1000,
        "transaction_type": "deposit",
        "idempotency_key": "test_key_123",
        "account_id": 1,
    }


@pytest.fixture
def auth_headers(mock_user: dict) -> dict:
    """Generate authentication headers for protected endpoints."""
    # In a real implementation, this would create a valid JWT token
    # For now, we'll use a mock token
    return {"Authorization": "Bearer mock_token_123"}


@pytest.fixture
def async_client() -> AsyncMock:
    """Mock async HTTP client for testing."""
    return AsyncMock()
