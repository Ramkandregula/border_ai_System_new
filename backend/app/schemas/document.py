from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    PASSPORT = "passport"
    VISA = "visa"
    ID_CARD = "id_card"
    DRIVER_LICENSE = "driver_license"
    TRAVEL_PERMIT = "travel_permit"
    OTHER = "other"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    SUSPICIOUS = "suspicious"


class DocumentCreate(BaseModel):
    person_id: Optional[int] = None
    document_type: DocumentType
    document_number: Optional[str] = Field(None, max_length=255)
    holder_name: Optional[str] = Field(None, max_length=255)
    holder_date_of_birth: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    issuing_country: Optional[str] = Field(None, max_length=100)
    document_image_path: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "person_id": 1,
                "document_type": "passport",
                "document_number": "AB1234567",
                "holder_name": "John Doe",
                "issuing_country": "US"
            }
        }


class DocumentUpdate(BaseModel):
    status: Optional[DocumentStatus] = None
    is_authentic: Optional[bool] = None
    verification_notes: Optional[str] = None
    ocr_text: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    id: int
    person_id: Optional[int]
    document_type: DocumentType
    status: DocumentStatus
    document_number: Optional[str]
    holder_name: Optional[str]
    holder_date_of_birth: Optional[str]
    issue_date: Optional[str]
    expiry_date: Optional[str]
    issuing_country: Optional[str]
    is_authentic: Optional[bool]
    verification_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
