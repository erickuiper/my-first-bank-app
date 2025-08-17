from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Child, Chore, ChoreCompletion, User
from app.schemas import ChoreBase, ChoreCompletionBase, ChoreCompletionResponse, ChoreResponse, ChoreUpdate

router = APIRouter()


@router.post("/children/{child_id}/chores", response_model=ChoreResponse)
async def create_chore(
    child_id: int,
    chore: ChoreBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a chore for a child."""
    # Verify the child belongs to the current user
    child = await db.execute(select(Child).where(and_(Child.id == child_id, Child.parent_id == current_user.id)))
    child = child.scalar_one_or_none()

    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found or access denied")

    # Create the chore
    db_chore = Chore(
        child_id=child_id,
        allowance_rule_id=chore.allowance_rule_id,
        name=chore.name,
        description=chore.description,
        expected_per_week=chore.expected_per_week,
        penalty_cents=chore.penalty_cents,
        active=chore.active,
    )

    db.add(db_chore)
    await db.commit()
    await db.refresh(db_chore)

    return db_chore


@router.get("/children/{child_id}/chores", response_model=List[ChoreResponse])
async def get_chores(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all chores for a child."""
    # Verify the child belongs to the current user
    child = await db.execute(select(Child).where(and_(Child.id == child_id, Child.parent_id == current_user.id)))
    child = child.scalar_one_or_none()

    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found or access denied")

    # Get chores
    result = await db.execute(select(Chore).where(Chore.child_id == child_id))
    chores = result.scalars().all()

    return chores


@router.put("/chores/{chore_id}", response_model=ChoreResponse)
async def update_chore(
    chore_id: int,
    chore: ChoreUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a chore."""
    # Get the chore and verify ownership
    result = await db.execute(select(Chore).options(selectinload(Chore.child)).where(Chore.id == chore_id))
    db_chore = result.scalar_one_or_none()

    if not db_chore:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chore not found")

    if db_chore.child.parent_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Update fields
    update_data = chore.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_chore, field, value)

    db_chore.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(db_chore)

    return db_chore


@router.delete("/chores/{chore_id}")
async def delete_chore(
    chore_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a chore."""
    # Get the chore and verify ownership
    result = await db.execute(select(Chore).options(selectinload(Chore.child)).where(Chore.id == chore_id))
    db_chore = result.scalar_one_or_none()

    if not db_chore:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chore not found")

    if db_chore.child.parent_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    await db.delete(db_chore)
    await db.commit()

    return {"message": "Chore deleted successfully"}


@router.post("/chores/{chore_id}/complete", response_model=ChoreCompletionResponse)
async def complete_chore(
    chore_id: int,
    completion: ChoreCompletionBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a chore as completed."""
    # Get the chore and verify ownership
    result = await db.execute(select(Chore).options(selectinload(Chore.child)).where(Chore.id == chore_id))
    db_chore = result.scalar_one_or_none()

    if not db_chore:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chore not found")

    if db_chore.child.parent_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Create chore completion
    db_completion = ChoreCompletion(
        chore_id=chore_id,
        verified_by=current_user.id,
        notes=completion.notes,
    )

    db.add(db_completion)
    await db.commit()
    await db.refresh(db_completion)

    return db_completion


@router.get("/children/{child_id}/chore-summary")
async def get_chore_summary(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a summary of chores and completions for a child."""
    # Verify the child belongs to the current user
    child = await db.execute(select(Child).where(and_(Child.id == child_id, Child.parent_id == current_user.id)))
    child = child.scalar_one_or_none()

    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found or access denied")

    # Get chores with completion counts for the current week
    week_start = datetime.now(timezone.utc) - timedelta(days=datetime.now(timezone.utc).weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    result = await db.execute(
        select(
            Chore.id,
            Chore.name,
            Chore.expected_per_week,
            Chore.penalty_cents,
            func.count(ChoreCompletion.id).label("completed_this_week"),
        )
        .outerjoin(
            ChoreCompletion, and_(ChoreCompletion.chore_id == Chore.id, ChoreCompletion.completed_at >= week_start)
        )
        .where(Chore.child_id == child_id)
        .group_by(Chore.id, Chore.name, Chore.expected_per_week, Chore.penalty_cents)
    )

    chore_summaries = []
    total_penalty_cents = 0

    for row in result:
        completed = row.completed_this_week or 0
        missed = max(0, row.expected_per_week - completed)
        penalty = missed * row.penalty_cents

        chore_summaries.append(
            {
                "chore_id": row.id,
                "name": row.name,
                "expected_per_week": row.expected_per_week,
                "completed_this_week": completed,
                "missed_this_week": missed,
                "penalty_cents": penalty,
            }
        )

        total_penalty_cents += penalty

    return {
        "child_id": child_id,
        "week_start": week_start.isoformat(),
        "chores": chore_summaries,
        "total_penalty_cents": total_penalty_cents,
        "summary": {
            "total_chores": len(chore_summaries),
            "total_completed": sum(c["completed_this_week"] for c in chore_summaries),
            "total_missed": sum(c["missed_this_week"] for c in chore_summaries),
        },
    }
