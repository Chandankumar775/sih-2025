"""
Application Configuration
Loads environment variables and provides settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Info
    APP_NAME: str = "WatchTower"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str = ""
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Services
    GOOGLE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:8080,http://localhost:5173,http://localhost:3000"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = "application/pdf,image/jpeg,image/png,image/gif"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        return [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
