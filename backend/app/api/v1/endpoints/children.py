from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.account import Account
from app.models.child import Child
from app.models.user import User
from app.schemas.account import AccountResponse
from app.schemas.child import ChildCreate, ChildResponse, ChildWithAccounts

router = APIRouter()


@router.post("/", response_model=ChildWithAccounts)
async def create_child(
    child_data: ChildCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChildWithAccounts:
    # Create child
    db_child = Child(name=child_data.name, birthdate=child_data.birthdate, parent_id=current_user.id)

    db.add(db_child)
    await db.commit()
    await db.refresh(db_child)

    # Create checking and savings accounts
    checking_account = Account(account_type="checking", balance_cents=Decimal(0), child_id=db_child.id)

    savings_account = Account(account_type="savings", balance_cents=Decimal(0), child_id=db_child.id)

    db.add_all([checking_account, savings_account])
    await db.commit()
    await db.refresh(checking_account)
    await db.refresh(savings_account)

    # Return child with accounts
    return ChildWithAccounts(
        id=int(db_child.id),
        name=str(db_child.name),
        birthdate=db_child.birthdate,  # type: ignore[arg-type]
        parent_id=int(db_child.parent_id),
        created_at=db_child.created_at,  # type: ignore[arg-type]
        accounts=[
            AccountResponse(
                id=int(checking_account.id),
                account_type=str(checking_account.account_type),
                balance_cents=checking_account.balance_cents,  # type: ignore[arg-type]
                child_id=int(checking_account.child_id),
                created_at=checking_account.created_at,  # type: ignore[arg-type]
                updated_at=checking_account.updated_at,  # type: ignore[arg-type]
            ),
            AccountResponse(
                id=int(savings_account.id),
                account_type=str(savings_account.account_type),
                balance_cents=savings_account.balance_cents,  # type: ignore[arg-type]
                child_id=int(savings_account.child_id),
                created_at=savings_account.created_at,  # type: ignore[arg-type]
                updated_at=savings_account.updated_at,  # type: ignore[arg-type]
            ),
        ],
    )


@router.get("/", response_model=List[ChildResponse])
async def list_children(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> List[ChildResponse]:
    result = await db.execute(select(Child).where(Child.parent_id == current_user.id))
    children = result.scalars().all()
    return list(children)
