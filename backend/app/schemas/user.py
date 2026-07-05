from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    OFFICER = "officer"
    ANALYST = "analyst"
    VIEWER = "viewer"


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)

    class Config:
        schema_extra = {
            "example": {
                "username": "officer_001",
                "password": "password123"
            }
        }


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)
    role: UserRole = UserRole.VIEWER

    class Config:
        schema_extra = {
            "example": {
                "username": "officer_001",
                "email": "officer@border.gov",
                "full_name": "John Doe",
                "password": "securepassword",
                "role": "officer"
            }
        }


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "email": "newemail@border.gov",
                "full_name": "Jane Doe",
                "role": "analyst"
            }
        }


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "officer_001",
                "email": "officer@border.gov",
                "full_name": "John Doe",
                "role": "officer",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "last_login": "2024-01-01T10:00:00Z"
            }
        }
