from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ChoreCompletion(Base):
    __tablename__ = "chore_completions"

    id = Column(Integer, primary_key=True, index=True)
    chore_id = Column(Integer, ForeignKey("chores.id"), nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # parent verification
    notes = Column(Text)  # optional notes about completion
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chore = relationship("Chore", back_populates="completions")
    verifier = relationship("User", back_populates="chore_verifications")
