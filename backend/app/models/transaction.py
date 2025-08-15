from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount_cents = Column(Numeric(20, 0), nullable=False)  # Store in cents
    transaction_type = Column(String, nullable=False, default="deposit")
    idempotency_key = Column(String, nullable=False, unique=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    account = relationship("Account", back_populates="transactions")

    # Ensure idempotency key is unique
    __table_args__ = (UniqueConstraint("idempotency_key"),)
