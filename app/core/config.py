"""Core configuration settings"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "SportStatBot"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Database Configuration
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # External APIs
    ESPN_API_KEY: Optional[str] = None
    SPORTSRADAR_API_KEY: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None

    # Analytics Configuration
    ENABLE_LIVE_INGESTION: bool = True
    MOMENTUM_WINDOW_SECONDS: int = 300  # 5 minutes
    FORM_TRAJECTORY_GAMES: int = 5
    SIMILARITY_CLUSTER_COUNT: int = 10

    # Performance
    CACHE_TTL_SECONDS: int = 300
    MAX_WORKERS: int = 4


settings = Settings()
