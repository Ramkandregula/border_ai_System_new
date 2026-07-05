from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


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


class QueueEntryCreate(BaseModel):
    person_id: int
    priority: QueuePriority = QueuePriority.NORMAL
    notes: Optional[str] = Field(None, max_length=1000)

    class Config:
        schema_extra = {
            "example": {
                "person_id": 1,
                "priority": "normal",
                "notes": "Requires additional document verification"
            }
        }


class QueueEntryUpdate(BaseModel):
    priority: Optional[QueuePriority] = None
    status: Optional[QueueStatus] = None
    assigned_officer: Optional[str] = None
    notes: Optional[str] = None
    is_escalated: Optional[bool] = None
    escalation_reason: Optional[str] = None


class QueueEntryResponse(BaseModel):
    id: int
    person_id: int
    queue_number: int
    priority: QueuePriority
    status: QueueStatus
    assigned_officer: Optional[str]
    notes: Optional[str]
    is_escalated: bool
    escalation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
