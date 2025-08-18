from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Account, AllowanceRule, Child, Chore, ChoreCompletion, User

router = APIRouter()


@router.get("/dashboard")
async def get_parental_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a comprehensive parental dashboard with children, accounts, chores, and allowances."""

    # Get all children for the current user
    children_result = await db.execute(select(Child).where(Child.parent_id == current_user.id))
    children = children_result.scalars().all()

    dashboard_data = {
        "parent_id": current_user.id,
        "parent_email": current_user.email,
        "children": [],
        "summary": {
            "total_children": len(children),
            "total_accounts": 0,
            "total_chores": 0,
            "total_allowance_rules": 0,
        },
    }

    for child in children:
        # Get child's accounts
        accounts_result = await db.execute(select(Account).where(Account.child_id == child.id))
        accounts = accounts_result.scalars().all()

        # Get child's allowance rules
        allowance_rules_result = await db.execute(select(AllowanceRule).where(AllowanceRule.child_id == child.id))
        allowance_rules = allowance_rules_result.scalars().all()

        # Get child's chores
        chores_result = await db.execute(select(Chore).where(Chore.child_id == child.id))
        chores = chores_result.scalars().all()

        # Get chore completions for this week
        week_start = datetime.now(timezone.utc) - timedelta(days=datetime.now(timezone.utc).weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        chore_summaries = []
        for chore in chores:
            completions_result = await db.execute(
                select(func.count(ChoreCompletion.id)).where(
                    and_(ChoreCompletion.chore_id == chore.id, ChoreCompletion.completed_at >= week_start)
                )
            )
            completed_this_week = completions_result.scalar() or 0

            chore_summaries.append(
                {
                    "id": chore.id,
                    "name": chore.name,
                    "expected_per_week": chore.expected_per_week,
                    "completed_this_week": completed_this_week,
                    "missed_this_week": max(0, chore.expected_per_week - completed_this_week),
                    "penalty_cents": chore.penalty_cents,
                    "active": chore.active,
                }
            )

        # Calculate total penalties for the week
        total_penalty_cents = sum(c["missed_this_week"] * c["penalty_cents"] for c in chore_summaries)

        child_data = {
            "id": child.id,
            "name": child.name,
            "birthdate": child.birthdate.isoformat() if child.birthdate else None,
            "accounts": [
                {
                    "id": account.id,
                    "account_type": account.account_type,
                    "balance_cents": float(account.balance_cents),
                    "pin_configured": bool(account.pin_hash),
                    "created_at": account.created_at.isoformat(),
                }
                for account in accounts
            ],
            "allowance_rules": [
                {
                    "id": rule.id,
                    "base_amount_cents": rule.base_amount_cents,
                    "frequency": rule.frequency,
                    "pay_day": rule.pay_day,
                    "active": rule.active,
                }
                for rule in allowance_rules
            ],
            "chores": chore_summaries,
            "weekly_summary": {
                "total_chores": len(chores),
                "total_completed": sum(c["completed_this_week"] for c in chore_summaries),
                "total_missed": sum(c["missed_this_week"] for c in chore_summaries),
                "total_penalty_cents": total_penalty_cents,
            },
        }

        dashboard_data["children"].append(child_data)
        dashboard_data["summary"]["total_accounts"] += len(accounts)
        dashboard_data["summary"]["total_chores"] += len(chores)
        dashboard_data["summary"]["total_allowance_rules"] += len(allowance_rules)

    return dashboard_data


@router.get("/children/{child_id}/summary")
async def get_child_summary(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a detailed summary for a specific child."""

    # Verify the child belongs to the current user
    child = await db.execute(select(Child).where(and_(Child.id == child_id, Child.parent_id == current_user.id)))
    child = child.scalar_one_or_none()

    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found or access denied")

    # Get child's accounts
    accounts_result = await db.execute(select(Account).where(Account.child_id == child_id))
    accounts = accounts_result.scalars().all()

    # Get child's allowance rules
    allowance_rules_result = await db.execute(select(AllowanceRule).where(AllowanceRule.child_id == child_id))
    allowance_rules = allowance_rules_result.scalars().all()

    # Get child's chores
    chores_result = await db.execute(select(Chore).where(Chore.child_id == child_id))
    chores = chores_result.scalars().all()

    # Get chore completions for this week
    week_start = datetime.now(timezone.utc) - timedelta(days=datetime.now(timezone.utc).weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    chore_summaries = []
    for chore in chores:
        completions_result = await db.execute(
            select(func.count(ChoreCompletion.id)).where(
                and_(ChoreCompletion.chore_id == chore.id, ChoreCompletion.completed_at >= week_start)
            )
        )
        completed_this_week = completions_result.scalar() or 0

        chore_summaries.append(
            {
                "id": chore.id,
                "name": chore.name,
                "expected_per_week": chore.expected_per_week,
                "completed_this_week": completed_this_week,
                "missed_this_week": max(0, chore.expected_per_week - completed_this_week),
                "penalty_cents": chore.penalty_cents,
                "active": chore.active,
            }
        )

    # Calculate total penalties for the week
    total_penalty_cents = sum(c["missed_this_week"] * c["penalty_cents"] for c in chore_summaries)

    return {
        "child": {
            "id": child.id,
            "name": child.name,
            "birthdate": child.birthdate.isoformat() if child.birthdate else None,
        },
        "accounts": [
            {
                "id": account.id,
                "account_type": account.account_type,
                "balance_cents": float(account.balance_cents),
                "pin_configured": bool(account.pin_hash),
                "created_at": account.created_at.isoformat(),
            }
            for account in accounts
        ],
        "allowance_rules": [
            {
                "id": rule.id,
                "base_amount_cents": rule.base_amount_cents,
                "frequency": rule.frequency,
                "pay_day": rule.pay_day,
                "active": rule.active,
            }
            for rule in allowance_rules
        ],
        "chores": chore_summaries,
        "weekly_summary": {
            "week_start": week_start.isoformat(),
            "total_chores": len(chores),
            "total_completed": sum(c["completed_this_week"] for c in chore_summaries),
            "total_missed": sum(c["missed_this_week"] for c in chore_summaries),
            "total_penalty_cents": total_penalty_cents,
        },
    }
