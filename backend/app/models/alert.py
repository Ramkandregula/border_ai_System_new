from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum
from datetime import datetime


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True, index=True)
    
    # Alert information
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.WARNING, nullable=False)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE, nullable=False)
    
    # Alert type
    alert_type = Column(String(100), nullable=False)  # threat_match, behavior_anomaly, etc.
    
    # Details
    details = Column(JSON, nullable=True)
    
    # Acknowledgment
    acknowledged_by = Column(String(255), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledgment_notes = Column(String(500), nullable=True)
    
    # Resolution
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<Alert(id={self.id}, severity={self.severity}, status={self.status})>"
