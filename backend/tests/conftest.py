"""
Test configuration and fixtures for backend tests.
Uses SQLite in-memory database for fast, isolated testing.
"""

import asyncio
from typing import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# Test database configuration - use standard SQLite for better CI compatibility
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create engine for tests
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Create test session factory
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=Session,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def setup_database() -> Generator[None, None, None]:
    """Set up test database schema."""
    with test_engine.begin() as conn:
        Base.metadata.create_all(conn)
    yield
    test_engine.dispose()


@pytest.fixture
def db_session(setup_database) -> Session:
    """Create a fresh database session for each test."""
    with TestingSessionLocal() as session:
        yield session
        # Clean up any pending changes and close the session properly
        try:
            session.rollback()
        except Exception:  # nosec B110
            # If rollback fails, just close the session
            pass
        finally:
            session.close()

    # Clear the database between tests to ensure isolation
    from sqlalchemy import text

    with test_engine.begin() as conn:
        conn.execute(text("DELETE FROM transactions"))
        conn.execute(text("DELETE FROM accounts"))
        conn.execute(text("DELETE FROM children"))
        conn.execute(text("DELETE FROM users"))


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with in-memory database."""

    def override_get_db() -> Generator[Session, None, None]:
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
