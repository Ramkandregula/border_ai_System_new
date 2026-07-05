from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum
from datetime import datetime


class QueuePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class QueueStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"


class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)
    
    # Queue management
    queue_number = Column(Integer, nullable=False)
    priority = Column(SQLEnum(QueuePriority), default=QueuePriority.NORMAL, nullable=False)
    status = Column(SQLEnum(QueueStatus), default=QueueStatus.WAITING, nullable=False)
    
    # Processing
    assigned_officer = Column(String(255), nullable=True)
    processing_start = Column(DateTime(timezone=True), nullable=True)
    processing_end = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    notes = Column(String(1000), nullable=True)
    
    # Escalation
    is_escalated = Column(Boolean, default=False, nullable=False)
    escalation_reason = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<QueueEntry(id={self.id}, person_id={self.person_id}, priority={self.priority}, status={self.status})>"
