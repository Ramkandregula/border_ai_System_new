import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address
    
    Args:
        email: Email address
        
    Returns:
        Tuple of (is_valid, message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, "Valid email"
    return False, "Invalid email format"


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number
    
    Args:
        phone: Phone number
        
    Returns:
        Tuple of (is_valid, message)
    """
    # Remove common separators
    cleaned = re.sub(r'[\s\-().]', '', phone)
    
    # Check if valid international format
    if re.match(r'^\+?1?\d{9,15}$', cleaned):
        return True, "Valid phone number"
    return False, "Invalid phone format"


def validate_document_number(doc_number: str, doc_type: str = None) -> Tuple[bool, str]:
    """
    Validate document number
    
    Args:
        doc_number: Document number
        doc_type: Document type (passport, id_card, etc.)
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not doc_number or len(doc_number) < 5:
        return False, "Document number too short"
    
    if doc_type == "passport":
        # Passport: Usually 6-9 alphanumeric characters
        if re.match(r'^[A-Z0-9]{6,9}$', doc_number):
            return True, "Valid passport number"
        return False, "Invalid passport format"
    
    elif doc_type == "id_card":
        # ID Card: Usually 10-12 characters
        if re.match(r'^[A-Z0-9]{10,12}$', doc_number):
            return True, "Valid ID card number"
        return False, "Invalid ID card format"
    
    else:
        # Generic validation
        if re.match(r'^[A-Z0-9]{5,20}$', doc_number):
            return True, "Valid document number"
        return False, "Invalid document format"


def validate_date(date_str: str, format: str = "%Y-%m-%d") -> Tuple[bool, str]:
    """
    Validate date string
    
    Args:
        date_str: Date string
        format: Expected date format
        
    Returns:
        Tuple of (is_valid, message)
    """
    from datetime import datetime
    try:
        datetime.strptime(date_str, format)
        return True, "Valid date"
    except ValueError:
        return False, f"Invalid date format. Expected: {format}"


def validate_risk_score(score: float) -> Tuple[bool, str]:
    """
    Validate risk score
    
    Args:
        score: Risk score
        
    Returns:
        Tuple of (is_valid, message)
    """
    if isinstance(score, (int, float)) and 0.0 <= score <= 1.0:
        return True, "Valid risk score"
    return False, "Risk score must be between 0.0 and 1.0"
