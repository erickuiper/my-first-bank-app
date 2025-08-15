from pydantic import BaseModel, ConfigDict
from typing import List, TYPE_CHECKING, Annotated, Optional
from datetime import datetime
from decimal import Decimal

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
