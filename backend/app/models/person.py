from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    JSON,
    Enum as SQLEnum
)
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum


class PersonStatus(str, Enum):
    DETECTED = "detected"
    IN_QUEUE = "in_queue"
    UNDER_REVIEW = "under_review"
    CLEARED = "cleared"
    FLAGGED = "flagged"
    DETAINED = "detained"


class Person(Base):
    __tablename__ = "persons"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Detection identifier
    detection_id = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    # Tracking identifier (ByteTrack/DeepSORT)
    track_id = Column(
        Integer,
        index=True,
        nullable=True
    )

    # Current status
    status = Column(
        SQLEnum(PersonStatus),
        default=PersonStatus.DETECTED,
        nullable=False
    )

    # Physical characteristics
    age_estimated = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)
    height = Column(Float, nullable=True)
    distinguishing_marks = Column(String(500), nullable=True)

    # Face recognition
    face_embedding = Column(
        JSON,
        nullable=True
    )  # stores list of 512 floats

    face_confidence = Column(
        Float,
        nullable=True
    )

    # Detection information
    detection_frame = Column(
        String(500),
        nullable=True
    )

    detection_confidence = Column(
        Float,
        nullable=True
    )

    # AI risk analysis
    risk_score = Column(
        Float,
        default=0.0
    )

    threat_level = Column(
        String(20),
        default="LOW"
    )

    # Extra information
    person_metadata = Column(
        JSON,
        nullable=True
    )

    # Timestamps
    detected_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return (
            f"<Person("
            f"id={self.id}, "
            f"detection_id='{self.detection_id}', "
            f"track_id={self.track_id}, "
            f"status='{self.status}', "
            f"risk_score={self.risk_score}"
            f")>"
        )
