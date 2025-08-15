from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.child import Child
from app.models.account import Account
from app.schemas.child import ChildCreate, ChildResponse, ChildWithAccounts
from app.schemas.account import AccountResponse
from typing import List
from decimal import Decimal

router = APIRouter()

@router.post("/", response_model=ChildWithAccounts)
async def create_child(
    child_data: ChildCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Create child
    db_child = Child(
        name=child_data.name,
        birthdate=child_data.birthdate,
        parent_id=current_user.id
    )
    
    db.add(db_child)
    await db.commit()
    await db.refresh(db_child)
    
    # Create checking and savings accounts
    checking_account = Account(
        account_type="checking",
        balance_cents=Decimal(0),
        child_id=db_child.id
    )
    
    savings_account = Account(
        account_type="savings",
        balance_cents=Decimal(0),
        child_id=db_child.id
    )
    
    db.add_all([checking_account, savings_account])
    await db.commit()
    await db.refresh(checking_account)
    await db.refresh(savings_account)
    
    # Return child with accounts
    return ChildWithAccounts(
        id=db_child.id,
        name=db_child.name,
        birthdate=db_child.birthdate,
        parent_id=db_child.parent_id,
        created_at=db_child.created_at,
        accounts=[
            AccountResponse(
                id=checking_account.id,
                account_type=checking_account.account_type,
                balance_cents=checking_account.balance_cents,
                child_id=checking_account.child_id,
                created_at=checking_account.created_at,
                updated_at=checking_account.updated_at
            ),
            AccountResponse(
                id=savings_account.id,
                account_type=savings_account.account_type,
                balance_cents=savings_account.balance_cents,
                child_id=savings_account.child_id,
                created_at=savings_account.created_at,
                updated_at=savings_account.updated_at
            )
        ]
    )

@router.get("/", response_model=List[ChildResponse])
async def list_children(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Child).where(Child.parent_id == current_user.id)
    )
    children = result.scalars().all()
    return children
