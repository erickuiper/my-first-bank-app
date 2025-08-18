from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# Import directly to avoid forward reference issues
from .transaction import TransactionResponse


class AccountBase(BaseModel):
    account_type: str
    balance_cents: Decimal


class AccountResponse(AccountBase):
    id: int
    child_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AccountWithTransactions(AccountResponse):
    transactions: List[TransactionResponse] = []


class BalanceUpdate(BaseModel):
    new_balance_cents: Decimal
    transaction: TransactionResponse


class AccountPinSetup(BaseModel):
    pin: str = Field(..., min_length=4, max_length=6, description="4-6 digit PIN for parental access")


class AccountPinVerification(BaseModel):
    pin: str = Field(..., min_length=4, max_length=6, description="PIN to verify parental access")


class AccountPinChange(BaseModel):
    current_pin: str = Field(..., min_length=4, max_length=6, description="Current PIN")
    new_pin: str = Field(..., min_length=4, max_length=6, description="New PIN")
