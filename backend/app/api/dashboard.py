from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Person, Document, RiskAssessment, QueueEntry, Alert
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/stats", response_model=dict)
async def get_statistics(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_persons = db.query(Person).count()
    persons_today = db.query(Person).filter(Person.created_at >= today).count()
    high_risk = db.query(Person).filter(Person.status == "flagged").count()
    cleared = db.query(Person).filter(Person.status == "cleared").count()
    
    queue_waiting = db.query(QueueEntry).filter(QueueEntry.status == "waiting").count()
    
    total_documents = db.query(Document).count()
    documents_verified = db.query(Document).filter(Document.status == "verified").count()
    
    critical_alerts = db.query(Alert).filter(Alert.severity == "critical", Alert.status == "active").count()
    
    return {
        "total_persons_detected": total_persons,
        "persons_today": persons_today,
        "high_risk_detected": high_risk,
        "persons_cleared": cleared,
        "queue_waiting": queue_waiting,
        "total_documents": total_documents,
        "documents_verified": documents_verified,
        "critical_alerts": critical_alerts,
        "timestamp": now.isoformat()
    }


@router.get("/analytics", response_model=dict)
async def get_analytics(db: Session = Depends(get_db)):
    """Get analytics data"""
    # Risk distribution
    critical_count = db.query(RiskAssessment).filter(RiskAssessment.risk_level == "critical").count()
    high_count = db.query(RiskAssessment).filter(RiskAssessment.risk_level == "high").count()
    medium_count = db.query(RiskAssessment).filter(RiskAssessment.risk_level == "medium").count()
    low_count = db.query(RiskAssessment).filter(RiskAssessment.risk_level == "low").count()
    
    return {
        "risk_distribution": {
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        },
        "document_status": {
            "verified": db.query(Document).filter(Document.status == "verified").count(),
            "pending": db.query(Document).filter(Document.status == "pending").count(),
            "rejected": db.query(Document).filter(Document.status == "rejected").count(),
            "suspicious": db.query(Document).filter(Document.status == "suspicious").count()
        },
        "person_status": {
            "detected": db.query(Person).filter(Person.status == "detected").count(),
            "in_queue": db.query(Person).filter(Person.status == "in_queue").count(),
            "under_review": db.query(Person).filter(Person.status == "under_review").count(),
            "cleared": db.query(Person).filter(Person.status == "cleared").count(),
            "flagged": db.query(Person).filter(Person.status == "flagged").count(),
            "detained": db.query(Person).filter(Person.status == "detained").count()
        }
    }


@router.get("/alerts", response_model=list)
async def get_alerts(db: Session = Depends(get_db)):
    """Get active alerts"""
    alerts = db.query(Alert).filter(Alert.status == "active").order_by(Alert.severity.desc()).limit(50).all()
    return [
        {
            "id": a.id,
            "person_id": a.person_id,
            "title": a.title,
            "description": a.description,
            "severity": a.severity,
            "alert_type": a.alert_type,
            "created_at": a.created_at.isoformat()
        }
        for a in alerts
    ]
