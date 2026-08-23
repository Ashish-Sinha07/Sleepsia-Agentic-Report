import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = ConfigDict(
        extra='ignore',  # Ignore extra environment variables
        env_file=".env",
        env_file_encoding="utf-8"
    )

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

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    SQL_ECHO: bool = False

    # Analytics
    DEFAULT_DAYS_BACK: int = 30
    MAX_DATE_RANGE_DAYS: int = 365

    # SMTP Configuration for Report Distribution
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Sleepsia Reports")

    # Report Scheduling
    REPORT_SCHEDULE_HOUR: int = int(os.getenv("REPORT_SCHEDULE_HOUR", "6"))
    REPORT_SCHEDULE_MINUTE: int = int(os.getenv("REPORT_SCHEDULE_MINUTE", "0"))
    REPORT_RECIPIENT_EMAIL: str = os.getenv("REPORT_RECIPIENT_EMAIL", "ningthoujamrohit91@gmail.com")
    REPORT_CC_EMAILS: str = os.getenv("REPORT_CC_EMAILS", "")
    REPORT_BCC_EMAILS: str = os.getenv("REPORT_BCC_EMAILS", "")

    # Anthropic API
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    @property
    def DATABASE_URL(self) -> str:
        """Build SQLAlchemy database URL."""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
