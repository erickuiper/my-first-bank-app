from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChoreCompletionBase(BaseModel):
    notes: Optional[str] = Field(None, description="Optional notes about completion")


class ChoreCompletionCreate(ChoreCompletionBase):
    chore_id: int = Field(..., description="ID of the chore being completed")


class ChoreCompletionResponse(ChoreCompletionBase):
    id: int
    chore_id: int
    completed_at: datetime
    verified_by: Optional[int] = Field(None, description="ID of the user who verified completion")
    created_at: datetime

    class Config:
        from_attributes = True
