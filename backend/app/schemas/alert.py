from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertCreate(BaseModel):
    person_id: Optional[int] = None
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=1000)
    severity: AlertSeverity = AlertSeverity.WARNING
    alert_type: str = Field(..., max_length=100)
    details: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "person_id": 1,
                "title": "High Risk Individual Detected",
                "description": "Person matched threat database",
                "severity": "critical",
                "alert_type": "threat_match"
            }
        }


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[str] = None
    acknowledgment_notes: Optional[str] = None
    resolution_notes: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    person_id: Optional[int]
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    alert_type: str
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
