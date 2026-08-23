import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("APP_ENV", "development") == "development"

    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "sleepsia_reporting")
    DB_USER: str = os.getenv("DB_USER", "sleepsia")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "sleepsia")

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_TITLE: str = "Sleepsia Analytics API"
    API_VERSION: str = "1.0.0"

    # CORS - comma-separated list of allowed origins, e.g.
    # CORS_ORIGINS=http://localhost:3000,https://reports.sleepsia.com
    # (kept as a plain string field, not list, so pydantic-settings doesn't
    # try to JSON-decode the env var and crash on startup)
    CORS_ORIGINS_RAW: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:5174,"
        "http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:5174",
    )

    @property
    def CORS_ORIGINS(self) -> list:
        """Parsed list of allowed CORS origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    # Logging
    LOG_LEVEL: str = "INFO"
    SQL_ECHO: bool = False

    # Analytics
    DEFAULT_DAYS_BACK: int = 30
    MAX_DATE_RANGE_DAYS: int = 365

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def DATABASE_URL(self) -> str:
        """Build SQLAlchemy database URL."""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
