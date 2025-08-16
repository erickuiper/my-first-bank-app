import base64
import json
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.account import Account
from app.models.child import Child
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.account import BalanceUpdate
from app.schemas.transaction import TransactionCreate, TransactionList, TransactionResponse

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


@router.post("/{account_id}/deposit", response_model=BalanceUpdate)
async def deposit(
    account_id: int,
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BalanceUpdate:
    # Verify account access
    account = await verify_account_access(account_id, current_user, db)

    # Validate amount
    if transaction_data.amount_cents < settings.MIN_DEPOSIT_AMOUNT_CENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"Amount must be at least " f"${settings.MIN_DEPOSIT_AMOUNT_CENTS / 100:.2f}"),
        )

    if transaction_data.amount_cents > settings.MAX_DEPOSIT_AMOUNT_CENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"Amount cannot exceed " f"${settings.MAX_DEPOSIT_AMOUNT_CENTS / 100:.2f}"),
        )

    # Check for existing transaction with same idempotency key
    existing_transaction = await db.execute(
        select(Transaction).where(Transaction.idempotency_key == transaction_data.idempotency_key)
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
        amount_cents=Decimal(transaction_data.amount_cents),
        transaction_type=transaction_data.transaction_type,
        idempotency_key=transaction_data.idempotency_key,
        account_id=account_id,
    )

    db.add(new_transaction)

    # Update account balance
    account.balance_cents += Decimal(transaction_data.amount_cents)  # type: ignore[assignment]

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
