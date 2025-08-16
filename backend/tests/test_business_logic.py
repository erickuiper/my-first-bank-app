"""
Business logic tests using in-memory database.
These tests can run in CI/CD without external database dependencies.
"""

from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.child import Child
from app.models.transaction import Transaction
from app.models.user import User


# Helper function to generate unique emails for tests
def get_unique_email() -> str:
    """Generate a unique email address for testing"""
    import uuid

    return f"test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.mark.asyncio
async def test_create_child_with_accounts(db_session: AsyncSession) -> None:
    """Test creating a child and then manually creating accounts"""
    # Create a user
    user = User(email=get_unique_email(), hashed_password="hashed_password")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create a child
    child = Child(name="Test Child", birthdate=date(2015, 1, 1), parent_id=user.id)
    db_session.add(child)
    await db_session.commit()
    await db_session.refresh(child)

    # Manually create accounts for the child
    checking_account = Account(account_type="checking", balance_cents=0, child_id=child.id)
    savings_account = Account(account_type="savings", balance_cents=0, child_id=child.id)

    db_session.add(checking_account)
    db_session.add(savings_account)
    await db_session.commit()

    # Check that accounts were created
    assert checking_account.id is not None
    assert savings_account.id is not None
    assert checking_account.account_type == "checking"
    assert savings_account.account_type == "savings"
    assert checking_account.balance_cents == 0
    assert savings_account.balance_cents == 0


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession) -> None:
    """Test creating a user"""
    user = User(email=get_unique_email(), hashed_password="hashed_password")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.email is not None
    assert user.hashed_password == "hashed_password"


@pytest.mark.asyncio
async def test_create_child(db_session: AsyncSession) -> None:
    """Test creating a child"""
    # Create a user first
    user = User(email=get_unique_email(), hashed_password="hashed_password")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create a child
    child = Child(name="Test Child", birthdate=date(2015, 1, 1), parent_id=user.id)
    db_session.add(child)
    await db_session.commit()
    await db_session.refresh(child)

    assert child.id is not None
    assert child.name == "Test Child"
    assert child.birthdate == date(2015, 1, 1)
    assert child.parent_id == user.id


@pytest.mark.asyncio
async def test_create_account(db_session: AsyncSession) -> None:
    """Test creating an account"""
    # Create a user first
    user = User(email=get_unique_email(), hashed_password="hashed_password")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create a child
    child = Child(name="Test Child", birthdate=date(2015, 1, 1), parent_id=user.id)
    db_session.add(child)
    await db_session.commit()
    await db_session.refresh(child)

    # Create an account
    account = Account(account_type="checking", balance_cents=0, child_id=child.id)
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    assert account.id is not None
    assert account.account_type == "checking"
    assert account.balance_cents == 0
    assert account.child_id == child.id


@pytest.mark.asyncio
async def test_create_transaction(db_session: AsyncSession) -> None:
    """Test creating a transaction"""
    # Create a user first
    user = User(email=get_unique_email(), hashed_password="hashed_password")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create a child
    child = Child(name="Test Child", birthdate=date(2015, 1, 1), parent_id=user.id)
    db_session.add(child)
    await db_session.commit()
    await db_session.refresh(child)

    # Create an account
    account = Account(account_type="checking", balance_cents=0, child_id=child.id)
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create a transaction
    transaction = Transaction(
        amount_cents=1000, transaction_type="deposit", idempotency_key="test_key_123", account_id=account.id
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    assert transaction.id is not None
    assert transaction.amount_cents == 1000
    assert transaction.transaction_type == "deposit"
    assert transaction.idempotency_key == "test_key_123"
    assert transaction.account_id == account.id
