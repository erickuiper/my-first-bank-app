from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    amount_cents: Decimal
    transaction_type: str = "deposit"
    idempotency_key: str


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    account_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionList(BaseModel):
    transactions: list[TransactionResponse]
    next_cursor: Optional[str] = None
    has_more: bool
