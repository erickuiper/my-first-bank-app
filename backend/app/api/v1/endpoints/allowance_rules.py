from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Account, AllowanceRule, Child, Transaction, User
from app.schemas import AllowanceRuleBase, AllowanceRuleResponse, AllowanceRuleUpdate

router = APIRouter()


@router.post("/children/{child_id}/allowance-rules", response_model=AllowanceRuleResponse)
async def create_allowance_rule(
    child_id: int,
    allowance_rule: AllowanceRuleBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an allowance rule for a child."""
    # Verify the child belongs to the current user
    child = await db.execute(select(Child).where(and_(Child.id == child_id, Child.parent_id == current_user.id)))
    child = child.scalar_one_or_none()

    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found or access denied")

    # Create the allowance rule
    db_allowance_rule = AllowanceRule(
        child_id=child_id,
        base_amount_cents=allowance_rule.base_amount_cents,
        frequency=allowance_rule.frequency,
        pay_day=allowance_rule.pay_day,
        active=allowance_rule.active,
    )

    db.add(db_allowance_rule)
    await db.commit()
    await db.refresh(db_allowance_rule)

    return db_allowance_rule


@router.get("/children/{child_id}/allowance-rules", response_model=List[AllowanceRuleResponse])
async def get_allowance_rules(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all allowance rules for a child."""
    # Verify the child belongs to the current user
    child = await db.execute(select(Child).where(and_(Child.id == child_id, Child.parent_id == current_user.id)))
    child = child.scalar_one_or_none()

    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found or access denied")

    # Get allowance rules
    result = await db.execute(select(AllowanceRule).where(AllowanceRule.child_id == child_id))
    allowance_rules = result.scalars().all()

    return allowance_rules


@router.put("/allowance-rules/{rule_id}", response_model=AllowanceRuleResponse)
async def update_allowance_rule(
    rule_id: int,
    allowance_rule: AllowanceRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an allowance rule."""
    # Get the allowance rule and verify ownership
    result = await db.execute(
        select(AllowanceRule).options(selectinload(AllowanceRule.child)).where(AllowanceRule.id == rule_id)
    )
    db_allowance_rule = result.scalar_one_or_none()

    if not db_allowance_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allowance rule not found")

    if db_allowance_rule.child.parent_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Update fields
    update_data = allowance_rule.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_allowance_rule, field, value)

    db_allowance_rule.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(db_allowance_rule)

    return db_allowance_rule


@router.delete("/allowance-rules/{rule_id}")
async def delete_allowance_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an allowance rule."""
    # Get the allowance rule and verify ownership
    result = await db.execute(
        select(AllowanceRule).options(selectinload(AllowanceRule.child)).where(AllowanceRule.id == rule_id)
    )
    db_allowance_rule = result.scalar_one_or_none()

    if not db_allowance_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allowance rule not found")

    if db_allowance_rule.child.parent_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    await db.delete(db_allowance_rule)
    await db.commit()

    return {"message": "Allowance rule deleted successfully"}


@router.post("/children/{child_id}/allowance-payout")
async def process_allowance_payout(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process allowance payout for a child based on completed chores."""
    # Verify the child belongs to the current user
    child = await db.execute(select(Child).where(and_(Child.id == child_id, Child.parent_id == current_user.id)))
    child = child.scalar_one_or_none()

    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found or access denied")

    # Get active allowance rule
    result = await db.execute(
        select(AllowanceRule).where(and_(AllowanceRule.child_id == child_id, AllowanceRule.active))
    )
    allowance_rule = result.scalar_one_or_none()

    if not allowance_rule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No active allowance rule found for this child"
        )

    # TODO: Implement chore completion calculation logic
    # For now, just pay the base amount
    earned_amount_cents = allowance_rule.base_amount_cents

    # Get the child's checking account
    result = await db.execute(
        select(Account).where(and_(Account.child_id == child_id, Account.account_type == "checking"))
    )
    checking_account = result.scalar_one_or_none()

    if not checking_account:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Checking account not found")

    # Create allowance transaction
    allowance_transaction = Transaction(
        account_id=checking_account.id,
        amount_cents=earned_amount_cents,
        transaction_type="allowance",
        idempotency_key=f"allowance_{child_id}_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
    )

    db.add(allowance_transaction)

    # Update account balance
    checking_account.balance_cents += earned_amount_cents
    checking_account.updated_at = datetime.now(timezone.utc)

    await db.commit()

    return {
        "message": "Allowance payout processed successfully",
        "amount_cents": earned_amount_cents,
        "new_balance_cents": checking_account.balance_cents,
        "transaction_id": allowance_transaction.id,
    }
