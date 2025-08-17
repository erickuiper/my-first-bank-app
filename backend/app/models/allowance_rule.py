from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AllowanceRule(Base):
    __tablename__ = "allowance_rules"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    base_amount_cents = Column(Integer, nullable=False)  # Base allowance amount in cents
    frequency = Column(String(20), default="weekly")  # weekly, bi-weekly, monthly
    pay_day = Column(String(20), default="friday")  # day of week for payment
    active = Column(Boolean, default=True)  # whether the rule is active
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    child = relationship("Child", back_populates="allowance_rules")
    chores = relationship("Chore", back_populates="allowance_rule")
