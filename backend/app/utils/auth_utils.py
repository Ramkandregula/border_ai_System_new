import logging
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.config import settings
from datetime import datetime

logger = logging.getLogger(__name__)

security = HTTPBearer()


def verify_token(token: str) -> dict:
    """
    Verify JWT token
    
    Args:
        token: JWT token
        
    Returns:
        Token payload
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """
    Get current user from token
    
    Args:
        credentials: HTTP credentials
        
    Returns:
        Current user data
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    username = payload.get("username")
    role = payload.get("role")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims"
        )
    
    return {
        "user_id": int(user_id),
        "username": username,
        "role": role
    }


def is_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Check if user is admin
    
    Args:
        current_user: Current user
        
    Returns:
        Current user if admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def is_officer(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Check if user is officer
    
    Args:
        current_user: Current user
        
    Returns:
        Current user if officer
    """
    if current_user.get("role") not in ["admin", "officer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Officer access required"
        )
    return current_user
