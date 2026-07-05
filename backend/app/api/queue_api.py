from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import QueueEntryCreate, QueueEntryResponse, QueueEntryUpdate
from app.models import QueueEntry, Person
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/status", response_model=dict)
async def get_queue_status(db: Session = Depends(get_db)):
    """Get queue status"""
    waiting = db.query(QueueEntry).filter(QueueEntry.status == "waiting").count()
    in_progress = db.query(QueueEntry).filter(QueueEntry.status == "in_progress").count()
    completed = db.query(QueueEntry).filter(QueueEntry.status == "completed").count()
    
    return {
        "waiting": waiting,
        "in_progress": in_progress,
        "completed": completed,
        "total": waiting + in_progress + completed
    }


@router.post("/person", response_model=QueueEntryResponse)
async def add_to_queue(
    queue_entry_create: QueueEntryCreate,
    db: Session = Depends(get_db)
):
    """Add person to queue"""
    try:
        # Verify person exists
        person = db.query(Person).filter(Person.id == queue_entry_create.person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found"
            )
        
        # Get next queue number
        last_entry = db.query(QueueEntry).order_by(QueueEntry.queue_number.desc()).first()
        next_queue_number = (last_entry.queue_number + 1) if last_entry else 1
        
        new_entry = QueueEntry(
            person_id=queue_entry_create.person_id,
            queue_number=next_queue_number,
            priority=queue_entry_create.priority,
            notes=queue_entry_create.notes
        )
        
        # Update person status
        person.status = "in_queue"
        
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        logger.info(f"Person added to queue: {queue_entry_create.person_id}")
        return QueueEntryResponse.from_orm(new_entry)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding to queue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding to queue"
        )


@router.get("", response_model=List[QueueEntryResponse])
async def list_queue(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List queue entries"""
    entries = db.query(QueueEntry).order_by(QueueEntry.priority).offset(skip).limit(limit).all()
    return [QueueEntryResponse.from_orm(e) for e in entries]


@router.put("/{queue_entry_id}", response_model=QueueEntryResponse)
async def update_queue_entry(
    queue_entry_id: int,
    queue_update: QueueEntryUpdate,
    db: Session = Depends(get_db)
):
    """Update queue entry"""
    entry = db.query(QueueEntry).filter(QueueEntry.id == queue_entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue entry not found"
        )
    
    update_data = queue_update.dict(exclude_unset=True)
    
    # Handle status transitions
    if queue_update.status == "in_progress":
        entry.processing_start = datetime.utcnow()
    elif queue_update.status == "completed":
        entry.processing_end = datetime.utcnow()
        # Update person status
        person = db.query(Person).filter(Person.id == entry.person_id).first()
        if person:
            person.status = "cleared"
    
    for field, value in update_data.items():
        setattr(entry, field, value)
    
    db.commit()
    db.refresh(entry)
    
    logger.info(f"Queue entry updated: {queue_entry_id}")
    return QueueEntryResponse.from_orm(entry)
