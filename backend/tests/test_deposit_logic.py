import asyncio
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.account import Account
from app.models.child import Child
from app.models.transaction import Transaction
from app.models.user import User


@pytest.mark.asyncio
async def test_deposit_amount_validation():
    """Test deposit amount validation"""
    # Test minimum amount
    assert settings.MIN_DEPOSIT_AMOUNT_CENTS >= 1

    # Test maximum amount
    assert settings.MAX_DEPOSIT_AMOUNT_CENTS <= 1000000


@pytest.mark.asyncio
async def test_concurrent_deposits(db_session: AsyncSession):
    """Test that concurrent deposits produce consistent final balance"""
    # Create a test account
    account = Account(account_type="checking", balance_cents=Decimal(0), child_id=1)
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create multiple concurrent deposits
    deposit_amounts = [1000, 2000, 3000, 4000, 5000]  # $10, $20, $30, $40, $50
    expected_final_balance = sum(deposit_amounts)

    async def make_deposit(amount: int, idempotency_key: str):
        # Simulate deposit transaction
        transaction = Transaction(
            amount_cents=Decimal(amount),
            transaction_type="deposit",
            idempotency_key=idempotency_key,
            account_id=account.id,
        )
        db_session.add(transaction)

        # Update balance atomically
        account.balance_cents += Decimal(amount)
        await db_session.commit()
        await db_session.refresh(account)
        return account.balance_cents

    # Execute deposits concurrently
    tasks = [make_deposit(amount, f"key_{i}") for i, amount in enumerate(deposit_amounts)]

    results = await asyncio.gather(*tasks)

    # Verify final balance is correct
    final_balance = results[-1]
    assert final_balance == Decimal(expected_final_balance)

    # Verify account balance matches
    await db_session.refresh(account)
    assert account.balance_cents == Decimal(expected_final_balance)


@pytest.mark.asyncio
async def test_idempotency(db_session: AsyncSession):
    """Test that duplicate idempotency keys don't create duplicate transactions"""
    # Create a test account
    account = Account(account_type="checking", balance_cents=Decimal(0), child_id=1)
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    idempotency_key = "test_key_123"
    deposit_amount = 1000

    # First deposit
    transaction1 = Transaction(
        amount_cents=Decimal(deposit_amount),
        transaction_type="deposit",
        idempotency_key=idempotency_key,
        account_id=account.id,
    )
    db_session.add(transaction1)
    account.balance_cents += Decimal(deposit_amount)
    await db_session.commit()

    # Try to create duplicate with same idempotency key
    with pytest.raises(Exception):  # Should fail due to unique constraint
        transaction2 = Transaction(
            amount_cents=Decimal(deposit_amount),
            transaction_type="deposit",
            idempotency_key=idempotency_key,  # Same key
            account_id=account.id,
        )
        db_session.add(transaction2)
        await db_session.commit()

    # Verify only one transaction exists
    result = await db_session.execute(
        "SELECT COUNT(*) FROM transactions WHERE idempotency_key = :key",
        {"key": idempotency_key},
    )
    count = result.scalar()
    assert count == 1

    # Verify balance was only updated once
    await db_session.refresh(account)
    assert account.balance_cents == Decimal(deposit_amount)


@pytest.mark.asyncio
async def test_deposit_logic(db_session):
    """Test deposit logic with database session"""
    # Create test data
    user = User(email="test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    child = Child(name="Test Child", birthdate=date(2015, 1, 1), parent_id=user.id)
    db_session.add(child)
    await db_session.commit()
    await db_session.refresh(child)

    account = Account(account_type="checking", balance_cents=Decimal("0"), child_id=child.id)
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Test deposit
    transaction = Transaction(
        amount_cents=Decimal("1000"),
        transaction_type="deposit",
        idempotency_key="test-key-123",
        account_id=account.id,
    )
    db_session.add(transaction)

    # Update account balance
    account.balance_cents += Decimal("1000")

    await db_session.commit()
    await db_session.refresh(account)
    await db_session.refresh(transaction)

    # Verify results
    assert account.balance_cents == Decimal("1000")
    assert transaction.amount_cents == Decimal("1000")
    assert transaction.transaction_type == "deposit"
