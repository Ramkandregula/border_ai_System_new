from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PersonStatus(str, Enum):
    DETECTED = "detected"
    IN_QUEUE = "in_queue"
    UNDER_REVIEW = "under_review"
    CLEARED = "cleared"
    FLAGGED = "flagged"
    DETAINED = "detained"


class PersonCreate(BaseModel):
    detection_id: str = Field(..., max_length=255)
    age_estimated: Optional[int] = None
    gender: Optional[str] = Field(None, max_length=50)
    height: Optional[float] = None
    distinguishing_marks: Optional[str] = Field(None, max_length=500)
    detection_frame: Optional[str] = None
    detection_confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "detection_id": "DET_001_2024",
                "age_estimated": 35,
                "gender": "male",
                "height": 180,
                "distinguishing_marks": "Scar on left cheek",
                "detection_confidence": 0.95
            }
        }


class PersonUpdate(BaseModel):
    status: Optional[PersonStatus] = None
    age_estimated: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    distinguishing_marks: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PersonResponse(BaseModel):
    id: int
    detection_id: str
    status: PersonStatus
    age_estimated: Optional[int]
    gender: Optional[str]
    height: Optional[float]
    distinguishing_marks: Optional[str]
    detection_confidence: Optional[float]
    detected_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
