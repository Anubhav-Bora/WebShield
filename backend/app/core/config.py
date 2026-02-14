"""
Application configuration using Pydantic Settings.

Loads configuration from environment variables with type validation.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Create a .env file in the backend directory with these values.
    See .env.example for reference.
    """
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # JWT Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Rate Limiting
    RATE_LIMIT_MAX_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # Replay Protection
    REPLAY_PROTECTION_WINDOW_SECONDS: int = 300  # 5 minutes
    
    # Forwarding
    FORWARDING_TIMEOUT_SECONDS: int = 10
    
    # Security
    MAX_PAYLOAD_SIZE_BYTES: int = 1_000_000  # 1MB
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env
    )


# Global settings instance
settings = Settings()
