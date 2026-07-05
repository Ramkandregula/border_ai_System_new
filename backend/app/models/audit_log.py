from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum
from datetime import datetime


class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    VERIFY = "verify"
    ESCALATE = "escalate"
    CLEAR = "clear"
    DETAIN = "detain"
    LOGIN = "login"
    LOGOUT = "logout"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Action information
    action = Column(SQLEnum(AuditAction), nullable=False)
    resource_type = Column(String(100), nullable=False)  # person, document, queue_entry, etc.
    resource_id = Column(String(255), nullable=False)
    
    # User information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(255), nullable=True)
    
    # Change details
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changes_description = Column(Text, nullable=True)
    
    # Request information
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Status
    status = Column(String(50), nullable=True)  # success, failure, etc.
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource_type={self.resource_type})>"
