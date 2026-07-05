import logging
from datetime import datetime
from uuid import uuid4
import random
import string

logger = logging.getLogger(__name__)


def generate_id(prefix: str = "") -> str:
    """
    Generate unique ID
    
    Args:
        prefix: Optional prefix
        
    Returns:
        Generated ID
    """
    unique_id = str(uuid4()).replace("-", "")
    return f"{prefix}_{unique_id}" if prefix else unique_id


def generate_detection_id() -> str:
    """
    Generate detection ID
    
    Returns:
        Detection ID
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.digits, k=6))
    return f"DET_{timestamp}_{random_suffix}"


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format
    
    Returns:
        ISO format timestamp
    """
    return datetime.utcnow().isoformat()


def calculate_age(birth_date: str, date_format: str = "%Y-%m-%d") -> int:
    """
    Calculate age from birth date
    
    Args:
        birth_date: Birth date string
        date_format: Date format
        
    Returns:
        Age in years
    """
    try:
        born = datetime.strptime(birth_date, date_format)
        today = datetime.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    except ValueError:
        logger.error(f"Invalid date format for age calculation: {birth_date}")
        return None


def get_file_extension(filename: str) -> str:
    """
    Get file extension
    
    Args:
        filename: File name
        
    Returns:
        File extension
    """
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def format_bytes(bytes_size: int) -> str:
    """
    Format bytes to human readable format
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def paginate(items: list, page: int = 1, page_size: int = 20) -> dict:
    """
    Paginate items
    
    Args:
        items: List of items
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        Pagination dict with items and metadata
    """
    total = len(items)
    total_pages = (total + page_size - 1) // page_size
    
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "items": items[start:end],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }
