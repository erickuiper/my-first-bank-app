from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChoreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the chore")
    description: Optional[str] = Field(None, description="Description of the chore")
    expected_per_week: int = Field(default=1, ge=1, description="How many times per week this chore should be done")
    penalty_cents: int = Field(default=0, ge=0, description="Penalty amount in cents for missed chores")
    active: bool = Field(default=True, description="Whether the chore is active")
    allowance_rule_id: Optional[int] = Field(None, description="ID of the allowance rule this chore is associated with")


class ChoreCreate(ChoreBase):
    child_id: int = Field(..., description="ID of the child this chore is for")


class ChoreUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the chore")
    description: Optional[str] = Field(None, description="Description of the chore")
    expected_per_week: Optional[int] = Field(
        None, ge=1, description="How many times per week this chore should be done"
    )
    penalty_cents: Optional[int] = Field(None, ge=0, description="Penalty amount in cents for missed chores")
    active: Optional[bool] = Field(None, description="Whether the chore is active")
    allowance_rule_id: Optional[int] = Field(None, description="ID of the allowance rule this chore is associated with")


class ChoreResponse(ChoreBase):
    id: int
    child_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
