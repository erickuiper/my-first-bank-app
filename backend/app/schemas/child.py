from datetime import date, datetime
from typing import List

from pydantic import BaseModel, ConfigDict

# Import directly to avoid forward reference issues
from .account import AccountResponse


class ChildBase(BaseModel):
    name: str
    birthdate: date


class ChildCreate(ChildBase):
    pass


class ChildResponse(ChildBase):
    id: int
    parent_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChildWithAccounts(ChildResponse):
    accounts: List[AccountResponse] = []

    model_config = ConfigDict(from_attributes=True)
