"""Configuration settings for the Sleepsia Agentic Reporting System."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with support for environment variables."""

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost:3306/sleepsia_db"
    )

    # API
    api_title: str = "Sleepsia Agentic Reporting System"
    api_version: str = "1.0.0"

    # Agent settings
    use_mock_data: bool = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

    # LLM settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    # Reporting
    reports_output_dir: str = os.path.join(os.path.dirname(__file__), "..", "reports")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
