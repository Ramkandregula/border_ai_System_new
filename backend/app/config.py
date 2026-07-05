from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache


class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "your-secret-key")
    API_ALGORITHM: str = os.getenv("API_ALGORITHM", "HS256")
    API_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("API_TOKEN_EXPIRE_MINUTES", 30))
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://border_user:border_password@localhost:5432/border_ai_db"
    )
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000"
    ]
    
    # ML Models Configuration
    MODEL_PERSON_DETECTION: str = os.getenv("MODEL_PERSON_DETECTION", "yolov8m.pt")
    MODEL_PERSON_DETECTION_CONFIDENCE: float = float(
        os.getenv("MODEL_PERSON_DETECTION_CONFIDENCE", 0.5)
    )
    MODEL_OCR_ENGINE: str = os.getenv("MODEL_OCR_ENGINE", "tesseract")
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "/app/models")
    MAX_DETECTION_PERSONS: int = int(os.getenv("MAX_DETECTION_PERSONS", 50))
    DETECTION_FPS: int = int(os.getenv("DETECTION_FPS", 30))
    
    # Threat Analysis
    THREAT_MODEL_PATH: str = os.getenv("THREAT_MODEL_PATH", "/app/models/threat_analysis.pkl")
    THREAT_ANALYSIS_ENABLED: bool = os.getenv("THREAT_ANALYSIS_ENABLED", "true").lower() == "true"
    THREAT_THRESHOLD: float = float(os.getenv("THREAT_THRESHOLD", 0.6))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "/var/log/border_ai/app.log")
    
    # File Upload
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", 52428800))  # 50MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/uploads")
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".pdf"]
    
    # Queue Configuration
    MAX_QUEUE_SIZE: int = int(os.getenv("MAX_QUEUE_SIZE", 100))
    QUEUE_TIMEOUT_MINUTES: int = int(os.getenv("QUEUE_TIMEOUT_MINUTES", 30))
    QUEUE_PRIORITY_LEVELS: int = int(os.getenv("QUEUE_PRIORITY_LEVELS", 5))
    
    # Audit & Compliance
    AUDIT_LOGGING_ENABLED: bool = os.getenv("AUDIT_LOGGING_ENABLED", "true").lower() == "true"
    AUDIT_LOG_RETENTION_DAYS: int = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", 90))
    COMPLIANCE_MODE: bool = os.getenv("COMPLIANCE_MODE", "true").lower() == "true"
    
    # Feature Flags
    ENABLE_DETECTION: bool = os.getenv("ENABLE_DETECTION", "true").lower() == "true"
    ENABLE_OCR: bool = os.getenv("ENABLE_OCR", "true").lower() == "true"
    ENABLE_THREAT_ANALYSIS: bool = os.getenv("ENABLE_THREAT_ANALYSIS", "true").lower() == "true"
    ENABLE_QUEUE_MANAGEMENT: bool = os.getenv("ENABLE_QUEUE_MANAGEMENT", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
