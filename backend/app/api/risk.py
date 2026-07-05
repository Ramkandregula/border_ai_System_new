from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import RiskAssessmentCreate, RiskAssessmentResponse
from app.models import RiskAssessment, Person
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def calculate_risk_level(risk_score: float) -> str:
    """Calculate risk level based on score"""
    if risk_score >= 0.8:
        return "critical"
    elif risk_score >= 0.6:
        return "high"
    elif risk_score >= 0.4:
        return "medium"
    else:
        return "low"


@router.post("/calculate", response_model=RiskAssessmentResponse)
async def calculate_risk(
    assessment_create: RiskAssessmentCreate,
    db: Session = Depends(get_db)
):
    """Calculate risk score for a person"""
    try:
        # Verify person exists
        person = db.query(Person).filter(Person.id == assessment_create.person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found"
            )
        
        # Calculate risk score
        risk_factors = []
        if assessment_create.behavioral_risk:
            risk_factors.append(assessment_create.behavioral_risk)
        if assessment_create.document_risk:
            risk_factors.append(assessment_create.document_risk)
        if assessment_create.biometric_risk:
            risk_factors.append(assessment_create.biometric_risk)
        if assessment_create.intelligence_match_risk:
            risk_factors.append(assessment_create.intelligence_match_risk)
        
        risk_score = sum(risk_factors) / len(risk_factors) if risk_factors else 0.0
        risk_level = calculate_risk_level(risk_score)
        
        # Create assessment
        new_assessment = RiskAssessment(
            person_id=assessment_create.person_id,
            risk_score=risk_score,
            risk_level=risk_level,
            behavioral_risk=assessment_create.behavioral_risk,
            document_risk=assessment_create.document_risk,
            biometric_risk=assessment_create.biometric_risk,
            intelligence_match_risk=assessment_create.intelligence_match_risk,
            flagged_indicators=assessment_create.flagged_indicators,
            assessment_notes=assessment_create.assessment_notes,
            threat_matches=assessment_create.threat_matches
        )
        
        db.add(new_assessment)
        db.commit()
        db.refresh(new_assessment)
        
        logger.info(f"Risk assessment calculated for person {assessment_create.person_id}: {risk_level}")
        return RiskAssessmentResponse.from_orm(new_assessment)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error calculating risk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating risk"
        )


@router.get("/history", response_model=List[RiskAssessmentResponse])
async def get_risk_history(
    person_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get risk assessment history"""
    query = db.query(RiskAssessment)
    if person_id:
        query = query.filter(RiskAssessment.person_id == person_id)
    
    assessments = query.offset(skip).limit(limit).all()
    return [RiskAssessmentResponse.from_orm(a) for a in assessments]


@router.get("/threats", response_model=List[dict])
async def get_threats(db: Session = Depends(get_db)):
    """Get threat list"""
    # This would typically query a threat database
    return [
        {"id": 1, "name": "Watch List Match", "severity": "critical"},
        {"id": 2, "name": "Document Fraud", "severity": "high"},
        {"id": 3, "name": "Behavioral Anomaly", "severity": "medium"}
    ]
