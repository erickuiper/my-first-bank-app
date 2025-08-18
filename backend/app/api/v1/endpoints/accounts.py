import base64
import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import get_password_hash, verify_password
from app.models.account import Account
from app.models.child import Child
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.account import AccountPinChange, AccountPinSetup, AccountPinVerification, BalanceUpdate
from app.schemas.transaction import DepositRequest, TransactionList, TransactionResponse, TransferRequest

router = APIRouter()


async def verify_account_access(account_id: int, current_user: User, db: AsyncSession) -> Account:
    # Verify account belongs to current user's child
    result = await db.execute(
        select(Account).join(Child).where(and_(Account.id == account_id, Child.parent_id == current_user.id))
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    return account


async def verify_account_pin(account: Account, pin: str) -> bool:
    """Verify the PIN for an account."""
    if not account.pin_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account PIN not configured. Please set up a PIN first."
        )

    return verify_password(pin, account.pin_hash)


@router.post("/{account_id}/setup-pin")
async def setup_account_pin(
    account_id: int,
    pin_data: AccountPinSetup,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set up a PIN for an account."""
    # Verify account access
    account = await verify_account_access(account_id, current_user, db)

    # Check if PIN is already set
    if account.pin_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account PIN already configured. Use change-pin to modify."
        )

    # Hash and store the PIN
    account.pin_hash = get_password_hash(pin_data.pin)
    await db.commit()
    await db.refresh(account)

    return {"message": "Account PIN configured successfully"}


@router.post("/{account_id}/change-pin")
async def change_account_pin(
    account_id: int,
    pin_data: AccountPinChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the PIN for an account."""
    # Verify account access
    account = await verify_account_access(account_id, current_user, db)

    # Check if PIN is configured
    if not account.pin_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account PIN not configured. Use setup-pin first."
        )

    # Verify current PIN
    if not verify_password(pin_data.current_pin, account.pin_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current PIN is incorrect")

    # Update to new PIN
    account.pin_hash = get_password_hash(pin_data.new_pin)
    await db.commit()
    await db.refresh(account)

    return {"message": "Account PIN changed successfully"}


@router.post("/{account_id}/verify-pin")
async def verify_account_pin_endpoint(
    account_id: int,
    pin_data: AccountPinVerification,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify the PIN for an account."""
    # Verify account access
    account = await verify_account_access(account_id, current_user, db)

    # Verify the PIN
    if not await verify_account_pin(account, pin_data.pin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="PIN verification failed")

    return {"message": "PIN verification successful"}


@router.post("/{account_id}/deposit", response_model=BalanceUpdate)
async def deposit(
    account_id: int,
    deposit_data: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BalanceUpdate:
    # Verify account access
    account = await verify_account_access(account_id, current_user, db)

    # Verify PIN before allowing deposit
    if not await verify_account_pin(account, deposit_data.pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="PIN verification failed. Deposit not allowed."
        )

    # Validate amount
    if deposit_data.amount_cents < settings.MIN_DEPOSIT_AMOUNT_CENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"Amount must be at least " f"${settings.MIN_DEPOSIT_AMOUNT_CENTS / 100:.2f}"),
        )

    if deposit_data.amount_cents > settings.MAX_DEPOSIT_AMOUNT_CENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"Amount cannot exceed " f"${settings.MAX_DEPOSIT_AMOUNT_CENTS / 100:.2f}"),
        )

    # Check for existing transaction with same idempotency key
    existing_transaction = await db.execute(
        select(Transaction).where(Transaction.idempotency_key == deposit_data.idempotency_key)
    )
    existing = existing_transaction.scalar_one_or_none()
    if existing:
        # Return existing transaction info
        return BalanceUpdate(
            new_balance_cents=account.balance_cents,  # type: ignore[arg-type]
            transaction=TransactionResponse(
                id=int(existing.id),
                amount_cents=existing.amount_cents,  # type: ignore[arg-type]
                transaction_type=str(existing.transaction_type),
                idempotency_key=str(existing.idempotency_key),
                account_id=int(existing.account_id),
                created_at=existing.created_at,  # type: ignore[arg-type]
            ),
        )

    # Create transaction and update balance atomically
    new_transaction = Transaction(
        amount_cents=Decimal(deposit_data.amount_cents),
        transaction_type=deposit_data.transaction_type,
        idempotency_key=deposit_data.idempotency_key,
        account_id=account_id,
    )

    db.add(new_transaction)

    # Update account balance
    current_balance = float(account.balance_cents) if account.balance_cents else 0.0
    new_balance = current_balance + float(deposit_data.amount_cents)
    account.balance_cents = new_balance
    account.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(new_transaction)
    await db.refresh(account)

    return BalanceUpdate(
        new_balance_cents=account.balance_cents,  # type: ignore[arg-type]
        transaction=TransactionResponse(
            id=int(new_transaction.id),
            amount_cents=new_transaction.amount_cents,  # type: ignore[arg-type]
            transaction_type=str(new_transaction.transaction_type),
            idempotency_key=str(new_transaction.idempotency_key),
            account_id=int(new_transaction.account_id),
            created_at=new_transaction.created_at,  # type: ignore[arg-type]
        ),
    )


@router.get("/{account_id}/transactions", response_model=TransactionList)
async def get_transactions(
    account_id: int,
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionList:
    # Verify account access
    await verify_account_access(account_id, current_user, db)

    # Build query
    query = select(Transaction).where(Transaction.account_id == account_id)

    # Apply cursor pagination
    if cursor:
        try:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                query = query.where(Transaction.id < last_id)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cursor")

    # Order by id descending for consistent pagination
    query = query.order_by(desc(Transaction.id)).limit(limit + 1)

    result = await db.execute(query)
    transactions = result.scalars().all()

    # Check if there are more results
    has_more = len(transactions) > limit
    if has_more:
        transactions = transactions[:-1]  # Remove the extra item

    # Create next cursor
    next_cursor = None
    if has_more and transactions:
        cursor_data = {"last_id": transactions[-1].id}
        next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

    return TransactionList(
        transactions=[
            TransactionResponse(
                id=t.id,  # type: ignore[arg-type]
                amount_cents=t.amount_cents,  # type: ignore[arg-type]
                transaction_type=t.transaction_type,  # type: ignore[arg-type]
                idempotency_key=t.idempotency_key,  # type: ignore[arg-type]
                account_id=t.account_id,  # type: ignore[arg-type]
                created_at=t.created_at,  # type: ignore[arg-type]
            )
            for t in transactions
        ],
        next_cursor=next_cursor,
        has_more=has_more,
    )


@router.post("/transfer")
async def transfer_between_accounts(
    transfer_data: TransferRequest,
    pin_verification: AccountPinVerification,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transfer money between a child's checking and savings accounts."""

    # Verify source account access and PIN
    source_account = await verify_account_access(transfer_data.source_account_id, current_user, db)
    if not await verify_account_pin(source_account, pin_verification.pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="PIN verification failed. Transfer not allowed."
        )

    # Verify destination account access
    dest_account = await verify_account_access(transfer_data.destination_account_id, current_user, db)

    # Validate accounts belong to same child
    if source_account.child_id != dest_account.child_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Can only transfer between accounts of the same child"
        )

    # Validate transfer amount
    if transfer_data.amount_cents <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transfer amount must be positive")

    # Check sufficient funds in source account
    source_current_balance = float(source_account.balance_cents) if source_account.balance_cents else 0.0
    if source_current_balance < float(transfer_data.amount_cents):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Insufficient funds. Available: {source_current_balance}, " f"Required: {transfer_data.amount_cents}"
            ),
        )

    # Create transfer transaction (debit from source)
    debit_transaction = Transaction(
        account_id=source_account.id,
        amount_cents=-transfer_data.amount_cents,  # Negative for debit
        transaction_type="transfer_out",
        idempotency_key=f"transfer_{transfer_data.idempotency_key}_debit",
    )

    # Create transfer transaction (credit to destination)
    credit_transaction = Transaction(
        account_id=dest_account.id,
        amount_cents=transfer_data.amount_cents,  # Positive for credit
        transaction_type="transfer_in",
        idempotency_key=f"transfer_{transfer_data.idempotency_key}_credit",
    )

    # Update account balances atomically
    source_current_balance = float(source_account.balance_cents) if source_account.balance_cents else 0.0
    dest_current_balance = float(dest_account.balance_cents) if dest_account.balance_cents else 0.0

    source_account.balance_cents = source_current_balance - float(transfer_data.amount_cents)
    source_account.updated_at = datetime.now(timezone.utc)

    dest_account.balance_cents = dest_current_balance + float(transfer_data.amount_cents)
    dest_account.updated_at = datetime.now(timezone.utc)

    # Add all changes in single commit
    db.add(debit_transaction)
    db.add(credit_transaction)
    await db.commit()

    return {
        "message": "Transfer completed successfully",
        "transfer_id": f"transfer_{transfer_data.idempotency_key}",
        "amount_cents": transfer_data.amount_cents,
        "source_account_balance": source_account.balance_cents,
        "destination_account_balance": dest_account.balance_cents,
    }
