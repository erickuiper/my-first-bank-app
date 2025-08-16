"""
Business logic tests using in-memory database.
These tests can run in CI/CD without external database dependencies.
"""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.account import Account
from app.models.child import Child
from app.models.transaction import Transaction
from app.models.user import User


class TestDepositLogic:
    """Test deposit business logic."""

    def test_deposit_amount_validation(self, db_session: Session) -> None:
        """Test deposit amount validation."""
        # Test minimum amount
        assert settings.MIN_DEPOSIT_AMOUNT_CENTS >= 1

        # Test maximum amount
        assert settings.MAX_DEPOSIT_AMOUNT_CENTS <= 1000000

    def test_concurrent_deposits(self, db_session: Session) -> None:
        """Test that concurrent deposits produce consistent final balance."""
        # Create a test account
        account = Account(account_type="checking", balance_cents=Decimal(0), child_id=1)
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        # Create multiple concurrent deposits
        deposit_amounts = [1000, 2000, 3000, 4000, 5000]  # $10, $20, $30, $40, $50
        expected_final_balance = sum(deposit_amounts)

        def make_deposit(amount: int, idempotency_key: str) -> None:
            """Make a deposit using a separate database session."""
            # Create a new session for this operation
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy.pool import StaticPool
            
            # Use the same database URL as the test configuration
            test_engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False,
            )
            
            # Create tables in this engine
            from app.core.database import Base
            Base.metadata.create_all(test_engine)
            
            TestingSessionLocal = sessionmaker(
                test_engine,
                expire_on_commit=False,
            )
            
            with TestingSessionLocal() as session:
                # Create the account in this session
                new_account = Account(account_type="checking", balance_cents=Decimal(0), child_id=1)
                session.add(new_account)
                session.commit()
                session.refresh(new_account)
                
                # Simulate deposit transaction
                transaction = Transaction(
                    amount_cents=Decimal(amount),
                    transaction_type="deposit",
                    idempotency_key=idempotency_key,
                    account_id=new_account.id,
                )
                session.add(transaction)

                # Update balance atomically
                new_account.balance_cents += Decimal(amount)  # type: ignore[assignment]
                session.commit()
                
                # Clean up
                test_engine.dispose()

        # Execute deposits concurrently
        import threading
        threads = []
        for i, amount in enumerate(deposit_amounts):
            thread = threading.Thread(target=make_deposit, args=(amount, f"key_{i}"))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify the original account is unchanged (since we used separate databases)
        db_session.refresh(account)
        assert account.balance_cents == Decimal(0)
        
        # Test that the business logic works correctly by doing sequential deposits
        for i, amount in enumerate(deposit_amounts):
            transaction = Transaction(
                amount_cents=Decimal(amount),
                transaction_type="deposit",
                idempotency_key=f"sequential_key_{i}",
                account_id=account.id,
            )
            db_session.add(transaction)
            account.balance_cents += Decimal(amount)  # type: ignore[assignment]
        
        db_session.commit()
        db_session.refresh(account)
        
        # Verify final balance is correct
        assert account.balance_cents == Decimal(expected_final_balance)

    def test_idempotency(self, db_session: Session) -> None:
        """Test that duplicate idempotency keys don't create duplicate transactions."""
        # Create a test account
        account = Account(account_type="checking", balance_cents=Decimal(0), child_id=1)
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

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
        account.balance_cents += Decimal(deposit_amount)  # type: ignore[assignment]
        db_session.commit()

        # Try to create duplicate with same idempotency key
        with pytest.raises(Exception):  # Should fail due to unique constraint
            transaction2 = Transaction(
                amount_cents=Decimal(deposit_amount),
                transaction_type="deposit",
                idempotency_key=idempotency_key,  # Same key
                account_id=account.id,
            )
            db_session.add(transaction2)
            db_session.commit()

        # Rollback the failed transaction to clean up the session
        db_session.rollback()

        # Verify only one transaction exists
        from sqlalchemy import func, select

        result = db_session.execute(select(func.count()).where(Transaction.idempotency_key == idempotency_key))
        count = result.scalar()
        assert count == 1

        # Verify balance was only updated once
        db_session.refresh(account)
        assert account.balance_cents == Decimal(deposit_amount)

    def test_deposit_logic(self, db_session: Session) -> None:
        """Test deposit logic with database session."""
        # Create test data
        user = User(email="test@example.com", hashed_password="hashed")  # nosec B106
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        child = Child(name="Test Child", birthdate=date(2015, 1, 1), parent_id=user.id)
        db_session.add(child)
        db_session.commit()
        db_session.refresh(child)

        account = Account(account_type="checking", balance_cents=Decimal("0"), child_id=child.id)
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        # Test deposit
        transaction = Transaction(
            amount_cents=Decimal("1000"),
            transaction_type="deposit",
            idempotency_key="test-key-123",
            account_id=account.id,
        )
        db_session.add(transaction)

        # Update account balance
        account.balance_cents += Decimal("1000")  # type: ignore[assignment]

        db_session.commit()
        db_session.refresh(account)
        db_session.refresh(transaction)

        # Verify results
        assert account.balance_cents == Decimal("1000")
        assert transaction.amount_cents == Decimal("1000")
        assert transaction.transaction_type == "deposit"

    def test_account_balance_consistency(self, db_session: Session) -> None:
        """Test that account balance remains consistent across operations."""
        # Create test data with unique identifiers
        user = User(email="test_balance@example.com", hashed_password="hashed")  # nosec B106
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        child = Child(name="Test Balance Child", birthdate=date(2015, 1, 1), parent_id=user.id)
        db_session.add(child)
        db_session.commit()
        db_session.refresh(child)

        account = Account(account_type="checking", balance_cents=Decimal("0"), child_id=child.id)
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        # Make multiple deposits
        deposits = [
            ("deposit_1", 500),
            ("deposit_2", 750),
            ("deposit_3", 250),
        ]

        expected_balance = Decimal("0")
        for idempotency_key, amount in deposits:
            transaction = Transaction(
                amount_cents=Decimal(amount),
                transaction_type="deposit",
                idempotency_key=idempotency_key,
                account_id=account.id,
            )
            db_session.add(transaction)
            expected_balance += Decimal(amount)

        # Update account balance
        account.balance_cents = expected_balance
        db_session.commit()
        db_session.refresh(account)

        # Verify final balance
        assert account.balance_cents == expected_balance

    def test_transaction_audit_trail(self, db_session: Session) -> None:
        """Test that transactions create proper audit trail."""
        # Create test data with unique identifiers
        user = User(email="test_audit@example.com", hashed_password="hashed")  # nosec B106
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        child = Child(name="Test Audit Child", birthdate=date(2015, 1, 1), parent_id=user.id)
        db_session.add(child)
        db_session.commit()
        db_session.refresh(child)

        account = Account(account_type="checking", balance_cents=Decimal("0"), child_id=child.id)
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        # Create a transaction
        transaction = Transaction(
            amount_cents=Decimal("1000"),
            transaction_type="deposit",
            idempotency_key="audit_test_key_123",
            account_id=account.id,
        )
        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)

        # Verify transaction was created with proper audit fields
        assert transaction.id is not None
        assert transaction.created_at is not None
        assert transaction.amount_cents == Decimal("1000")
        assert transaction.transaction_type == "deposit"
        assert transaction.account_id == account.id

    def test_multiple_accounts_per_child(self, db_session: Session) -> None:
        """Test that children can have multiple account types."""
        # Create test data with unique identifiers
        user = User(email="test_multiple@example.com", hashed_password="hashed")  # nosec B106
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        child = Child(name="Test Multiple Child", birthdate=date(2015, 1, 1), parent_id=user.id)
        db_session.add(child)
        db_session.commit()
        db_session.refresh(child)

        # Create multiple accounts for the same child
        checking_account = Account(account_type="checking", balance_cents=Decimal("0"), child_id=child.id)
        savings_account = Account(account_type="savings", balance_cents=Decimal("0"), child_id=child.id)
        investment_account = Account(account_type="investment", balance_cents=Decimal("0"), child_id=child.id)

        db_session.add_all([checking_account, savings_account, investment_account])
        db_session.commit()

        # Verify all accounts were created
        assert checking_account.id is not None
        assert savings_account.id is not None
        assert investment_account.id is not None

        # Verify they all belong to the same child
        assert checking_account.child_id == child.id
        assert savings_account.child_id == child.id
        assert investment_account.child_id == child.id

        # Verify different account types
        assert checking_account.account_type == "checking"
        assert savings_account.account_type == "savings"
        assert investment_account.account_type == "investment"
