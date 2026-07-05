from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAssessmentCreate(BaseModel):
    person_id: int
    behavioral_risk: Optional[float] = None
    document_risk: Optional[float] = None
    biometric_risk: Optional[float] = None
    intelligence_match_risk: Optional[float] = None
    flagged_indicators: Optional[List[str]] = None
    assessment_notes: Optional[str] = None
    threat_matches: Optional[List[Dict[str, Any]]] = None

    class Config:
        schema_extra = {
            "example": {
                "person_id": 1,
                "behavioral_risk": 0.3,
                "document_risk": 0.2,
                "biometric_risk": 0.1,
                "flagged_indicators": ["Passport_Expired"],
                "assessment_notes": "Low risk profile"
            }
        }


class RiskAssessmentResponse(BaseModel):
    id: int
    person_id: int
    risk_score: float
    risk_level: RiskLevel
    behavioral_risk: Optional[float]
    document_risk: Optional[float]
    biometric_risk: Optional[float]
    intelligence_match_risk: Optional[float]
    flagged_indicators: Optional[List[str]]
    assessment_notes: Optional[str]
    assessed_by: Optional[str]
    threat_matches: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
