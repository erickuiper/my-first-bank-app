from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_type = Column(String, nullable=False)  # "checking" or "savings"
    balance_cents = Column(Numeric(20, 0), default=0, nullable=False)  # Store in cents
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    child = relationship("Child", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
