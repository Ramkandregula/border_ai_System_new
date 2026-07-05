from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import DocumentCreate, DocumentResponse, DocumentUpdate
from app.models import Document
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/scan", response_model=DocumentResponse)
async def scan_document(
    document_create: DocumentCreate,
    db: Session = Depends(get_db)
):
    """Scan and create document record"""
    try:
        new_document = Document(
            person_id=document_create.person_id,
            document_type=document_create.document_type,
            document_number=document_create.document_number,
            holder_name=document_create.holder_name,
            holder_date_of_birth=document_create.holder_date_of_birth,
            issue_date=document_create.issue_date,
            expiry_date=document_create.expiry_date,
            issuing_country=document_create.issuing_country,
            document_image_path=document_create.document_image_path
        )
        
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        
        logger.info(f"Document scanned: {new_document.id}")
        return DocumentResponse.from_orm(new_document)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error scanning document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error scanning document"
        )


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all documents"""
    documents = db.query(Document).offset(skip).limit(limit).all()
    return [DocumentResponse.from_orm(d) for d in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document details"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return DocumentResponse.from_orm(document)


@router.post("/{document_id}/verify", response_model=DocumentResponse)
async def verify_document(
    document_id: int,
    is_authentic: bool,
    verification_notes: str = None,
    db: Session = Depends(get_db)
):
    """Verify document authenticity"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document.is_authentic = is_authentic
    document.verification_notes = verification_notes
    document.status = "verified" if is_authentic else "rejected"
    
    db.commit()
    db.refresh(document)
    
    logger.info(f"Document verified: {document.id}")
    return DocumentResponse.from_orm(document)
