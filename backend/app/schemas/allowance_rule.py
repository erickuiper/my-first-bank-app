from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AllowanceRuleBase(BaseModel):
    base_amount_cents: int = Field(..., gt=0, description="Base allowance amount in cents")
    frequency: str = Field(default="weekly", description="Payment frequency: weekly, bi-weekly, monthly")
    pay_day: str = Field(default="friday", description="Day of week for payment")
    active: bool = Field(default=True, description="Whether the rule is active")


class AllowanceRuleCreate(AllowanceRuleBase):
    child_id: int = Field(..., description="ID of the child this rule applies to")


class AllowanceRuleUpdate(BaseModel):
    base_amount_cents: Optional[int] = Field(None, gt=0, description="Base allowance amount in cents")
    frequency: Optional[str] = Field(None, description="Payment frequency: weekly, bi-weekly, monthly")
    pay_day: Optional[str] = Field(None, description="Day of week for payment")
    active: Optional[bool] = Field(None, description="Whether the rule is active")


class AllowanceRuleResponse(AllowanceRuleBase):
    id: int
    child_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
