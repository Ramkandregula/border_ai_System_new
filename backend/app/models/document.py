from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum
from datetime import datetime


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


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True, index=True)
    
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    
    # Document information
    document_number = Column(String(255), nullable=True, index=True)
    holder_name = Column(String(255), nullable=True)
    holder_date_of_birth = Column(String(50), nullable=True)
    issue_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    issuing_country = Column(String(100), nullable=True)
    
    # OCR Results
    ocr_text = Column(JSON, nullable=True)
    ocr_confidence = Column(String(50), nullable=True)
    
    # Document image
    document_image_path = Column(String(500), nullable=True)
    document_image_url = Column(String(1000), nullable=True)
    
    # Verification results
    is_authentic = Column(Boolean, nullable=True)
    verification_notes = Column(String(1000), nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<Document(id={self.id}, type={self.document_type}, status={self.status})>"
