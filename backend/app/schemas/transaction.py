from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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


class TransferRequest(BaseModel):
    source_account_id: int = Field(..., description="ID of source account (checking)")
    destination_account_id: int = Field(..., description="ID of destination account (savings)")
    amount_cents: int = Field(..., gt=0, description="Amount to transfer in cents")
    idempotency_key: str = Field(..., description="Unique key to prevent duplicate transfers")


class DepositRequest(BaseModel):
    amount_cents: int = Field(..., ge=0, description="Amount to deposit in cents")
    transaction_type: str = Field(default="deposit", description="Type of transaction")
    idempotency_key: str = Field(..., description="Unique key to prevent duplicate deposits")
    pin: str = Field(..., min_length=4, max_length=6, description="PIN for account verification")
