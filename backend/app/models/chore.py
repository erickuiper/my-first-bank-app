from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Chore(Base):
    __tablename__ = "chores"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    allowance_rule_id = Column(Integer, ForeignKey("allowance_rules.id"), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    expected_per_week = Column(Integer, default=1)  # how many times per week this chore should be done
    penalty_cents = Column(Integer, default=0)  # penalty amount in cents for missed chores
    active = Column(Boolean, default=True)  # whether the chore is active
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    child = relationship("Child", back_populates="chores")
    allowance_rule = relationship("AllowanceRule", back_populates="chores")
    completions = relationship("ChoreCompletion", back_populates="chore")
