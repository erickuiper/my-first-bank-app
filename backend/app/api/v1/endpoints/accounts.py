from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.child import Child
from app.schemas.account import AccountResponse, BalanceUpdate
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionList
from app.core.config import settings
from typing import Optional
from decimal import Decimal
import base64
import json

router = APIRouter()

async def verify_account_access(
    account_id: int,
    current_user: User,
    db: AsyncSession
) -> Account:
    # Verify account belongs to current user's child
    result = await db.execute(
        select(Account)
        .join(Child)
        .where(
            and_(
                Account.id == account_id,
                Child.parent_id == current_user.id
            )
        )
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account

@router.post("/{account_id}/deposit", response_model=BalanceUpdate)
async def deposit(
    account_id: int,
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify account access
    account = await verify_account_access(account_id, current_user, db)
    
    # Validate amount
    if transaction_data.amount_cents < settings.MIN_DEPOSIT_AMOUNT_CENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Amount must be at least ${settings.MIN_DEPOSIT_AMOUNT_CENTS / 100:.2f}"
        )
    
    if transaction_data.amount_cents > settings.MAX_DEPOSIT_AMOUNT_CENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Amount cannot exceed ${settings.MAX_DEPOSIT_AMOUNT_CENTS / 100:.2f}"
        )
    
    # Check for existing transaction with same idempotency key
    existing_transaction = await db.execute(
        select(Transaction).where(Transaction.idempotency_key == transaction_data.idempotency_key)
    )
    existing = existing_transaction.scalar_one_or_none()
    if existing:
        # Return existing transaction info
        return BalanceUpdate(
            new_balance_cents=account.balance_cents,
            transaction=TransactionResponse(
                id=existing.id,
                amount_cents=existing.amount_cents,
                transaction_type=existing.transaction_type,
                idempotency_key=existing.idempotency_key,
                account_id=existing.account_id,
                created_at=existing.created_at
            )
        )
    
    # Create transaction and update balance atomically
    new_transaction = Transaction(
        amount_cents=Decimal(transaction_data.amount_cents),
        transaction_type=transaction_data.transaction_type,
        idempotency_key=transaction_data.idempotency_key,
        account_id=account_id
    )
    
    db.add(new_transaction)
    
    # Update account balance
    account.balance_cents += Decimal(transaction_data.amount_cents)
    
    await db.commit()
    await db.refresh(new_transaction)
    await db.refresh(account)
    
    return BalanceUpdate(
        new_balance_cents=account.balance_cents,
        transaction=TransactionResponse(
            id=new_transaction.id,
            amount_cents=new_transaction.amount_cents,
            transaction_type=new_transaction.transaction_type,
            idempotency_key=new_transaction.idempotency_key,
            account_id=new_transaction.account_id,
            created_at=new_transaction.created_at
        )
    )

@router.get("/{account_id}/transactions", response_model=TransactionList)
async def get_transactions(
    account_id: int,
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify account access
    account = await verify_account_access(account_id, current_user, db)
    
    # Build query
    query = select(Transaction).where(Transaction.account_id == account_id)
    
    # Apply cursor pagination
    if cursor:
        try:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            last_id = cursor_data.get("last_id")
            if last_id:
                query = query.where(Transaction.id < last_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cursor"
            )
    
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
                id=t.id,
                amount_cents=t.amount_cents,
                transaction_type=t.transaction_type,
                idempotency_key=t.idempotency_key,
                account_id=t.account_id,
                created_at=t.created_at
            ) for t in transactions
        ],
        next_cursor=next_cursor,
        has_more=has_more
    )
