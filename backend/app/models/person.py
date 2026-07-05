from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum
from datetime import datetime


class PersonStatus(str, Enum):
    DETECTED = "detected"
    IN_QUEUE = "in_queue"
    UNDER_REVIEW = "under_review"
    CLEARED = "cleared"
    FLAGGED = "flagged"
    DETAINED = "detained"


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(SQLEnum(PersonStatus), default=PersonStatus.DETECTED, nullable=False)
    
    # Physical characteristics
    age_estimated = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)
    height = Column(Float, nullable=True)  # in cm
    distinguishing_marks = Column(String(500), nullable=True)
    
    # Detection data
    face_embedding = Column(String(500), nullable=True)  # Base64 encoded
    detection_frame = Column(String(500), nullable=True)  # S3 or local path
    detection_confidence = Column(Float, nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<Person(id={self.id}, detection_id={self.detection_id}, status={self.status})>"
