from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum
from datetime import datetime


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)
    
    # Risk scoring
    risk_score = Column(Float, nullable=False)  # 0.0 to 1.0
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    
    # Assessment factors
    behavioral_risk = Column(Float, nullable=True)
    document_risk = Column(Float, nullable=True)
    biometric_risk = Column(Float, nullable=True)
    intelligence_match_risk = Column(Float, nullable=True)
    
    # Assessment details
    flagged_indicators = Column(JSON, nullable=True)  # List of risk indicators
    assessment_notes = Column(String(1000), nullable=True)
    
    # Assessment metadata
    assessed_by = Column(String(255), nullable=True)  # Officer ID
    is_manual_override = Column(Boolean, default=False, nullable=False)
    
    # Threat information
    threat_matches = Column(JSON, nullable=True)  # List of matched threats
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<RiskAssessment(id={self.id}, person_id={self.person_id}, risk_level={self.risk_level})>"
