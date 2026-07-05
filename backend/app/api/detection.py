from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import PersonCreate, PersonResponse, PersonUpdate
from app.models import Person
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/person", response_model=PersonResponse)
async def create_person_detection(
    person_create: PersonCreate,
    db: Session = Depends(get_db)
):
    """Record a person detection"""
    try:
        new_person = Person(
            detection_id=person_create.detection_id or f"DET_{uuid4()}",
            age_estimated=person_create.age_estimated,
            gender=person_create.gender,
            height=person_create.height,
            distinguishing_marks=person_create.distinguishing_marks,
            detection_frame=person_create.detection_frame,
            detection_confidence=person_create.detection_confidence,
            metadata=person_create.metadata
        )
        
        db.add(new_person)
        db.commit()
        db.refresh(new_person)
        
        logger.info(f"Person detection recorded: {new_person.detection_id}")
        return PersonResponse.from_orm(new_person)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating person detection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error recording detection"
        )


@router.get("/status", response_model=dict)
async def get_detection_status(db: Session = Depends(get_db)):
    """Get current detection status"""
    total_detected = db.query(Person).count()
    in_queue = db.query(Person).filter(Person.status == "in_queue").count()
    flagged = db.query(Person).filter(Person.status == "flagged").count()
    cleared = db.query(Person).filter(Person.status == "cleared").count()
    
    return {
        "total_detected": total_detected,
        "in_queue": in_queue,
        "flagged": flagged,
        "cleared": cleared,
        "detection_active": True
    }


@router.get("/persons", response_model=List[PersonResponse])
async def list_persons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all detected persons"""
    persons = db.query(Person).offset(skip).limit(limit).all()
    return [PersonResponse.from_orm(p) for p in persons]


@router.get("/person/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int, db: Session = Depends(get_db)):
    """Get person details"""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    return PersonResponse.from_orm(person)


@router.put("/person/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: int,
    person_update: PersonUpdate,
    db: Session = Depends(get_db)
):
    """Update person information"""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    update_data = person_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(person, field, value)
    
    db.commit()
    db.refresh(person)
    
    logger.info(f"Person updated: {person.id}")
    return PersonResponse.from_orm(person)
